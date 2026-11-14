import os, time

_conn = None
_cache = (0, None)

INV_SQL = ("SELECT i.*, e.variables_json AS variables, e.sensors_json AS sensors FROM investigations i "
           "LEFT JOIN experiments e ON e.investigation_id = i.id")
CHUNK_COLS = "c.investigation_id AS id, COALESCE(i.name, 'NASA brief') AS name, c.text"


def _run(sql, args=None):
    global _conn
    import psycopg
    from psycopg.rows import dict_row
    for attempt in (0, 1):
        try:
            if _conn is None or _conn.closed:
                _conn = psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row, autocommit=True, connect_timeout=10)
            with _conn.cursor() as cur:
                cur.execute(sql, args)
                return cur.fetchall()
        except psycopg.OperationalError:
            _conn = None
            if attempt:
                raise


def investigations():
    global _cache
    if time.time() - _cache[0] > 60 or _cache[1] is None:
        _cache = (time.time(), _run(INV_SQL))
    return _cache[1]


def search_chunks(tsquery, k=8):
    return _run(f"SELECT {CHUNK_COLS}, ts_rank(c.tsv, q) AS rank FROM chunks c "
                "LEFT JOIN investigations i ON i.id = c.investigation_id, to_tsquery('english', %s) q "
                "WHERE c.tsv @@ q ORDER BY rank DESC LIMIT %s", (tsquery, k))


def inv_chunks(inv_id):
    return _run(f"SELECT {CHUNK_COLS} FROM chunks c LEFT JOIN investigations i ON i.id = c.investigation_id "
                "WHERE c.investigation_id = %s ORDER BY c.id", (inv_id,))


def conditions(inv_id=None):
    sql = "SELECT investigation_id, o2_pct, pressure_psi, airflow_cm_s, note, source FROM test_conditions"
    if inv_id:
        return _run(sql + " WHERE investigation_id = %s ORDER BY id", (inv_id,))
    return _run(sql + " ORDER BY investigation_id, id")
