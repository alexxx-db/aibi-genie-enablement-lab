# Databricks notebook source
# MAGIC %md
# MAGIC # 📊 Module 1 - One Question, Many Answers
# MAGIC
# MAGIC Welcome! In this lab you'll experience first-hand why companies need
# MAGIC **one central definition of their metrics** - and how Databricks AI/BI
# MAGIC (Genie + metric views) delivers it.
# MAGIC
# MAGIC **In this module (~10 min):** get to know the data, then see how one
# MAGIC business question can produce several different "correct" answers.
# MAGIC
# MAGIC ▶️ **Run the cells top to bottom.** Start with the setup cell just below, and run it first in every notebook.

# COMMAND ----------

# MAGIC %run ./_bootstrap

# COMMAND ----------

# MAGIC %md ## Get to know the data
# MAGIC
# MAGIC You're looking at four tables from a fictional retailer: **customers**,
# MAGIC their **orders**, the **order_items** that make up each order, and the
# MAGIC **products** being sold.
# MAGIC
# MAGIC Run the next cell and follow the steps to browse your tables - the
# MAGIC **Sample data** tab shows you real rows. Notice that there is no
# MAGIC "revenue" column anywhere: revenue always has to be calculated, and how
# MAGIC to calculate it is exactly what teams disagree on.

# COMMAND ----------

displayHTML(ui.explore_steps(ctx))

# COMMAND ----------

# MAGIC %md ## Try it yourself 🧪
# MAGIC
# MAGIC Before you run the next two cells, decide for yourself: **what does
# MAGIC "revenue last month" mean for this retailer?** For example:
# MAGIC
# MAGIC - Which orders count? Also the cancelled and returned ones?
# MAGIC - List price or the price actually charged after sales discounts?
# MAGIC - Does shipping count as revenue?
# MAGIC - ...anything else you'd include or exclude - there is no fixed list
# MAGIC
# MAGIC Now run the cells and see how your definition compares.

# COMMAND ----------

displayHTML(ui.ambiguity_story(ctx))

# COMMAND ----------

displayHTML(ui.variant_results(spark, ctx))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Which is the right answer?
# MAGIC
# MAGIC Every one of those numbers is a *defensible* answer to the same question.
# MAGIC
# MAGIC Now imagine asking **Genie** that question - which of the four answers
# MAGIC do you think it will consider correct? Let's find out.

# COMMAND ----------

# MAGIC %md
# MAGIC ➡️ **[Continue to 02_genie_without_context]($./02_genie_without_context)** - Let's see what Genie does.
