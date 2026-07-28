# Databricks notebook source
# MAGIC %md
# MAGIC # 👋 START HERE
# MAGIC
# MAGIC Welcome to the **AI/BI Genie Lab**! One thing before you begin: everyone
# MAGIC needs their **own copy** of the lab notebooks (if we all ran these shared
# MAGIC ones, we'd overwrite each other's results).
# MAGIC
# MAGIC **Click ▶️ Run all.** The cell below copies the lab into your home folder
# MAGIC and gives you a link to your personal copy. That's it.
# MAGIC
# MAGIC ⚠️ Re-running this later **resets** the selected notebooks to the originals.
# MAGIC
# MAGIC *(Tip: leave **Refresh** on `all` the first time. To re-copy just one
# MAGIC notebook later - handy when iterating - pick it from the dropdown.)*

# COMMAND ----------

import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ExportFormat, ImportFormat, Language

import re

w = WorkspaceClient()
me = w.current_user.me().user_name
short = re.sub(r"[^a-z0-9]+", "_", me.split("@")[0].lower()).strip("_")
src_dir = os.getcwd()  # this folder (lab/) inside the shared Git folder
dest_dir = f"/Users/{me}/{short}_aibi-genie-lab"

# The notebooks this can copy: numbered modules + _bootstrap (never 00_* / itself).
copyable = []
for obj in w.workspace.list(src_dir):
    name = obj.path.rsplit("/", 1)[1]
    if name == "_bootstrap" or (name[:2].isdigit() and not name.startswith("00")):
        copyable.append(name)
copyable.sort()

ALL = "all (fresh copy)"
dbutils.widgets.dropdown("refresh", ALL, [ALL] + copyable, "Refresh")
choice = dbutils.widgets.get("refresh")
targets = copyable if choice == ALL else [choice]

w.workspace.mkdirs(dest_dir)
copied = []
for name in targets:
    data = w.workspace.export(f"{src_dir}/{name}", format=ExportFormat.SOURCE)
    w.workspace.import_(
        f"{dest_dir}/{name}",
        content=data.content,
        format=ImportFormat.SOURCE,
        language=Language.PYTHON,
        overwrite=True,
    )
    copied.append(name)

first_name = sorted(copied)[0]
link = f"{w.config.host}/#workspace{dest_dir}/{first_name}"
print(f"✓ copied {len(copied)} notebook(s) to {dest_dir}")
displayHTML(
    f"<div style='font-family:sans-serif;border-left:4px solid #1B7F4B;"
    f"background:#F0F7F3;padding:14px 18px;border-radius:0 8px 8px 0'>"
    f"✅ Your personal lab is ready.<br><br>"
    f"<a href='{link}' style='font-size:1.15em;font-weight:600'>"
    f"➡️ Open your copy of {first_name}</a></div>"
)
