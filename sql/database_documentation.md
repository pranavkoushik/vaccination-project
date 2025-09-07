
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
