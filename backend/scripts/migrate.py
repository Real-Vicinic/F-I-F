import os, pathlib, psycopg

M = pathlib.Path(__file__).parents[1] / "migrations"
with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as c:
    c.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY)")
    done = {r[0] for r in c.execute("SELECT name FROM schema_migrations")}
    for f in sorted(M.glob("*.sql")):
        if f.name in done:
            continue
        c.execute(f.read_text())
        c.execute("INSERT INTO schema_migrations VALUES (%s)", (f.name,))
        print("applied", f.name)
