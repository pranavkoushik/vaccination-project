"""
Main Execution Script for Vaccination Data Analysis Project
Run this script to execute the complete data analysis pipeline.
"""

import os
import sys
import time
from datetime import datetime

def print_banner():
    """Print project banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        VACCINATION DATA ANALYSIS AND VISUALIZATION           ║
    ║                      PROJECT PIPELINE                       ║
    ║                                                              ║
    ║  Skills: Python, SQL, Data Cleaning, EDA, Power BI          ║
    ║  Domain: Public Health and Epidemiology                     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

def run_step(step_name, script_path, description):
    """Run a single step of the pipeline."""
    print(f"\n{'='*20} {step_name} {'='*20}")
    print(f"Description: {description}")
    print(f"Executing: {script_path}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # Import and run the module
        if script_path == "data_loader":
            from src.data_loader import VaccinationDataLoader
            loader = VaccinationDataLoader(".")
            datasets = loader.load_all_datasets()
            info = loader.get_basic_info()
            print(f"Loaded {len(datasets)} datasets successfully")
            return datasets
            
        elif script_path == "data_cleaner":
            from src.data_cleaner import VaccinationDataCleaner
            from src.data_loader import VaccinationDataLoader
            
            # Load raw data
            loader = VaccinationDataLoader(".")
            raw_datasets = loader.load_all_datasets()
            
            # Clean data
            cleaner = VaccinationDataCleaner()
            cleaned_datasets = cleaner.clean_all_datasets(raw_datasets)
            
            # Save cleaned data
            cleaner.save_cleaned_data()
            
            # Generate quality report
            quality_report = cleaner.get_data_quality_report()
            print("Data cleaning completed successfully")
            return cleaned_datasets
            
        elif script_path == "database_setup":
            from src.database_setup import VaccinationDatabaseManager
            import pandas as pd
            
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
            
            # Set up database
            db_manager = VaccinationDatabaseManager("vaccination_database.db")
            success = db_manager.setup_complete_database(cleaned_datasets)
            print("Database setup completed successfully")
            return success
            
        elif script_path == "analysis":
            from src.simple_analysis import SimpleVaccinationAnalyst
            
            analyst = SimpleVaccinationAnalyst()
            results, report = analyst.run_analysis()
            print("Analysis completed successfully")
            return results
            
        elif script_path == "powerbi_connector":
            from src.powerbi_connector import PowerBIConnector
            
            connector = PowerBIConnector()
            connector.export_powerbi_datasets()
            
            guide = connector.generate_powerbi_guide()
            with open("./powerbi_data/PowerBI_Setup_Guide.md", "w") as f:
                f.write(guide)
            
            print("Power BI materials generated successfully")
            return True
            
    except Exception as e:
        print(f"ERROR in {step_name}: {str(e)}")
        return None
    
    finally:
        elapsed_time = time.time() - start_time
        print(f"\nStep completed in {elapsed_time:.2f} seconds")

def main():
    """Execute the complete vaccination data analysis pipeline."""
    print_banner()
    
    # Pipeline steps
    steps = [
        {
            'name': 'STEP 1: DATA LOADING',
            'script': 'data_loader',
            'description': 'Load vaccination datasets from Excel files'
        },
        {
            'name': 'STEP 2: DATA CLEANING',
            'script': 'data_cleaner',
            'description': 'Clean and preprocess vaccination data'
        },
        {
            'name': 'STEP 3: DATABASE SETUP',
            'script': 'database_setup',
            'description': 'Create normalized SQL database with vaccination data'
        },
        {
            'name': 'STEP 4: DATA ANALYSIS',
            'script': 'analysis',
            'description': 'Perform comprehensive vaccination data analysis'
        },
        {
            'name': 'STEP 5: POWER BI INTEGRATION',
            'script': 'powerbi_connector',
            'description': 'Generate Power BI datasets and connection guides'
        }
    ]
    
    # Execute pipeline
    results = {}
    total_start_time = time.time()
    
    for step in steps:
        result = run_step(step['name'], step['script'], step['description'])
        results[step['script']] = result
        
        if result is None:
            print(f"\nPipeline stopped due to error in {step['name']}")
            return False
    
    # Pipeline completion summary
    total_time = time.time() - total_start_time
    
    print("\n" + "="*70)
    print("🎉 VACCINATION DATA ANALYSIS PIPELINE COMPLETED SUCCESSFULLY! 🎉")
    print("="*70)
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary of generated files
    print("\n📂 GENERATED FILES AND OUTPUTS:")
    print("-" * 40)
    
    generated_files = [
        "📊 Cleaned Datasets:",
        "  • ./cleaned_data/coverage_cleaned.csv",
        "  • ./cleaned_data/incidence_cleaned.csv", 
        "  • ./cleaned_data/reported_cases_cleaned.csv",
        "  • ./cleaned_data/vaccine_introduction_cleaned.csv",
        "  • ./cleaned_data/vaccine_schedule_cleaned.csv",
        "",
        "🗄️ SQL Database:",
        "  • ./vaccination_database.db (SQLite database)",
        "  • ./sql/sample_queries.sql",
        "  • ./sql/database_documentation.md",
        "",
        "📈 Analysis Reports:",
        "  • ./reports/vaccination_analysis_report.txt",
        "  • ./reports/insights_report.txt",
        "  • ./reports/regional_coverage_simple.png",
        "  • ./reports/antigen_coverage_simple.png",
        "",
        "💼 Power BI Materials:",
        "  • ./powerbi_data/coverage_summary.csv",
        "  • ./powerbi_data/disease_burden_summary.csv",
        "  • ./powerbi_data/vaccination_effectiveness.csv",
        "  • ./powerbi_data/kpi_metrics.csv",
        "  • ./powerbi_data/regional_trends.csv",
        "  • ./powerbi_data/PowerBI_Setup_Guide.md",
        "",
        "📚 Documentation:",
        "  • ./README.md (Project overview and findings)"
    ]
    
    for item in generated_files:
        print(item)
    
    print("\n🎯 NEXT STEPS:")
    print("-" * 20)
    print("1. Review the analysis report in ./reports/vaccination_analysis_report.txt")
    print("2. Open Power BI and import datasets from ./powerbi_data/")
    print("3. Follow the Power BI setup guide for dashboard creation")
    print("4. Use SQL queries in ./sql/sample_queries.sql for additional analysis")
    print("5. Explore the comprehensive README.md for detailed project insights")
    
    print("\n🏆 PROJECT DELIVERABLES COMPLETED:")
    print("-" * 35)
    deliverables = [
        "✅ Data extraction and cleaning scripts",
        "✅ Normalized SQL database with vaccination data",
        "✅ Comprehensive exploratory data analysis",
        "✅ Statistical insights and visualizations", 
        "✅ Power BI integration materials",
        "✅ Business question analysis and answers",
        "✅ Resource allocation recommendations",
        "✅ Performance metrics and KPIs",
        "✅ Technical and business documentation"
    ]
    
    for deliverable in deliverables:
        print(deliverable)
    
    print("\n" + "="*70)
    print("Thank you for using the Vaccination Data Analysis Pipeline!")
    print("For questions or support, refer to the documentation files.")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
