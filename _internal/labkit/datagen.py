"""Generic synthetic-data engine, driven entirely by a dataset bundle.

No dataset-specific logic lives here: the ``tables:`` section of
``dataset.yaml`` declares tables, columns and generators; this module turns
that spec into Delta tables. Deterministic per (seed, scale).

Supported generators (``gen:`` on each column):

    id            sequential integer key, 1..n
    int           uniform integer            (min, max)
    float         uniform float              (min, max, round)
    choice        weighted categorical       (values, weights?)
    date          absolute window (start, end: YYYY-MM-DD) or relative past
                  (days_back_min, days_back_max, recency_bias?: skew recent)
    person_name   realistic-looking "First Last"
    product_name  realistic-looking "Adjective Noun"
    fk            random key sampled from a parent table (table, column)
    parent_key    parent's key (only with rows_per_parent tables)
    lookup        copy a parent column via an fk column   (via, table, key, column)
    derived       Spark SQL expression over this table's columns (expr)

Tables generate in the order listed in the bundle - parents before children.
Child cardinality: either ``rows:`` or ``rows_per_parent: {table, key, min, max}``.
"""

from __future__ import annotations

import datetime as dt
import random


def _as_date(value) -> dt.date:
    """YAML gives datetime.date for YYYY-MM-DD; JSON gives a string."""
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))

_FIRST_NAMES = [
    "Ava", "Ben", "Carlos", "Dana", "Elif", "Femke", "Grace", "Hugo", "Ines",
    "Jonas", "Kira", "Liam", "Mia", "Noah", "Olga", "Pieter", "Quinn", "Rosa",
    "Sven", "Tara", "Umut", "Vera", "Wim", "Xena", "Yusuf", "Zoe",
]
_LAST_NAMES = [
    "Anderson", "Bakker", "Chen", "Dubois", "Eriksen", "Fischer", "Garcia",
    "Hansen", "Ivanov", "Jansen", "Kim", "Lopez", "Meyer", "Nguyen", "Okafor",
    "Peeters", "Quist", "Rossi", "Schmidt", "Tanaka", "Ueda", "Visser",
    "Weber", "Xu", "Yilmaz", "Zhang",
]
_ADJECTIVES = [
    "Aurora", "Blaze", "Cascade", "Delta", "Echo", "Flux", "Glide", "Halo",
    "Ion", "Jet", "Kinetic", "Lumen", "Momentum", "Nimbus", "Orbit", "Pulse",
    "Quartz", "Ridge", "Summit", "Terra", "Ultra", "Vertex", "Wave", "Zenith",
]
_NOUNS = [
    "Backpack", "Blender", "Camera", "Desk Lamp", "Earbuds", "Grill", "Hoodie",
    "Jacket", "Kettle", "Keyboard", "Monitor", "Mug", "Puzzle", "Scooter",
    "Sleeping Bag", "Smartwatch", "Sneakers", "Speaker", "Tent", "Toaster",
    "Tripod", "Water Bottle",
]


def ensure_data(spark, ctx, scale: float = 1.0) -> bool:
    """Create the learner's schema and generate their data copy if missing.

    Deterministic per seed, so every learner's copy holds identical numbers.
    Returns True if data was (re)generated, False if it already existed.
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {ctx.catalog}.{ctx.user_schema}")
    first_table = next(iter(ctx.raw["tables"]))
    if spark.catalog.tableExists(f"{ctx.catalog}.{ctx.user_schema}.{first_table}"):
        return False
    DataGenerator(spark, ctx, scale=scale).run()
    return True


def column_comments(ctx) -> list[tuple[str, str, str]]:
    """(table, column, comment) triples declared in the bundle.

    Deliberately NOT applied at generation time: adding them is a lab step
    (module 3) - learners must first experience Genie without documentation.
    """
    return [
        (t, c["name"], c["comment"])
        for t, spec in ctx.raw["tables"].items()
        for c in spec["columns"]
        if c.get("comment")
    ]


def apply_column_comments(spark, ctx) -> int:
    """Apply the bundle's column comments to the learner's tables.

    Returns the number of comments applied.
    """
    triples = column_comments(ctx)
    for table, column, comment in triples:
        fqn = f"{ctx.catalog}.{ctx.data_schema}.{table}"
        safe = comment.replace("'", "\\'")
        spark.sql(f"COMMENT ON COLUMN {fqn}.{column} IS '{safe}'")
    return len(triples)


class DataGenerator:
    """Generates all tables of a bundle into ``catalog.data_schema``."""

    def __init__(self, spark, ctx, scale: float = 1.0):
        self.spark = spark
        self.ctx = ctx
        self.scale = scale
        self.rng = random.Random(ctx.raw.get("seed", 0))
        self._generated: dict[str, list[dict]] = {}  # table -> rows (python)

    # ------------------------------------------------------------------ public
    def run(self) -> dict[str, int]:
        """Generate and save every table. Returns {table: row_count}."""
        counts = {}
        for table_name, spec in self.ctx.raw["tables"].items():
            rows = self._build_rows(table_name, spec)
            self._generated[table_name] = rows
            self._save(table_name, spec, rows)
            counts[table_name] = len(rows)
        return counts

    # ------------------------------------------------------------- row builder
    def _build_rows(self, table_name: str, spec: dict) -> list[dict]:
        parent_keys = self._expand_parents(spec)
        n = len(parent_keys) if parent_keys is not None else max(
            1, int(spec["rows"] * self.scale)
        )
        columns = spec["columns"]
        rows: list[dict] = []
        for i in range(n):
            row: dict = {}
            for col in columns:
                gen = col["gen"]
                if gen == "derived":
                    continue  # applied later in Spark
                row[col["name"]] = self._value(gen, col, i, row, parent_keys)
            rows.append(row)
        return rows

    def _expand_parents(self, spec: dict) -> list | None:
        """For rows_per_parent tables: one entry per child row = parent key."""
        rpp = spec.get("rows_per_parent")
        if not rpp:
            return None
        parent_rows = self._generated[rpp["table"]]
        keys = []
        for parent in parent_rows:
            for _ in range(self.rng.randint(rpp["min"], rpp["max"])):
                keys.append(parent[rpp["key"]])
        return keys

    # -------------------------------------------------------------- generators
    def _value(self, gen: str, col: dict, i: int, row: dict, parent_keys):
        if gen == "id":
            return i + 1
        if gen == "int":
            return self.rng.randint(col["min"], col["max"])
        if gen == "float":
            v = self.rng.uniform(col["min"], col["max"])
            return round(v, col.get("round", 2))
        if gen == "choice":
            values = col["values"]
            weights = col.get("weights")
            return self.rng.choices(values, weights=weights, k=1)[0]
        if gen == "date":
            if "start" in col and "end" in col:
                # absolute window: fully deterministic regardless of run date
                start, end = _as_date(col["start"]), _as_date(col["end"])
                return start + dt.timedelta(
                    days=self.rng.randint(0, (end - start).days)
                )
            lo, hi = col["days_back_min"], col["days_back_max"]
            if col.get("recency_bias"):
                # beta(1,3) skews toward 0 days back -> more recent activity
                back = lo + int(self.rng.betavariate(1, 3) * (hi - lo))
            else:
                back = self.rng.randint(lo, hi)
            return dt.date.today() - dt.timedelta(days=back)
        if gen == "person_name":
            return f"{self.rng.choice(_FIRST_NAMES)} {self.rng.choice(_LAST_NAMES)}"
        if gen == "product_name":
            return f"{self.rng.choice(_ADJECTIVES)} {self.rng.choice(_NOUNS)}"
        if gen == "fk":
            parent = self._generated[col["table"]]
            return self.rng.choice(parent)[col["column"]]
        if gen == "parent_key":
            return parent_keys[i]
        if gen == "lookup":
            mapping = self._lookup_map(col["table"], col["key"], col["column"])
            return mapping[row[col["via"]]]
        raise ValueError(f"Unknown generator '{gen}' on column '{col['name']}'")

    def _lookup_map(self, table: str, key: str, column: str) -> dict:
        cache_key = f"__lk_{table}_{key}_{column}"
        cached = getattr(self, cache_key, None)
        if cached is None:
            cached = {r[key]: r[column] for r in self._generated[table]}
            setattr(self, cache_key, cached)
        return cached

    # ------------------------------------------------------------------- save
    def _save(self, table_name: str, spec: dict, rows: list[dict]) -> None:
        from pyspark.sql import functions as F
        from pyspark.sql import types as T

        def spark_type(col: dict) -> T.DataType:
            """Infer the Spark type from the generator spec / actual values."""
            fixed = {
                "id": T.LongType(), "int": T.LongType(), "float": T.DoubleType(),
                "date": T.DateType(), "parent_key": T.LongType(),
                "fk": T.LongType(), "person_name": T.StringType(),
                "product_name": T.StringType(),
            }
            if col["gen"] in fixed:
                return fixed[col["gen"]]
            if col["gen"] == "choice":  # numeric choices must stay numeric
                values = col["values"]
                if all(isinstance(v, (int, float)) and not isinstance(v, bool)
                       for v in values):
                    return (T.DoubleType()
                            if any(isinstance(v, float) for v in values)
                            else T.LongType())
                return T.StringType()
            # lookup & anything else: infer from the first generated value
            sample = rows[0][col["name"]]
            if isinstance(sample, bool):
                return T.BooleanType()
            if isinstance(sample, int):
                return T.LongType()
            if isinstance(sample, float):
                return T.DoubleType()
            return T.StringType()

        base_cols = [c for c in spec["columns"] if c["gen"] != "derived"]
        schema = T.StructType(
            [T.StructField(c["name"], spark_type(c)) for c in base_cols]
        )
        def coerce(value, dtype):
            if value is not None and isinstance(dtype, T.DoubleType):
                return float(value)  # e.g. YAML `0` among float choices
            return value

        df = self.spark.createDataFrame(
            [
                tuple(coerce(r[c["name"]], f.dataType)
                      for c, f in zip(base_cols, schema.fields))
                for r in rows
            ],
            schema,
        )
        for c in spec["columns"]:
            if c["gen"] == "derived":
                df = df.withColumn(c["name"], F.expr(c["expr"]))

        fqn = f"{self.ctx.catalog}.{self.ctx.data_schema}.{table_name}"
        df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(fqn)
        comment = spec.get("comment", "").replace("'", "\\'")
        if comment:
            self.spark.sql(f"COMMENT ON TABLE {fqn} IS '{comment}'")
