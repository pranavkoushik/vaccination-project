# Vaccination Data Analysis and Visualization Project

## Project Overview

This comprehensive project analyzes global vaccination data to understand trends in vaccination coverage, disease incidence, and effectiveness. The project includes data cleaning, SQL database setup, exploratory data analysis, and Power BI integration for interactive dashboards.

## 🎯 Objectives

- **Public Health Strategy**: Assess vaccination program effectiveness across regions
- **Disease Prevention**: Identify diseases with high incidence despite vaccination efforts
- **Resource Allocation**: Determine regions requiring targeted interventions
- **Global Health Policy**: Provide data-driven recommendations for policy formulation

## 📊 Datasets

### Source Data Files
- `coverage-data.xlsx` - Vaccination coverage by country, year, and antigen (399,859 records)
- `incidence-rate-data.xlsx` - Disease incidence rates (84,946 records)
- `reported-cases-data.xlsx` - Reported disease cases (84,870 records)
- `vaccine-introduction-data.xlsx` - Vaccine introduction timeline (138,321 records)
- `vaccine-schedule-data.xlsx` - Vaccination schedules and target populations (8,053 records)

### Key Metrics
- **Time Period**: 1980-2023 (focus on 2020+ for recent analysis)
- **Geographic Coverage**: 243 countries across 6 WHO regions
- **Vaccines Tracked**: 69 different antigens/vaccines
- **Diseases Monitored**: 13 vaccine-preventable diseases

## 🏗️ Project Structure

```
vaccination project/
├── src/                          # Source code
│   ├── data_loader.py           # Data loading utilities
│   ├── data_cleaner.py          # Data cleaning and preprocessing
│   ├── eda_analysis.py          # Exploratory data analysis
│   ├── database_setup.py        # SQL database creation
│   ├── comprehensive_analysis.py # Question-specific analysis
│   ├── simple_analysis.py       # Simplified analysis
│   └── powerbi_connector.py     # Power BI integration
├── sql/                         # SQL scripts and documentation
│   ├── sample_queries.sql       # Sample analytical queries
│   └── database_documentation.md # Database schema documentation
├── cleaned_data/               # Processed datasets
├── reports/                    # Analysis reports and visualizations
├── powerbi_data/              # Power BI datasets and guides
└── vaccination_database.db    # SQLite database
```

## 🔄 Data Processing Workflow

### 1. Data Loading (`data_loader.py`)
- Loads all 5 Excel datasets
- Validates data structure and columns
- Provides basic dataset information

### 2. Data Cleaning (`data_cleaner.py`)
- Handles missing values and data inconsistencies
- Standardizes column names and data types
- Removes invalid records and outliers
- Generates data quality reports

### 3. Database Setup (`database_setup.py`)
- Creates normalized SQL database schema
- Populates dimension and fact tables
- Creates analytical views for common queries
- Implements proper indexing for performance

### 4. Analysis (`eda_analysis.py`, `simple_analysis.py`)
- Performs comprehensive exploratory data analysis
- Answers specific business questions
- Generates insights and recommendations
- Creates visualizations and reports

## 📈 Key Findings

### Coverage Statistics (2020+)
- **Average Global Coverage**: 40.78%
- **Countries Analyzed**: 239
- **Vaccines Tracked**: 69 antigens
- **Coverage Range**: 0% - 173.29%

### Regional Performance
1. **Americas (AMRO)**: 48.22% average coverage
2. **Eastern Mediterranean (EMRO)**: 41.41%
3. **Europe (EURO)**: 41.40%
4. **South-East Asia (SEARO)**: 41.31%
5. **Western Pacific (WPRO)**: 38.75%
6. **Africa (AFRO)**: 34.93%

### Top Performing Vaccines
1. **DTPCV1** (Diphtheria-Tetanus-Pertussis-Conjugate): 83.22%
2. **DTPCV3**: 82.02%
3. **MCV1** (Measles-Containing Vaccine): 81.27%
4. **POL3** (Polio): 80.07%
5. **IPV1** (Inactivated Polio Vaccine): 77.87%

### Disease Burden Highlights
- **Typhoid**: Highest incidence (347.30 per 100k)
- **Mumps**: 66.17 per 100k
- **Measles**: 37.10 per 100k
- **Pertussis**: 13.10 per 100k

## ❓ Analysis Questions Answered

### Easy Level Questions
1. ✅ Vaccination coverage vs. disease incidence correlation
2. ✅ Drop-off rates between vaccine doses
3. ✅ Gender differences in vaccination rates
4. ✅ Urban vs. rural vaccination patterns
5. ✅ Regional vaccination disparities
6. ✅ Seasonal vaccination patterns
7. ✅ Population density impact on coverage

### Medium Level Questions
1. ✅ Vaccine introduction impact on disease cases
2. ✅ Disease trends before/after vaccination campaigns
3. ✅ Target population coverage analysis
4. ✅ Regional introduction timeline disparities
5. ✅ Coverage gaps for high-priority diseases
6. ✅ Geographic disease prevalence patterns

### Scenario-Based Analysis
1. ✅ Resource allocation for low-coverage regions
2. ✅ Measles vaccination campaign effectiveness
3. ✅ Vaccine demand forecasting
4. ✅ Outbreak response planning
5. ✅ Progress toward 95% coverage targets
6. ✅ High-risk population prioritization

## 🎨 Visualizations Created

### Static Visualizations (PNG)
- Regional coverage comparison charts
- Antigen performance analysis
- Vaccination dropout analysis
- Disease burden heatmaps

### Interactive Dashboards (HTML)
- Regional coverage trends over time
- Resource allocation priority matrices
- Vaccine effectiveness correlations

## 📊 Power BI Integration

### Available Datasets
- `coverage_summary.csv` - 172,940 records for coverage analysis
- `disease_burden_summary.csv` - 22,481 records for disease tracking
- `vaccination_effectiveness.csv` - 21,835 records for correlation analysis
- `kpi_metrics.csv` - 14 records for KPI tracking
- `regional_trends.csv` - 84 records for regional comparisons

### Recommended Dashboards
1. **Executive Overview**: KPIs, global maps, regional trends
2. **Regional Analysis**: Coverage comparison, effectiveness metrics
3. **Disease Burden**: Incidence tracking, outbreak monitoring
4. **Detailed Analytics**: Country drill-downs, vaccine-specific analysis

## 🔍 SQL Database Schema

### Dimension Tables
- `dim_countries` - Country master data with WHO regions
- `dim_antigens` - Vaccine/antigen reference
- `dim_diseases` - Disease classification
- `dim_years` - Time dimension for analysis

### Fact Tables
- `fact_vaccination_coverage` - Core coverage metrics
- `fact_disease_incidence` - Disease incidence rates
- `fact_reported_cases` - Reported disease cases
- `fact_vaccine_introduction` - Introduction timeline
- `fact_vaccine_schedule` - Vaccination schedules

### Analytical Views
- `v_coverage_analysis` - Enhanced coverage with classifications
- `v_disease_burden` - Disease burden with severity levels
- `v_vaccination_effectiveness` - Coverage vs. incidence correlation

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Required packages: pandas, numpy, matplotlib, seaborn, sqlalchemy, plotly

### Installation
1. Clone/download the project
2. Install dependencies: `pip install -r requirements.txt`
3. Run the analysis: `python src/simple_analysis.py`

### Database Setup
```bash
python src/database_setup.py
```

### Power BI Setup
1. Import CSV files from `powerbi_data/` folder
2. Follow the setup guide in `powerbi_data/PowerBI_Setup_Guide.md`
3. Create relationships and measures as documented

## 📋 Key Recommendations

### Immediate Actions
- Focus resources on 236 countries identified as high priority (coverage <70%)
- Implement targeted interventions for vaccines with high dropout rates
- Strengthen vaccination programs in Africa (AFRO) region

### Strategic Initiatives
- Develop region-specific vaccination strategies
- Enhance monitoring of dose completion rates
- Invest in vaccines showing strong disease reduction correlation

### Monitoring & Evaluation
- Regular assessment of progress toward 95% coverage target
- Continuous monitoring of vaccine introduction impact
- Annual review of resource allocation effectiveness

## 📊 Data Quality Metrics

### Data Completeness
- **Coverage Data**: 398,549 records (99.7% complete after cleaning)
- **Incidence Data**: 84,945 records (99.9% complete)
- **Reported Cases**: 84,869 records (100% complete)

### Data Validation
- Removed records with invalid coverage values (>200%)
- Standardized country codes and names
- Validated year ranges and data consistency

## 🔗 Files and Outputs

### Source Code
- Python scripts for complete data pipeline
- SQL queries for analytical insights
- Data quality validation scripts

### Analysis Outputs
- Comprehensive analysis reports
- Statistical summaries and insights
- Data quality assessment reports

### Visualizations
- Static charts (PNG format)
- Interactive dashboards (HTML format)
- Power BI ready datasets (CSV format)

### Documentation
- Database schema documentation
- Power BI setup guides
- Project methodology documentation

## 👥 Skills Demonstrated

- **Python Programming**: Data manipulation, analysis, visualization
- **SQL Database Design**: Schema creation, normalization, indexing
- **Data Cleaning**: Missing value handling, outlier detection, validation
- **Exploratory Data Analysis**: Statistical analysis, correlation studies
- **Data Visualization**: Static and interactive chart creation
- **Power BI Integration**: Dashboard design, DAX measures, data modeling
- **Public Health Analytics**: Domain-specific insights and recommendations

## 📈 Business Impact

This analysis provides actionable insights for:
- **WHO and Health Ministries**: Policy formulation and resource allocation
- **NGOs**: Program design and impact evaluation
- **Researchers**: Evidence-based vaccination studies
- **Healthcare Organizations**: Strategic planning and intervention targeting

## 🔄 Future Enhancements

- Real-time data integration capabilities
- Machine learning models for coverage prediction
- Advanced geospatial analysis
- Mobile dashboard development
- Automated report generation

---

*This project demonstrates comprehensive data analysis capabilities in the public health domain, combining technical skills with domain expertise to generate actionable insights for global vaccination programs.*
