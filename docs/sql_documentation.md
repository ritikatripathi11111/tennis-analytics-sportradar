# SQL documentation

All queries live in `src/database/queries.sql` and are executable from the dashboard page **SQL Query Lab**. 
Rankings queries read `v_latest_rankings` (newest weekly snapshot per tour). Tested on MySQL 8 and SQLite.


## Competitions

### C1 - List all competitions along with their category name

```sql
SELECT c.competition_id, c.competition_name, c.type, c.gender, cat.category_name
FROM competitions c
LEFT JOIN categories cat ON cat.category_id = c.category_id
ORDER BY cat.category_name, c.competition_name;
```

### C2 - Count the number of competitions in each category

```sql
SELECT cat.category_name, COUNT(c.competition_id) AS competition_count
FROM categories cat
LEFT JOIN competitions c ON c.category_id = cat.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY competition_count DESC;
```

### C3 - Find all competitions of type 'doubles'

```sql
SELECT c.competition_id, c.competition_name, c.gender, cat.category_name
FROM competitions c
LEFT JOIN categories cat ON cat.category_id = c.category_id
WHERE c.type = 'doubles'
ORDER BY c.competition_name;
```

### C4 - Get competitions that belong to a specific category

Default parameters: `category_name=ITF Men`

```sql
SELECT c.competition_id, c.competition_name, c.type, c.gender
FROM competitions c
JOIN categories cat ON cat.category_id = c.category_id
WHERE cat.category_name = :category_name
ORDER BY c.competition_name;
```

### C5 - Identify parent competitions and their sub-competitions

```sql
SELECT p.competition_id AS parent_id, p.competition_name AS parent_name,
       ch.competition_id AS sub_competition_id, ch.competition_name AS sub_competition_name,
       ch.type AS sub_type
FROM competitions p
JOIN competitions ch ON ch.parent_id = p.competition_id
ORDER BY p.competition_name, ch.competition_name;
```

### C6 - Analyze the distribution of competition types by category

```sql
SELECT cat.category_name, c.type, COUNT(*) AS competition_count
FROM competitions c
JOIN categories cat ON cat.category_id = c.category_id
GROUP BY cat.category_name, c.type
ORDER BY cat.category_name, competition_count DESC;
```

### C7 - List all competitions with no parent (top-level competitions)

```sql
SELECT c.competition_id, c.competition_name, c.type, c.gender, cat.category_name
FROM competitions c
LEFT JOIN categories cat ON cat.category_id = c.category_id
WHERE c.parent_id IS NULL
ORDER BY cat.category_name, c.competition_name;
```


## Venues

### V1 - List all venues along with their associated complex name

```sql
SELECT v.venue_id, v.venue_name, v.city_name, v.country_name, cx.complex_name
FROM venues v
JOIN complexes cx ON cx.complex_id = v.complex_id
ORDER BY cx.complex_name, v.venue_name;
```

### V2 - Count the number of venues in each complex

```sql
SELECT cx.complex_name, COUNT(v.venue_id) AS venue_count
FROM complexes cx
LEFT JOIN venues v ON v.complex_id = cx.complex_id
GROUP BY cx.complex_id, cx.complex_name
ORDER BY venue_count DESC, cx.complex_name;
```

### V3 - Get details of venues in a specific country

Default parameters: `country_name=Chile`

```sql
SELECT v.venue_id, v.venue_name, v.city_name, v.country_name, v.country_code, v.timezone, cx.complex_name
FROM venues v
JOIN complexes cx ON cx.complex_id = v.complex_id
WHERE v.country_name = :country_name
ORDER BY v.city_name, v.venue_name;
```

### V4 - Identify all venues and their timezones

```sql
SELECT v.venue_name, v.city_name, v.country_name, v.timezone
FROM venues v
ORDER BY v.timezone, v.venue_name;
```

### V5 - Find complexes that have more than one venue

```sql
SELECT cx.complex_name, COUNT(v.venue_id) AS venue_count
FROM complexes cx
JOIN venues v ON v.complex_id = cx.complex_id
GROUP BY cx.complex_id, cx.complex_name
HAVING COUNT(v.venue_id) > 1
ORDER BY venue_count DESC;
```

### V6 - List venues grouped by country

```sql
SELECT v.country_name, v.country_code, COUNT(*) AS venue_count
FROM venues v
GROUP BY v.country_name, v.country_code
ORDER BY venue_count DESC, v.country_name;
```

### V7 - Find all venues for a specific complex

Default parameters: `complex_name=Nacional`

```sql
SELECT v.venue_id, v.venue_name, v.city_name, v.country_name, v.timezone
FROM venues v
JOIN complexes cx ON cx.complex_id = v.complex_id
WHERE cx.complex_name = :complex_name
ORDER BY v.venue_name;
```


## Rankings

### R1 - Get all competitors with their rank and points

```sql
SELECT lr.tour, lr.`rank`, cp.name, cp.country, lr.points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
ORDER BY lr.tour, lr.`rank`, cp.name;
```

### R2 - Find competitors ranked in the top 5

```sql
SELECT lr.tour, lr.`rank`, cp.name, cp.country, lr.points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.`rank` <= 5
ORDER BY lr.tour, lr.`rank`, cp.name;
```

### R3 - List competitors with no rank movement (stable rank)

```sql
SELECT lr.tour, lr.`rank`, cp.name, cp.country, lr.points, lr.movement
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.movement = 0
ORDER BY lr.tour, lr.`rank`;
```

### R4 - Get the total points of competitors from a specific country

Default parameters: `country=Croatia`

```sql
SELECT cp.country, COUNT(*) AS competitors_ranked, SUM(lr.points) AS total_points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE cp.country = :country
GROUP BY cp.country;
```

### R5 - Count the number of competitors per country

```sql
SELECT cp.country, COUNT(*) AS competitor_count
FROM competitors cp
GROUP BY cp.country
ORDER BY competitor_count DESC, cp.country;
```

### R6 - Find competitors with the highest points in the current week

```sql
SELECT lr.tour, lr.ranking_year, lr.ranking_week, cp.name, cp.country, lr.points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.points = (SELECT MAX(x.points) FROM v_latest_rankings x WHERE x.tour = lr.tour)
ORDER BY lr.tour, cp.name;
```


## Bonus analytics

### B1 - Biggest weekly movers (largest positive movement)

```sql
SELECT lr.tour, cp.name, cp.country, lr.`rank`, lr.movement, lr.points
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
ORDER BY lr.movement DESC, lr.`rank`
LIMIT 10;
```

### B2 - Efficiency - points earned per competition played (top 10, min 10 events)

```sql
SELECT lr.tour, cp.name, cp.country, lr.points, lr.competitions_played,
       ROUND(lr.points * 1.0 / NULLIF(lr.competitions_played, 0), 1) AS points_per_event
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.competitions_played >= 10
ORDER BY points_per_event DESC
LIMIT 10;
```

### B3 - Country share of total points among the top 100 (all tours)

```sql
SELECT cp.country, COUNT(*) AS players_in_top_100, SUM(lr.points) AS points,
       ROUND(100.0 * SUM(lr.points) /
             (SELECT SUM(t.points) FROM v_latest_rankings t WHERE t.`rank` <= 100), 2) AS share_pct
FROM v_latest_rankings lr
JOIN competitors cp ON cp.competitor_id = lr.competitor_id
WHERE lr.`rank` <= 100
GROUP BY cp.country
ORDER BY points DESC
LIMIT 10;
```

### B4 - Competition mix by gender and type

```sql
SELECT c.gender, c.type, COUNT(*) AS competition_count
FROM competitions c
GROUP BY c.gender, c.type
ORDER BY c.gender, competition_count DESC;
```
