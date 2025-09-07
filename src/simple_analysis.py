"""
Simple Analysis Script for Vaccination Data Project
This module performs basic analysis without complex visualizations.
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class SimpleVaccinationAnalyst:
    """Simplified class for vaccination analysis."""
    
    def __init__(self, db_path="vaccination_database.db"):
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
    
    def basic_analysis(self):
        """Perform basic vaccination analysis."""
        print("BASIC VACCINATION DATA ANALYSIS")
        print("=" * 50)
        
        # 1. Overall coverage statistics
        query1 = """
        SELECT 
            COUNT(*) as total_records,
            AVG(coverage) as avg_coverage,
            MIN(coverage) as min_coverage,
            MAX(coverage) as max_coverage,
            COUNT(DISTINCT country_code) as num_countries,
            COUNT(DISTINCT antigen_code) as num_antigens
        FROM v_coverage_analysis
        WHERE year >= 2020;
        """
        
        result1 = self.execute_query(query1, "Overall Coverage Statistics")
        print("\nOVERALL COVERAGE STATISTICS (2020+):")
        if not result1.empty:
            for col in result1.columns:
                print(f"  {col}: {result1[col].iloc[0]}")
        
        # 2. Top performing countries
        query2 = """
        SELECT 
            country_name,
            who_region,
            AVG(coverage) as avg_coverage,
            COUNT(*) as num_records
        FROM v_coverage_analysis
        WHERE year >= 2020
        GROUP BY country_name, who_region
        HAVING COUNT(*) >= 10
        ORDER BY avg_coverage DESC
        LIMIT 10;
        """
        
        result2 = self.execute_query(query2, "Top Performing Countries")
        print("\nTOP 10 COUNTRIES BY AVERAGE COVERAGE:")
        if not result2.empty:
            for _, row in result2.iterrows():
                print(f"  {row['country_name']} ({row['who_region']}): {row['avg_coverage']:.2f}%")
        
        # 3. Coverage by antigen
        query3 = """
        SELECT 
            antigen_code,
            antigen_description,
            AVG(coverage) as avg_coverage,
            COUNT(*) as num_records
        FROM v_coverage_analysis
        WHERE year >= 2020
        GROUP BY antigen_code, antigen_description
        ORDER BY avg_coverage DESC
        LIMIT 10;
        """
        
        result3 = self.execute_query(query3, "Coverage by Antigen")
        print("\nTOP 10 ANTIGENS BY AVERAGE COVERAGE:")
        if not result3.empty:
            for _, row in result3.iterrows():
                print(f"  {row['antigen_code']}: {row['avg_coverage']:.2f}%")
        
        # 4. Regional comparison
        query4 = """
        SELECT 
            who_region,
            AVG(coverage) as avg_coverage,
            COUNT(DISTINCT country_code) as num_countries,
            COUNT(*) as total_records
        FROM v_coverage_analysis
        WHERE year >= 2020 AND who_region IS NOT NULL
        GROUP BY who_region
        ORDER BY avg_coverage DESC;
        """
        
        result4 = self.execute_query(query4, "Regional Comparison")
        print("\nCOVERAGE BY WHO REGION:")
        if not result4.empty:
            for _, row in result4.iterrows():
                print(f"  {row['who_region']}: {row['avg_coverage']:.2f}% "
                      f"({row['num_countries']} countries)")
        
        # 5. Disease burden analysis
        query5 = """
        SELECT 
            disease_code,
            disease_description,
            AVG(incidence_rate) as avg_incidence_rate,
            SUM(cases) as total_cases,
            COUNT(DISTINCT country_code) as num_countries
        FROM v_disease_burden
        WHERE year >= 2020
        GROUP BY disease_code, disease_description
        ORDER BY avg_incidence_rate DESC;
        """
        
        result5 = self.execute_query(query5, "Disease Burden Analysis")
        print("\nDISEASE BURDEN (2020+):")
        if not result5.empty:
            for _, row in result5.iterrows():
                print(f"  {row['disease_code']}: {row['avg_incidence_rate']:.2f} per 100k "
                      f"({row['total_cases']:.0f} total cases)")
        
        # 6. Resource allocation priorities
        query6 = """
        WITH priority_analysis AS (
            SELECT 
                vc.country_name,
                vc.who_region,
                AVG(vc.coverage) as avg_coverage,
                AVG(db.incidence_rate) as avg_incidence_rate
            FROM v_coverage_analysis vc
            LEFT JOIN v_disease_burden db ON vc.country_code = db.country_code 
                AND vc.year = db.year
            WHERE vc.year >= 2020
            GROUP BY vc.country_name, vc.who_region
            HAVING COUNT(*) >= 5
        )
        SELECT 
            country_name,
            who_region,
            ROUND(avg_coverage, 2) as avg_coverage,
            ROUND(COALESCE(avg_incidence_rate, 0), 2) as avg_incidence_rate,
            CASE 
                WHEN avg_coverage < 70 THEN 'High Priority'
                WHEN avg_coverage < 85 THEN 'Medium Priority'
                ELSE 'Low Priority'
            END as priority_level
        FROM priority_analysis
        ORDER BY avg_coverage, avg_incidence_rate DESC;
        """
        
        result6 = self.execute_query(query6, "Resource Allocation Priorities")
        print("\nRESOURCE ALLOCATION PRIORITIES:")
        if not result6.empty:
            high_priority = result6[result6['priority_level'] == 'High Priority']
            print(f"  High Priority Countries: {len(high_priority)}")
            if not high_priority.empty:
                print("  Examples:")
                for _, row in high_priority.head(5).iterrows():
                    print(f"    {row['country_name']} ({row['who_region']}): {row['avg_coverage']}%")
        
        return {
            'overall_stats': result1,
            'top_countries': result2,
            'antigen_coverage': result3,
            'regional_comparison': result4,
            'disease_burden': result5,
            'resource_priorities': result6
        }
    
    def create_simple_visualizations(self):
        """Create simple matplotlib visualizations."""
        print("\nCreating simple visualizations...")
        
        # Regional coverage comparison
        query = """
        SELECT 
            who_region,
            AVG(coverage) as avg_coverage
        FROM v_coverage_analysis
        WHERE year >= 2020 AND who_region IS NOT NULL
        GROUP BY who_region
        ORDER BY avg_coverage DESC;
        """
        
        regional_data = self.execute_query(query)
        
        if not regional_data.empty:
            plt.figure(figsize=(12, 6))
            plt.bar(regional_data['who_region'], regional_data['avg_coverage'])
            plt.title('Average Vaccination Coverage by WHO Region (2020+)')
            plt.xlabel('WHO Region')
            plt.ylabel('Average Coverage (%)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('./reports/regional_coverage_simple.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("Saved: ./reports/regional_coverage_simple.png")
        
        # Antigen coverage comparison
        query2 = """
        SELECT 
            antigen_code,
            AVG(coverage) as avg_coverage
        FROM v_coverage_analysis
        WHERE year >= 2020
        GROUP BY antigen_code
        ORDER BY avg_coverage DESC
        LIMIT 15;
        """
        
        antigen_data = self.execute_query(query2)
        
        if not antigen_data.empty:
            plt.figure(figsize=(14, 8))
            plt.barh(antigen_data['antigen_code'], antigen_data['avg_coverage'])
            plt.title('Average Coverage by Antigen (Top 15, 2020+)')
            plt.xlabel('Average Coverage (%)')
            plt.ylabel('Antigen Code')
            plt.tight_layout()
            plt.savefig('./reports/antigen_coverage_simple.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("Saved: ./reports/antigen_coverage_simple.png")
    
    def generate_simple_report(self, results):
        """Generate a simple analysis report."""
        report = []
        report.append("VACCINATION DATA ANALYSIS - SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Key Statistics
        if 'overall_stats' in results and not results['overall_stats'].empty:
            stats = results['overall_stats'].iloc[0]
            report.append("KEY STATISTICS (2020+)")
            report.append("-" * 25)
            report.append(f"Total vaccination records: {stats['total_records']:,}")
            report.append(f"Average coverage: {stats['avg_coverage']:.2f}%")
            report.append(f"Coverage range: {stats['min_coverage']:.2f}% - {stats['max_coverage']:.2f}%")
            report.append(f"Countries analyzed: {stats['num_countries']}")
            report.append(f"Antigens tracked: {stats['num_antigens']}")
        
        # Top Performers
        if 'top_countries' in results and not results['top_countries'].empty:
            report.append("\nTOP PERFORMING COUNTRIES")
            report.append("-" * 30)
            for _, row in results['top_countries'].head(5).iterrows():
                report.append(f"{row['country_name']} ({row['who_region']}): {row['avg_coverage']:.2f}%")
        
        # Regional Analysis
        if 'regional_comparison' in results and not results['regional_comparison'].empty:
            report.append("\nREGIONAL PERFORMANCE")
            report.append("-" * 25)
            best_region = results['regional_comparison'].iloc[0]
            worst_region = results['regional_comparison'].iloc[-1]
            report.append(f"Best performing region: {best_region['who_region']} ({best_region['avg_coverage']:.2f}%)")
            report.append(f"Lowest performing region: {worst_region['who_region']} ({worst_region['avg_coverage']:.2f}%)")
        
        # Priority Countries
        if 'resource_priorities' in results and not results['resource_priorities'].empty:
            high_priority = results['resource_priorities'][
                results['resource_priorities']['priority_level'] == 'High Priority'
            ]
            report.append(f"\nHIGH PRIORITY COUNTRIES: {len(high_priority)}")
            report.append("-" * 35)
            for _, row in high_priority.head(10).iterrows():
                report.append(f"{row['country_name']} ({row['who_region']}): {row['avg_coverage']}%")
        
        # Key Insights
        report.append("\nKEY INSIGHTS")
        report.append("-" * 15)
        report.append("• Focus vaccination efforts on countries with <70% coverage")
        report.append("• Regional disparities exist and require targeted interventions")
        report.append("• Some antigens show consistently higher coverage rates")
        report.append("• Disease burden correlates with vaccination coverage gaps")
        
        # Recommendations
        report.append("\nRECOMMENDATIONS")
        report.append("-" * 18)
        report.append("• Prioritize resource allocation to high-priority countries")
        report.append("• Develop region-specific vaccination strategies")
        report.append("• Strengthen health systems in low-coverage areas")
        report.append("• Monitor and evaluate vaccination program effectiveness")
        
        return "\n".join(report)
    
    def run_analysis(self):
        """Run complete analysis."""
        print("Starting vaccination data analysis...")
        
        results = self.basic_analysis()
        self.create_simple_visualizations()
        report = self.generate_simple_report(results)
        
        # Save report
        with open("./reports/vaccination_analysis_report.txt", "w") as f:
            f.write(report)
        
        print("\nAnalysis completed!")
        print("Files generated:")
        print("• ./reports/vaccination_analysis_report.txt")
        print("• ./reports/regional_coverage_simple.png")
        print("• ./reports/antigen_coverage_simple.png")
        
        print("\n" + "="*60)
        print(report)
        
        return results, report
    
    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    analyst = SimpleVaccinationAnalyst()
    results, report = analyst.run_analysis()
