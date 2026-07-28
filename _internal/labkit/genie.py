"""Genie Spaces API helpers - powers the notebooks' "fast-forward" cells.

Uses the Databricks SDK with default notebook auth (no tokens to manage).
Two capabilities:

1. Create a Genie space from the dataset bundle (create_space_from_bundle)
2. Ask a space questions programmatically and pull back the generated SQL
   (ask / ask_pairs) - used to demo divergence/convergence in-notebook.

serialized_space format reference:
  https://docs.databricks.com/api/workspace/genie/createspace
If Databricks evolves the serialized format, create a space once in the UI and
run ``export_space(space_id)`` to inspect the current schema, then adjust
``_serialized_space``.
"""

from __future__ import annotations

import json
import time
import uuid


def client():
    """WorkspaceClient with default notebook authentication."""
    from databricks.sdk import WorkspaceClient

    return WorkspaceClient()


def default_warehouse_id(w=None) -> str:
    """Pick a usable SQL warehouse (prefer serverless, then pro)."""
    w = w or client()
    warehouses = list(w.warehouses.list())
    if not warehouses:
        raise RuntimeError("No SQL warehouse visible to you - ask the instructor.")
    for wh in warehouses:
        if getattr(wh, "enable_serverless_compute", False):
            return wh.id
    return warehouses[0].id


# --------------------------------------------------------------------- create
def _serialized_space(space_cfg: dict) -> str:
    """Build the serialized_space JSON from a bundle's genie.* section."""
    data_sources: dict = {}
    if space_cfg.get("tables_fqn"):
        data_sources["tables"] = [  # API requires sorting by identifier
            {"identifier": t} for t in sorted(space_cfg["tables_fqn"])
        ]
    if space_cfg.get("metric_views"):
        data_sources["metric_views"] = [
            {"identifier": mv} for mv in sorted(space_cfg["metric_views"])
        ]

    payload: dict = {"version": 2, "data_sources": data_sources}

    instructions = (space_cfg.get("instructions") or "").strip()
    if instructions:
        payload["instructions"] = {
            "text_instructions": [
                {"id": uuid.uuid4().hex, "content": [instructions]}
            ]
        }

    questions = space_cfg.get("sample_questions") or []
    if questions:
        payload["config"] = {
            "sample_questions": [
                {"id": uuid.uuid4().hex, "question": [q]} for q in questions
            ]
        }
    return json.dumps(payload)


def create_space_from_bundle(ctx, kind: str, warehouse_id: str | None = None):
    """Create a Genie space from the bundle ('raw_space' or 'mv_space').

    Returns the created GenieSpace (with .space_id).
    """
    w = client()
    cfg = dict(ctx.section("genie", kind))
    if "tables" in cfg:  # bundle lists bare table names -> qualify them
        fqns = ctx.data_table_fqns()
        cfg["tables_fqn"] = [fqns[t] for t in cfg["tables"]]

    title = cfg["title_template"].replace("{user}", ctx.user)
    return w.genie.create_space(
        warehouse_id=warehouse_id or default_warehouse_id(w),
        serialized_space=_serialized_space(cfg),
        title=title,
        description=cfg.get("description", ""),
    )


def apply_curation(ctx, space_id: str):
    """Module 3 catch-up: add the bundle's curation (text instructions +
    example question/SQL pairs) to an existing Genie space."""
    w = client()
    space = w.genie.get_space(space_id, include_serialized_space=True)
    payload = json.loads(space.serialized_space)
    cur = ctx.section("genie", "curation")

    instructions = payload.setdefault("instructions", {})
    if cur.get("instructions"):
        instructions["text_instructions"] = [
            {"id": uuid.uuid4().hex, "content": [cur["instructions"]]}
        ]
    if cur.get("example_question_sqls"):
        instructions["example_question_sqls"] = [
            {
                "id": uuid.uuid4().hex,
                "question": [ex["question"]],
                "sql": [ex["sql"].strip()],
            }
            for ex in cur["example_question_sqls"]
        ]
    return w.genie.update_space(
        space_id=space_id, serialized_space=json.dumps(payload)
    )


def export_space(space_id: str) -> dict:
    """Fetch an existing space's serialized definition (schema reference)."""
    w = client()
    space = w.genie.get_space(space_id, include_serialized_space=True)
    return json.loads(space.serialized_space)


# ------------------------------------------------------------------------ ask
def ask(space_id: str, question: str, timeout_s: int = 180) -> dict:
    """Ask a Genie space one question. Returns {'text': ..., 'sql': ...}."""
    import datetime

    w = client()
    conv = None
    if hasattr(w.genie, "start_conversation_and_wait"):
        conv = w.genie.start_conversation_and_wait(
            space_id, question, timeout=datetime.timedelta(seconds=timeout_s)
        )

    if conv is None:  # older SDK: manual poll
        started = w.genie.start_conversation(space_id, question)
        conv_id, msg_id = started.conversation_id, started.message_id
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            msg = w.genie.get_message(space_id, conv_id, msg_id)
            status = str(getattr(msg, "status", ""))
            if "COMPLETED" in status:
                conv = msg
                break
            if any(s in status for s in ("FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED")):
                return {"text": f"(Genie message ended with status {status})", "sql": None}
            time.sleep(3)
        else:
            return {"text": "(timed out waiting for Genie)", "sql": None}

    text, sql = [], None
    for att in getattr(conv, "attachments", None) or []:
        if getattr(att, "text", None):
            text.append(att.text.content)
        if getattr(att, "query", None):
            sql = att.query.query
            if getattr(att.query, "description", None):
                text.append(att.query.description)
    return {"text": "\n".join(text) or "(no text answer)", "sql": sql}


def ask_pairs(space_id: str, pairs: list[list[str]]) -> list[dict]:
    """Ask each pair of rephrasings; return results for side-by-side display."""
    results = []
    for a, b in pairs:
        results.append(
            {"question_a": a, "answer_a": ask(space_id, a),
             "question_b": b, "answer_b": ask(space_id, b)}
        )
    return results
