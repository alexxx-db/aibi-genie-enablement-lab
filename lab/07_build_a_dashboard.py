# Databricks notebook source
# MAGIC %md
# MAGIC # 📈 Module 7 - AI/BI Dashboard on the Same Governed Metrics
# MAGIC
# MAGIC Genie was one surface for your certified metrics. A **dashboard** is
# MAGIC another - and it reads the *same* metric view, so every tile shows the
# MAGIC exact definitions you built. No re-implementing revenue or return rate in
# MAGIC the dashboard; you just reference the measures.
# MAGIC
# MAGIC **In this module (~15 min):**
# MAGIC 1. Create an AI/BI dashboard on your metric view
# MAGIC 2. Add a couple of tiles built from the measures
# MAGIC 3. Ask the assistant to build one more, in plain language
# MAGIC
# MAGIC ▶️ **Run the cells top to bottom.** Start with the setup cell just below, and run it first in every notebook.

# COMMAND ----------

# MAGIC %run ./_bootstrap

# COMMAND ----------

print(f"✓ Your dashboard will read from: {ctx.metric_view_fqn}")

# COMMAND ----------

# MAGIC %md ## Step 1 · Build the dashboard
# MAGIC Two tiles by hand, then let the assistant build one - all reading the same
# MAGIC metric view, so every number matches Genie.

# COMMAND ----------

displayHTML(ui.dashboard_ui_steps(ctx))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🏁 One definition, every surface
# MAGIC SQL, notebooks, Genie and now a dashboard - all reading the **same**
# MAGIC certified metric view. Define a metric once, and it's consistent
# MAGIC everywhere the business looks. That's the whole point of the semantic
# MAGIC layer.

