"""
SQL Database Setup Module for Vaccination Data Analysis Project
This module creates and populates SQL database with cleaned vaccination data.
"""

import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text
import os

class VaccinationDatabaseManager:
    """Class to manage SQL database operations for vaccination data."""
    
    def __init__(self, db_path="vaccination_data.db"):
        """
        Initialize database manager.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.connection = None
        
    def create_database_schema(self):
        """Create database schema with proper table structures."""
        print("Creating database schema...")
        
        schema_sql = """
        -- Countries dimension table
        CREATE TABLE IF NOT EXISTS dim_countries (
            country_code TEXT PRIMARY KEY,
            country_name TEXT NOT NULL,
            who_region TEXT
        );
        
        -- Antigens/Vaccines dimension table
        CREATE TABLE IF NOT EXISTS dim_antigens (
            antigen_code TEXT PRIMARY KEY,
            antigen_description TEXT NOT NULL
        );
        
        -- Diseases dimension table
        CREATE TABLE IF NOT EXISTS dim_diseases (
            disease_code TEXT PRIMARY KEY,
            disease_description TEXT NOT NULL
        );
        
        -- Years dimension table
        CREATE TABLE IF NOT EXISTS dim_years (
            year INTEGER PRIMARY KEY,
            decade INTEGER,
            period TEXT
        );
        
        -- Vaccination coverage fact table
        CREATE TABLE IF NOT EXISTS fact_vaccination_coverage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT,
            year INTEGER,
            antigen_code TEXT,
            coverage_category TEXT,
            coverage_category_description TEXT,
            target_number INTEGER,
            doses INTEGER,
            coverage REAL,
            FOREIGN KEY (country_code) REFERENCES dim_countries(country_code),
            FOREIGN KEY (year) REFERENCES dim_years(year),
            FOREIGN KEY (antigen_code) REFERENCES dim_antigens(antigen_code)
        );
        
        -- Disease incidence fact table
        CREATE TABLE IF NOT EXISTS fact_disease_incidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT,
            year INTEGER,
            disease_code TEXT,
            denominator TEXT,
            incidence_rate REAL,
            FOREIGN KEY (country_code) REFERENCES dim_countries(country_code),
            FOREIGN KEY (year) REFERENCES dim_years(year),
            FOREIGN KEY (disease_code) REFERENCES dim_diseases(disease_code)
        );
        
        -- Reported cases fact table
        CREATE TABLE IF NOT EXISTS fact_reported_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT,
            year INTEGER,
            disease_code TEXT,
            cases INTEGER,
            FOREIGN KEY (country_code) REFERENCES dim_countries(country_code),
            FOREIGN KEY (year) REFERENCES dim_years(year),
            FOREIGN KEY (disease_code) REFERENCES dim_diseases(disease_code)
        );
        
        -- Vaccine introduction fact table
        CREATE TABLE IF NOT EXISTS fact_vaccine_introduction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT,
            year INTEGER,
            vaccine_description TEXT,
            introduction_status TEXT,
            FOREIGN KEY (country_code) REFERENCES dim_countries(country_code),
            FOREIGN KEY (year) REFERENCES dim_years(year)
        );
        
        -- Vaccine schedule fact table
        CREATE TABLE IF NOT EXISTS fact_vaccine_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT,
            year INTEGER,
            vaccine_code TEXT,
            vaccine_description TEXT,
            schedule_rounds TEXT,
            target_population TEXT,
            target_population_description TEXT,
            geo_area TEXT,
            age_administered TEXT,
            source_comment TEXT,
            FOREIGN KEY (country_code) REFERENCES dim_countries(country_code),
            FOREIGN KEY (year) REFERENCES dim_years(year)
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_coverage_country_year ON fact_vaccination_coverage(country_code, year);
        CREATE INDEX IF NOT EXISTS idx_incidence_country_year ON fact_disease_incidence(country_code, year);
        CREATE INDEX IF NOT EXISTS idx_cases_country_year ON fact_reported_cases(country_code, year);
        CREATE INDEX IF NOT EXISTS idx_coverage_antigen ON fact_vaccination_coverage(antigen_code);
        CREATE INDEX IF NOT EXISTS idx_incidence_disease ON fact_disease_incidence(disease_code);
        """
        
        with self.engine.connect() as conn:
            # Split and execute each statement
            statements = schema_sql.split(';')
            for statement in statements:
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
        
        print("Database schema created successfully!")
    
    def populate_dimension_tables(self, datasets):
        """Populate dimension tables with reference data."""
        print("Populating dimension tables...")
        
        with self.engine.connect() as conn:
            # Populate countries dimension
            if 'coverage' in datasets:
                countries_df = datasets['coverage'][['CODE', 'NAME']].drop_duplicates()
                countries_df.columns = ['country_code', 'country_name']
                
                # Add WHO regions if available
                if 'vaccine_introduction' in datasets:
                    who_regions = datasets['vaccine_introduction'][['ISO_3_CODE', 'WHO_REGION']].drop_duplicates()
                    who_regions.columns = ['country_code', 'who_region']
                    countries_df = countries_df.merge(who_regions, on='country_code', how='left')
                
                countries_df.to_sql('dim_countries', conn, if_exists='replace', index=False)
                print(f"Inserted {len(countries_df)} countries")
            
            # Populate antigens dimension
            if 'coverage' in datasets:
                antigens_df = datasets['coverage'][['ANTIGEN', 'ANTIGEN_DESCRIPTION']].drop_duplicates()
                antigens_df.columns = ['antigen_code', 'antigen_description']
                antigens_df.to_sql('dim_antigens', conn, if_exists='replace', index=False)
                print(f"Inserted {len(antigens_df)} antigens")
            
            # Populate diseases dimension
            if 'incidence' in datasets:
                diseases_df = datasets['incidence'][['DISEASE', 'DISEASE_DESCRIPTION']].drop_duplicates()
                diseases_df.columns = ['disease_code', 'disease_description']
                diseases_df.to_sql('dim_diseases', conn, if_exists='replace', index=False)
                print(f"Inserted {len(diseases_df)} diseases")
            
            # Populate years dimension
            all_years = set()
            for dataset in datasets.values():
                if 'YEAR' in dataset.columns:
                    all_years.update(dataset['YEAR'].unique())
            
            years_df = pd.DataFrame({'year': sorted(all_years)})
            years_df['decade'] = (years_df['year'] // 10) * 10
            years_df['period'] = years_df['year'].apply(lambda x: 
                'Pre-2000' if x < 2000 else
                '2000-2010' if x < 2010 else
                '2010-2020' if x < 2020 else
                '2020+'
            )
            years_df.to_sql('dim_years', conn, if_exists='replace', index=False)
            print(f"Inserted {len(years_df)} years")
            
            conn.commit()
    
    def populate_fact_tables(self, datasets):
        """Populate fact tables with vaccination and disease data."""
        print("Populating fact tables...")
        
        with self.engine.connect() as conn:
            # Vaccination coverage fact table
            if 'coverage' in datasets:
                coverage_fact = datasets['coverage'][[
                    'CODE', 'YEAR', 'ANTIGEN', 'COVERAGE_CATEGORY', 
                    'COVERAGE_CATEGORY_DESCRIPTION', 'TARGET_NUMBER', 'DOSES', 'COVERAGE'
                ]].copy()
                coverage_fact.columns = [
                    'country_code', 'year', 'antigen_code', 'coverage_category',
                    'coverage_category_description', 'target_number', 'doses', 'coverage'
                ]
                coverage_fact.to_sql('fact_vaccination_coverage', conn, if_exists='replace', index=False)
                print(f"Inserted {len(coverage_fact)} coverage records")
            
            # Disease incidence fact table
            if 'incidence' in datasets:
                incidence_fact = datasets['incidence'][[
                    'CODE', 'YEAR', 'DISEASE', 'DENOMINATOR', 'INCIDENCE_RATE'
                ]].copy()
                incidence_fact.columns = [
                    'country_code', 'year', 'disease_code', 'denominator', 'incidence_rate'
                ]
                incidence_fact.to_sql('fact_disease_incidence', conn, if_exists='replace', index=False)
                print(f"Inserted {len(incidence_fact)} incidence records")
            
            # Reported cases fact table
            if 'reported_cases' in datasets:
                cases_fact = datasets['reported_cases'][['CODE', 'YEAR', 'DISEASE', 'CASES']].copy()
                cases_fact.columns = ['country_code', 'year', 'disease_code', 'cases']
                cases_fact.to_sql('fact_reported_cases', conn, if_exists='replace', index=False)
                print(f"Inserted {len(cases_fact)} reported cases records")
            
            # Vaccine introduction fact table
            if 'vaccine_introduction' in datasets:
                intro_fact = datasets['vaccine_introduction'][[
                    'ISO_3_CODE', 'YEAR', 'DESCRIPTION', 'INTRO'
                ]].copy()
                intro_fact.columns = [
                    'country_code', 'year', 'vaccine_description', 'introduction_status'
                ]
                intro_fact.to_sql('fact_vaccine_introduction', conn, if_exists='replace', index=False)
                print(f"Inserted {len(intro_fact)} vaccine introduction records")
            
            # Vaccine schedule fact table
            if 'vaccine_schedule' in datasets:
                schedule_fact = datasets['vaccine_schedule'][[
                    'ISO_3_CODE', 'YEAR', 'VACCINECODE', 'VACCINE_DESCRIPTION',
                    'SCHEDULEROUNDS', 'TARGETPOP', 'TARGETPOP_DESCRIPTION',
                    'GEOAREA', 'AGEADMINISTERED', 'SOURCECOMMENT'
                ]].copy()
                schedule_fact.columns = [
                    'country_code', 'year', 'vaccine_code', 'vaccine_description',
                    'schedule_rounds', 'target_population', 'target_population_description',
                    'geo_area', 'age_administered', 'source_comment'
                ]
                schedule_fact.to_sql('fact_vaccine_schedule', conn, if_exists='replace', index=False)
                print(f"Inserted {len(schedule_fact)} vaccine schedule records")
            
            conn.commit()
        
        print("All fact tables populated successfully!")
    
    def create_analytical_views(self):
        """Create analytical views for common queries."""
        print("Creating analytical views...")
        
        views_sql = """
        -- View for coverage analysis with country and antigen details
        CREATE VIEW IF NOT EXISTS v_coverage_analysis AS
        SELECT 
            fc.country_code,
            dc.country_name,
            dc.who_region,
            fc.year,
            dy.decade,
            dy.period,
            fc.antigen_code,
            da.antigen_description,
            fc.coverage,
            fc.target_number,
            fc.doses,
            CASE 
                WHEN fc.coverage >= 95 THEN 'High'
                WHEN fc.coverage >= 80 THEN 'Medium'
                ELSE 'Low'
            END AS coverage_level
        FROM fact_vaccination_coverage fc
        JOIN dim_countries dc ON fc.country_code = dc.country_code
        JOIN dim_years dy ON fc.year = dy.year
        JOIN dim_antigens da ON fc.antigen_code = da.antigen_code;
        
        -- View for disease burden analysis
        CREATE VIEW IF NOT EXISTS v_disease_burden AS
        SELECT 
            fdi.country_code,
            dc.country_name,
            dc.who_region,
            fdi.year,
            dy.decade,
            fdi.disease_code,
            dd.disease_description,
            fdi.incidence_rate,
            frc.cases,
            CASE 
                WHEN fdi.incidence_rate > 100 THEN 'High'
                WHEN fdi.incidence_rate > 10 THEN 'Medium'
                ELSE 'Low'
            END AS incidence_level
        FROM fact_disease_incidence fdi
        JOIN dim_countries dc ON fdi.country_code = dc.country_code
        JOIN dim_years dy ON fdi.year = dy.year
        JOIN dim_diseases dd ON fdi.disease_code = dd.disease_code
        LEFT JOIN fact_reported_cases frc ON fdi.country_code = frc.country_code 
            AND fdi.year = frc.year AND fdi.disease_code = frc.disease_code;
        
        -- View for vaccination effectiveness analysis
        CREATE VIEW IF NOT EXISTS v_vaccination_effectiveness AS
        SELECT 
            vc.country_code,
            vc.country_name,
            vc.who_region,
            vc.year,
            vc.antigen_code,
            vc.antigen_description,
            vc.coverage,
            db.disease_code,
            db.disease_description,
            db.incidence_rate,
            db.cases
        FROM v_coverage_analysis vc
        LEFT JOIN v_disease_burden db ON vc.country_code = db.country_code 
            AND vc.year = db.year
        WHERE (
            (vc.antigen_code LIKE '%DTP%' AND db.disease_code = 'DIPHTHERIA') OR
            (vc.antigen_code LIKE '%MCV%' AND db.disease_code = 'MEASLES') OR
            (vc.antigen_code LIKE '%POL%' AND db.disease_code = 'POLIOMYELITIS') OR
            (vc.antigen_code = 'BCG' AND db.disease_code = 'TUBERCULOSIS') OR
            (vc.antigen_code LIKE '%HepB%' AND db.disease_code = 'HEPATITISB')
        );
        """
        
        with self.engine.connect() as conn:
            statements = views_sql.split(';')
            for statement in statements:
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
        
        print("Analytical views created successfully!")
    
    def create_sample_queries(self):
        """Create and save sample SQL queries for analysis."""
        print("Creating sample queries...")
        
        sample_queries = """
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
"""
        
        with open("./sql/sample_queries.sql", "w") as f:
            f.write(sample_queries)
        
        print("Sample queries saved to ./sql/sample_queries.sql")
    
    def generate_database_documentation(self):
        """Generate database documentation."""
        documentation = """
# VACCINATION DATABASE DOCUMENTATION

## Database Structure

### Dimension Tables
1. **dim_countries**: Country reference data
   - country_code (PK): ISO 3-letter country code
   - country_name: Full country name
   - who_region: WHO region classification

2. **dim_antigens**: Vaccine/antigen reference data
   - antigen_code (PK): Antigen identifier
   - antigen_description: Full antigen description

3. **dim_diseases**: Disease reference data
   - disease_code (PK): Disease identifier
   - disease_description: Full disease description

4. **dim_years**: Year dimension for time-based analysis
   - year (PK): Year value
   - decade: Decade grouping
   - period: Period classification

### Fact Tables
1. **fact_vaccination_coverage**: Vaccination coverage data
   - Measures: coverage, target_number, doses
   - Dimensions: country, year, antigen

2. **fact_disease_incidence**: Disease incidence rates
   - Measures: incidence_rate
   - Dimensions: country, year, disease

3. **fact_reported_cases**: Reported disease cases
   - Measures: cases
   - Dimensions: country, year, disease

4. **fact_vaccine_introduction**: Vaccine introduction timeline
   - Measures: introduction_status
   - Dimensions: country, year

5. **fact_vaccine_schedule**: Vaccine administration schedules
   - Measures: schedule details
   - Dimensions: country, year

### Analytical Views
1. **v_coverage_analysis**: Enhanced coverage data with classifications
2. **v_disease_burden**: Disease burden analysis with severity levels
3. **v_vaccination_effectiveness**: Coverage vs. incidence correlation

## Usage Guidelines
- Use views for most analytical queries
- Filter by recent years (>= 2020) for current analysis
- Join fact tables through dimension tables for referential integrity
- Consider data availability when analyzing historical trends

## Performance Notes
- Indexes are created on country_code, year combinations
- Use LIMIT clauses for large result sets
- Consider aggregation for summary reports
"""
        
        with open("./sql/database_documentation.md", "w") as f:
            f.write(documentation)
        
        print("Database documentation saved to ./sql/database_documentation.md")
    
    def setup_complete_database(self, datasets):
        """Set up complete database with all components."""
        print("Setting up complete vaccination database...")
        
        self.create_database_schema()
        self.populate_dimension_tables(datasets)
        self.populate_fact_tables(datasets)
        self.create_analytical_views()
        self.create_sample_queries()
        self.generate_database_documentation()
        
        print(f"Database setup completed! Database file: {self.db_path}")
        
        # Verify database
        with self.engine.connect() as conn:
            tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in tables_result]
            
            views_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='view'"))
            views = [row[0] for row in views_result]
            
            print(f"Created {len(tables)} tables: {', '.join(tables)}")
            print(f"Created {len(views)} views: {', '.join(views)}")
        
        return True

if __name__ == "__main__":
    # Load cleaned datasets
    cleaned_datasets = {}
    data_files = {
        'coverage': './cleaned_data/coverage_cleaned.csv',
        'incidence': './cleaned_data/incidence_cleaned.csv',
        'reported_cases': './cleaned_data/reported_cases_cleaned.csv',
        'vaccine_introduction': './cleaned_data/vaccine_introduction_cleaned.csv',
        'vaccine_schedule': './cleaned_data/vaccine_schedule_cleaned.csv'
    }
    
    for name, file_path in data_files.items():
        if os.path.exists(file_path):
            cleaned_datasets[name] = pd.read_csv(file_path)
            print(f"Loaded {name} dataset: {cleaned_datasets[name].shape}")
    
    # Set up database
    db_manager = VaccinationDatabaseManager("vaccination_database.db")
    success = db_manager.setup_complete_database(cleaned_datasets)
