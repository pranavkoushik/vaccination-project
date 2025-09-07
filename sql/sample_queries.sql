
-- VACCINATION DATA ANALYSIS - SAMPLE QUERIES

-- 1. EASY LEVEL QUERIES

-- Q1: How do vaccination rates correlate with a decrease in disease incidence?
SELECT 
    ve.antigen_code,
    ve.disease_code,
    CORR(ve.coverage, ve.incidence_rate) AS correlation_coefficient,
    COUNT(*) AS data_points
FROM v_vaccination_effectiveness ve
WHERE ve.coverage IS NOT NULL AND ve.incidence_rate IS NOT NULL
GROUP BY ve.antigen_code, ve.disease_code
HAVING COUNT(*) > 50
ORDER BY correlation_coefficient;

-- Q2: What is the drop-off rate between 1st dose and subsequent doses?
SELECT 
    country_name,
    year,
    antigen_code,
    coverage AS dose_coverage,
    LAG(coverage) OVER (
        PARTITION BY country_code, LEFT(antigen_code, 3) 
        ORDER BY antigen_code
    ) AS previous_dose_coverage,
    coverage - LAG(coverage) OVER (
        PARTITION BY country_code, LEFT(antigen_code, 3) 
        ORDER BY antigen_code
    ) AS dropout_rate
FROM v_coverage_analysis
WHERE antigen_code LIKE '%1' OR antigen_code LIKE '%2' OR antigen_code LIKE '%3'
ORDER BY country_name, year, antigen_code;

-- Q3: Regional vaccination coverage comparison
SELECT 
    who_region,
    year,
    AVG(coverage) AS avg_coverage,
    COUNT(*) AS total_records
FROM v_coverage_analysis
WHERE year >= 2020
GROUP BY who_region, year
ORDER BY year, avg_coverage DESC;

-- Q4: Countries with lowest vaccination coverage
SELECT 
    country_name,
    who_region,
    AVG(coverage) AS avg_coverage
FROM v_coverage_analysis
WHERE year >= 2020
GROUP BY country_name, who_region
HAVING COUNT(*) >= 5
ORDER BY avg_coverage
LIMIT 20;

-- Q5: Vaccination coverage trends over time
SELECT 
    year,
    antigen_code,
    AVG(coverage) AS avg_coverage,
    COUNT(DISTINCT country_code) AS num_countries
FROM v_coverage_analysis
GROUP BY year, antigen_code
ORDER BY year, antigen_code;

-- 2. MEDIUM LEVEL QUERIES (Multiple tables)

-- Q6: Correlation between vaccine introduction and disease case reduction
WITH vaccine_intro AS (
    SELECT country_code, year, vaccine_description
    FROM fact_vaccine_introduction
    WHERE introduction_status = 'Yes'
),
pre_post_cases AS (
    SELECT 
        vi.country_code,
        vi.vaccine_description,
        vi.year AS intro_year,
        AVG(CASE WHEN frc.year < vi.year THEN frc.cases END) AS avg_cases_before,
        AVG(CASE WHEN frc.year > vi.year THEN frc.cases END) AS avg_cases_after
    FROM vaccine_intro vi
    JOIN fact_reported_cases frc ON vi.country_code = frc.country_code
    WHERE frc.year BETWEEN vi.year - 5 AND vi.year + 5
    GROUP BY vi.country_code, vi.vaccine_description, vi.year
    HAVING avg_cases_before IS NOT NULL AND avg_cases_after IS NOT NULL
)
SELECT 
    vaccine_description,
    COUNT(*) AS num_countries,
    AVG(avg_cases_before) AS avg_cases_before_intro,
    AVG(avg_cases_after) AS avg_cases_after_intro,
    AVG((avg_cases_before - avg_cases_after) / avg_cases_before * 100) AS avg_reduction_percent
FROM pre_post_cases
GROUP BY vaccine_description
ORDER BY avg_reduction_percent DESC;

-- Q7: Coverage gaps by antigen and region
SELECT 
    antigen_code,
    antigen_description,
    who_region,
    AVG(coverage) AS avg_coverage,
    MIN(coverage) AS min_coverage,
    MAX(coverage) AS max_coverage,
    MAX(coverage) - MIN(coverage) AS coverage_gap
FROM v_coverage_analysis
WHERE year >= 2020
GROUP BY antigen_code, antigen_description, who_region
ORDER BY coverage_gap DESC;

-- Q8: Disease burden analysis by region
SELECT 
    who_region,
    disease_code,
    disease_description,
    AVG(incidence_rate) AS avg_incidence_rate,
    SUM(cases) AS total_cases,
    COUNT(DISTINCT country_code) AS num_countries
FROM v_disease_burden
WHERE year >= 2020
GROUP BY who_region, disease_code, disease_description
ORDER BY avg_incidence_rate DESC;

-- 3. SCENARIO-BASED QUERIES

-- Q9: Identify regions for resource allocation (low coverage, high disease burden)
SELECT 
    vc.country_name,
    vc.who_region,
    AVG(vc.coverage) AS avg_coverage,
    AVG(db.incidence_rate) AS avg_incidence_rate,
    CASE 
        WHEN AVG(vc.coverage) < 80 AND AVG(db.incidence_rate) > 50 THEN 'High Priority'
        WHEN AVG(vc.coverage) < 80 OR AVG(db.incidence_rate) > 50 THEN 'Medium Priority'
        ELSE 'Low Priority'
    END AS priority_level
FROM v_coverage_analysis vc
LEFT JOIN v_disease_burden db ON vc.country_code = db.country_code AND vc.year = db.year
WHERE vc.year >= 2020
GROUP BY vc.country_name, vc.who_region
ORDER BY priority_level, avg_coverage;

-- Q10: Progress toward 95% vaccination target
SELECT 
    antigen_code,
    antigen_description,
    COUNT(CASE WHEN coverage >= 95 THEN 1 END) AS countries_above_95,
    COUNT(*) AS total_countries,
    ROUND(COUNT(CASE WHEN coverage >= 95 THEN 1 END) * 100.0 / COUNT(*), 2) AS percent_above_95
FROM v_coverage_analysis
WHERE year = (SELECT MAX(year) FROM v_coverage_analysis)
GROUP BY antigen_code, antigen_description
ORDER BY percent_above_95 DESC;
