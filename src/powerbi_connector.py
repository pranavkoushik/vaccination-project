"""
Power BI Connection Guide for Vaccination Data Analysis Project

This script provides guidance and sample code for connecting Power BI to the vaccination database.
"""

import sqlite3
import pandas as pd

class PowerBIConnector:
    """Helper class for Power BI database connections."""
    
    def __init__(self, db_path="vaccination_database.db"):
        self.db_path = db_path
        
    def get_connection_info(self):
        """Get database connection information for Power BI."""
        info = {
            'database_type': 'SQLite',
            'database_path': self.db_path,
            'connection_string': f'Data Source={self.db_path}',
            'tables': [
                'dim_countries',
                'dim_antigens', 
                'dim_diseases',
                'dim_years',
                'fact_vaccination_coverage',
                'fact_disease_incidence',
                'fact_reported_cases',
                'fact_vaccine_introduction',
                'fact_vaccine_schedule'
            ],
            'views': [
                'v_coverage_analysis',
                'v_disease_burden',
                'v_vaccination_effectiveness'
            ]
        }
        return info
    
    def create_powerbi_queries(self):
        """Create sample queries for Power BI reports."""
        queries = {
            'coverage_summary': """
                SELECT 
                    country_name,
                    who_region,
                    year,
                    antigen_code,
                    coverage,
                    coverage_level
                FROM v_coverage_analysis
                WHERE year >= 2015
            """,
            
            'disease_burden_summary': """
                SELECT 
                    country_name,
                    who_region,
                    year,
                    disease_code,
                    incidence_rate,
                    cases,
                    incidence_level
                FROM v_disease_burden
                WHERE year >= 2015
            """,
            
            'vaccination_effectiveness': """
                SELECT 
                    country_name,
                    who_region,
                    year,
                    antigen_code,
                    coverage,
                    disease_code,
                    incidence_rate
                FROM v_vaccination_effectiveness
                WHERE year >= 2015
            """,
            
            'kpi_metrics': """
                SELECT 
                    year,
                    COUNT(DISTINCT country_code) as countries_reporting,
                    AVG(coverage) as avg_coverage,
                    COUNT(CASE WHEN coverage >= 95 THEN 1 END) as countries_above_95,
                    COUNT(CASE WHEN coverage >= 80 THEN 1 END) as countries_above_80
                FROM v_coverage_analysis
                WHERE year >= 2010
                GROUP BY year
            """,
            
            'regional_trends': """
                SELECT 
                    who_region,
                    year,
                    AVG(coverage) as avg_coverage,
                    COUNT(DISTINCT country_code) as num_countries
                FROM v_coverage_analysis
                WHERE year >= 2010 AND who_region IS NOT NULL
                GROUP BY who_region, year
            """
        }
        return queries
    
    def export_powerbi_datasets(self, output_path="./powerbi_data"):
        """Export datasets for Power BI import."""
        import os
        os.makedirs(output_path, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        queries = self.create_powerbi_queries()
        
        for name, query in queries.items():
            try:
                df = pd.read_sql_query(query, conn)
                file_path = f"{output_path}/{name}.csv"
                df.to_csv(file_path, index=False)
                print(f"Exported {name}: {len(df)} records to {file_path}")
            except Exception as e:
                print(f"Error exporting {name}: {e}")
        
        conn.close()
        print(f"\nAll datasets exported to {output_path}")
    
    def generate_powerbi_guide(self):
        """Generate Power BI connection and setup guide."""
        guide = """
# POWER BI SETUP GUIDE FOR VACCINATION DATA ANALYSIS

## Database Connection

### Option 1: Direct SQLite Connection
1. Open Power BI Desktop
2. Click "Get Data" > "Database" > "SQLite database"
3. Browse to: vaccination_database.db
4. Select tables and views to import

### Option 2: CSV Import (Recommended for easier deployment)
1. Use the exported CSV files from the powerbi_data folder
2. In Power BI: "Get Data" > "Text/CSV"
3. Import the following files:
   - coverage_summary.csv
   - disease_burden_summary.csv
   - vaccination_effectiveness.csv
   - kpi_metrics.csv
   - regional_trends.csv

## Data Model Setup

### Relationships
Create the following relationships in Power BI:
- Country relationships: Use country_name or country_code as the key
- Time relationships: Use year as the key
- Antigen/Disease relationships: Use the respective code fields

### Calculated Measures

#### Coverage Metrics
```DAX
Average Coverage = AVERAGE(coverage_summary[coverage])
Coverage Above 95% = CALCULATE(COUNT(coverage_summary[country_name]), coverage_summary[coverage] >= 95)
Coverage Below 80% = CALCULATE(COUNT(coverage_summary[country_name]), coverage_summary[coverage] < 80)
```

#### Trend Analysis
```DAX
Coverage Trend = 
VAR CurrentYear = MAX(coverage_summary[year])
VAR PreviousYear = CurrentYear - 1
VAR CurrentCoverage = CALCULATE(AVERAGE(coverage_summary[coverage]), coverage_summary[year] = CurrentYear)
VAR PreviousCoverage = CALCULATE(AVERAGE(coverage_summary[coverage]), coverage_summary[year] = PreviousYear)
RETURN CurrentCoverage - PreviousCoverage
```

#### KPI Measures
```DAX
Countries Reporting = DISTINCTCOUNT(coverage_summary[country_name])
Target Achievement Rate = DIVIDE([Coverage Above 95%], [Countries Reporting])
```

## Recommended Visualizations

### Dashboard 1: Executive Overview
- KPI cards: Total countries, average coverage, target achievement
- Line chart: Coverage trends over time by region
- Map visualization: Coverage by country (color-coded)
- Bar chart: Top/bottom 10 countries by coverage

### Dashboard 2: Regional Analysis
- Regional comparison bar chart
- Coverage vs. incidence scatter plot
- Regional trend lines over time
- Heat map of coverage by region and antigen

### Dashboard 3: Disease Burden Analysis
- Disease incidence trends
- Coverage effectiveness analysis
- Correlation analysis between vaccination and disease reduction
- Case reduction after vaccine introduction

### Dashboard 4: Detailed Analytics
- Drill-down by country, antigen, and year
- Vaccination schedule analysis
- Target population coverage
- Vaccine introduction timeline

## Filters and Slicers
Add the following slicers for interactivity:
- Year range slider
- WHO Region multi-select
- Country multi-select
- Antigen multi-select
- Coverage level (High/Medium/Low)

## Refresh Schedule
Set up automatic data refresh if using direct database connection:
- Frequency: Daily or weekly based on data update frequency
- Time: During off-peak hours
- Alerts: Configure failure notifications

## Performance Optimization
- Use aggregated views (v_coverage_analysis, etc.) instead of fact tables
- Limit date ranges to relevant periods (e.g., 2010+)
- Use DirectQuery for large datasets
- Implement row-level security if needed

## Sample Report Layouts

### Page 1: Global Overview
- Title: "Global Vaccination Coverage Dashboard"
- KPI cards across the top
- World map in center
- Regional trends on the right

### Page 2: Country Deep Dive
- Country selector at top
- Coverage trends over time
- Antigen-specific coverage
- Disease burden comparison

### Page 3: Regional Comparison
- Regional performance matrix
- Coverage gaps analysis
- Resource allocation priorities
- Progress toward targets

## Export and Sharing
- Publish to Power BI Service
- Share with stakeholders
- Set up email subscriptions for regular reports
- Enable mobile app access

## Troubleshooting
- Ensure proper data types for date fields
- Check for null values in key fields
- Validate relationships between tables
- Test calculations with sample data
"""
        
        return guide

def main():
    """Generate Power BI connection materials."""
    print("Generating Power BI connection materials...")
    
    connector = PowerBIConnector()
    
    # Export datasets for Power BI
    connector.export_powerbi_datasets()
    
    # Generate connection guide
    guide = connector.generate_powerbi_guide()
    with open("./powerbi_data/PowerBI_Setup_Guide.md", "w") as f:
        f.write(guide)
    
    # Save connection info
    info = connector.get_connection_info()
    with open("./powerbi_data/connection_info.txt", "w") as f:
        f.write("VACCINATION DATABASE CONNECTION INFO\n")
        f.write("=" * 40 + "\n\n")
        for key, value in info.items():
            f.write(f"{key}: {value}\n")
    
    print("\nPower BI materials generated:")
    print("• ./powerbi_data/ - Exported CSV datasets")
    print("• ./powerbi_data/PowerBI_Setup_Guide.md - Setup instructions")
    print("• ./powerbi_data/connection_info.txt - Connection details")

if __name__ == "__main__":
    main()
