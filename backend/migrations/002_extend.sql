ALTER TABLE investigations
  ADD COLUMN IF NOT EXISTS hardware_family text,
  ADD COLUMN IF NOT EXISTS tier text,
  ADD COLUMN IF NOT EXISTS fuel_geometry text,
  ADD COLUMN IF NOT EXISTS informs text[] DEFAULT '{}';
CREATE TABLE IF NOT EXISTS test_conditions (
  id serial PRIMARY KEY,
  investigation_id text REFERENCES investigations(id) ON DELETE CASCADE,
  o2_pct real,
  pressure_psi real,
  airflow_cm_s real,
  note text,
  source text DEFAULT 'import'
);
CREATE INDEX IF NOT EXISTS test_conditions_inv_idx ON test_conditions (investigation_id);
