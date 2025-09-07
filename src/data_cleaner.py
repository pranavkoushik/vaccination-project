"""
Data Cleaning Module for Vaccination Data Analysis Project
This module handles data cleaning, preprocessing, and quality assurance.
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class VaccinationDataCleaner:
    """Class to handle data cleaning and preprocessing for vaccination datasets."""
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.cleaned_datasets = {}
        
    def clean_coverage_data(self, df):
        """
        Clean vaccination coverage data.
        
        Args:
            df (pd.DataFrame): Raw coverage data
            
        Returns:
            pd.DataFrame: Cleaned coverage data
        """
        print("Cleaning coverage data...")
        df_clean = df.copy()
        
        # Standardize column names
        df_clean.columns = df_clean.columns.str.upper()
        
        # Handle missing values
        # Remove rows where essential fields are missing
        essential_cols = ['CODE', 'NAME', 'YEAR', 'ANTIGEN']
        df_clean = df_clean.dropna(subset=essential_cols)
        
        # Fill missing coverage with 0 (assuming no coverage data means 0%)
        df_clean['COVERAGE'] = pd.to_numeric(df_clean['COVERAGE'], errors='coerce')
        df_clean['COVERAGE'] = df_clean['COVERAGE'].fillna(0)
        
        # Fill missing target numbers and doses with 0
        df_clean['TARGET_NUMBER'] = pd.to_numeric(df_clean['TARGET_NUMBER'], errors='coerce')
        df_clean['DOSES'] = pd.to_numeric(df_clean['DOSES'], errors='coerce')
        df_clean['TARGET_NUMBER'] = df_clean['TARGET_NUMBER'].fillna(0)
        df_clean['DOSES'] = df_clean['DOSES'].fillna(0)
        
        # Ensure year is integer
        df_clean['YEAR'] = pd.to_numeric(df_clean['YEAR'], errors='coerce')
        df_clean = df_clean.dropna(subset=['YEAR'])
        df_clean['YEAR'] = df_clean['YEAR'].astype(int)
        
        # Remove invalid coverage values (should be between 0 and 100)
        df_clean = df_clean[(df_clean['COVERAGE'] >= 0) & (df_clean['COVERAGE'] <= 200)]  # Allow up to 200% for some reporting variations
        
        print(f"Coverage data cleaned: {df_clean.shape}")
        return df_clean
    
    def clean_incidence_data(self, df):
        """
        Clean disease incidence data.
        
        Args:
            df (pd.DataFrame): Raw incidence data
            
        Returns:
            pd.DataFrame: Cleaned incidence data
        """
        print("Cleaning incidence data...")
        df_clean = df.copy()
        
        # Standardize column names
        df_clean.columns = df_clean.columns.str.upper()
        
        # Handle missing values
        essential_cols = ['CODE', 'NAME', 'YEAR', 'DISEASE']
        df_clean = df_clean.dropna(subset=essential_cols)
        
        # Clean incidence rate
        df_clean['INCIDENCE_RATE'] = pd.to_numeric(df_clean['INCIDENCE_RATE'], errors='coerce')
        df_clean['INCIDENCE_RATE'] = df_clean['INCIDENCE_RATE'].fillna(0)
        
        # Ensure year is integer
        df_clean['YEAR'] = pd.to_numeric(df_clean['YEAR'], errors='coerce')
        df_clean = df_clean.dropna(subset=['YEAR'])
        df_clean['YEAR'] = df_clean['YEAR'].astype(int)
        
        # Remove negative incidence rates
        df_clean = df_clean[df_clean['INCIDENCE_RATE'] >= 0]
        
        print(f"Incidence data cleaned: {df_clean.shape}")
        return df_clean
    
    def clean_reported_cases_data(self, df):
        """
        Clean reported cases data.
        
        Args:
            df (pd.DataFrame): Raw reported cases data
            
        Returns:
            pd.DataFrame: Cleaned reported cases data
        """
        print("Cleaning reported cases data...")
        df_clean = df.copy()
        
        # Standardize column names
        df_clean.columns = df_clean.columns.str.upper()
        
        # Handle missing values
        essential_cols = ['CODE', 'NAME', 'YEAR', 'DISEASE']
        df_clean = df_clean.dropna(subset=essential_cols)
        
        # Clean cases count
        df_clean['CASES'] = pd.to_numeric(df_clean['CASES'], errors='coerce')
        df_clean['CASES'] = df_clean['CASES'].fillna(0)
        
        # Ensure year is integer
        df_clean['YEAR'] = pd.to_numeric(df_clean['YEAR'], errors='coerce')
        df_clean = df_clean.dropna(subset=['YEAR'])
        df_clean['YEAR'] = df_clean['YEAR'].astype(int)
        
        # Remove negative case counts
        df_clean = df_clean[df_clean['CASES'] >= 0]
        
        print(f"Reported cases data cleaned: {df_clean.shape}")
        return df_clean
    
    def clean_vaccine_introduction_data(self, df):
        """
        Clean vaccine introduction data.
        
        Args:
            df (pd.DataFrame): Raw vaccine introduction data
            
        Returns:
            pd.DataFrame: Cleaned vaccine introduction data
        """
        print("Cleaning vaccine introduction data...")
        df_clean = df.copy()
        
        # Standardize column names
        df_clean.columns = df_clean.columns.str.upper()
        
        # Handle missing values
        essential_cols = ['ISO_3_CODE', 'COUNTRYNAME', 'YEAR']
        df_clean = df_clean.dropna(subset=essential_cols)
        
        # Ensure year is integer
        df_clean['YEAR'] = pd.to_numeric(df_clean['YEAR'], errors='coerce')
        df_clean = df_clean.dropna(subset=['YEAR'])
        df_clean['YEAR'] = df_clean['YEAR'].astype(int)
        
        # Clean introduction status
        df_clean['INTRO'] = df_clean['INTRO'].fillna('Unknown')
        
        print(f"Vaccine introduction data cleaned: {df_clean.shape}")
        return df_clean
    
    def clean_vaccine_schedule_data(self, df):
        """
        Clean vaccine schedule data.
        
        Args:
            df (pd.DataFrame): Raw vaccine schedule data
            
        Returns:
            pd.DataFrame: Cleaned vaccine schedule data
        """
        print("Cleaning vaccine schedule data...")
        df_clean = df.copy()
        
        # Standardize column names
        df_clean.columns = df_clean.columns.str.upper()
        
        # Handle missing values
        essential_cols = ['ISO_3_CODE', 'COUNTRYNAME', 'YEAR']
        df_clean = df_clean.dropna(subset=essential_cols)
        
        # Ensure year is integer
        df_clean['YEAR'] = pd.to_numeric(df_clean['YEAR'], errors='coerce')
        df_clean = df_clean.dropna(subset=['YEAR'])
        df_clean['YEAR'] = df_clean['YEAR'].astype(int)
        
        print(f"Vaccine schedule data cleaned: {df_clean.shape}")
        return df_clean
    
    def clean_all_datasets(self, datasets):
        """
        Clean all vaccination datasets.
        
        Args:
            datasets (dict): Dictionary of raw datasets
            
        Returns:
            dict: Dictionary of cleaned datasets
        """
        print("Starting data cleaning process...")
        
        if 'coverage' in datasets:
            self.cleaned_datasets['coverage'] = self.clean_coverage_data(datasets['coverage'])
        
        if 'incidence' in datasets:
            self.cleaned_datasets['incidence'] = self.clean_incidence_data(datasets['incidence'])
        
        if 'reported_cases' in datasets:
            self.cleaned_datasets['reported_cases'] = self.clean_reported_cases_data(datasets['reported_cases'])
        
        if 'vaccine_introduction' in datasets:
            self.cleaned_datasets['vaccine_introduction'] = self.clean_vaccine_introduction_data(datasets['vaccine_introduction'])
        
        if 'vaccine_schedule' in datasets:
            self.cleaned_datasets['vaccine_schedule'] = self.clean_vaccine_schedule_data(datasets['vaccine_schedule'])
        
        print("Data cleaning completed!")
        return self.cleaned_datasets
    
    def save_cleaned_data(self, output_path="./cleaned_data"):
        """
        Save cleaned datasets to CSV files.
        
        Args:
            output_path (str): Path to save cleaned data files
        """
        import os
        os.makedirs(output_path, exist_ok=True)
        
        for name, df in self.cleaned_datasets.items():
            file_path = f"{output_path}/{name}_cleaned.csv"
            df.to_csv(file_path, index=False)
            print(f"Saved {name} data to {file_path}")
    
    def get_data_quality_report(self):
        """Generate a data quality report for cleaned datasets."""
        report = {}
        
        for name, df in self.cleaned_datasets.items():
            report[name] = {
                'total_records': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().sum(),
                'duplicate_records': df.duplicated().sum(),
                'data_types': df.dtypes.to_dict(),
                'year_range': (df['YEAR'].min(), df['YEAR'].max()) if 'YEAR' in df.columns else None,
                'unique_countries': df['CODE'].nunique() if 'CODE' in df.columns else 
                                 df['ISO_3_CODE'].nunique() if 'ISO_3_CODE' in df.columns else None
            }
        
        return report

if __name__ == "__main__":
    # Test the data cleaner
    from data_loader import VaccinationDataLoader
    
    loader = VaccinationDataLoader(".")
    raw_datasets = loader.load_all_datasets()
    
    cleaner = VaccinationDataCleaner()
    cleaned_datasets = cleaner.clean_all_datasets(raw_datasets)
    
    # Generate data quality report
    quality_report = cleaner.get_data_quality_report()
    
    print("\n" + "="*50)
    print("DATA QUALITY REPORT")
    print("="*50)
    
    for dataset_name, report in quality_report.items():
        print(f"\n{dataset_name.upper()} Dataset:")
        print(f"  Records: {report['total_records']:,}")
        print(f"  Columns: {report['total_columns']}")
        print(f"  Missing values: {report['missing_values']:,}")
        print(f"  Duplicate records: {report['duplicate_records']:,}")
        if report['year_range']:
            print(f"  Year range: {report['year_range'][0]} - {report['year_range'][1]}")
        if report['unique_countries']:
            print(f"  Unique countries: {report['unique_countries']}")
    
    # Save cleaned data
    cleaner.save_cleaned_data()
