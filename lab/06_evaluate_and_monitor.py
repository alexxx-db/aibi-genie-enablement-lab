# Databricks notebook source
# MAGIC %md
# MAGIC # 📊 Module 6 - Evaluate & Monitor Your Genie Agent
# MAGIC
# MAGIC A trustworthy agent isn't "set and forget." Two built-in tools keep it
# MAGIC honest as data, instructions and models change:
# MAGIC
# MAGIC - **Benchmarks** (evaluation) test the quality of your Genie - a set of
# MAGIC   questions with known-good answers you run to measure how often it gets
# MAGIC   them right.
# MAGIC - **Monitoring** reviews real usage - what users actually ask, which answers
# MAGIC   they rated, and where Genie struggles.
# MAGIC
# MAGIC **In this module (~15 min):**
# MAGIC 1. Add a benchmark and run an evaluation
# MAGIC 2. Review the Monitoring tab
# MAGIC
# MAGIC ▶️ **Run the cells top to bottom.** Start with the setup cell just below, and run it first in every notebook.

# COMMAND ----------

# MAGIC %run ./_bootstrap

# COMMAND ----------

# MAGIC %md ## Step 1 · Benchmark your agent (evaluation)
# MAGIC A benchmark pins a question to a known-correct answer, then scores how
# MAGIC often Genie matches - so you catch regressions before your users do. We'll
# MAGIC benchmark a fresh question - return rate *by category* - to check the metric
# MAGIC view holds up beyond the two you asked in [**Module 5**]($./05_genie_with_governed_metrics).

# COMMAND ----------

displayHTML(ui.benchmark_ui_steps(ctx))

# COMMAND ----------

# MAGIC %md ### When should you run benchmarks?
# MAGIC A benchmark is only useful if you re-run it whenever something that feeds an
# MAGIC answer changes. Run it again when:
# MAGIC
# MAGIC - the **data** updates - new rows, a backfill, or restated history
# MAGIC - the **agent instructions** change - a new instruction, synonym or example query
# MAGIC - a **metric definition** changes, or a **new metric is added** to the metric view
# MAGIC
# MAGIC Re-running after each of these is how you catch a regression before your users do.

# COMMAND ----------

# MAGIC %md ## Step 2 · Monitor real usage
# MAGIC Monitoring shows how the agent is actually used - questions asked, the
# MAGIC ratings users gave, and where Genie struggled. Leave a rating and watch it
# MAGIC show up.

# COMMAND ----------

displayHTML(ui.monitor_ui_steps(ctx))

# COMMAND ----------

# MAGIC %md
# MAGIC You can also set up **alerts** here - for example, get notified when
# MAGIC questions start getting **downvoted** - so you hear about problems
# MAGIC automatically instead of having to watch this tab.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Why this matters
# MAGIC Evaluation and monitoring close the loop: **define** metrics ([**Module 4**]($./04_build_a_metric_view)),
# MAGIC **serve** them through Genie ([**Module 5**]($./05_genie_with_governed_metrics)), then **continuously verify**
# MAGIC accuracy and watch real usage. That's what turns a Genie Agent from a demo
# MAGIC into something you can put in front of the business.

# COMMAND ----------

# MAGIC %md
# MAGIC ➡️ **[Continue to 07_build_a_dashboard]($./07_build_a_dashboard)** - the same metric view, now as an AI/BI dashboard.
