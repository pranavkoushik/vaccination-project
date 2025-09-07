
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
