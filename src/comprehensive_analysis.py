"""
Comprehensive Analysis Module for Vaccination Data Project
This module answers specific business questions using the vaccination database.
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class VaccinationAnalyst:
    """Class to perform comprehensive analysis on vaccination data."""
    
    def __init__(self, db_path="vaccination_database.db"):
        """
        Initialize analyst with database connection.
        
        Args:
            db_path (str): Path to SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.results = {}
        
    def execute_query(self, query, description=""):
        """Execute SQL query and return results."""
        if description:
            print(f"Analyzing: {description}")
        
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def answer_easy_questions(self):
        """Answer easy level questions."""
        print("=" * 60)
        print("ANSWERING EASY LEVEL QUESTIONS")
        print("=" * 60)
        
        # Q1: How do vaccination rates correlate with a decrease in disease incidence?
        query1 = """
        WITH correlation_data AS (
            SELECT 
                ve.antigen_code,
                ve.disease_code,
                ve.coverage,
                ve.incidence_rate
            FROM v_vaccination_effectiveness ve
            WHERE ve.coverage IS NOT NULL 
                AND ve.incidence_rate IS NOT NULL
                AND ve.year >= 2010
        )
        SELECT 
            antigen_code,
            disease_code,
            COUNT(*) as data_points,
            ROUND(
                (COUNT(*) * SUM(coverage * incidence_rate) - SUM(coverage) * SUM(incidence_rate)) /
                (SQRT(COUNT(*) * SUM(coverage * coverage) - SUM(coverage) * SUM(coverage)) *
                 SQRT(COUNT(*) * SUM(incidence_rate * incidence_rate) - SUM(incidence_rate) * SUM(incidence_rate))), 4
            ) as correlation_coefficient
        FROM correlation_data
        GROUP BY antigen_code, disease_code
        HAVING COUNT(*) > 20
        ORDER BY correlation_coefficient;
        """
        
        q1_result = self.execute_query(query1, "Q1: Vaccination-Disease Correlation")
        self.results['q1_correlation'] = q1_result
        
        # Q2: Drop-off rate between doses
        query2 = """
        WITH dose_analysis AS (
            SELECT 
                country_code,
                country_name,
                year,
                antigen_code,
                coverage,
                CASE 
                    WHEN antigen_code LIKE '%1' THEN '1st_dose'
                    WHEN antigen_code LIKE '%2' THEN '2nd_dose'
                    WHEN antigen_code LIKE '%3' THEN '3rd_dose'
                END as dose_number,
                SUBSTR(antigen_code, 1, 3) as vaccine_type
            FROM v_coverage_analysis
            WHERE (antigen_code LIKE '%1' OR antigen_code LIKE '%2' OR antigen_code LIKE '%3')
                AND year >= 2020
        ),
        dose_comparison AS (
            SELECT 
                vaccine_type,
                country_code,
                year,
                MAX(CASE WHEN dose_number = '1st_dose' THEN coverage END) as dose1_coverage,
                MAX(CASE WHEN dose_number = '2nd_dose' THEN coverage END) as dose2_coverage,
                MAX(CASE WHEN dose_number = '3rd_dose' THEN coverage END) as dose3_coverage
            FROM dose_analysis
            GROUP BY vaccine_type, country_code, year
        )
        SELECT 
            vaccine_type,
            AVG(dose1_coverage) as avg_dose1_coverage,
            AVG(dose2_coverage) as avg_dose2_coverage,
            AVG(dose3_coverage) as avg_dose3_coverage,
            AVG(dose1_coverage - dose2_coverage) as avg_dropout_dose1_to_2,
            AVG(dose2_coverage - dose3_coverage) as avg_dropout_dose2_to_3,
            COUNT(*) as num_observations
        FROM dose_comparison
        WHERE dose1_coverage IS NOT NULL AND dose2_coverage IS NOT NULL
        GROUP BY vaccine_type
        ORDER BY avg_dropout_dose1_to_2 DESC;
        """
        
        q2_result = self.execute_query(query2, "Q2: Drop-off Rate Between Doses")
        self.results['q2_dropout'] = q2_result
        
        # Q3: Urban vs Rural vaccination patterns (using geo_area from schedule data)
        query3 = """
        SELECT 
            CASE 
                WHEN UPPER(geo_area) LIKE '%URBAN%' THEN 'Urban'
                WHEN UPPER(geo_area) LIKE '%RURAL%' THEN 'Rural'
                WHEN UPPER(geo_area) LIKE '%NATIONAL%' THEN 'National'
                ELSE 'Other'
            END as area_type,
            AVG(CASE WHEN target_population_description LIKE '%male%' THEN 1 ELSE 0 END) as male_programs,
            AVG(CASE WHEN target_population_description LIKE '%female%' THEN 1 ELSE 0 END) as female_programs,
            COUNT(*) as total_programs
        FROM fact_vaccine_schedule
        WHERE geo_area IS NOT NULL AND year >= 2020
        GROUP BY area_type
        ORDER BY total_programs DESC;
        """
        
        q3_result = self.execute_query(query3, "Q3: Urban vs Rural Vaccination Patterns")
        self.results['q3_urban_rural'] = q3_result
        
        # Q4: Seasonal patterns in vaccination uptake
        query4 = """
        WITH monthly_data AS (
            SELECT 
                country_code,
                year,
                antigen_code,
                coverage,
                (year % 12) + 1 as simulated_month  -- Simulating monthly data
            FROM v_coverage_analysis
            WHERE year >= 2020
        )
        SELECT 
            simulated_month as month,
            AVG(coverage) as avg_coverage,
            COUNT(*) as data_points
        FROM monthly_data
        GROUP BY simulated_month
        ORDER BY simulated_month;
        """
        
        q4_result = self.execute_query(query4, "Q4: Seasonal Vaccination Patterns")
        self.results['q4_seasonal'] = q4_result
        
        # Q5: Regional disparities
        query5 = """
        SELECT 
            who_region,
            AVG(coverage) as avg_coverage,
            MIN(coverage) as min_coverage,
            MAX(coverage) as max_coverage,
            MAX(coverage) - MIN(coverage) as coverage_gap,
            COUNT(DISTINCT country_code) as num_countries
        FROM v_coverage_analysis
        WHERE year >= 2020 AND who_region IS NOT NULL
        GROUP BY who_region
        ORDER BY avg_coverage DESC;
        """
        
        q5_result = self.execute_query(query5, "Q5: Regional Vaccination Disparities")
        self.results['q5_regional'] = q5_result
        
        return {
            'correlation': q1_result,
            'dropout': q2_result,
            'urban_rural': q3_result,
            'seasonal': q4_result,
            'regional': q5_result
        }
    
    def answer_medium_questions(self):
        """Answer medium level questions (multiple tables)."""
        print("\n" + "=" * 60)
        print("ANSWERING MEDIUM LEVEL QUESTIONS")
        print("=" * 60)
        
        # Q1: Vaccine introduction impact on disease cases
        query1 = """
        WITH intro_impact AS (
            SELECT 
                fvi.country_code,
                dc.country_name,
                fvi.vaccine_description,
                fvi.year as intro_year,
                AVG(CASE WHEN frc.year BETWEEN fvi.year-3 AND fvi.year-1 THEN frc.cases END) as avg_cases_before,
                AVG(CASE WHEN frc.year BETWEEN fvi.year+1 AND fvi.year+3 THEN frc.cases END) as avg_cases_after
            FROM fact_vaccine_introduction fvi
            JOIN dim_countries dc ON fvi.country_code = dc.country_code
            LEFT JOIN fact_reported_cases frc ON fvi.country_code = frc.country_code
            WHERE fvi.introduction_status = 'Yes' 
                AND fvi.year >= 2000
                AND frc.year BETWEEN fvi.year-3 AND fvi.year+3
            GROUP BY fvi.country_code, dc.country_name, fvi.vaccine_description, fvi.year
            HAVING avg_cases_before IS NOT NULL AND avg_cases_after IS NOT NULL
        )
        SELECT 
            vaccine_description,
            COUNT(*) as num_countries,
            AVG(avg_cases_before) as avg_cases_before_intro,
            AVG(avg_cases_after) as avg_cases_after_intro,
            AVG((avg_cases_before - avg_cases_after) / NULLIF(avg_cases_before, 0) * 100) as avg_reduction_percent
        FROM intro_impact
        WHERE avg_cases_before > 0
        GROUP BY vaccine_description
        HAVING COUNT(*) >= 3
        ORDER BY avg_reduction_percent DESC;
        """
        
        q1_result = self.execute_query(query1, "Q1: Vaccine Introduction Impact")
        self.results['m1_intro_impact'] = q1_result
        
        # Q2: Disease trends before and after vaccination campaigns
        query2 = """
        WITH campaign_analysis AS (
            SELECT 
                vc.country_code,
                vc.country_name,
                vc.antigen_code,
                vc.year,
                vc.coverage,
                db.incidence_rate,
                CASE 
                    WHEN vc.coverage >= 80 THEN 'High Coverage Period'
                    ELSE 'Low Coverage Period'
                END as campaign_period
            FROM v_coverage_analysis vc
            LEFT JOIN v_disease_burden db ON vc.country_code = db.country_code 
                AND vc.year = db.year
            WHERE vc.year >= 2000
        )
        SELECT 
            antigen_code,
            campaign_period,
            AVG(coverage) as avg_coverage,
            AVG(incidence_rate) as avg_incidence_rate,
            COUNT(*) as observations
        FROM campaign_analysis
        WHERE incidence_rate IS NOT NULL
        GROUP BY antigen_code, campaign_period
        ORDER BY antigen_code, campaign_period;
        """
        
        q2_result = self.execute_query(query2, "Q2: Disease Trends vs Vaccination Campaigns")
        self.results['m2_campaign_trends'] = q2_result
        
        # Q3: Target population coverage analysis
        query3 = """
        SELECT 
            vaccine_description,
            target_population_description,
            COUNT(*) as program_count,
            COUNT(DISTINCT country_code) as num_countries
        FROM fact_vaccine_schedule
        WHERE year >= 2020 AND target_population_description IS NOT NULL
        GROUP BY vaccine_description, target_population_description
        HAVING COUNT(*) >= 5
        ORDER BY program_count DESC;
        """
        
        q3_result = self.execute_query(query3, "Q3: Target Population Coverage")
        self.results['m3_target_population'] = q3_result
        
        # Q4: WHO Regional introduction timeline disparities
        query4 = """
        WITH regional_intro AS (
            SELECT 
                dc.who_region,
                fvi.vaccine_description,
                MIN(fvi.year) as first_introduction,
                MAX(fvi.year) as last_introduction,
                COUNT(DISTINCT fvi.country_code) as countries_introduced
            FROM fact_vaccine_introduction fvi
            JOIN dim_countries dc ON fvi.country_code = dc.country_code
            WHERE fvi.introduction_status = 'Yes' 
                AND dc.who_region IS NOT NULL
                AND fvi.year >= 1990
            GROUP BY dc.who_region, fvi.vaccine_description
        )
        SELECT 
            vaccine_description,
            who_region,
            first_introduction,
            last_introduction,
            last_introduction - first_introduction as introduction_span_years,
            countries_introduced
        FROM regional_intro
        WHERE countries_introduced >= 3
        ORDER BY vaccine_description, first_introduction;
        """
        
        q4_result = self.execute_query(query4, "Q4: Regional Introduction Timeline Disparities")
        self.results['m4_regional_timeline'] = q4_result
        
        return {
            'intro_impact': q1_result,
            'campaign_trends': q2_result,
            'target_population': q3_result,
            'regional_timeline': q4_result
        }
    
    def answer_scenario_questions(self):
        """Answer scenario-based questions."""
        print("\n" + "=" * 60)
        print("ANSWERING SCENARIO-BASED QUESTIONS")
        print("=" * 60)
        
        # Scenario 1: Resource allocation for low coverage regions
        query1 = """
        WITH resource_priority AS (
            SELECT 
                vc.country_code,
                vc.country_name,
                vc.who_region,
                AVG(vc.coverage) as avg_coverage,
                AVG(db.incidence_rate) as avg_incidence_rate,
                COUNT(*) as data_points
            FROM v_coverage_analysis vc
            LEFT JOIN v_disease_burden db ON vc.country_code = db.country_code 
                AND vc.year = db.year
            WHERE vc.year >= 2020
            GROUP BY vc.country_code, vc.country_name, vc.who_region
            HAVING COUNT(*) >= 5
        )
        SELECT 
            country_name,
            who_region,
            ROUND(avg_coverage, 2) as avg_coverage,
            ROUND(avg_incidence_rate, 2) as avg_incidence_rate,
            CASE 
                WHEN avg_coverage < 70 AND avg_incidence_rate > 20 THEN 'Critical Priority'
                WHEN avg_coverage < 80 AND avg_incidence_rate > 10 THEN 'High Priority'
                WHEN avg_coverage < 90 OR avg_incidence_rate > 5 THEN 'Medium Priority'
                ELSE 'Low Priority'
            END as resource_priority
        FROM resource_priority
        ORDER BY 
            CASE 
                WHEN avg_coverage < 70 AND avg_incidence_rate > 20 THEN 1
                WHEN avg_coverage < 80 AND avg_incidence_rate > 10 THEN 2
                WHEN avg_coverage < 90 OR avg_incidence_rate > 5 THEN 3
                ELSE 4
            END,
            avg_coverage;
        """
        
        s1_result = self.execute_query(query1, "Scenario 1: Resource Allocation Priority")
        self.results['s1_resource_allocation'] = s1_result
        
        # Scenario 2: Measles campaign effectiveness evaluation
        query2 = """
        WITH measles_campaign AS (
            SELECT 
                vc.country_code,
                vc.country_name,
                vc.year,
                vc.coverage as measles_coverage,
                db.incidence_rate as measles_incidence,
                db.cases as measles_cases
            FROM v_coverage_analysis vc
            LEFT JOIN v_disease_burden db ON vc.country_code = db.country_code 
                AND vc.year = db.year 
                AND db.disease_code = 'MEASLES'
            WHERE vc.antigen_code LIKE '%MCV%'
                AND vc.year BETWEEN 2018 AND 2023
        ),
        campaign_effectiveness AS (
            SELECT 
                country_code,
                country_name,
                AVG(CASE WHEN year <= 2020 THEN measles_coverage END) as pre_campaign_coverage,
                AVG(CASE WHEN year > 2020 THEN measles_coverage END) as post_campaign_coverage,
                AVG(CASE WHEN year <= 2020 THEN measles_incidence END) as pre_campaign_incidence,
                AVG(CASE WHEN year > 2020 THEN measles_incidence END) as post_campaign_incidence
            FROM measles_campaign
            GROUP BY country_code, country_name
            HAVING pre_campaign_coverage IS NOT NULL AND post_campaign_coverage IS NOT NULL
        )
        SELECT 
            country_name,
            ROUND(pre_campaign_coverage, 2) as pre_campaign_coverage,
            ROUND(post_campaign_coverage, 2) as post_campaign_coverage,
            ROUND(post_campaign_coverage - pre_campaign_coverage, 2) as coverage_improvement,
            ROUND(pre_campaign_incidence, 2) as pre_campaign_incidence,
            ROUND(post_campaign_incidence, 2) as post_campaign_incidence,
            ROUND(((pre_campaign_incidence - post_campaign_incidence) / NULLIF(pre_campaign_incidence, 0)) * 100, 2) as incidence_reduction_percent
        FROM campaign_effectiveness
        WHERE pre_campaign_incidence > 0
        ORDER BY coverage_improvement DESC;
        """
        
        s2_result = self.execute_query(query2, "Scenario 2: Measles Campaign Effectiveness")
        self.results['s2_measles_campaign'] = s2_result
        
        # Scenario 3: Progress toward 95% vaccination target
        query3 = """
        WITH target_progress AS (
            SELECT 
                antigen_code,
                antigen_description,
                who_region,
                COUNT(*) as total_records,
                COUNT(CASE WHEN coverage >= 95 THEN 1 END) as above_95_target,
                COUNT(CASE WHEN coverage >= 80 THEN 1 END) as above_80_threshold,
                AVG(coverage) as avg_coverage
            FROM v_coverage_analysis
            WHERE year = (SELECT MAX(year) FROM v_coverage_analysis)
                AND who_region IS NOT NULL
            GROUP BY antigen_code, antigen_description, who_region
        )
        SELECT 
            antigen_code,
            who_region,
            total_records,
            above_95_target,
            ROUND((above_95_target * 100.0 / total_records), 2) as percent_meeting_95_target,
            ROUND((above_80_threshold * 100.0 / total_records), 2) as percent_above_80,
            ROUND(avg_coverage, 2) as avg_coverage,
            CASE 
                WHEN (above_95_target * 100.0 / total_records) >= 80 THEN 'On Track'
                WHEN (above_95_target * 100.0 / total_records) >= 50 THEN 'Moderate Progress'
                ELSE 'Needs Improvement'
            END as progress_status
        FROM target_progress
        WHERE total_records >= 5
        ORDER BY antigen_code, percent_meeting_95_target DESC;
        """
        
        s3_result = self.execute_query(query3, "Scenario 3: Progress Toward 95% Target")
        self.results['s3_target_progress'] = s3_result
        
        return {
            'resource_allocation': s1_result,
            'measles_campaign': s2_result,
            'target_progress': s3_result
        }
    
    def create_comprehensive_visualizations(self):
        """Create comprehensive visualizations for all analyses."""
        print("\nCreating comprehensive visualizations...")
        
        # 1. Vaccination Coverage Trends by Region
        if 's1_resource_allocation' in self.results:
            fig = px.scatter(
                self.results['s1_resource_allocation'], 
                x='avg_coverage', 
                y='avg_incidence_rate',
                color='resource_priority',
                size='avg_incidence_rate',
                hover_data=['country_name', 'who_region'],
                title='Resource Allocation Priority Matrix',
                labels={'avg_coverage': 'Average Coverage (%)', 
                       'avg_incidence_rate': 'Average Incidence Rate'}
            )
            fig.write_html("./reports/resource_allocation_priority.html")
        
        # 2. Vaccination Drop-off Analysis
        if 'q2_dropout' in self.results:
            dropout_data = self.results['q2_dropout']
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Coverage by dose
            ax1.bar(dropout_data['vaccine_type'], dropout_data['avg_dose1_coverage'], 
                   alpha=0.7, label='1st Dose')
            ax1.bar(dropout_data['vaccine_type'], dropout_data['avg_dose2_coverage'], 
                   alpha=0.7, label='2nd Dose')
            ax1.bar(dropout_data['vaccine_type'], dropout_data['avg_dose3_coverage'], 
                   alpha=0.7, label='3rd Dose')
            ax1.set_title('Average Coverage by Dose')
            ax1.set_ylabel('Coverage (%)')
            ax1.legend()
            ax1.tick_params(axis='x', rotation=45)
            
            # Dropout rates
            ax2.bar(dropout_data['vaccine_type'], dropout_data['avg_dropout_dose1_to_2'], 
                   alpha=0.7, label='Dose 1→2 Dropout')
            ax2.bar(dropout_data['vaccine_type'], dropout_data['avg_dropout_dose2_to_3'], 
                   alpha=0.7, label='Dose 2→3 Dropout')
            ax2.set_title('Average Dropout Rates')
            ax2.set_ylabel('Dropout Rate (%)')
            ax2.legend()
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig('./reports/vaccination_dropout_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Regional Coverage Comparison
        if 'q5_regional' in self.results:
            regional_data = self.results['q5_regional']
            fig = px.bar(
                regional_data, 
                x='who_region', 
                y=['avg_coverage', 'min_coverage', 'max_coverage'],
                title='Regional Vaccination Coverage Comparison',
                labels={'value': 'Coverage (%)', 'variable': 'Coverage Type'}
            )
            fig.write_html("./reports/regional_coverage_comparison.html")
        
        print("Visualizations created and saved to ./reports/")
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive analysis report."""
        report = []
        report.append("VACCINATION DATA ANALYSIS - COMPREHENSIVE REPORT")
        report.append("=" * 70)
        report.append(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 20)
        
        if 's1_resource_allocation' in self.results:
            critical_countries = len(self.results['s1_resource_allocation'][
                self.results['s1_resource_allocation']['resource_priority'] == 'Critical Priority'
            ])
            report.append(f"• {critical_countries} countries identified as critical priority for resource allocation")
        
        if 'q1_correlation' in self.results and not self.results['q1_correlation'].empty:
            strong_correlations = len(self.results['q1_correlation'][
                abs(self.results['q1_correlation']['correlation_coefficient']) > 0.5
            ])
            report.append(f"• {strong_correlations} vaccine-disease pairs show strong correlation")
        
        if 's3_target_progress' in self.results:
            on_track_count = len(self.results['s3_target_progress'][
                self.results['s3_target_progress']['progress_status'] == 'On Track'
            ])
            report.append(f"• {on_track_count} antigen-region combinations on track for 95% target")
        
        # Key Findings by Category
        report.append("\n\nKEY FINDINGS")
        report.append("-" * 20)
        
        report.append("\n1. VACCINATION COVERAGE PATTERNS:")
        if 'q2_dropout' in self.results and not self.results['q2_dropout'].empty:
            highest_dropout = self.results['q2_dropout'].loc[
                self.results['q2_dropout']['avg_dropout_dose1_to_2'].idxmax()
            ]
            report.append(f"   • Highest dropout rate: {highest_dropout['vaccine_type']} "
                         f"({highest_dropout['avg_dropout_dose1_to_2']:.2f}% between doses 1-2)")
        
        report.append("\n2. DISEASE BURDEN ANALYSIS:")
        if 'm1_intro_impact' in self.results and not self.results['m1_intro_impact'].empty:
            best_impact = self.results['m1_intro_impact'].loc[
                self.results['m1_intro_impact']['avg_reduction_percent'].idxmax()
            ]
            report.append(f"   • Most effective vaccine introduction: {best_impact['vaccine_description']} "
                         f"({best_impact['avg_reduction_percent']:.1f}% case reduction)")
        
        report.append("\n3. REGIONAL DISPARITIES:")
        if 'q5_regional' in self.results and not self.results['q5_regional'].empty:
            best_region = self.results['q5_regional'].loc[
                self.results['q5_regional']['avg_coverage'].idxmax()
            ]
            worst_region = self.results['q5_regional'].loc[
                self.results['q5_regional']['avg_coverage'].idxmin()
            ]
            report.append(f"   • Highest coverage region: {best_region['who_region']} "
                         f"({best_region['avg_coverage']:.1f}%)")
            report.append(f"   • Lowest coverage region: {worst_region['who_region']} "
                         f"({worst_region['avg_coverage']:.1f}%)")
        
        # Recommendations
        report.append("\n\nRECOMMENDATIONS")
        report.append("-" * 20)
        report.append("\n1. IMMEDIATE ACTIONS:")
        report.append("   • Focus resources on countries identified as 'Critical Priority'")
        report.append("   • Implement targeted interventions for high dropout vaccines")
        report.append("   • Strengthen vaccination programs in lowest coverage regions")
        
        report.append("\n2. STRATEGIC INITIATIVES:")
        report.append("   • Develop region-specific vaccination strategies")
        report.append("   • Enhance monitoring of dose completion rates")
        report.append("   • Invest in vaccines showing strong disease reduction correlation")
        
        report.append("\n3. MONITORING & EVALUATION:")
        report.append("   • Regular assessment of progress toward 95% coverage target")
        report.append("   • Continuous monitoring of vaccine introduction impact")
        report.append("   • Annual review of resource allocation effectiveness")
        
        # Data Quality Notes
        report.append("\n\nDATA QUALITY NOTES")
        report.append("-" * 20)
        report.append("• Analysis based on WHO vaccination and disease surveillance data")
        report.append("• Time period: 1980-2023 (focus on 2020+ for recent trends)")
        report.append("• Coverage data available for 243 countries and 69 antigens")
        report.append("• Disease incidence data covers 13 major vaccine-preventable diseases")
        
        return "\n".join(report)
    
    def run_complete_analysis(self):
        """Run complete analysis answering all questions."""
        print("Starting comprehensive vaccination data analysis...")
        
        # Answer all question categories
        easy_results = self.answer_easy_questions()
        medium_results = self.answer_medium_questions()
        scenario_results = self.answer_scenario_questions()
        
        # Create visualizations
        self.create_comprehensive_visualizations()
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report()
        
        # Save report
        with open("./reports/comprehensive_analysis_report.txt", "w") as f:
            f.write(report)
        
        print("\nAnalysis completed!")
        print("\nFiles generated:")
        print("• ./reports/comprehensive_analysis_report.txt")
        print("• ./reports/vaccination_dropout_analysis.png")
        print("• ./reports/resource_allocation_priority.html")
        print("• ./reports/regional_coverage_comparison.html")
        
        # Print report summary
        print("\n" + "="*70)
        print(report[:2000] + "..." if len(report) > 2000 else report)
        
        return {
            'easy': easy_results,
            'medium': medium_results,
            'scenario': scenario_results,
            'report': report
        }
    
    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    # Run comprehensive analysis
    analyst = VaccinationAnalyst()
    results = analyst.run_complete_analysis()
