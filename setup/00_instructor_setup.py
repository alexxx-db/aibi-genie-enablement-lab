# Databricks notebook source
# MAGIC %md
# MAGIC # 🛠️ Instructor Setup - AI/BI Genie Enablement Lab
# MAGIC
# MAGIC **Audience: instructor only.** Learners never run this notebook.
# MAGIC
# MAGIC The lab is self-provisioning: each learner's first notebook run creates
# MAGIC their personal schema and generates their own (deterministic, identical)
# MAGIC copy of the dataset. So setup is a **preflight**, not a build:
# MAGIC 1. Verify the lab catalog (nobody needs CREATE CATALOG)
# MAGIC 2. Grant learners `USE CATALOG` + `CREATE SCHEMA`
# MAGIC 3. Self-test: generate your own copy and verify the ambiguity is reproducible

# COMMAND ----------

# MAGIC %md ## 1 · Configure

# COMMAND ----------

import os, sys

sys.dont_write_bytecode = True  # never write __pycache__ into the Git folder
repo_root = os.path.dirname(os.getcwd())
sys.path.insert(0, os.path.join(repo_root, "_internal"))

from labkit.config import LabContext, list_datasets
from labkit.notebook import _resolve_catalog

dbutils.widgets.dropdown("dataset", "retail_sales", list_datasets(repo_root), "1. Dataset bundle")
dbutils.widgets.text("catalog", "aibi_genie_lab", "2. Lab catalog")
dbutils.widgets.text("learner_group", "", "3. Learner group (REQUIRED)")
dbutils.widgets.dropdown("fan_out", "yes", ["yes", "no"], "4. Copy lab to group members")

catalog = _resolve_catalog(spark, dbutils.widgets.get("catalog"))
ctx = LabContext.load(
    repo_root,
    dataset_name=dbutils.widgets.get("dataset"),
    current_user=spark.sql("SELECT current_user()").first()[0],
    catalog=catalog,
)

# The learner group is REQUIRED and must exist: grants and notebook fan-out
# both target exactly this group (run setup once per cohort/group).
from databricks.sdk import WorkspaceClient

_w = WorkspaceClient()
learner_group = dbutils.widgets.get("learner_group").strip()
assert learner_group, (
    "Set the '3. Learner group' widget to the group for THIS session "
    "(e.g. genie-lab-cohort-1). Create it under Settings → Identity and "
    "access → Groups, and add the attendees."
)

def group_member_emails(group_name: str) -> list[str]:
    found = list(_w.groups.list(filter=f'displayName eq "{group_name}"'))
    if not found:
        raise RuntimeError(
            f"Group '{group_name}' doesn't exist in this workspace. Create it "
            "(Settings → Identity and access → Groups), add the attendees, "
            "and re-run."
        )
    members = _w.groups.get(found[0].id).members or []
    emails = [
        _w.users.get(m.ref.split("/")[1]).user_name
        for m in members
        if m.ref and m.ref.startswith("Users/")
    ]
    if not emails:
        raise RuntimeError(
            f"Group '{group_name}' has no user members - add the attendees "
            "and re-run. (Nested groups aren't expanded.)"
        )
    return sorted(emails)

learners = group_member_emails(learner_group)

from labkit.notebook import ROOT_POINTER

with open(ROOT_POINTER, "w") as f:
    f.write(repo_root)
print(f"✓ published lab location to {ROOT_POINTER}")
print(f"Dataset : {ctx.dataset_name} - {ctx.raw['display_name']}")
print(f"Catalog : {ctx.catalog}")
print(f"Learners: {learner_group} ({len(learners)} members)")
for u in learners:
    print(f"  - {u}")
print(f"Each learner gets: {ctx.catalog}.user_<name> (data + metric view)")

# COMMAND ----------

# MAGIC %md ## 2 · Grant learner access
# MAGIC Learners need exactly two privileges on the catalog: `USE CATALOG` and
# MAGIC `CREATE SCHEMA` (their first notebook run creates `user_<name>` and fills
# MAGIC it with data they own).

# COMMAND ----------

grants = [
    f"GRANT USE CATALOG ON CATALOG {ctx.catalog} TO `{learner_group}`",
    f"GRANT CREATE SCHEMA ON CATALOG {ctx.catalog} TO `{learner_group}`",
]
for g in grants:
    spark.sql(g)
    print(f"✓ {g}")

# Learners also need READ on this Git folder: START_HERE copies notebooks out
# of it, and the copies import the lab code from it. (Without this grant,
# other users can't see anything under your user folder.)
from databricks.sdk.service.workspace import (
    RepoAccessControlRequest, RepoPermissionLevel)

_status = _w.workspace.get_status(repo_root)
if str(getattr(_status, "object_type", "")).endswith("REPO"):
    _w.repos.set_permissions(str(_status.object_id), access_control_list=[
        RepoAccessControlRequest(group_name="users",
                                 permission_level=RepoPermissionLevel.CAN_READ)])
    print("✓ granted CAN_READ on the lab Git folder to workspace group 'users'")
else:
    print("⚠️ lab folder is not a Git folder - grant read access to learners manually")

# CAN USE on a SQL warehouse: Genie spaces, metric view queries and Catalog
# Explorer all need one. Grants on the first serverless (else first) warehouse.
from databricks.sdk.service.sql import (
    WarehouseAccessControlRequest, WarehousePermissionLevel)

_warehouses = list(_w.warehouses.list())
assert _warehouses, "No SQL warehouse in this workspace - create one first."
_wh = next((x for x in _warehouses
            if getattr(x, "enable_serverless_compute", False)), _warehouses[0])
_w.warehouses.update_permissions(_wh.id, access_control_list=[
    WarehouseAccessControlRequest(group_name=learner_group,
                                  permission_level=WarehousePermissionLevel.CAN_USE)])
print(f"✓ granted CAN USE on warehouse '{_wh.name}' to '{learner_group}'")
print(f"  → tell learners to pick warehouse: {_wh.name}")

# COMMAND ----------

# MAGIC %md ## 3 · Fan out the lab to the learner group
# MAGIC Copies the module notebooks into the home folder of **every member of the
# MAGIC learner group** - each gets `/Users/<them>/<name>_aibi-genie-lab/`, so
# MAGIC nobody shares a notebook. Existing copies are left untouched (safe to
# MAGIC re-run mid-session; late joiners can also self-serve via
# MAGIC `lab/00_START_HERE`). Running multiple cohorts? Run setup once per group.

# COMMAND ----------

if dbutils.widgets.get("fan_out") == "yes":
    from databricks.sdk.service.workspace import ExportFormat, ImportFormat, Language

    src = os.path.join(repo_root, "lab")
    modules = {}
    for obj in _w.workspace.list(src):
        name = obj.path.rsplit("/", 1)[1]
        # numbered modules plus _bootstrap (modules %run it), not 00_START_HERE
        if (name[:2].isdigit() and not name.startswith("00")) or name == "_bootstrap":
            modules[name] = _w.workspace.export(obj.path, format=ExportFormat.SOURCE).content

    from labkit.config import sanitize_user

    print(f"fanning out {len(modules)} notebooks to {len(learners)} members of '{learner_group}'…")
    for u in learners:
        dest = f"/Users/{u}/{sanitize_user(u)}_aibi-genie-lab"
        _w.workspace.mkdirs(dest)
        fresh = 0
        for name, content in modules.items():
            try:
                _w.workspace.import_(f"{dest}/{name}", content=content,
                                     format=ImportFormat.SOURCE,
                                     language=Language.PYTHON, overwrite=False)
                fresh += 1
            except Exception:
                pass  # already has it - never clobber a learner's work
        print(f"  ✓ {u:<45} ({fresh} new)")
else:
    print("skipped - learners self-serve via lab/00_START_HERE")

# COMMAND ----------

# MAGIC %md ## 4 · Self-test: generate your copy & reproduce the ambiguity
# MAGIC This does exactly what every learner's first run will do - creates *your*
# MAGIC `user_<name>` schema and dataset - then verifies the lab's core promise:
# MAGIC each defensible definition of the headline metric returns a **different
# MAGIC number**. (Datagen is deterministic, so learners will see these exact
# MAGIC numbers too.)

# COMMAND ----------

from labkit.datagen import ensure_data

generated = ensure_data(spark, ctx)
print(("✓ generated" if generated else "✓ already present") +
      f": {ctx.catalog}.{ctx.user_schema}")
for t, fqn in ctx.data_table_fqns().items():
    print(f"  {fqn:<60} {spark.table(fqn).count():>8,} rows")

# COMMAND ----------

amb = ctx.section("ambiguity")
print(f"Ambiguous metric: {amb['metric']}\n")
results = []
for variant in amb["sql_variants"]:
    value = spark.sql(variant["sql"]).first()[0]
    results.append((variant["label"], value))
    print(f"{variant['label']:<55} -> {value:,}")

distinct = len({v for _, v in results})
assert distinct == len(results), (
    "⚠️ Some revenue variants returned the SAME number - the ambiguity demo "
    "will fall flat. Re-check the dataset bundle or adjust the seed."
)
print(f"\n✓ Ambiguity reproduced: {distinct} definitions, {distinct} different answers.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Done
# MAGIC Every learner now has the lab at **`Workspace → Home → <name>_aibi-genie-lab`** - 
# MAGIC they start with `01_explore_the_data`. Late joiners: run
# MAGIC `lab/00_START_HERE` in this Git folder once.
# MAGIC
# MAGIC Before the session, also confirm:
# MAGIC - Learners have **CAN USE** on a serverless SQL warehouse
# MAGIC - Genie is enabled in this workspace, and learners can create Genie spaces
# MAGIC - Tell learners the **catalog name** in case auto-detection picks wrong
# MAGIC   (they'd set the `Catalog` widget)
# MAGIC - (Optional) run `lab/01`-`05` yourself as a dry run
