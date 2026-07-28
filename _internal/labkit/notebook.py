"""Learner-notebook presentation helpers.

Everything a learner sees is rendered HERE from the dataset bundle, so the
lab/ notebooks stay generic and dataset-agnostic. Learners never look at
YAML/config - they see formatted instructions produced by these functions.
"""

from __future__ import annotations

import html as _html
import os
import sys


def bootstrap(spark, dbutils, ensure_data: bool = True):
    """One-liner used at the top of every learner notebook.

    Adds _internal to sys.path, creates the (rarely touched) widgets, picks a
    usable catalog, makes sure the learner's personal schema + data copy exist
    (first run generates them, ~30s), and returns a resolved LabContext.
    """
    repo_root = _find_repo_root()
    internal = os.path.join(repo_root, "_internal")
    if internal not in sys.path:
        sys.path.insert(0, internal)

    from labkit.config import LabContext, list_datasets

    datasets = list_datasets(repo_root)
    dbutils.widgets.dropdown("dataset", datasets[0], datasets, "Dataset")
    name = dbutils.widgets.get("dataset")

    probe = LabContext.load(repo_root, name, "probe")  # to read bundle default
    dbutils.widgets.text("catalog", probe.raw["defaults"]["catalog"], "Catalog")
    catalog = _resolve_catalog(spark, dbutils.widgets.get("catalog"))

    ctx = LabContext.load(
        repo_root,
        dataset_name=name,
        current_user=spark.sql("SELECT current_user()").first()[0],
        catalog=catalog,
    )
    if ensure_data:
        from labkit.datagen import ensure_data as _ensure

        if _ensure(spark, ctx):
            print(f"✓ generated your personal dataset in {ctx.catalog}.{ctx.user_schema}")
        else:
            print(f"✓ your dataset is ready in {ctx.catalog}.{ctx.user_schema}")
    return ctx


ROOT_POINTER = "/Workspace/Shared/aibi_genie_lab_root.txt"


def _find_repo_root() -> str:
    """Locate the lab repo even when a notebook was copied elsewhere.

    Learners copy lab notebooks into their home folder; the instructor setup
    publishes the Git folder's path to a pointer file in /Workspace/Shared/.
    """
    candidate = os.path.dirname(os.getcwd())
    if os.path.isdir(os.path.join(candidate, "_internal")):
        return candidate
    try:
        pointed = open(ROOT_POINTER).read().strip()
        if os.path.isdir(os.path.join(pointed, "_internal")):
            return pointed
    except OSError:
        pass
    raise RuntimeError(
        "Can't find the lab's code. Either run this notebook inside the lab "
        "Git folder, or ask the instructor to run setup/00_instructor_setup "
        f"(it publishes the lab location to {ROOT_POINTER})."
    )


def _resolve_catalog(spark, wanted: str) -> str:
    """Use the widget's catalog if it exists; otherwise auto-pick the
    workspace's regular catalog (labs run in workspaces where nobody can
    create catalogs, so the bundle default may not exist)."""
    catalogs = [r[0] for r in spark.sql("SHOW CATALOGS").collect()]
    if wanted in catalogs:
        return wanted
    deny = {"system", "samples", "main", "hive_metastore", "__databricks_internal"}
    candidates = [
        c for c in catalogs if c not in deny and "share" not in c.lower()
    ]
    if not candidates:
        raise RuntimeError(
            f"Catalog '{wanted}' doesn't exist here and no usable catalog was "
            "found. Set the 'Catalog' widget to the name your instructor gave you."
        )
    return candidates[0]


# ---------------------------------------------------------------- html blocks
_CSS = """
<style>
  .lab { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, sans-serif;
         line-height: 1.55; color: #1F2937; font-size: 15px;
         display: flow-root; padding: 2px 2px 14px 2px; }
  .lab > :last-child { margin-bottom: 0; }
  .lab h3 { margin: 0 0 12px; font-size: 1.2em; letter-spacing: -0.01em; color: #0F2E3A; }
  .lab p { margin: 8px 0; }

  .lab .question { background: #F5F8FA; border: 1px solid #E3EBF0; border-left: 4px solid #14607A;
                   border-radius: 10px; padding: 16px 20px; margin: 12px 0;
                   font-size: 1.3em; font-weight: 650; color: #0F2E3A; }

  .lab .callout { background: #F5F8FA; border: 1px solid #E3EBF0; border-left: 4px solid #14607A;
                  padding: 14px 18px; border-radius: 10px; margin: 12px 0; }
  .lab .warn { background: #FDF6EE; border-color: #F3E2CD; border-left-color: #C2571A; }
  .lab .hint { display: inline-flex; align-items: center; gap: 8px; background: #EFF6F8;
               border: 1px solid #D8E7EC; color: #0F4C5F; border-radius: 999px;
               padding: 8px 16px; font-weight: 550; margin-top: 6px; }

  .lab ol.steps { list-style: none; counter-reset: step; padding: 0; margin: 8px 0; }
  .lab ol.steps > li { counter-increment: step; position: relative; padding: 9px 0 9px 42px;
                       border-bottom: 1px solid #EEF3F6; }
  .lab ol.steps > li:last-child { border-bottom: none; }
  .lab ol.steps > li::before { content: counter(step); position: absolute; left: 0; top: 9px;
                               width: 26px; height: 26px; border-radius: 50%; background: #0E4A5C;
                               color: #fff; font-weight: 650; font-size: .78em;
                               display: flex; align-items: center; justify-content: center; }
  .lab ul { margin: 6px 0; padding-left: 20px; }
  .lab li { margin: 3px 0; }

  .lab ul.qs { list-style: none; padding: 0; margin: 10px 0; }
  .lab ul.qs > li { position: relative; padding: 8px 0 8px 42px;
                    border-bottom: 1px solid #EEF3F6; }
  .lab ul.qs > li:last-child { border-bottom: none; }
  .lab ul.qs > li::before { content: '?'; position: absolute; left: 0; top: 8px;
                            width: 26px; height: 26px; border-radius: 50%;
                            background: #EFF6F8; border: 1px solid #D8E7EC;
                            color: #0F4C5F; font-weight: 700; font-size: .85em;
                            display: flex; align-items: center; justify-content: center; }

  .lab a { font-weight: 650; }
  .lab a code { font-weight: 650; }

  .lab code { background: #EDF2F5; border: 1px solid #E0E8EC; border-radius: 5px;
              padding: 1px 6px; font-size: .92em; }
  .lab pre { background: #F6F8FA; border: 1px solid #E3EBF0; border-radius: 8px;
             padding: 12px 14px; overflow-x: auto; white-space: pre-wrap; font-size: .9em; }

  .lab table { width: 100%; border-collapse: separate; border-spacing: 0; margin: 10px 0;
               border: 1px solid #E2EAEF; border-radius: 10px; overflow: hidden; }
  .lab th { background: #F2F6F8; text-align: left; font-size: .74em; text-transform: uppercase;
            letter-spacing: .07em; color: #51626C; padding: 10px 14px; }
  .lab td { padding: 11px 14px; border-top: 1px solid #EDF2F5; vertical-align: top; }
  .lab tr:nth-child(even) td { background: #FAFCFD; }
  .lab .num { text-align: right; font-variant-numeric: tabular-nums; font-weight: 650; white-space: nowrap; }
  .lab .idx { color: #8CA0AB; font-weight: 600; width: 1%; white-space: nowrap; }

  .lab .big { font-size: 1.25em; font-weight: 600; }
  .lab .diff { color: #B00020; font-weight: 650; }
  .lab .same { color: #1B7F4B; font-weight: 650; }

</style>
"""


def _esc(s) -> str:
    return _html.escape(str(s))


def _wrap(inner: str) -> str:
    return f"{_CSS}<div class='lab'>{inner}</div>"


def _png_size(path) -> tuple[int, int] | None:
    """(width, height) from a PNG header, so <img> can reserve its space
    before the bytes decode - otherwise Databricks measures the output frame
    too early and clips the bottom of the block."""
    import struct

    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
        return struct.unpack(">II", head[16:24])
    return None


def _aspect(path) -> str:
    size = _png_size(path)
    return f"aspect-ratio:{size[0]}/{size[1]};" if size else ""


def _copy_pre(text: str) -> str:
    """A <pre> code block with a one-click Copy button (for pasting into the UI)."""
    btn = (
        "<button onclick=\""
        "var p=this.parentElement.querySelector('pre');"
        "var a=document.createElement('textarea');a.value=p.innerText;"
        "document.body.appendChild(a);a.select();"
        "try{document.execCommand('copy')}catch(e){}a.remove();"
        "var o=this.textContent;this.textContent='Copied';"
        "setTimeout(function(){this.textContent=o}.bind(this),1500);\" "
        "style=\"position:absolute;top:6px;right:6px;font-family:inherit;"
        "font-size:.75em;background:#0E4A5C;color:#fff;border:none;"
        "border-radius:6px;padding:3px 10px;cursor:pointer;\">Copy</button>"
    )
    return (
        f"<div style='position:relative'>{btn}"
        f"<pre style='white-space:pre-wrap;margin:6px 0;padding-top:16px'>"
        f"{_esc(text.strip())}</pre></div>"
    )


def _wide_img(ctx, name: str | None) -> str:
    """Embedded screenshot at the top of a steps block ('' if no file yet)."""
    import base64

    if not name:
        return ""
    path = ctx.repo_root / "assets" / "screenshots" / name
    if not path.exists():
        return ""
    b64 = base64.b64encode(path.read_bytes()).decode()
    return (
        f"<img src='data:image/png;base64,{b64}' "
        f"style='display:block;width:100%;max-width:1200px;{_aspect(path)}"
        f"margin:0 0 20px;border:1px solid #D5DCE0;"
        f"border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.08)'/>"
    )


def screenshot(ctx, name: str, caption: str = "") -> str:
    """Embed a UI screenshot from assets/screenshots/ (base64, portable).

    Renders a subtle placeholder if the file doesn't exist yet, so notebooks
    work before all screenshots are captured.
    """
    import base64

    path = ctx.repo_root / "assets" / "screenshots" / name
    cap = f"<div style='color:#5A6B73;font-size:0.9em;margin:4px 0 12px'>{_esc(caption)}</div>" if caption else ""
    if path.exists():
        b64 = base64.b64encode(path.read_bytes()).decode()
        return _wrap(
            f"<img src='data:image/png;base64,{b64}' "
            f"style='max-width:100%;{_aspect(path)}border:1px solid #D5DCE0;"
            f"border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08)'/>{cap}"
        )
    return _wrap(
        f"<div style='border:2px dashed #C4CDD2;border-radius:8px;padding:18px;"
        f"color:#7A8A92;text-align:center'>📷 screenshot pending: "
        f"<code>{_esc(name)}</code></div>{cap}"
    )


def callout(text: str, warn: bool = False) -> str:
    cls = "callout warn" if warn else "callout"
    return _wrap(f"<div class='{cls}'>{text}</div>")


def code(text: str, max_height: str = "360px") -> str:
    """A compact, scrollable code window with a one-click Copy button.

    The Copy button grabs the full text regardless of scroll position, so the
    box can stay small while the learner pastes the whole thing elsewhere.
    """
    btn = (
        "<button onclick=\""
        "var p=this.parentElement.querySelector('pre');"
        "var a=document.createElement('textarea');a.value=p.innerText;"
        "document.body.appendChild(a);a.select();"
        "try{document.execCommand('copy')}catch(e){}a.remove();"
        "var o=this.textContent;this.textContent='Copied';"
        "setTimeout(function(){this.textContent=o}.bind(this),1500);\" "
        "style=\"position:absolute;top:8px;right:8px;font-family:inherit;"
        "font-size:.8em;background:#0E4A5C;color:#fff;border:none;"
        "border-radius:6px;padding:4px 12px;cursor:pointer;z-index:1;\">Copy</button>"
    )
    return (
        f"{_CSS}<div class='lab' style='position:relative'>{btn}"
        f"<pre style='white-space:pre;overflow:auto;max-height:{max_height};"
        f"margin:0;padding-top:16px'>{_esc(text.strip())}</pre></div>"
    )


def benchmark_ui_steps(ctx) -> str:
    """Module 6: the click-path to add and run a benchmark, as numbered steps.

    Mirrors curation_ui_steps - screenshots inline, the Question in the
    distinctive box, and a copyable Ground Truth Answer.
    """
    bm = ctx.section("genie", "benchmark")
    lbl = ("font-size:.74em;text-transform:uppercase;letter-spacing:.07em;"
           "color:#51626C;font-weight:700;margin:12px 0 4px")
    qa = (
        f"<div style='{lbl}'>Question</div>"
        f"<div class='question'>{_esc(bm['question'])}</div>"
        f"<div style='{lbl}'>Ground Truth Answer</div>"
        + _copy_pre(bm["sql"])
    )
    results_img = _wide_img(ctx, "06_5_benchmark_results.png") or (
        "<div style='border:2px dashed #C4CDD2;border-radius:10px;padding:18px;"
        "color:#7A8A92;text-align:center;margin:6px 0 20px'>📷 screenshot pending: "
        "<code>06_5_benchmark_results.png</code></div>"
    )
    items = [
        "Open your metric-view Genie Agent, click the <b>Benchmark</b> tab (top), "
        "then <b>+ Add benchmark</b>. Make sure the agent is in <b>Chat mode</b> "
        "(the Agent / Chat toggle, top right), not Agent - Chat mode scores "
        "Genie's generated SQL against your ground-truth SQL."
        + _wide_img(ctx, "06_1_benchmark_empty.png"),
        "Enter the <b>Question</b> and paste the <b>Ground Truth Answer</b> below, "
        "then click <b>Add benchmark</b>. The ground truth queries the metric view "
        "with <code>MEASURE(...)</code> - this agent only exposes the view, not the "
        "raw tables."
        + qa
        + _wide_img(ctx, "06_2_benchmark_add.png"),
        "Your benchmark is now saved."
        + _wide_img(ctx, "06_3_benchmark_added.png"),
        "Click <b>Run all benchmarks</b> - Genie answers each question and scores "
        "it against the ground truth. Re-run it after any change to instructions, "
        "the metric view, or the model to confirm nothing regressed."
        + _wide_img(ctx, "06_4_benchmark_run.png"),
        "The <b>Evaluations</b> tab shows the result for each question - whether "
        "Genie's answer matched the ground truth. That score is your before/after "
        "whenever you tune the agent. Re-running it regularly is how you "
        "<b>catch drift</b>: when a model update, a new instruction, or changed "
        "data quietly breaks an answer, the score flags it before your users do."
        + results_img,
    ]
    return steps("Benchmark your Genie Agent", items)


def monitor_ui_steps(ctx) -> str:
    """Module 6: leave a rating, then watch it land in the Monitor tab."""
    items = [
        "In a <b>chat</b> with your agent, rate one of Genie's answers - click "
        "👍 or 👎 under the response (add a comment if you thumbs it down). "
        "This is the feedback your real users would be leaving."
        + _wide_img(ctx, "06_6_rate_answer.png"),
        "Open the <b>Monitor</b> tab (top). Your rating shows up in the activity "
        "digest (questions asked, unique users, thumbs up/down) and in the history "
        "table below, next to every question the agent has been asked."
        + _wide_img(ctx, "06_7_monitor.png"),
        "Use the low-rated or failed questions to decide what to improve next - a "
        "new instruction, a synonym, or a measure in the metric view.",
    ]
    return steps("See real usage in Monitoring", items)


def dashboard_ui_steps(ctx) -> str:
    """Module 7: build an AI/BI dashboard on the metric view, as numbered steps."""
    def img(name: str) -> str:
        return _wide_img(ctx, name) or (
            "<div style='border:2px dashed #C4CDD2;border-radius:10px;padding:18px;"
            "color:#7A8A92;text-align:center;margin:6px 0 20px'>📷 screenshot pending: "
            f"<code>{name}</code></div>"
        )
    items = [
        "In the left sidebar, navigate to <b>Dashboards</b>, then click "
        "<b>Create dashboard</b>."
        + img("07_1_create_dashboard.png"),
        "Name it <b>Retail Sales and Customer Analytics - &lt;your name&gt;</b> - "
        "same base name as your Genie Agent, plus your own name so it's unique in "
        "the shared workspace. Pick your SQL warehouse, and rename the first page "
        "to <b>Overview</b>.",
        "On the <b>Data</b> tab, click <b>Add data</b> and select your metric view "
        "<code>retail_metrics</code> from Unity Catalog - the dashboard reads the "
        "same certified definitions as Genie."
        + img("07_2_add_data.png"),
        "Add a visualization to the page - click the <b>chart icon</b> in the "
        "canvas toolbar."
        + img("07_3_add_visualization.png"),
        "Set <b>Visualization</b> to <b>Line</b>, put <code>Order Month</code> on "
        "the <b>X-axis</b> and <code>MEASURE(`Net Revenue`)</code> on the "
        "<b>Y-axis</b> - that's your revenue trend over time."
        + img("07_4_tile_line.png"),
        "Add a second tile and set <b>Visualization</b> to <b>Bar</b>. Put "
        "<code>Product Category</code> on the <b>X-axis</b> and "
        "<code>MEASURE(`Completed Orders`)</code> on the <b>Y-axis</b> - order "
        "volume varies by category, so the bars actually differ. It's a different "
        "certified measure from the revenue trend, and still matches Genie exactly."
        + img("07_5_tile_bar.png"),
        "Open the <b>Genie Code</b> assistant (the ✨ icon, top right) and describe "
        "what you want in plain English. <b>Be creative here</b> - ask for KPI "
        "counters, different chart types, colours, a tidier layout, whatever tells "
        "your story (e.g. <i>add KPI counters and a Net Revenue by Region chart, "
        "and restyle every tile into one colour palette</i>). Turn on "
        "<b>auto-approve</b> so it applies each change without stopping to ask. It "
        "writes against your metric view, so even AI-generated tiles use the "
        "<b>certified definitions</b>."
        + img("07_6_dashboard_assistant.png"),
        "Review the result, then click <b>Publish</b> (top right) to share your "
        "dashboard - every tile reads the same certified metric view as Genie and "
        "SQL."
        + img("07_7_dashboard_published.png"),
    ]
    return steps("Build it on your metric view", items)


def catalog_link(ctx, schema: str | None = None) -> str:
    """Inline <a> into Catalog Explorer for the lab catalog or one schema."""
    from databricks.sdk import WorkspaceClient

    path = ctx.catalog + (f"/{schema}" if schema else "")
    url = f"{WorkspaceClient().config.host}/explore/data/{path}"
    return (
        f"<a href='{url}' target='_blank'>"
        f"<code>{_esc(path.replace('/', '.'))}</code></a>"
    )


def explore_steps(ctx) -> str:
    """Module 1: Catalog Explorer walk, driven by the bundle's explore: section.

    Renders as one block: title, intro, the bundle's screenshot (if the file
    exists) and the numbered steps. Wider than regular text blocks so the
    screenshot stays readable.
    """
    from databricks.sdk import WorkspaceClient

    url = (
        f"{WorkspaceClient().config.host}/explore/data/"
        f"{ctx.catalog}/{ctx.data_schema}"
    )
    cat_link = f"<a href='{url}' target='_blank'>Catalog</a>"

    exp = ctx.section("explore")
    items = [
        f"In the left sidebar, click {cat_link}.",
        f"Expand <code>{_esc(ctx.catalog)}</code>, then open your own schema "
        f"<code>{_esc(ctx.user_schema)}</code> - your tables are in there. "
        f"(Shortcut: {catalog_link(ctx, ctx.data_schema)} opens it directly.)",
    ] + list(exp.get("steps", []))
    lis = "".join(f"<li>{s}</li>" for s in items)

    intro = (exp.get("intro") or "").replace("{catalog_ui}", cat_link)
    inner = (
        _wide_img(ctx, exp.get("screenshot"))
        + "<h3>Explore your tables in the Catalog</h3>"
        + (f"<p>{intro}</p>" if intro else "")
        + f"<ol class='steps'>{lis}</ol>"
    )
    return f"{_CSS}<div class='lab'>{inner}</div>"


def tables_overview(spark, ctx) -> str:
    """Module 1: name, row count and description of every lab table."""
    rows = []
    for t, fqn in ctx.data_table_fqns().items():
        n = spark.table(fqn).count()
        comment = (
            spark.sql(f"DESCRIBE TABLE EXTENDED {fqn}")
            .where("col_name = 'Comment'")
            .select("data_type")
            .first()
        )
        rows.append(
            f"<tr><td><code>{_esc(t)}</code></td><td class='num'>{n:,}</td>"
            f"<td>{_esc(comment[0] if comment else '')}</td></tr>"
        )
    return _wrap(
        "<table><tr><th>Table</th><th style='text-align:right'>Rows</th>"
        f"<th>Description</th></tr>{''.join(rows)}</table>"
    )


def welcome(ctx) -> str:
    """Module-1 intro callout with a link into Catalog Explorer."""
    from databricks.sdk import WorkspaceClient

    url = (
        f"{WorkspaceClient().config.host}/explore/data/"
        f"{ctx.catalog}/{ctx.data_schema}"
    )
    return callout(
        f"You're working with the <b>{_esc(ctx.raw['display_name'])}</b> "
        f"dataset in <code>{_esc(ctx.catalog)}.{_esc(ctx.data_schema)}</code> "
        f"- browse your tables in the "
        f"<a href='{url}' target='_blank'>Catalog</a>."
    )


def steps(title: str, items: list[str], intro: str = "") -> str:
    lis = "".join(f"<li>{s}</li>" for s in items)
    return _wrap(
        f"<h3>{_esc(title)}</h3>"
        + (f"<p>{intro}</p>" if intro else "")
        + f"<ol class='steps'>{lis}</ol>"
    )


def ambiguity_story(ctx) -> str:
    amb = ctx.section("ambiguity")
    if amb.get("story_questions"):
        bullets = "".join(f"<li>{_esc(q)}</li>" for q in amb["story_questions"])
        body = (
            f"<p>{_esc(amb.get('story_intro', ''))}</p>"
            f"<ul class='qs'>{bullets}</ul>"
            f"<p><b>{_esc(amb.get('story_punchline', ''))}</b></p>"
        )
    else:  # older bundles: single prose paragraph
        body = f"<p>{_esc(amb['story'])}</p>"
    return _wrap(
        "<h3>One simple question</h3>"
        f"<div class='question'>“What was our {_esc(amb['metric'])} "
        f"in June 2026?”</div>"
        + body
    )


def variant_results(spark, ctx) -> str:
    amb = ctx.section("ambiguity")
    unit = amb.get("unit", "")

    def fmt(v):
        try:
            return f"{unit}{v:,.0f}"
        except (TypeError, ValueError):
            return f"{unit}{v}"

    rows, values = [], []
    for i, v in enumerate(amb["sql_variants"], 1):
        val = spark.sql(v["sql"]).first()[0]
        values.append(val)
        rows.append(
            f"<tr><td class='idx'>{i}</td><td>{_esc(v['label'])}</td>"
            f"<td class='num diff'>{fmt(val)}</td></tr>"
        )
    try:
        spread = (
            f" The largest and smallest answers are "
            f"<b>{fmt(max(values) - min(values))}</b> apart - same month, "
            f"same data."
        )
    except TypeError:
        spread = ""
    return _wrap(
        f"<table><tr><th></th><th>Possible definition of “{_esc(amb['metric'])} "
        f"June 2026”</th><th style='text-align:right'>Result</th></tr>"
        f"{''.join(rows)}</table>"
        f"<div class='callout warn'>Same question, <b>{len(rows)} different "
        f"answers</b> - so which one is right?{spread}</div>"
    )



def genie_ui_steps(ctx, kind: str) -> str:
    """Numbered UI click-path for creating the module's Genie Agent."""
    cfg = ctx.section("genie", kind)
    title = cfg["title_template"].replace("{user}", ctx.user)
    if kind == "raw_space":
        fqns = ctx.data_table_fqns()
        assets = "".join(f"<li><code>{_esc(fqns[t])}</code></li>" for t in cfg["tables"])
        asset_step = (
            "In the <b>Connect your data</b> dialog, select these tables and click "
            f"<b>Create</b>:<ul>{assets}</ul>"
        )
    else:
        assets = "".join(f"<li><code>{_esc(mv)}</code></li>" for mv in cfg["metric_views"])
        asset_step = (
            "In the <b>Connect your data</b> dialog, select your <b>metric view</b> "
            f"and click <b>Create</b>:<ul>{assets}</ul>"
        )

    from databricks.sdk import WorkspaceClient

    genie_url = f"{WorkspaceClient().config.host}/genie/rooms"
    connect_img = _wide_img(ctx, cfg.get("screenshot"))
    rename_img = _wide_img(ctx, cfg.get("rename_screenshot"))
    items = [
        f"In the left sidebar, go to "
        f"<a href='{genie_url}' target='_blank'>Genie Agents</a>, then click "
        "<b>+ New</b> in the top right.",
        asset_step + connect_img,
    ]
    if kind == "raw_space":
        items.append(
            "Open <b>Configure</b> (top right) → the <b>About</b> tab. Genie "
            "suggests a <b>Description</b> for the agent - click <b>Accept</b> "
            "(or edit it first)."
            + _wide_img(ctx, "02_2_agent_description.png")
        )
    items.append(
        "Genie gives the agent a default name. Open <b>Configure</b> (top right) "
        "→ <b>About</b>, then <b>scroll down to About this agent</b> and click the "
        "<b>pencil</b> next to the name to rename it to something unique so you "
        f"can find it later - for example <code>{_esc(title)}</code>."
        + rename_img
    )
    instructions = (cfg.get("instructions") or "").strip()
    if instructions:
        items.append(
            "Open <b>Instructions</b> (left panel inside the agent) and paste:"
            f"<pre>{_esc(instructions)}</pre>"
        )
    lis = "".join(f"<li>{s}</li>" for s in items)
    return _wrap(
        "<h3>Create your Genie Agent (UI)</h3>"
        + f"<ol class='steps'>{lis}</ol>"
    )


def column_comments_table(ctx, table: str | None = None,
                          only: list[str] | None = None,
                          screenshots: list[str] | None = None) -> str:
    """Module 3: the column documentation to add in Catalog Explorer.

    Pass ``table`` to scope to one table and ``only`` to a few column names -
    the hands-on focus. Every column's comment is applied programmatically in
    the following cell. ``screenshots`` are embedded (in order) below the table.
    """
    from labkit.datagen import column_comments

    from databricks.sdk import WorkspaceClient

    triples = [
        c for c in column_comments(ctx)
        if (table is None or c[0] == table) and (only is None or c[1] in only)
    ]
    rows = "".join(
        f"<tr><td><code>{_esc(c)}</code></td><td>{_esc(txt)}</td></tr>"
        for _, c, txt in triples
    )
    url = (
        f"{WorkspaceClient().config.host}/explore/data/"
        f"{ctx.catalog}/{ctx.data_schema}"
    )
    cat_link = f"<a href='{url}' target='_blank'>Catalog</a>"
    scope = f"the <code>{_esc(table)}</code> table" if table else "each table"
    return _wrap(
        "<h3>Document a column by hand</h3>"
        f"<p>In {cat_link} → <b>your</b> schema → open {scope}, click a "
        "column, and add its description - try the ✨ <b>Generate a comment</b> "
        "button. Do a "
        "couple to see how it works; the next cell fills in the rest:</p>"
        f"<table><tr><th>Column</th><th>Comment</th></tr>{rows}</table>"
        + "".join(_wide_img(ctx, s) for s in (screenshots or []))
        + "<div class='callout'>Comments live in Unity Catalog - every user, "
        "tool <i>and Genie Agent</i> sees them from now on.</div>"
    )


def curation_ui_steps(ctx) -> str:
    """Module 3: curate a Genie Agent - general instructions (Instructions tab)
    plus measures, a filter, a join and an example query (Examples tab)."""
    cur = ctx.section("genie", "curation")
    ex = cur["example_query"]
    join = cur["join"]

    def img(name):
        if not name:
            return ""
        return _wide_img(ctx, name) or (
            "<div style='border:2px dashed #C4CDD2;border-radius:10px;padding:18px;"
            "color:#7A8A92;text-align:center;margin:6px 0 20px'>📷 screenshot "
            f"pending: <code>{_esc(name)}</code></div>"
        )

    items = [
        "Open your agent, then click <b>Configure</b> → the <b>Instructions</b> "
        "tab. Under <b>General Instructions</b>, paste this plain-language guidance "
        "for how the agent should behave, then click <b>Save</b>:"
        + _copy_pre(cur["general_instructions"])
        + img(cur.get("general_screenshot")),
        "Now switch to the <b>Examples</b> tab and click <b>Add</b>. This is where "
        "the structured context lives. The options are:"
        "<ul>"
        "<li><b>Measure</b> - a KPI rolled up across rows, e.g. net revenue or "
        "return rate.</li>"
        "<li><b>Filter</b> - a reusable row condition you can name, e.g. \"last "
        "month\".</li>"
        "<li><b>Join</b> - how two tables relate, so Genie combines them correctly.</li>"
        "<li><b>Field</b> - a derived or relabelled column, e.g. a bucket or "
        "category.</li>"
        "<li><b>Example query</b> - a worked question + SQL that teaches a hard "
        "pattern.</li>"
        "</ul>"
        "You'll add a join, two measures, a filter and an example query."
        + img(cur.get("expression_types_screenshot")),
        f"<b>Add → Join</b>: relate <b>{_esc(join['tables'])}</b> on "
        f"<code>{_esc(join['on'])}</code> ({_esc(join['note'])}), relationship "
        "type <b>Many to One</b>, then <b>Save</b> - so Genie joins them correctly "
        "every time."
        + img(join.get("screenshot")),
    ]
    for expr in cur["sql_expressions"]:
        hint = f"<p>{_esc(expr['hint'])}</p>" if expr.get("hint") else ""
        items.append(
            f"<b>Add → {_esc(expr['kind'])}</b>, then fill in:"
            "<ul>"
            f"<li><b>Name</b>: <code>{_esc(expr['name'])}</code></li>"
            f"<li><b>Synonyms</b>: "
            f"<code>{_esc(', '.join(expr['synonyms']))}</code></li>"
            "</ul>"
            "<b>Expression</b>:" + _copy_pre(expr["expr"])
            + hint
            + img(expr.get("screenshot"))
            + "Click <b>Save</b>."
        )
    items.append(
        "<b>Add → Example query</b> - a hard, multi-step pattern Genie won't "
        f"reliably get on its own. Question:<pre>{_esc(ex['question'])}</pre>"
        "with this SQL:"
        + _copy_pre(ex["sql"])
        + img(ex.get("screenshot"))
        + "Click <b>Save</b>."
    )
    items.append(
        "Your <b>Examples</b> tab now lists all five - the join, two measures, the "
        "filter and the example query. Start a <b>new chat</b> with your agent to "
        "test them."
        + img("03_10_examples_list.png")
    )
    return steps("Curate your Genie Agent", items)


def metric_view_ui_steps(ctx) -> str:
    """Module 4: UI click-path to create the metric view (mirrors genie_ui_steps)."""
    from databricks.sdk import WorkspaceClient

    url = (
        f"{WorkspaceClient().config.host}/explore/data/"
        f"{ctx.catalog}/{ctx.user_schema}"
    )
    items = [
        f"In the sidebar, open <a href='{url}' target='_blank'>Catalog</a> and "
        f"go to your schema <code>{_esc(ctx.user_schema)}</code>.",
        "Click <b>Create</b> → <b>Metric view</b>."
        + _wide_img(ctx, "04_1_create_menu.png"),
        f"Name it <code>{_esc(ctx.metric_view_name)}</code>, leave the location "
        "set to your catalog and schema, then click <b>Create</b>."
        + _wide_img(ctx, "04_2_create_dialog.png"),
        "Switch to the <b>YAML editor</b> (the <code>&lt;&gt;</code> toggle, top "
        "right), paste the YAML from above, then click <b>Save</b>."
        + _wide_img(ctx, "04_3_yaml_editor.png"),
        "Your metric view now exists - with all its measures and dimensions "
        "defined in one place."
        + _wide_img(ctx, "04_4_metric_view_created.png"),
    ]
    lis = "".join(f"<li>{s}</li>" for s in items)
    return _wrap(
        "<h3>Create your metric view (UI)</h3>"
        f"<ol class='steps'>{lis}</ol>"
    )


def _answer_cards(ctx, answers) -> str:
    """Render one card per question: 'Qn: <question>' + verdict badge, note,
    screenshot (and SQL if present). Answers pair with questions.ask by order."""
    questions = ctx.section("questions", "ask")
    cards = ""
    for i, a in enumerate(ctx.resolve(answers or [])):
        ok = a.get("verdict") == "correct"
        badge = (
            f"<span class='{'same' if ok else 'diff'}' "
            f"style='font-size:1.2em;white-space:nowrap'>"
            f"{'✅ Correct' if ok else '❌ Wrong'}</span>"
        )
        heading = f"Q{i+1}: {_esc(questions[i])}" if i < len(questions) else _esc(a["metric"])
        sql = f"<pre>{_esc(a['sql'].strip())}</pre>" if a.get("sql") else ""
        cards += (
            f"<h4 style='margin:16px 0 6px'>{heading} &nbsp;{badge}</h4>"
            f"<p>{a['note']}</p>"
            + _wide_img(ctx, a.get("screenshot"))
            + sql
        )
    return cards


def question_scorecard(ctx, screenshot: str | None = None,
                       mode: str = "discover") -> str:
    """Ask-Genie block. `mode` sets the framing:
       discover  (Module 2) - Genie has no context, watch it guess.
       taught    (Module 3) - you gave it context, check it follows it.
       governed  (Module 5) - on the metric view, check it uses MEASURE().
    """
    questions = ctx.section("questions", "ask")
    rows = "".join(
        f"<tr><td class='idx'>{i+1}</td><td>{_esc(q)}</td></tr>"
        for i, q in enumerate(questions)
    )
    table = f"<table><tr><th></th><th>Question</th></tr>{rows}</table>"

    if mode == "taught":
        return _wrap(
            "<h3>Ask Genie again</h3>"
            "<p>Ask the same questions in your agent - start a <b>new chat</b>. "
            "This time Genie has the measures, filter and instructions you just "
            "gave it:</p>"
            + table
            + "<h3>Did it use your definitions?</h3>"
            "<p>Click <b>Show code</b> under each answer and compare to Module 2:</p>"
            "<ul>"
            "<li><b>Return rate</b>: it should now divide by <b>fulfilled "
            "orders</b> (completed + returned) - your <code>return_rate</code> "
            "measure - instead of all orders. The number moves from ~10.9% to "
            "~11.5%.</li>"
            "<li><b>Revenue</b>: still completed orders, net of discounts - but "
            "now it's your <code>net_revenue</code> measure, not a guess.</li>"
            "</ul>"
            + _answer_cards(ctx, ctx.raw.get("genie", {}).get("taught_answers"))
        )
    if mode == "governed":
        return _wrap(
            "<h3>Ask the same questions</h3>"
            "<p>In your metric-view agent, ask the same questions - "
            "<b>new chat</b> - then open <b>Show code</b>:</p>"
            + table
            + "<h3>Genie uses the metric view</h3>"
            + _answer_cards(ctx, ctx.raw.get("genie", {}).get("governed_answers"))
        )
    return _wrap(
        "<h3>Ask Genie</h3>"
        "<p>Ask each of these in your agent, then open <b>Show code</b> to see "
        "the SQL Genie wrote:</p>"
        + table
        + "<h3>What Genie generated</h3>"
        + _answer_cards(ctx, ctx.raw.get("questions", {}).get("answers"))
        + "<div class='callout'>Genie is powerful - but definitions like these "
        "are <b>business decisions</b>, not something to leave to a guess. "
        "Next, you'll give Genie some business context.</div>"
    )


def qa_compare(results: list[dict]) -> str:
    """Side-by-side rendering of ask_pairs() output."""
    blocks = []
    for i, r in enumerate(results):
        sql_a = _esc(r["answer_a"]["sql"] or "(no SQL)")
        sql_b = _esc(r["answer_b"]["sql"] or "(no SQL)")
        same = (r["answer_a"]["sql"] or "") == (r["answer_b"]["sql"] or "")
        verdict = (
            "<span class='same'>identical SQL</span>" if same
            else "<span class='diff'>different SQL</span>"
        )
        blocks.append(
            f"<h3>Pair {i+1} - {verdict}</h3>"
            f"<table><tr><th>{_esc(r['question_a'])}</th>"
            f"<th>{_esc(r['question_b'])}</th></tr>"
            f"<tr><td><pre>{sql_a}</pre></td><td><pre>{sql_b}</pre></td></tr></table>"
        )
    return _wrap("".join(blocks))
