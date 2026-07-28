# Databricks notebook source
# MAGIC %md
# MAGIC # 🧹 Teardown - AI/BI Genie Enablement Lab
# MAGIC
# MAGIC **Instructor only.** Drops every `user_*` schema the lab created in the
# MAGIC catalog - data copies and metric views. The **catalog itself is never
# MAGIC touched** (it's the workspace's).
# MAGIC
# MAGIC ⚠️ Genie spaces are *not* deleted here - they belong to each learner.
# MAGIC Ask learners to delete their spaces, or remove them via the Genie UI/API.

# COMMAND ----------

dbutils.widgets.text("catalog", "aibi_genie_lab", "Lab catalog")
dbutils.widgets.dropdown("confirm", "no", ["no", "yes"], "Really drop user_* schemas?")

import os, sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.getcwd()), "_internal"))
from labkit.notebook import _resolve_catalog

catalog = _resolve_catalog(spark, dbutils.widgets.get("catalog"))
schemas = [
    r.databaseName
    for r in spark.sql(f"SHOW SCHEMAS IN {catalog}").collect()
    if r.databaseName.startswith("user_")
]
print(f"Catalog: {catalog}")
print(f"Would drop {len(schemas)} schema(s): {', '.join(schemas) or '(none)'}")

# COMMAND ----------

if dbutils.widgets.get("confirm") != "yes":
    print(
        "🔒 Safety check: nothing was dropped.\n"
        "Set the 'Really drop user_* schemas?' widget (top of this notebook) "
        "to 'yes' and re-run this cell."
    )
elif not schemas:
    print(f"Nothing to do - no user_* schemas in {catalog}.")
else:
    for s in schemas:
        spark.sql(f"DROP SCHEMA IF EXISTS {catalog}.{s} CASCADE")
        print(f"✓ dropped {catalog}.{s}")
