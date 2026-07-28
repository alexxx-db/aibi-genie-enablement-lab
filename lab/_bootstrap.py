# Databricks notebook source
# Lab bootstrap (run via %run from each module): locates the lab code,
# prepares the learner's data copy on first run, and shows the greeting.
import os, sys

sys.dont_write_bytecode = True
_root = os.path.dirname(os.getcwd())  # inside the lab Git folder
if not os.path.isdir(os.path.join(_root, "_internal")):  # copied elsewhere?
    _root = open("/Workspace/Shared/aibi_genie_lab_root.txt").read().strip()
sys.path.insert(0, os.path.join(_root, "_internal"))
for _m in [m for m in list(sys.modules) if m.startswith("labkit")]:
    del sys.modules[_m]  # drop cached lab code so updates apply immediately
from labkit import notebook as ui

ctx = ui.bootstrap(spark, dbutils)

# Greet only in Module 1 - later modules just confirm the data is ready.
_nb_name = (
    dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    .notebookPath().get().rsplit("/", 1)[1]
)
if _nb_name.startswith("01"):
    displayHTML(ui.welcome(ctx))
