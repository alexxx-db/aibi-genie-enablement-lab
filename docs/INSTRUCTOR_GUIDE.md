# Instructor Guide

Run-of-show for delivering the AI/BI Genie enablement lab to a group of
learners (low-code comfort assumed).

## The story you're telling

> An AI assistant is only as trustworthy as the semantics you give it.

1. **Module 1** - one simple question ("revenue last month?") returns 4
   different, equally defensible numbers. *The pain.*
2. **Module 2** - Genie on raw tables improvises: rephrasing the question can
   change the answer. *The pain, AI edition.*
3. **Module 3** - teach Genie: column comments, agent instructions,
   example SQL. Answers improve. *The craft - and its limits: it's prose,
   per-agent, advisory.*
4. **Module 4** - a Unity Catalog **metric view** settles the debate in code:
   one certified definition of every metric. *The fix.*
5. **Module 5** - Genie on governed metrics: same questions, consistent
   answers via `MEASURE(...)`. *The proof.*
6. **Module 6** - benchmark the agent against known answers and watch real
   usage. *Keep it honest over time.*
7. **Module 7** - an AI/BI dashboard on the same metric view. *One definition,
   every surface.*

Total learner time: ~90 minutes (7 modules).

## Before the session (15 min, once)

The lab is **self-provisioning**: each learner's first notebook run creates
their `user_<name>` schema and generates their own copy of the dataset
(deterministic - identical numbers for everyone). Nobody needs
`CREATE CATALOG`; the notebooks auto-detect the workspace catalog.

1. **Load the repo** into the workspace: *Workspace → Create → Git folder* →
   this repo's URL. Learners don't need GitHub access - they use the
   workspace copy.
2. **Run `setup/00_instructor_setup`** ("Run all"). It grants learners
   `USE CATALOG` + `CREATE SCHEMA`, generates *your* copy, and **verifies the
   ambiguity is reproducible** (the revenue variants must return different
   numbers - the notebook asserts it).
3. **Check the boxes:**
   - [ ] Group is **assigned to the workspace** with *Workspace access* and
     *Databricks SQL access* entitlements (setup can't do this)
   - [ ] Warehouse CAN USE is granted by setup automatically (it picks the
     first serverless warehouse and prints its name - tell learners)
   - [ ] Genie enabled; learners can create Genie Agents
   - [ ] Metric views available (needs SQL warehouse; Genie can consume metric views)
   - [ ] **Learner group is required.** Create a group per cohort (Settings →
     Identity and access → Groups, e.g. `genie-lab-cohort-1`), add the
     attendees, and put its name in the widget - grants AND notebook fan-out
     both target exactly that group. Running 3 cohorts? Run setup 3 times,
     once per group. Setup refuses to run with an empty/unknown group.
4. **Dry-run** `lab/01`-`07` yourself as a non-admin user if possible.
5. Setup **fans the lab out to every user's home folder** automatically
   (requires you to be a **workspace admin** - writing into other users'
   folders is an admin right; non-admin instructors set the fan-out widget
   to `no` and have learners use `lab/00_START_HERE` instead)
   (everyone must run their own copies; shared notebooks trample each other's
   results). Learners open *Workspace → Home → `<name>_aibi-genie-lab` →
   `01_explore_the_data`*. Late joiners run `lab/00_START_HERE` in the Git
   folder once to self-serve a copy. Copies find the lab code via the pointer
   setup publishes to `/Workspace/Shared/aibi_genie_lab_root.txt`.

## During the session

| When | What | Watch out for |
|---|---|---|
| 0:00 | Frame the story (slide or whiteboard: "who trusts their revenue number?") | |
| 0:05 | `01_explore_the_data` | Let them *react* to the 4 numbers before moving on |
| 0:15 | `02_genie_without_context` | UI path first. Divergence is likely but not guaranteed - if a learner gets consistent answers, compare across learners instead (also divergent!) |
| 0:30 | `03_provide_context_for_genie` | Learners own their tables, so they add column comments themselves - point out the ✨ AI-suggested descriptions. Then instructions + example SQL on their own agent |
| 0:45 | `04_build_a_metric_view` | The YAML is printed for them; UI path via Catalog Explorer → Create → Metric view |
| 1:00 | `05_genie_with_governed_metrics` | Point at `MEASURE(...)` in Genie's generated SQL - that is the key moment |
| 1:10 | `06_evaluate_and_monitor` | Add a benchmark (Chat mode + ground-truth SQL), run it, then the Monitor tab |
| 1:25 | `07_build_a_dashboard` | Dashboard on the metric view: two tiles, then the Genie Code assistant to beautify, then Publish |
| 1:40 | Debrief - one definition, every surface (SQL, Genie, dashboards) | |

## After the session

- `setup/99_teardown` drops the lab catalog (set the confirm widget to `yes`).
- Genie Agents belong to learners - ask them to delete their two agents.

## Swapping datasets

Pick a different bundle in the `dataset` widget of every notebook (learners:
same widget). To add a new dataset, see `ADDING_A_DATASET.md`.
