CREATE TABLE templates(
  template_name VARCHAR(30) CONSTRAINT form_templates_pk PRIMARY KEY,
  measurement_name VARCHAR(30),
  description VARCHAR(300),
  user_email VARCHAR(50),
  warmup INTEGER NOT NULL,
  series_duration INTEGER NOT NULL,
  frequency INTEGER NOT NULL,
  relay_wait INTEGER NOT NULL,
  active_ports JSONB NOT NULL,
  phases JSONB NOT NULL);
  
CREATE TABLE measured_values(
  id SERIAL PRIMARY KEY,
  m_id INTEGER REFERENCES measurements ON DELETE CASCADE,
  time INTEGER,
  values JSONB);

CREATE TABLE measurements(
  id serial PRIMARY KEY,
  measurement_name VARCHAR(30),
  description VARCHAR(300),
  user_email VARCHAR(50),
  warmup INTEGER NOT NULL,
  series_duration INTEGER NOT NULL,
  frequency INTEGER NOT NULL,
  relay_wait INTEGER NOT NULL,
  active_ports JSONB NOT NULL,
  phases JSONB NOT NULL,
  start TIMESTAMP(0) NOT NULL,
  expected_end TIMESTAMP(0) NOT NULL,
  actual_end TIMESTAMP(0),
  running BOOLEAN NOT NULL,
  natural_finish BOOLEAN);
