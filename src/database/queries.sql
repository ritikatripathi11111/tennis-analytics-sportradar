-- =====================================================================
-- Required analysis queries (20) + bonus analytics (4)
-- Format: "-- @key: value" header lines, then one SQL statement.
-- Named parameters (:name) get their defaults from "-- @params".
-- Rankings queries read v_latest_rankings = newest weekly snapshot per tour.
-- Works on MySQL 8 and SQLite 3.25+.
-- =====================================================================

-- @id: C1
-- @group: Competitions
-- @title: List all competitions along with their category name
SELECT c.competition_id, c.competition_name, c.type, c.gender, cat.category_name
FROM competitions c
LEFT JOIN categories cat ON cat.category_id = c.category_id
ORDER BY cat.category_name, c.competition_name;

-- @id: C2
-- @group: Competitions
-- @title: Count the number of competitions in each category
SELECT cat.category_name, COUNT(c.competition_id) AS competition_count
FROM categories cat
LEFT JOIN competitions c ON c.category_id = cat.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY competition_count DESC;

-- @id: C3
-- @group: Competitions
-- @title: Find all competitions of type 'doubles'
SELECT c.competition_id, c.competition_name, c.gender, cat.category_name
FROM competitions c
LEFT JOIN categories cat ON cat.category_id = c.category_id
WHERE c.type = 'doubles'
ORDER BY c.competition_name;

-- @id: C4
-- @group: Competitions
-- @title: Get competitions that belong to a specific category
-- @params: category_name=ITF Men
SELECT c.competition_id, c.competition_name, c.type, c.gender
FROM competitions c
JOIN categories cat ON cat.category_id = c.category_id
WHERE cat.category_name = :category_name
ORDER BY c.competition_name;

-- @id: C5
-- @group: Competitions
-- @title: Identify parent competitions and their sub-competitions
SELECT p.competition_id AS parent_id, p.competition_name AS parent_name,
       ch.competition_id AS sub_competition_id, ch.competition_name AS sub_competition_name,
       ch.type AS sub_type
FROM competitions p
JOIN competitions ch ON ch.parent_id = p.competition_id
ORDER BY p.competition_name, ch.competition_name;

-- @id: C6
-- @group: Competitions
-- @title: Analyze the distribution of competition types by category
SELECT cat.category_name, c.type, COUNT(*) AS competition_count
FROM competitions c
JOIN categories cat ON cat.category_id = c.category_id
GROUP BY cat.category_name, c.type
ORDER BY cat.category_name, competition_count DESC;

-- @id: C7
-- @group: Competitions
-- @title: List all competitions with no parent (top-level competitions)
SELECT c.competition_id, c.competition_name, c.type, c.gender, cat.category_name
FROM competitions c
LEFT JOIN categories cat ON cat.category_id = c.category_id
WHERE c.parent_id IS NULL
ORDER BY cat.category_name, c.competition_name;

-- @id: V1
-- @group: Venues
-- @title: List all venues along with their associated complex name
SELECT v.venue_id, v.venue_name, v.city_name, v.country_name, cx.complex_name
FROM venues v
JOIN complexes cx ON cx.complex_id = v.complex_id
ORDER BY cx.complex_name, v.venue_name;

-- @id: V2
-- @group: Venues
-- @title: Count the number of venues in each complex
SELECT cx.complex_name, COUNT(v.venue_id) AS venue_count
FROM complexes cx
LEFT JOIN venues v ON v.complex_id = cx.complex_id
GROUP BY cx.complex_id, cx.complex_name
ORDER BY venue_count DESC, cx.complex_name;

-- @id: V3
-- @group: Venues
-- @title: Get details of venues in a specific country
-- @params: country_name=Chile
SELECT v.venue_id, v.venue_name, v.city_name, v.country_name, v.country_code, v.timezone, cx.complex_name
FROM venues v
JOIN complexes cx ON cx.complex_id = v.complex_id
WHERE v.country_name = :country_name
ORDER BY v.city_name, v.venue_name;

-- @id: V4
-- @group: Venues
-- @title: Identify all venues and their timezones
SELECT v.venue_name, v.city_name, v.country_name, v.timezone
FROM venues v
ORDER BY v.timezone, v.venue_name;

-- @id: V5
-- @group: Venues
-- @title: Find complexes that have more than one venue
SELECT cx.complex_name, COUNT(v.venue_id) AS venue_count
FROM complexes cx
JOIN venues v ON v.complex_id = cx.complex_id
GROUP BY cx.complex_id, cx.complex_name
HAVING COUNT(v.venue_id) > 1
ORDER BY venue_count DESC;

-- @id: V6
-- @group: Venues
-- @title: List venues grouped by country
SELECT v.country_name, v.country_code, COUNT(*) AS venue_count
FROM venues v
GROUP BY v.country_name, v.country_code
ORDER BY venue_count DESC, v.country_name;

-- @id: V7
-- @group: Venues
-- @title: Find all venues for a specific complex
-- @params: complex_name=Nacional
SELECT v.venue_id, v.venue_name, v.city_name, v.country_name, v.timezone
FROM venues v
JOIN complexes cx ON cx.complex_id = v.complex_id
WHERE cx.complex_name = :complex_name
ORDER BY v.venue_name;

-- @id: R1
-- @group: Rankings
-- @title: Get all competitors with their rank and points
SELECT lr.tour, lr.`rank`, cp.name, cp.country, lr.points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
ORDER BY lr.tour, lr.`rank`, cp.name;

-- @id: R2
-- @group: Rankings
-- @title: Find competitors ranked in the top 5
SELECT lr.tour, lr.`rank`, cp.name, cp.country, lr.points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.`rank` <= 5
ORDER BY lr.tour, lr.`rank`, cp.name;

-- @id: R3
-- @group: Rankings
-- @title: List competitors with no rank movement (stable rank)
SELECT lr.tour, lr.`rank`, cp.name, cp.country, lr.points, lr.movement
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.movement = 0
ORDER BY lr.tour, lr.`rank`;

-- @id: R4
-- @group: Rankings
-- @title: Get the total points of competitors from a specific country
-- @params: country=Croatia
SELECT cp.country, COUNT(*) AS competitors_ranked, SUM(lr.points) AS total_points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE cp.country = :country
GROUP BY cp.country;

-- @id: R5
-- @group: Rankings
-- @title: Count the number of competitors per country
SELECT cp.country, COUNT(*) AS competitor_count
FROM competitors cp
GROUP BY cp.country
ORDER BY competitor_count DESC, cp.country;

-- @id: R6
-- @group: Rankings
-- @title: Find competitors with the highest points in the current week
SELECT lr.tour, lr.ranking_year, lr.ranking_week, cp.name, cp.country, lr.points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.points = (SELECT MAX(x.points) FROM v_latest_rankings x WHERE x.tour = lr.tour)
ORDER BY lr.tour, cp.name;

-- @id: B1
-- @group: Bonus analytics
-- @title: Biggest weekly movers (largest positive movement)
SELECT lr.tour, cp.name, cp.country, lr.`rank`, lr.movement, lr.points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
ORDER BY lr.movement DESC, lr.`rank`
LIMIT 10;

-- @id: B2
-- @group: Bonus analytics
-- @title: Efficiency - points earned per competition played (top 10, min 10 events)
SELECT lr.tour, cp.name, cp.country, lr.points, lr.competitions_played,
       ROUND(lr.points * 1.0 / NULLIF(lr.competitions_played, 0), 1) AS points_per_event
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.competitions_played >= 10
ORDER BY points_per_event DESC
LIMIT 10;

-- @id: B3
-- @group: Bonus analytics
-- @title: Country share of total points among the top 100 (all tours)
SELECT cp.country, COUNT(*) AS players_in_top_100, SUM(lr.points) AS points,
       ROUND(100.0 * SUM(lr.points) /
             (SELECT SUM(t.points) FROM v_latest_rankings t WHERE t.`rank` <= 100), 2) AS share_pct
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.`rank` <= 100
GROUP BY cp.country
ORDER BY points DESC
LIMIT 10;

-- @id: B4
-- @group: Bonus analytics
-- @title: Competition mix by gender and type
SELECT c.gender, c.type, COUNT(*) AS competition_count
FROM competitions c
GROUP BY c.gender, c.type
ORDER BY c.gender, competition_count DESC;
-- Add the 20 required analysis queries here.
