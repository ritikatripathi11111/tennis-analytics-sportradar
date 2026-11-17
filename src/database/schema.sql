-- Create the six logical tables described in the project brief.
-- Categories, Competitions, Complexes, Venues, Competitors, Competitor_Rankings
-- =====================================================================
-- Tennis Analytics schema (MySQL 8+). Statements are separated by ';'
-- Normalised: categories -> competitions, complexes -> venues,
--             competitors -> competitor_rankings (weekly snapshots)
-- NOTE: `rank` is a reserved word in MySQL 8, so it is always quoted.
-- =====================================================================

CREATE TABLE IF NOT EXISTS categories (
    category_id   VARCHAR(50)  PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS competitions (
    competition_id   VARCHAR(50)  PRIMARY KEY,
    competition_name VARCHAR(100) NOT NULL,
    parent_id        VARCHAR(50)  NULL,
    type             VARCHAR(20)  NOT NULL,
    gender           VARCHAR(10)  NOT NULL,
    category_id      VARCHAR(50)  NULL,
    CONSTRAINT fk_competitions_category
        FOREIGN KEY (category_id) REFERENCES categories (category_id),
    INDEX idx_competitions_category (category_id),
    INDEX idx_competitions_parent   (parent_id),
    INDEX idx_competitions_type     (type)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS complexes (
    complex_id   VARCHAR(50)  PRIMARY KEY,
    complex_name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS venues (
    venue_id     VARCHAR(50)  PRIMARY KEY,
    venue_name   VARCHAR(100) NOT NULL,
    city_name    VARCHAR(100) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    country_code CHAR(3)      NOT NULL,
    timezone     VARCHAR(100) NOT NULL,
    complex_id   VARCHAR(50)  NULL,
    CONSTRAINT fk_venues_complex
        FOREIGN KEY (complex_id) REFERENCES complexes (complex_id),
    INDEX idx_venues_complex (complex_id),
    INDEX idx_venues_country (country_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS competitors (
    competitor_id VARCHAR(50)  PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    country       VARCHAR(100) NOT NULL,
    country_code  CHAR(3)      NOT NULL,
    abbreviation  VARCHAR(10)  NOT NULL,
    INDEX idx_competitors_country (country),
    INDEX idx_competitors_name    (name)
) ENGINE=InnoDB;

-- tour / gender / ranking_year / ranking_week extend the brief so weekly
-- snapshots can be filtered (the sample UI filters by year, week, gender).
CREATE TABLE IF NOT EXISTS competitor_rankings (
    rank_id            INT AUTO_INCREMENT PRIMARY KEY,
    `rank`             INT NOT NULL,
    movement           INT NOT NULL,
    points             INT NOT NULL,
    competitions_played INT NOT NULL,
    competitor_id      VARCHAR(50) NOT NULL,
    tour               VARCHAR(10) NOT NULL,
    gender             VARCHAR(10) NOT NULL,
    ranking_year       SMALLINT    NOT NULL,
    ranking_week       SMALLINT    NOT NULL,
    CONSTRAINT fk_rankings_competitor
        FOREIGN KEY (competitor_id) REFERENCES competitors (competitor_id),
    UNIQUE KEY uq_ranking_snapshot (tour, ranking_year, ranking_week, competitor_id),
    INDEX idx_rankings_rank   (`rank`),
    INDEX idx_rankings_points (points),
    INDEX idx_rankings_period (ranking_year, ranking_week)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS etl_runs (
    run_id            INT AUTO_INCREMENT PRIMARY KEY,
    data_source       VARCHAR(20) NOT NULL,
    loaded_at         DATETIME    NOT NULL,
    competitions_rows INT NOT NULL,
    venues_rows       INT NOT NULL,
    rankings_rows     INT NOT NULL
) ENGINE=InnoDB;

-- Latest weekly snapshot per tour (used by dashboard and SQL queries)
CREATE OR REPLACE VIEW v_latest_rankings AS
SELECT r.*
FROM competitor_rankings r
JOIN (
    SELECT tour, MAX(ranking_year * 100 + ranking_week) AS year_week
    FROM competitor_rankings
    GROUP BY tour
) latest
  ON latest.tour = r.tour
 AND latest.year_week = r.ranking_year * 100 + r.ranking_week;
