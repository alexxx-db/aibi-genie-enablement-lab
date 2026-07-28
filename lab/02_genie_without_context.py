# Databricks notebook source
# MAGIC %md
# MAGIC # 🧞 Module 2 - Genie Without Context
# MAGIC
# MAGIC You'll create your own **Genie Agent** pointed at the raw tables - no
# MAGIC instructions, no documentation - and ask it two everyday business
# MAGIC questions: **revenue** and **return rate**.
# MAGIC
# MAGIC **In this module (~10 min):**
# MAGIC 1. Create a Genie Agent in the UI
# MAGIC 2. Ask about revenue and return rate
# MAGIC 3. Open Show code and see which definition Genie chose for each
# MAGIC
# MAGIC ▶️ **Run the cells top to bottom.** Start with the setup cell just below, and run it first in every notebook.

# COMMAND ----------

# MAGIC %run ./_bootstrap

# COMMAND ----------

# MAGIC %md ## Step 1 · Create your Genie Agent
# MAGIC Point a fresh Genie Agent at the four raw tables - no instructions, no
# MAGIC documentation. We want to see what Genie does with zero context.

# COMMAND ----------

displayHTML(ui.genie_ui_steps(ctx, "raw_space"))

# COMMAND ----------

# MAGIC %md ## Step 2 · Ask Genie your questions
# MAGIC Time to put it to work - let's ask Genie a couple of everyday business questions.

# COMMAND ----------

displayHTML(ui.question_scorecard(ctx))

# COMMAND ----------

# MAGIC %md
# MAGIC ## What did you observe?
# MAGIC
# MAGIC Genie is genuinely capable - on **revenue** it landed on a sensible
# MAGIC definition (completed orders, net of sales discounts) with no help at all.
# MAGIC That's the good news.
# MAGIC
# MAGIC The catch is **return rate**: there's no single right way to calculate it
# MAGIC - returns as a share of *what?* - so Genie quietly picked one. Its answer
# MAGIC isn't wrong - but it made a
# MAGIC **business decision for you**, without saying so.
# MAGIC
# MAGIC That's the real gap: some definitions live in people's heads, not in the
# MAGIC data. In the next module, you'll make them explicit - inside the agent.

# COMMAND ----------

# MAGIC %md
# MAGIC ➡️ **[Continue to 03_provide_context_for_genie]($./03_provide_context_for_genie)** - Genie needs business context. Let's add it.
