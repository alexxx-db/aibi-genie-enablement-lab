# Adding a Dataset

The lab is dataset-agnostic: notebooks and helper code never change. A dataset
is one folder under `datasets/` with two files:

```
datasets/<your_dataset>/
├── dataset.yaml        # setup & customization: data spec, story, questions, Genie config
└── metric_view.yaml    # the Databricks metric view body (standard metric view YAML)
```

(`dataset.json` is also accepted if you prefer JSON - same structure.)

Once the folder exists, it automatically appears in every notebook's
**Dataset** widget. That's the whole integration.

## Authoring checklist

Start by copying `datasets/retail_sales/` and work through it:

### 1. `tables:` - the data
Declare tables in dependency order (parents first). Generators available:
`id`, `int`, `float`, `choice` (weighted), `date`,
`person_name`, `product_name`, `fk`, `parent_key` (with `rows_per_parent`),
`lookup` (copy a column from a parent via an fk), `derived` (Spark SQL expr).

Prefer an **absolute date window** (`start`/`end`, e.g. `2026-01-01` to
`2027-12-31`): it is deterministic regardless of when data is generated, keeps
the demo focus month (June 2026) populated, and gives dashboards a full
timeline including the future. Relative windows (`days_back_min`/`_max`,
optional `recency_bias`) are also supported.

**Design an ambiguity in.** The lab only works if the headline metric is
genuinely debatable. Retail uses: discounts (list vs charged price), order
status (cancelled = never charged, returned = refunded), shipping fees.
Equivalents elsewhere: sessions vs unique users (web), booked vs recognized
(finance), gross vs net churn (SaaS).

### 2. `ambiguity:` - the module-1 experiment
Write the story as `story_intro` (one sentence of setup), `story_questions`
(bulleted definition dilemmas) and `story_punchline` ("none of these answers
is wrong..."). Set `unit` (e.g. `"$"`) so results format nicely. Then give
3-4 `sql_variants` that each compute the headline metric a *defensible but
different* way. The instructor setup notebook **asserts** that they return
different numbers.

### 3. `questions:` - what learners ask Genie
`ambiguous:` is a list of **pairs**: the same question phrased two ways.
Good pairs mix precise wording ("total revenue") with colloquial wording
("how much money did we make") - the colloquial one invites improvisation.
Test them: they should diverge on raw tables, converge on the metric view.

### 4. `genie:` - the agents and the curation step
- `raw_space`: keep `instructions` **empty or minimal** - the ambiguity is
  the lesson. List the tables by bare name (they resolve to the shared schema).
- `curation` (module 3): the text `instructions` and `example_question_sqls`
  learners paste into their agent; the example SQL should implement the
  canonical metric definition.
- `mv_space`: reference `{metric_view}` in the instructions and tell Genie the
  measures are the official definitions.

Also add `comment:` to the handful of columns whose meaning resolves the
ambiguity (e.g. status, net amount). They are deliberately NOT applied at
datagen time - learners add them by hand in module 3, so they first
experience Genie without documentation. Keep table-level comments neutral:
no spoilers about the ambiguity.

### 5. `metric_view.yaml` - the fix
Standard [metric view YAML](https://docs.databricks.com/aws/en/business-semantics/metric-views/yaml-reference)
(version 1.1) with `{catalog}`/`{data_schema}` placeholders in the `source:`.
Make the certified measure resolve the exact ambiguity from step 2, and say so
in comments.

## Placeholders

Any string in either file may use:

| Token | Resolves to |
|---|---|
| `{catalog}` | lab catalog |
| `{data_schema}` | shared data schema |
| `{user_schema}` | learner's personal schema |
| `{user}` | learner short name |
| `{metric_view}` | learner's fully qualified metric view |

## Validate before shipping

From the repo root:

```bash
python3 -c "
import sys; sys.path.insert(0, '_internal')
from labkit.config import LabContext
ctx = LabContext.load('.', '<your_dataset>', 'test@example.com')
print(ctx.section('ambiguity')['metric'])
print(ctx.metric_view_ddl()[:120])
"
```

Then run `setup/00_instructor_setup` against a dev workspace and dry-run the
four lab notebooks end-to-end - especially the divergence in module 2.
