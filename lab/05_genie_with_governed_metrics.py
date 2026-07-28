# Databricks notebook source
# MAGIC %md
# MAGIC # 🧞📐 Module 5 - Genie on Governed Metrics
# MAGIC
# MAGIC In [**Module 3**]($./03_provide_context_for_genie) you hand-wrote measures, a join and instructions
# MAGIC into one agent. Now you'll point a **fresh** Genie Agent at your metric
# MAGIC view - and it inherits all of that automatically: the measures, their
# MAGIC synonyms, the formats. **No instructions to write.**
# MAGIC
# MAGIC **In this module (~10 min):**
# MAGIC 1. Create a Genie Agent on your metric view
# MAGIC 2. Ask the same questions - and get the same certified answer every time
# MAGIC
# MAGIC ▶️ **Run the cells top to bottom.** Start with the setup cell just below, and run it first in every notebook.

# COMMAND ----------

# MAGIC %run ./_bootstrap

# COMMAND ----------

# MAGIC %md ## Step 1 · Create a Genie Agent on your metric view
# MAGIC Same as [**Module 2**]($./02_genie_without_context), but the data source is your **metric view**, not the raw
# MAGIC tables. The view already carries the measures, their synonyms and formats,
# MAGIC so unlike [**Module 3**]($./03_provide_context_for_genie) you don't re-write any of those.
# MAGIC
# MAGIC General instructions still matter, though - they're where you capture
# MAGIC business context that can't be defined as a metric (tone, default
# MAGIC assumptions, wording rules). In a real deployment you'd almost
# MAGIC always have some. For this lab the view covers our two questions on its
# MAGIC own, so we'll leave the instructions empty this time.

# COMMAND ----------

displayHTML(ui.genie_ui_steps(ctx, "mv_space"))

# COMMAND ----------

# MAGIC %md ## Step 2 · Ask the same questions
# MAGIC Same two questions as before - this time against the governed metric view.

# COMMAND ----------

displayHTML(ui.question_scorecard(ctx, mode="governed"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🏁 The three approaches, side by side
# MAGIC
# MAGIC | | Genie, no context ([**Module 2**]($./02_genie_without_context)) | + instructions ([**Module 3**]($./03_provide_context_for_genie)) | On the metric view (**Module 5**) |
# MAGIC |---|---|---|---|
# MAGIC | Who decides what "revenue" means | Genie, each time it answers | you, but only in this agent | the metric view, defined once |
# MAGIC | Where that definition can be used | this chat only | this agent only | every Genie Agent, dashboard, SQL query and notebook |
# MAGIC | How it's governed | not at all | per-agent configuration | a Unity Catalog asset: owner, permissions, certification, lineage |
# MAGIC
# MAGIC **The takeaway:** Genie is powerful, but a metric view is
# MAGIC what makes its answers *trustworthy* - one definition, owned and certified in
# MAGIC Unity Catalog, that SQL, dashboards and Genie all share.

# COMMAND ----------

# MAGIC %md
# MAGIC ➡️ **[Continue to 06_evaluate_and_monitor]($./06_evaluate_and_monitor)** - keep the agent honest with benchmarks and monitoring.
