# Databricks notebook source
# MAGIC %md
# MAGIC # 📐 Module 4 - Define Your Metrics Once in UC
# MAGIC
# MAGIC In [**Module 3**]($./03_provide_context_for_genie) you defined measures and a join - but only inside one Genie
# MAGIC Agent. A **metric view** captures the same kind of definitions in Unity
# MAGIC Catalog instead: **defined once, in code**, then queried the same way from
# MAGIC SQL, notebooks, AI/BI dashboards and Genie.
# MAGIC
# MAGIC **In this module (~15 min):**
# MAGIC 1. Look at the certified metric definitions
# MAGIC 2. Create the metric view in your schema
# MAGIC 3. Query metrics *by name* - no formulas, no guessing
# MAGIC
# MAGIC ▶️ **Run the cells top to bottom.** Start with the setup cell just below, and run it first in every notebook.

# COMMAND ----------

# MAGIC %run ./_bootstrap

# COMMAND ----------

# MAGIC %md ## What's a metric view?
# MAGIC In plain terms: a metric view is a file that defines your business terms and
# MAGIC metrics once, so other tools - Genie, dashboards, SQL - can all reference the
# MAGIC same definitions.
# MAGIC
# MAGIC More precisely, it's an object in Unity Catalog that stores your business
# MAGIC metrics as named, reusable definitions. You describe it once, in a short
# MAGIC YAML block:
# MAGIC
# MAGIC - **Source** - the tables it reads, and how they join.
# MAGIC - **Dimensions** - the things you slice by (month, category, region).
# MAGIC - **Measures** - the calculations (net revenue, return rate), each defined once.
# MAGIC
# MAGIC Each measure or dimension can carry more than just a formula:
# MAGIC
# MAGIC - **Synonyms** - alternate names so Genie and BI tools find it (*sales*,
# MAGIC   *earnings* → Net Revenue) - the same synonyms you gave Genie in [**Module 3**]($./03_provide_context_for_genie).
# MAGIC - **Display name** - a friendly label for dashboards.
# MAGIC - **Format** - how the value shows: currency (`$`), percentage (`%`),
# MAGIC   decimal places.
# MAGIC
# MAGIC And the view itself can be **certified** in Unity Catalog, so everyone
# MAGIC knows it's the official definition.
# MAGIC
# MAGIC After that, nobody rewrites the formula. They ask for a measure by name -
# MAGIC `MEASURE(\`Net Revenue\`)` - and SQL, notebooks, dashboards and Genie all
# MAGIC get the same number.

# COMMAND ----------

# MAGIC %md ## Step 1 · Where it lives
# MAGIC Your metric view goes into **your schema**, right next to your tables - 
# MAGIC in real life it would be built once by the data team and shared with
# MAGIC everyone.

# COMMAND ----------

print(f"✓ Your metric view will be: {ctx.metric_view_fqn}")

# COMMAND ----------

# MAGIC %md ## Step 2 · Look at the metric definitions
# MAGIC Run the next cell to see the YAML you'll paste into the metric view.
# MAGIC Notice:
# MAGIC - **`Return Rate`** - the metric Genie guessed wrong in [**Module 2**]($./02_genie_without_context). Here the
# MAGIC   base is pinned down: returned orders over **fulfilled** orders (completed
# MAGIC   + returned), never all orders. This is the 11.5% definition, in code.
# MAGIC - **`Net Revenue`** - completed orders only, net of sales discounts, no shipping.
# MAGIC - Every measure has one expression; dimensions get friendly names.

# COMMAND ----------

displayHTML(ui.code(ctx.metric_view_body()))

# COMMAND ----------

# MAGIC %md ## Step 3 · Create your metric view (UI)
# MAGIC Now create the view in Unity Catalog and paste in the YAML you just
# MAGIC reviewed. The steps below follow the Catalog Explorer path.

# COMMAND ----------

displayHTML(ui.metric_view_ui_steps(ctx))

# COMMAND ----------

# MAGIC %md ## Step 4 · Query metrics by NAME
# MAGIC Just `MEASURE(...)` - no formulas, no JOINs, and the currency/percentage
# MAGIC formatting comes from the view itself, so the query stays clean. The top
# MAGIC row is **last month (June 2026)**: the same $852,085 and 11.5% Genie
# MAGIC produced once you'd defined the measures.

# COMMAND ----------

display(spark.sql(f"""
    SELECT `Order Month`,
           MEASURE(`Net Revenue`) AS `Revenue`,
           MEASURE(`Return Rate`) AS `Return Rate`
    FROM {ctx.metric_view_fqn}
    WHERE `Order Month` < DATE '2026-07-01'
    GROUP BY `Order Month`
    ORDER BY `Order Month` DESC
    LIMIT 6
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🏁 Defined once, queried by name
# MAGIC Your metrics now live in Unity Catalog as a certified metric view -
# MAGIC `MEASURE(\`Net Revenue\`)` returns the same number for SQL, notebooks,
# MAGIC dashboards and Genie. No more re-deriving formulas per tool.
# MAGIC
# MAGIC ➡️ **[Continue to 05_genie_with_governed_metrics]($./05_genie_with_governed_metrics)** - Now let's give Genie the certified definitions.
