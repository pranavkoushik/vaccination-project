"""
Data Loader Module for Vaccination Data Analysis Project
This module handles loading and initial processing of vaccination-related datasets.
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class VaccinationDataLoader:
    """Class to handle loading and initial processing of vaccination datasets."""
    
    def __init__(self, data_path):
        """
        Initialize the data loader with the path to data files.
        
        Args:
            data_path (str): Path to the directory containing Excel files
        """
        self.data_path = data_path
        self.datasets = {}
        
    def load_coverage_data(self):
        """Load vaccination coverage data from Excel file."""
        try:
            file_path = f"{self.data_path}/coverage-data.xlsx"
            df = pd.read_excel(file_path)
            print(f"Coverage data loaded: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            self.datasets['coverage'] = df
            return df
        except Exception as e:
            print(f"Error loading coverage data: {e}")
            return None
    
    def load_incidence_data(self):
        """Load disease incidence rate data from Excel file."""
        try:
            file_path = f"{self.data_path}/incidence-rate-data.xlsx"
            df = pd.read_excel(file_path)
            print(f"Incidence data loaded: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            self.datasets['incidence'] = df
            return df
        except Exception as e:
            print(f"Error loading incidence data: {e}")
            return None
    
    def load_reported_cases_data(self):
        """Load reported disease cases data from Excel file."""
        try:
            file_path = f"{self.data_path}/reported-cases-data.xlsx"
            df = pd.read_excel(file_path)
            print(f"Reported cases data loaded: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            self.datasets['reported_cases'] = df
            return df
        except Exception as e:
            print(f"Error loading reported cases data: {e}")
            return None
    
    def load_vaccine_introduction_data(self):
        """Load vaccine introduction data from Excel file."""
        try:
            file_path = f"{self.data_path}/vaccine-introduction-data.xlsx"
            df = pd.read_excel(file_path)
            print(f"Vaccine introduction data loaded: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            self.datasets['vaccine_introduction'] = df
            return df
        except Exception as e:
            print(f"Error loading vaccine introduction data: {e}")
            return None
    
    def load_vaccine_schedule_data(self):
        """Load vaccine schedule data from Excel file."""
        try:
            file_path = f"{self.data_path}/vaccine-schedule-data.xlsx"
            df = pd.read_excel(file_path)
            print(f"Vaccine schedule data loaded: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            self.datasets['vaccine_schedule'] = df
            return df
        except Exception as e:
            print(f"Error loading vaccine schedule data: {e}")
            return None
    
    def load_all_datasets(self):
        """Load all vaccination datasets."""
        print("Loading all vaccination datasets...")
        self.load_coverage_data()
        self.load_incidence_data()
        self.load_reported_cases_data()
        self.load_vaccine_introduction_data()
        self.load_vaccine_schedule_data()
        
        print(f"\nDatasets loaded: {list(self.datasets.keys())}")
        return self.datasets
    
    def get_basic_info(self):
        """Get basic information about all loaded datasets."""
        info = {}
        for name, df in self.datasets.items():
            if df is not None:
                info[name] = {
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'missing_values': df.isnull().sum().sum(),
                    'dtypes': df.dtypes.to_dict()
                }
        return info

if __name__ == "__main__":
    # Test the data loader
    loader = VaccinationDataLoader(".")
    datasets = loader.load_all_datasets()
    info = loader.get_basic_info()
    
    for dataset_name, dataset_info in info.items():
        print(f"\n{dataset_name.upper()} Dataset Info:")
        print(f"Shape: {dataset_info['shape']}")
        print(f"Missing values: {dataset_info['missing_values']}")
        print(f"Columns: {dataset_info['columns']}")
