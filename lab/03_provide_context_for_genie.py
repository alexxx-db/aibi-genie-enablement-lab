# Databricks notebook source
# MAGIC %md
# MAGIC # 🎓 Module 3 - Context for Genie, Can It Answer The Questions?
# MAGIC
# MAGIC Genie guessed in [**Module 2**]($./02_genie_without_context) because **nobody gave it context**. Here you'll
# MAGIC add that context yourself - the everyday craft of running a Genie Agent.
# MAGIC It lives at two levels:
# MAGIC
# MAGIC | Where | What | Who sees it |
# MAGIC |---|---|---|
# MAGIC | **Unity Catalog** | 📝 Column comments | everyone - all users, tools and agents |
# MAGIC | **Genie Agent → Instructions** | 📝 General instructions | this agent only |
# MAGIC | **Genie Agent → Examples** | 🧮 Measures & filters, 🔗 joins, 🧩 example queries | this agent only |
# MAGIC
# MAGIC > 💡 As you go, notice that most of these - the **measures**, the
# MAGIC **filter**, the **join** - are definitions you'd want *everywhere*, not
# MAGIC locked inside one agent. **Keep that in mind.**
# MAGIC
# MAGIC **In this module (~20 min):** add column comments, add the agent
# MAGIC instructions, and re-ask the [**Module 2**]($./02_genie_without_context) questions.
# MAGIC
# MAGIC ▶️ **Run the cells top to bottom.** Start with the setup cell just below, and run it first in every notebook.

# COMMAND ----------

# MAGIC %run ./_bootstrap

# COMMAND ----------

# MAGIC %md ## Step 1 · Add column comments
# MAGIC Before you give the agent instructions, add comments to the data itself. **Column
# MAGIC comments** in Unity Catalog are the cheapest, widest-reaching context you
# MAGIC can give - every user, every tool, and *every* Genie Agent sees them, not
# MAGIC just this one.
# MAGIC
# MAGIC In a real deployment you'd add these in the Catalog (Databricks can even
# MAGIC draft them with the ✨ **Generate a comment** button).

# COMMAND ----------

displayHTML(ui.screenshot(ctx, "03_1_generate_comment.png",
    "In the Catalog, ✨ Generate a comment drafts a column description for you"))

# COMMAND ----------

# MAGIC %md To keep the lab moving, we've written a comment for every column in
# MAGIC advance. **Run the next cell to apply them all at once.**

# COMMAND ----------

from labkit.datagen import apply_column_comments

n = apply_column_comments(spark, ctx)
print(f"✓ {n} column comments in place")

# COMMAND ----------

# MAGIC %md
# MAGIC Open the table in Catalog Explorer and you'll see the comments now sit
# MAGIC next to every column - this is exactly what Genie, dashboards and
# MAGIC analysts read:

# COMMAND ----------

displayHTML(ui.screenshot(ctx, "03_2_documented_columns.png",
    "Column comments now visible on the table in Catalog Explorer"))

# COMMAND ----------

# MAGIC %md
# MAGIC > ⚠️ **Take this with you.** Documenting columns is a
# MAGIC small, one-time effort that makes *every* AI/BI experience better -
# MAGIC Genie, dashboards and analysts all read these descriptions. It's one of
# MAGIC the highest-value, lowest-effort things a data team can do.

# COMMAND ----------

# MAGIC %md ## Step 2 · Curate your agent (hands-on 🛠️)
# MAGIC Now the per-agent context. In your agent's **Configure** panel it lives in
# MAGIC two tabs: **Instructions** (general text) and **Examples** (measures,
# MAGIC filters, joins and example queries). You'll add one of each - together they
# MAGIC give the agent the business context it was missing.

# COMMAND ----------

displayHTML(ui.curation_ui_steps(ctx))

# COMMAND ----------

# MAGIC %md ## Step 3 · Re-ask the Module 2 questions
# MAGIC Same questions, **same agent**, in a **new chat**. Open **Show code** and
# MAGIC check: revenue now follows the definition you wrote, and return rate uses
# MAGIC your `return_rate` measure instead of one Genie guessed at.

# COMMAND ----------

displayHTML(ui.question_scorecard(ctx, mode="taught"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## It works - but the context lives in the Genie Agent you just created
# MAGIC
# MAGIC Genie now answers correctly, and this is a real skill you'll use with
# MAGIC customers. But everything you just defined - the measures, the filter, the
# MAGIC join - lives inside **this one Genie Agent**.
# MAGIC
# MAGIC A dashboard, a SQL query, a notebook, or the next person's Genie Agent
# MAGIC can't use your `return_rate` measure. They'd each define it again, their
# MAGIC own way.
# MAGIC
# MAGIC A **metric view** puts those same measures and joins in Unity Catalog
# MAGIC instead: defined once, then queried the same way from SQL, notebooks,
# MAGIC AI/BI dashboards and Genie. Let's build one.

# COMMAND ----------

# MAGIC %md
# MAGIC ➡️ **[Continue to 04_build_a_metric_view]($./04_build_a_metric_view)** - Let's build exactly that.
