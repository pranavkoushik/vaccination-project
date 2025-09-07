"""
Exploratory Data Analysis Module for Vaccination Data Analysis Project
This module performs comprehensive EDA on vaccination datasets.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('default')
sns.set_palette("husl")

class VaccinationEDA:
    """Class to perform exploratory data analysis on vaccination datasets."""
    
    def __init__(self, cleaned_datasets):
        """
        Initialize EDA with cleaned datasets.
        
        Args:
            cleaned_datasets (dict): Dictionary of cleaned datasets
        """
        self.datasets = cleaned_datasets
        self.insights = {}
        
    def analyze_coverage_trends(self):
        """Analyze vaccination coverage trends over time."""
        print("Analyzing vaccination coverage trends...")
        
        coverage_df = self.datasets['coverage']
        
        # Overall coverage trends by year
        yearly_coverage = coverage_df.groupby('YEAR')['COVERAGE'].agg(['mean', 'median', 'std']).reset_index()
        
        # Coverage by antigen over time
        antigen_trends = coverage_df.groupby(['YEAR', 'ANTIGEN'])['COVERAGE'].mean().reset_index()
        
        # Top antigens by coverage
        top_antigens = coverage_df.groupby('ANTIGEN')['COVERAGE'].mean().sort_values(ascending=False).head(10)
        
        # Regional analysis (using WHO regions from vaccine introduction data if available)
        if 'vaccine_introduction' in self.datasets:
            # Merge with WHO region data
            intro_df = self.datasets['vaccine_introduction'][['ISO_3_CODE', 'WHO_REGION']].drop_duplicates()
            coverage_with_region = coverage_df.merge(
                intro_df, 
                left_on='CODE', 
                right_on='ISO_3_CODE', 
                how='left'
            )
            regional_coverage = coverage_with_region.groupby(['WHO_REGION', 'YEAR'])['COVERAGE'].mean().reset_index()
        else:
            regional_coverage = None
        
        self.insights['coverage_trends'] = {
            'yearly_trends': yearly_coverage,
            'antigen_trends': antigen_trends,
            'top_antigens': top_antigens,
            'regional_trends': regional_coverage
        }
        
        return self.insights['coverage_trends']
    
    def analyze_disease_incidence(self):
        """Analyze disease incidence patterns."""
        print("Analyzing disease incidence patterns...")
        
        incidence_df = self.datasets['incidence']
        
        # Overall incidence trends by year
        yearly_incidence = incidence_df.groupby('YEAR')['INCIDENCE_RATE'].agg(['mean', 'median', 'std']).reset_index()
        
        # Incidence by disease over time
        disease_trends = incidence_df.groupby(['YEAR', 'DISEASE'])['INCIDENCE_RATE'].mean().reset_index()
        
        # Top diseases by incidence rate
        top_diseases = incidence_df.groupby('DISEASE')['INCIDENCE_RATE'].mean().sort_values(ascending=False).head(10)
        
        self.insights['incidence_patterns'] = {
            'yearly_trends': yearly_incidence,
            'disease_trends': disease_trends,
            'top_diseases': top_diseases
        }
        
        return self.insights['incidence_patterns']
    
    def analyze_coverage_vs_incidence(self):
        """Analyze relationship between vaccination coverage and disease incidence."""
        print("Analyzing coverage vs incidence correlation...")
        
        coverage_df = self.datasets['coverage']
        incidence_df = self.datasets['incidence']
        
        # Create mapping between antigens and diseases
        antigen_disease_mapping = {
            'DTP1': 'DIPHTHERIA',
            'DTP3': 'DIPHTHERIA',
            'MCV1': 'MEASLES',
            'MCV2': 'MEASLES',
            'POL3': 'POLIOMYELITIS',
            'BCG': 'TUBERCULOSIS',
            'HepB3': 'HEPATITISB',
            'Hib3': 'HIB',
            'PCV3': 'PNEUMONIA',
            'RCV1': 'RUBELLA'
        }
        
        correlation_results = []
        
        for antigen, disease in antigen_disease_mapping.items():
            # Get coverage data for specific antigen
            antigen_coverage = coverage_df[coverage_df['ANTIGEN'] == antigen].groupby(['CODE', 'YEAR'])['COVERAGE'].mean().reset_index()
            
            # Get incidence data for corresponding disease
            disease_incidence = incidence_df[incidence_df['DISEASE'] == disease].groupby(['CODE', 'YEAR'])['INCIDENCE_RATE'].mean().reset_index()
            
            # Merge coverage and incidence data
            merged_data = antigen_coverage.merge(
                disease_incidence, 
                on=['CODE', 'YEAR'], 
                how='inner'
            )
            
            if len(merged_data) > 10:  # Only analyze if we have enough data points
                correlation = merged_data['COVERAGE'].corr(merged_data['INCIDENCE_RATE'])
                correlation_results.append({
                    'antigen': antigen,
                    'disease': disease,
                    'correlation': correlation,
                    'data_points': len(merged_data)
                })
        
        self.insights['coverage_incidence_correlation'] = correlation_results
        return correlation_results
    
    def analyze_vaccination_gaps(self):
        """Identify vaccination coverage gaps and disparities."""
        print("Analyzing vaccination gaps and disparities...")
        
        coverage_df = self.datasets['coverage']
        
        # Countries with lowest coverage rates
        latest_year = coverage_df['YEAR'].max()
        recent_coverage = coverage_df[coverage_df['YEAR'] >= latest_year - 2]
        
        country_coverage = recent_coverage.groupby(['CODE', 'NAME'])['COVERAGE'].mean().reset_index()
        lowest_coverage = country_coverage.sort_values('COVERAGE').head(20)
        
        # Antigens with largest coverage gaps
        antigen_gaps = coverage_df.groupby('ANTIGEN')['COVERAGE'].agg(['mean', 'std', 'min', 'max']).reset_index()
        antigen_gaps['gap'] = antigen_gaps['max'] - antigen_gaps['min']
        largest_gaps = antigen_gaps.sort_values('gap', ascending=False).head(10)
        
        # Year-over-year coverage changes
        yearly_changes = []
        for country in coverage_df['CODE'].unique()[:50]:  # Analyze top 50 countries
            country_data = coverage_df[coverage_df['CODE'] == country].groupby('YEAR')['COVERAGE'].mean().reset_index()
            if len(country_data) > 1:
                country_data['change'] = country_data['COVERAGE'].diff()
                avg_change = country_data['change'].mean()
                yearly_changes.append({
                    'country': country,
                    'avg_yearly_change': avg_change
                })
        
        coverage_changes = pd.DataFrame(yearly_changes).sort_values('avg_yearly_change')
        
        self.insights['vaccination_gaps'] = {
            'lowest_coverage_countries': lowest_coverage,
            'largest_antigen_gaps': largest_gaps,
            'coverage_changes': coverage_changes
        }
        
        return self.insights['vaccination_gaps']
    
    def create_visualizations(self, save_path="./reports"):
        """Create comprehensive visualizations."""
        print("Creating visualizations...")
        
        import os
        os.makedirs(save_path, exist_ok=True)
        
        # 1. Vaccination Coverage Trends Over Time
        if 'coverage_trends' in self.insights:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # Overall coverage trend
            yearly_data = self.insights['coverage_trends']['yearly_trends']
            axes[0, 0].plot(yearly_data['YEAR'], yearly_data['mean'], marker='o')
            axes[0, 0].fill_between(yearly_data['YEAR'], 
                                  yearly_data['mean'] - yearly_data['std'], 
                                  yearly_data['mean'] + yearly_data['std'], 
                                  alpha=0.3)
            axes[0, 0].set_title('Overall Vaccination Coverage Trends')
            axes[0, 0].set_xlabel('Year')
            axes[0, 0].set_ylabel('Coverage (%)')
            
            # Top antigens coverage
            top_antigens = self.insights['coverage_trends']['top_antigens']
            axes[0, 1].barh(top_antigens.index[:10], top_antigens.values[:10])
            axes[0, 1].set_title('Top 10 Antigens by Average Coverage')
            axes[0, 1].set_xlabel('Average Coverage (%)')
            
            # Disease incidence trends if available
            if 'incidence_patterns' in self.insights:
                incidence_data = self.insights['incidence_patterns']['yearly_trends']
                axes[1, 0].plot(incidence_data['YEAR'], incidence_data['mean'], marker='s', color='red')
                axes[1, 0].set_title('Disease Incidence Trends')
                axes[1, 0].set_xlabel('Year')
                axes[1, 0].set_ylabel('Incidence Rate')
            
            # Coverage gaps
            if 'vaccination_gaps' in self.insights:
                gaps_data = self.insights['vaccination_gaps']['largest_antigen_gaps']
                axes[1, 1].bar(range(len(gaps_data)), gaps_data['gap'])
                axes[1, 1].set_title('Vaccination Coverage Gaps by Antigen')
                axes[1, 1].set_xlabel('Antigen')
                axes[1, 1].set_ylabel('Coverage Gap (%)')
                axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(f"{save_path}/vaccination_analysis_overview.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Interactive Plotly Visualizations
        if 'coverage_trends' in self.insights and self.insights['coverage_trends']['regional_trends'] is not None:
            regional_data = self.insights['coverage_trends']['regional_trends']
            
            fig = px.line(regional_data, x='YEAR', y='COVERAGE', color='WHO_REGION',
                         title='Vaccination Coverage by WHO Region Over Time')
            fig.write_html(f"{save_path}/regional_coverage_trends.html")
        
        # 3. Correlation Heatmap
        if 'coverage_incidence_correlation' in self.insights:
            corr_data = pd.DataFrame(self.insights['coverage_incidence_correlation'])
            if not corr_data.empty:
                plt.figure(figsize=(10, 6))
                plt.barh(corr_data['antigen'] + ' vs ' + corr_data['disease'], corr_data['correlation'])
                plt.title('Correlation between Vaccination Coverage and Disease Incidence')
                plt.xlabel('Correlation Coefficient')
                plt.axvline(x=0, color='black', linestyle='-', alpha=0.3)
                plt.tight_layout()
                plt.savefig(f"{save_path}/coverage_incidence_correlation.png", dpi=300, bbox_inches='tight')
                plt.close()
        
        print(f"Visualizations saved to {save_path}")
    
    def generate_insights_report(self):
        """Generate a comprehensive insights report."""
        report = []
        report.append("VACCINATION DATA ANALYSIS - KEY INSIGHTS")
        report.append("=" * 50)
        
        if 'coverage_trends' in self.insights:
            report.append("\n1. VACCINATION COVERAGE TRENDS:")
            yearly_data = self.insights['coverage_trends']['yearly_trends']
            latest_coverage = yearly_data.iloc[-1]['mean']
            report.append(f"   - Latest average coverage: {latest_coverage:.2f}%")
            
            top_antigen = self.insights['coverage_trends']['top_antigens'].index[0]
            top_coverage = self.insights['coverage_trends']['top_antigens'].iloc[0]
            report.append(f"   - Highest coverage antigen: {top_antigen} ({top_coverage:.2f}%)")
        
        if 'incidence_patterns' in self.insights:
            report.append("\n2. DISEASE INCIDENCE PATTERNS:")
            top_disease = self.insights['incidence_patterns']['top_diseases'].index[0]
            top_incidence = self.insights['incidence_patterns']['top_diseases'].iloc[0]
            report.append(f"   - Highest incidence disease: {top_disease} ({top_incidence:.2f} per 100,000)")
        
        if 'coverage_incidence_correlation' in self.insights:
            report.append("\n3. COVERAGE-INCIDENCE CORRELATIONS:")
            for result in self.insights['coverage_incidence_correlation']:
                if abs(result['correlation']) > 0.3:  # Only report strong correlations
                    report.append(f"   - {result['antigen']} vs {result['disease']}: {result['correlation']:.3f}")
        
        if 'vaccination_gaps' in self.insights:
            report.append("\n4. VACCINATION GAPS:")
            lowest_country = self.insights['vaccination_gaps']['lowest_coverage_countries'].iloc[0]
            report.append(f"   - Lowest coverage country: {lowest_country['NAME']} ({lowest_country['COVERAGE']:.2f}%)")
            
            largest_gap = self.insights['vaccination_gaps']['largest_antigen_gaps'].iloc[0]
            report.append(f"   - Largest coverage gap: {largest_gap['ANTIGEN']} ({largest_gap['gap']:.2f}% difference)")
        
        return "\n".join(report)
    
    def run_complete_analysis(self):
        """Run complete EDA analysis."""
        print("Starting comprehensive EDA...")
        
        self.analyze_coverage_trends()
        self.analyze_disease_incidence()
        self.analyze_coverage_vs_incidence()
        self.analyze_vaccination_gaps()
        self.create_visualizations()
        
        # Generate and save insights report
        insights_report = self.generate_insights_report()
        
        with open("./reports/insights_report.txt", "w") as f:
            f.write(insights_report)
        
        print("EDA completed!")
        print("\n" + insights_report)
        
        return self.insights

if __name__ == "__main__":
    # Load cleaned datasets
    import os
    
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
    
    # Run EDA
    eda = VaccinationEDA(cleaned_datasets)
    insights = eda.run_complete_analysis()
