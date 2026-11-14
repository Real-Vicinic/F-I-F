CREATE TABLE investigations (
  id text PRIMARY KEY,
  name text NOT NULL,
  full_name text,
  family text,
  hardware text,
  facility text,
  fuel_type text,
  fuels text,
  objective text,
  o2_min real,
  o2_max real,
  o2_note text,
  pressure_psi real,
  airflow text,
  gravity text DEFAULT 'microgravity',
  tags text[] DEFAULT '{}',
  prevention int DEFAULT 0,
  detection int DEFAULT 0,
  suppression int DEFAULT 0,
  earth_application text,
  source_url text,
  safety_relevance_score int DEFAULT 0
);
CREATE TABLE experiments (
  id serial PRIMARY KEY,
  investigation_id text UNIQUE REFERENCES investigations(id) ON DELETE CASCADE,
  variables_json jsonb DEFAULT '[]',
  sensors_json jsonb DEFAULT '[]'
);
CREATE TABLE chunks (
  id serial PRIMARY KEY,
  investigation_id text REFERENCES investigations(id) ON DELETE CASCADE,
  kind text,
  text text NOT NULL,
  tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED
);
CREATE INDEX chunks_tsv_idx ON chunks USING gin (tsv);
