# AI/BI Genie Enablement Lab

A hands-on Databricks lab that teaches **why centralized metric definitions
matter** - by letting learners feel the pain first, then fix it:

| Module | What happens | The lesson |
|---|---|---|
| [`lab/01_explore_the_data`](lab/01_explore_the_data.py) | One question - *"revenue last month?"* - four different, defensible answers | Metrics are ambiguous by default |
| [`lab/02_genie_without_context`](lab/02_genie_without_context.py) | Build a Genie Agent on raw tables; rephrasing a question changes the answer | AI improvises when semantics are missing |
| [`lab/03_provide_context_for_genie`](lab/03_provide_context_for_genie.py) | Add column comments, agent instructions & example SQL; answers improve | Context helps - but it's prose, per-agent, advisory |
| [`lab/04_build_a_metric_view`](lab/04_build_a_metric_view.py) | Deploy a Unity Catalog **metric view**: every metric defined once, certified | Comments/instructions *inform*; metric views *define* |
| [`lab/05_genie_with_governed_metrics`](lab/05_genie_with_governed_metrics.py) | Genie on governed metrics: same questions, consistent `MEASURE(...)` answers | Define once - SQL, dashboards and Genie all agree |
| [`lab/06_evaluate_and_monitor`](lab/06_evaluate_and_monitor.py) | Benchmark the agent against known answers, and watch real usage | Keep the agent accurate as data, instructions and models change |
| [`lab/07_build_a_dashboard`](lab/07_build_a_dashboard.py) | Build an AI/BI dashboard on the same metric view | One definition, every surface - SQL, Genie and dashboards |

Designed for non-technical learners: UI-first, click-through instructions
throughout.

## Quick start

**Instructor** (once, ~15 min):
1. Workspace → **Create → Git folder** → this repo's URL
2. Run **`setup/00_instructor_setup`** (Run all) - grants learner access and
   self-tests the demo (the lab is otherwise self-provisioning)
3. Setup fans the lab out to every user's home folder automatically
   (late joiners run `lab/00_START_HERE` once to self-serve)

**Learners:** open *Home → `<your name>_aibi-genie-lab` → 01_explore_the_data*
and follow along. That's it.

Full run-of-show: [`docs/INSTRUCTOR_GUIDE.md`](docs/INSTRUCTOR_GUIDE.md)

## Repo layout

```
lab/          ← learner-facing notebooks (the ONLY folder learners open)
setup/        ← instructor: 00_instructor_setup, 99_teardown
datasets/     ← pluggable dataset bundles (data spec + story + questions + metric view)
_internal/    ← plumbing: config loader, data generator, Genie API helpers
docs/         ← instructor guide, dataset authoring guide
```

## Pluggable datasets

Everything dataset-specific - synthetic data spec, the ambiguity story, Genie
instructions, sample questions, metric definitions - lives in one bundle
folder under `datasets/`. Add a folder, and it appears in every notebook's
**Dataset** widget; the notebooks themselves never change.

How to author one: [`docs/ADDING_A_DATASET.md`](docs/ADDING_A_DATASET.md)

## Per-user isolation

One pre-existing catalog (auto-detected - nobody needs `CREATE CATALOG`).
Each learner's first notebook run creates their own `user_<name>` schema and
generates their personal copy of the dataset there - **deterministic per
seed, so every learner sees identical numbers** while fully owning their
tables (needed for the column-comments exercise), their metric view, and
their Genie Agents. Learner privileges: just `USE CATALOG` + `CREATE SCHEMA`.

## Roadmap

- More dataset bundles - industry-specific variants (same notebooks, new story)
- Metric-view-level instructions & verified queries, once the platform ships them

## How to get help

Databricks support doesn't cover this content. For questions or bugs, please
open a GitHub issue and the team will help on a best effort basis.

## License

&copy; 2025 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the Databricks License [https://databricks.com/db-license-source]. All included or referenced third party libraries are subject to the licenses set forth below.

| library | description | license | source |
|---------|-------------|---------|--------|
| databricks-sdk | Databricks SDK for Python | Apache 2.0 | https://github.com/databricks/databricks-sdk-py |
| pyyaml | YAML parser | MIT | https://github.com/yaml/pyyaml |
