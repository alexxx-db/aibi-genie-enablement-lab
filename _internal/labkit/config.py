"""Dataset bundle loading and placeholder resolution.

A *dataset bundle* is a folder under ``datasets/`` containing:

- ``dataset.yaml`` (or ``dataset.json``) - the lab setup & customization file:
  data-generation spec, ambiguity story, Genie questions/instructions.
- ``metric_view.yaml`` - the Databricks metric view body deployed in module 4.

Every string in a bundle may contain placeholders that are resolved at
runtime against the learner/instructor context:

    {catalog}      UC catalog for the lab (pre-existing; never created)
    {data_schema}  schema holding the learner's data copy (= their user schema)
    {user_schema}  learner's personal schema (user_<name>)
    {user}         short learner name derived from their login email
    {metric_view}  fully qualified metric view name
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _yaml():
    """PyYAML, auto-installed if missing (serverless base env lacks it)."""
    try:
        import yaml
    except ModuleNotFoundError:
        import subprocess
        import sys as _sys

        subprocess.check_call(
            [_sys.executable, "-m", "pip", "install", "-q",
             "--disable-pip-version-check", "--no-input", "pyyaml"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        import yaml
    return yaml


def _load_structured(path_yaml: Path, path_json: Path) -> dict:
    """Load a bundle manifest from YAML or JSON (either is accepted)."""
    if path_yaml.exists():
        return _yaml().safe_load(path_yaml.read_text())
    if path_json.exists():
        return json.loads(path_json.read_text())
    raise FileNotFoundError(
        f"No dataset.yaml or dataset.json found next to {path_yaml.parent}"
    )


def sanitize_user(email_or_name: str) -> str:
    """'Jane.Doe@databricks.com' -> 'jane_doe' (safe for schema/object names)."""
    local = email_or_name.split("@")[0].lower()
    return re.sub(r"[^a-z0-9]+", "_", local).strip("_")


def list_datasets(repo_root: str | Path) -> list[str]:
    """Names of all dataset bundles available under datasets/."""
    root = Path(repo_root) / "datasets"
    return sorted(
        p.name
        for p in root.iterdir()
        if p.is_dir() and ((p / "dataset.yaml").exists() or (p / "dataset.json").exists())
    )


@dataclass
class LabContext:
    """Everything notebooks need to know, in one object."""

    repo_root: Path
    dataset_name: str
    catalog: str
    user: str
    raw: dict = field(repr=False, default_factory=dict)

    # ---------------------------------------------------------------- loading
    @classmethod
    def load(
        cls,
        repo_root: str | Path,
        dataset_name: str,
        current_user: str,
        catalog: str | None = None,
    ) -> "LabContext":
        bundle_dir = Path(repo_root) / "datasets" / dataset_name
        raw = _load_structured(bundle_dir / "dataset.yaml", bundle_dir / "dataset.json")
        return cls(
            repo_root=Path(repo_root),
            dataset_name=dataset_name,
            catalog=catalog or raw["defaults"]["catalog"],
            user=sanitize_user(current_user),
            raw=raw,
        )

    # ------------------------------------------------------------- identities
    @property
    def user_schema(self) -> str:
        return f"user_{self.user}"

    @property
    def data_schema(self) -> str:
        """Where this user's data tables live: their own schema.

        Every learner generates an identical copy (datagen is deterministic
        per seed), so numbers match across the room while each learner fully
        owns their tables (needed for module 3's column comments).
        """
        return self.user_schema

    @property
    def metric_view_name(self) -> str:
        return self.raw["metric_view"]["name"]

    @property
    def metric_view_fqn(self) -> str:
        return f"{self.catalog}.{self.user_schema}.{self.metric_view_name}"

    @property
    def placeholders(self) -> dict[str, str]:
        return {
            "{catalog}": self.catalog,
            "{data_schema}": self.data_schema,
            "{user_schema}": self.user_schema,
            "{user}": self.user,
            "{metric_view}": self.metric_view_fqn,
        }

    # ------------------------------------------------------------- resolution
    def resolve(self, value: Any) -> Any:
        """Recursively substitute placeholders in strings/lists/dicts."""
        if isinstance(value, str):
            for token, replacement in self.placeholders.items():
                value = value.replace(token, replacement)
            return value
        if isinstance(value, list):
            return [self.resolve(v) for v in value]
        if isinstance(value, dict):
            return {k: self.resolve(v) for k, v in value.items()}
        return value

    def section(self, *keys: str) -> Any:
        """Fetch a bundle section with placeholders resolved.

        Example: ctx.section("genie", "raw_space")
        """
        node: Any = self.raw
        for key in keys:
            node = node[key]
        return self.resolve(node)

    # ---------------------------------------------------------------- assets
    def metric_view_body(self) -> str:
        """The metric view YAML body with placeholders resolved."""
        file_name = self.raw["metric_view"].get("file", "metric_view.yaml")
        body = (self.repo_root / "datasets" / self.dataset_name / file_name).read_text()
        return self.resolve(body)

    def metric_view_ddl(self) -> str:
        """Full CREATE statement deploying the metric view to the user schema."""
        if "$$" in self.metric_view_body():
            raise ValueError(
                "metric_view.yaml must not contain '$$' - it is deployed "
                "inside a dollar-quoted SQL string ($$...$$) and would "
                "terminate it early."
            )
        return (
            f"CREATE OR REPLACE VIEW {self.metric_view_fqn}\n"
            f"WITH METRICS\nLANGUAGE YAML\nAS $$\n{self.metric_view_body()}\n$$"
        )

    def data_table_fqns(self) -> dict[str, str]:
        """table name -> fully qualified name in the shared data schema."""
        return {
            t: f"{self.catalog}.{self.data_schema}.{t}" for t in self.raw["tables"]
        }
