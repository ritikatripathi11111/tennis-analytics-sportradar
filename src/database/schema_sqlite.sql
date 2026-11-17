-- SQLite fallback with the same logical schema (zero-setup demo mode).

CREATE TABLE IF NOT EXISTS categories (
    category_id   VARCHAR(50)  PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS competitions (
    competition_id   VARCHAR(50)  PRIMARY KEY,
    competition_name VARCHAR(100) NOT NULL,
    parent_id        VARCHAR(50)  NULL,
    type             VARCHAR(20)  NOT NULL,
    gender           VARCHAR(10)  NOT NULL,
    category_id      VARCHAR(50)  NULL REFERENCES categories (category_id)
);
CREATE INDEX IF NOT EXISTS idx_competitions_category ON competitions (category_id);
CREATE INDEX IF NOT EXISTS idx_competitions_parent   ON competitions (parent_id);
CREATE INDEX IF NOT EXISTS idx_competitions_type     ON competitions (type);

CREATE TABLE IF NOT EXISTS complexes (
    complex_id   VARCHAR(50)  PRIMARY KEY,
    complex_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS venues (
    venue_id     VARCHAR(50)  PRIMARY KEY,
    venue_name   VARCHAR(100) NOT NULL,
    city_name    VARCHAR(100) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    country_code CHAR(3)      NOT NULL,
    timezone     VARCHAR(100) NOT NULL,
    complex_id   VARCHAR(50)  NULL REFERENCES complexes (complex_id)
);
CREATE INDEX IF NOT EXISTS idx_venues_complex ON venues (complex_id);
CREATE INDEX IF NOT EXISTS idx_venues_country ON venues (country_name);

CREATE TABLE IF NOT EXISTS competitors (
    competitor_id VARCHAR(50)  PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    country       VARCHAR(100) NOT NULL,
    country_code  CHAR(3)      NOT NULL,
    abbreviation  VARCHAR(10)  NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_competitors_country ON competitors (country);
CREATE INDEX IF NOT EXISTS idx_competitors_name    ON competitors (name);

CREATE TABLE IF NOT EXISTS competitor_rankings (
    rank_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    `rank`              INT NOT NULL,
    movement            INT NOT NULL,
    points              INT NOT NULL,
    competitions_played INT NOT NULL,
    competitor_id       VARCHAR(50) NOT NULL REFERENCES competitors (competitor_id),
    tour                VARCHAR(10) NOT NULL,
    gender              VARCHAR(10) NOT NULL,
    ranking_year        SMALLINT    NOT NULL,
    ranking_week        SMALLINT    NOT NULL,
    UNIQUE (tour, ranking_year, ranking_week, competitor_id)
);
CREATE INDEX IF NOT EXISTS idx_rankings_rank   ON competitor_rankings (`rank`);
CREATE INDEX IF NOT EXISTS idx_rankings_points ON competitor_rankings (points);
CREATE INDEX IF NOT EXISTS idx_rankings_period ON competitor_rankings (ranking_year, ranking_week);

CREATE TABLE IF NOT EXISTS etl_runs (
    run_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    data_source       VARCHAR(20) NOT NULL,
    loaded_at         DATETIME    NOT NULL,
    competitions_rows INT NOT NULL,
    venues_rows       INT NOT NULL,
    rankings_rows     INT NOT NULL
);

DROP VIEW IF EXISTS v_latest_rankings;

CREATE VIEW v_latest_rankings AS
SELECT r.*
FROM competitor_rankings r
JOIN (
    SELECT tour, MAX(ranking_year * 100 + ranking_week) AS year_week
    FROM competitor_rankings
    GROUP BY tour
) latest
  ON latest.tour = r.tour
 AND latest.year_week = r.ranking_year * 100 + r.ranking_week;
