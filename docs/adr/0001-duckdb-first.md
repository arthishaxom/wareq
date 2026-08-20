# DuckDB-first engine

Wareq is built DuckDB-first: checks execute against local DuckDB databases, and the local CI loop runs entirely on DuckDB. Snowflake and PySpark adapters are explicitly deferred from v1.

This is a deliberate scope decision, not a temporary implementation detail: the v1 mission is a local, CLI-first data-quality engine, and adding warehouse adapters before the first vertical slice is proven would multiply surface area without a demonstrated need. See the migrated mission in `docs/product/mission.md` for the full v1 boundary.