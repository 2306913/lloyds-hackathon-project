# Complete Marketplace Visualization Suite - Individual Components
# File: marketplace_visualizations_simplified.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

class MarketplaceVisualizer:
    def __init__(self, csv_file_path):
        """Initialize with CSV data"""
        self.df = pd.read_csv(csv_file_path)
        self.df.columns = self.df.columns.str.strip()  # Clean column names
        self.df['Supply_Demand_Ratio'] = self.df['Quantity'] / self.df['Demand']
        self.df['Estimated_Sales'] = np.minimum(self.df['Demand'], self.df['Quantity'])
        print(f"✅ Data loaded successfully! {len(self.df)} records from {len(self.df['Store Name'].unique())} stores.")

# =============================================================================
# GRAPH 1 COMPONENTS: Supply vs Demand Analysis
# =============================================================================

    def graph_1a_supply_demand_overview(self, save_path=None):
        """Graph 1A: Clean Supply vs Demand Overview - No Labels"""
        plt.figure(figsize=(12, 8))
        
        colors = []
        for ratio in self.df['Supply_Demand_Ratio']:
            if ratio < 0.8:
                colors.append('red')
            elif ratio > 1.5:
                colors.append('blue')
            else:
                colors.append('green')
        
        plt.scatter(self.df['Demand'], self.df['Quantity'], 
                   c=colors, alpha=0.8, s=self.df['FootFall']*3, 
                   edgecolors='black', linewidth=0.5)
        
        # Add diagonal line for perfect balance
        max_val = max(self.df['Demand'].max(), self.df['Quantity'].max())
        plt.plot([0, max_val], [0, max_val], 'k--', alpha=0.6, linewidth=2)
        
        plt.xlabel('Demand', fontsize=14, fontweight='bold')
        plt.ylabel('Quantity in Stock', fontsize=14, fontweight='bold')
        plt.title('Supply vs Demand Overview\nBubble Size = FootFall | Red=Understocked, Green=Balanced, Blue=Overstocked', 
                  fontsize=16, fontweight='bold', pad=20)
        
        # Simple legend
        legend_elements = [
            Patch(facecolor='red', label='Understocked (<80%)', alpha=0.7),
            Patch(facecolor='green', label='Well-stocked (80-150%)', alpha=0.7),
            Patch(facecolor='blue', label='Overstocked (>150%)', alpha=0.7)
        ]
        plt.legend(handles=legend_elements, loc='upper left', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_1b_critical_understocked(self, save_path=None):
        """Graph 1B: Critical Understocked Items"""
        understocked = self.df[self.df['Supply_Demand_Ratio'] < 0.8].copy()
        if len(understocked) == 0:
            print("No understocked items found!")
            return
            
        understocked = understocked.nsmallest(10, 'Supply_Demand_Ratio')
        understocked['Item_Label'] = (understocked['Product Name'].str[:15] + '\n' + 
                                    understocked['Store Name'].str[:12] + '\n' + 
                                    understocked['Store Location'])
        
        plt.figure(figsize=(14, 8))
        bars = plt.barh(understocked['Item_Label'], understocked['Supply_Demand_Ratio'],
                       color='darkred', alpha=0.8)
        
        plt.xlabel('Supply/Demand Ratio', fontsize=14, fontweight='bold')
        plt.title('🚨 Most Critical Understocked Items\n(Lower ratio = More urgent)', 
                  fontsize=16, fontweight='bold', pad=20)
        
        # Add ratio values on bars
        for bar, ratio in zip(bars, understocked['Supply_Demand_Ratio']):
            plt.text(ratio + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{ratio:.2f}', va='center', fontweight='bold')
        
        plt.axvline(x=0.8, color='orange', linestyle='--', alpha=0.7, label='Target: 0.8')
        plt.legend()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_1c_overstocked_items(self, save_path=None):
        """Graph 1C: Overstocked Items"""
        overstocked = self.df[self.df['Supply_Demand_Ratio'] > 1.5].copy()
        if len(overstocked) == 0:
            print("No overstocked items found!")
            return
            
        overstocked = overstocked.nlargest(10, 'Supply_Demand_Ratio')
        overstocked['Item_Label'] = (overstocked['Product Name'].str[:15] + '\n' + 
                                   overstocked['Store Name'].str[:12] + '\n' + 
                                   overstocked['Store Location'])
        
        plt.figure(figsize=(14, 8))
        bars = plt.barh(overstocked['Item_Label'], overstocked['Supply_Demand_Ratio'],
                       color='darkblue', alpha=0.8)
        
        plt.xlabel('Supply/Demand Ratio', fontsize=14, fontweight='bold')
        plt.title('📦 Most Overstocked Items\n(Higher ratio = More excess inventory)', 
                  fontsize=16, fontweight='bold', pad=20)
        
        # Add ratio values
        for bar, ratio in zip(bars, overstocked['Supply_Demand_Ratio']):
            plt.text(ratio + 0.05, bar.get_y() + bar.get_height()/2,
                    f'{ratio:.2f}', va='center', fontweight='bold')
        
        plt.axvline(x=1.5, color='orange', linestyle='--', alpha=0.7, label='Target: 1.5')
        plt.legend()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

# =============================================================================
# GRAPH 2 COMPONENTS: Aggregate Performance Analysis
# =============================================================================

    def graph_2a_marketplace_totals(self, save_path=None):
        """Graph 2A: Marketplace Total Metrics"""
        plt.figure(figsize=(12, 6))
        
        metrics = ['Total Inventory', 'Total Demand', 'Avg FootFall', 'Total Stores', 'Unique Products']
        values = [
            self.df['Quantity'].sum(),
            self.df['Demand'].sum(), 
            self.df['FootFall'].mean(),
            len(self.df[['Store Name', 'Store Location']].drop_duplicates()),
            len(self.df['Product Name'].unique())
        ]
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        
        bars = plt.bar(metrics, values, color=colors, alpha=0.8, edgecolor='black')
        plt.title('🏪 Marketplace Overview - Key Metrics', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Values', fontsize=12, fontweight='bold')
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                    f'{int(value):,}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_2b_location_performance(self, save_path=None):
        """Graph 2B: Performance by Location"""
        location_metrics = self.df.groupby('Store Location').agg({
            'Quantity': 'sum',
            'Demand': 'sum',
            'FootFall': 'mean'
        }).reset_index().sort_values('Demand', ascending=False)
        
        plt.figure(figsize=(12, 8))
        x_pos = np.arange(len(location_metrics))
        width = 0.25
        
        plt.bar(x_pos - width, location_metrics['Quantity'], width, 
                label='Total Inventory', color='#3498db', alpha=0.8)
        plt.bar(x_pos, location_metrics['Demand'], width, 
                label='Total Demand', color='#e74c3c', alpha=0.8)
        plt.bar(x_pos + width, location_metrics['FootFall'], width, 
                label='Avg FootFall', color='#2ecc71', alpha=0.8)
        
        plt.xlabel('Store Location', fontsize=12, fontweight='bold')
        plt.ylabel('Values', fontsize=12, fontweight='bold')
        plt.title('📍 Performance Comparison by Location', fontsize=16, fontweight='bold', pad=20)
        plt.xticks(x_pos, location_metrics['Store Location'], rotation=45, ha='right')
        plt.legend(fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_2c_store_rankings(self, save_path=None):
        """Graph 2C: Individual Store Performance Rankings"""
        store_metrics = self.df.groupby(['Store Name', 'Store Location']).agg({
            'Quantity': 'sum',
            'Demand': 'sum',
            'FootFall': 'mean'
        }).reset_index()
        
        store_metrics['Sales_Potential'] = (store_metrics['Demand'] * store_metrics['FootFall'] / 100).round(1)
        store_metrics = store_metrics.sort_values('Sales_Potential', ascending=True)
        store_metrics['Store_Label'] = (store_metrics['Store Name'] + ' (' + 
                                       store_metrics['Store Location'] + ')')
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(store_metrics['Store_Label'], store_metrics['Sales_Potential'],
                       color='#f39c12', alpha=0.8, edgecolor='#d35400')
        
        plt.xlabel('Sales Potential Score', fontsize=12, fontweight='bold')
        plt.title('🏆 Store Performance Rankings\nSales Potential = (Demand × FootFall) ÷ 100', 
                  fontsize=16, fontweight='bold', pad=20)
        
        # Add value labels
        for bar, value in zip(bars, store_metrics['Sales_Potential']):
            plt.text(value + 1, bar.get_y() + bar.get_height()/2,
                    f'{value:.1f}', va='center', fontweight='bold')
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_2d_market_share(self, save_path=None):
        """Graph 2D: Company Market Share"""
        company_metrics = self.df.groupby('Store Name').agg({
            'Demand': 'sum'
        }).reset_index().sort_values('Demand', ascending=False)
        
        plt.figure(figsize=(10, 8))
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'][:len(company_metrics)]
        
        wedges, texts, autotexts = plt.pie(company_metrics['Demand'], 
                                          labels=company_metrics['Store Name'],
                                          autopct=lambda pct: f'{pct:.1f}%\n({int(pct*company_metrics["Demand"].sum()/100):,})',
                                          startangle=90,
                                          colors=colors,
                                          explode=[0.05] * len(company_metrics))
        
        plt.title('📊 Company Market Share by Total Demand', fontsize=16, fontweight='bold', pad=20)
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

# =============================================================================
# GRAPH 3 COMPONENTS: Product Performance Analysis  
# =============================================================================

    def graph_3a_product_location_heatmap(self, save_path=None):
        """Graph 3A: Product Performance by Location Heatmap"""
        plt.figure(figsize=(12, 8))
        
        product_location_pivot = self.df.pivot_table(
            values='Demand', 
            index='Product Name', 
            columns='Store Location', 
            aggfunc='sum'
        ).fillna(0)
        
        sns.heatmap(product_location_pivot, annot=True, fmt='.0f', cmap='YlOrRd',
                   cbar_kws={'label': 'Total Demand'}, linewidths=0.5)
        
        plt.title('🔥 Product Demand by Location\n(Darker colors = Higher demand)', 
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Store Location', fontsize=12, fontweight='bold')
        plt.ylabel('Product Name', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_3b_best_locations_per_product(self, save_path=None):
        """Graph 3B: Best Location for Each Product"""
        product_best = self.df.groupby(['Product Name', 'Store Location']).agg({
            'Demand': 'sum'
        }).reset_index()
        
        best_locations = product_best.groupby('Product Name').apply(
            lambda x: x.loc[x['Demand'].idxmax()]
        ).reset_index(drop=True)
        
        best_locations = best_locations.sort_values('Demand', ascending=True)
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(best_locations['Product Name'], best_locations['Demand'],
                       color='lightcoral', alpha=0.8, edgecolor='darkred')
        
        plt.xlabel('Peak Demand at Best Location', fontsize=12, fontweight='bold')
        plt.title('⭐ Best Performing Location for Each Product', fontsize=16, fontweight='bold', pad=20)
        
        # Add location labels
        for bar, location, demand in zip(bars, best_locations['Store Location'], best_locations['Demand']):
            plt.text(demand + 1, bar.get_y() + bar.get_height()/2,
                    f'★ {location}', va='center', fontsize=10, fontweight='bold', color='darkred')
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_3c_product_store_heatmap(self, save_path=None):
        """Graph 3C: Product Performance by Store Heatmap"""
        plt.figure(figsize=(12, 8))
        
        product_store_pivot = self.df.pivot_table(
            values='Demand', 
            index='Product Name', 
            columns='Store Name', 
            aggfunc='sum'
        ).fillna(0)
        
        sns.heatmap(product_store_pivot, annot=True, fmt='.0f', cmap='Blues',
                   cbar_kws={'label': 'Total Demand'}, linewidths=0.5)
        
        plt.title('🏪 Product Demand by Store\n(Darker colors = Higher demand)', 
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Store Name', fontsize=12, fontweight='bold')
        plt.ylabel('Product Name', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_3d_overall_product_rankings(self, save_path=None):
        """Graph 3D: Overall Product Rankings"""
        product_totals = self.df.groupby('Product Name').agg({
            'Demand': 'sum',
            'Quantity': 'sum',
            'FootFall': 'mean'
        }).reset_index().sort_values('Demand', ascending=True)
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(product_totals['Product Name'], product_totals['Demand'],
                       color='gold', alpha=0.8, edgecolor='orange')
        
        plt.xlabel('Total Demand Across All Stores', fontsize=12, fontweight='bold')
        plt.title('🏆 Overall Product Performance Rankings', fontsize=16, fontweight='bold', pad=20)
        
        # Add demand values
        for bar, demand in zip(bars, product_totals['Demand']):
            plt.text(demand + 1, bar.get_y() + bar.get_height()/2,
                    f'{demand:,}', va='center', fontweight='bold')
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

# =============================================================================
# GRAPH 4 COMPONENTS: FootFall Conversion Analysis
# =============================================================================

    def graph_4a_location_conversion_rates(self, save_path=None):
        """Graph 4A: Conversion Rates by Location"""
        location_conversion = self.df.groupby('Store Location').agg({
            'FootFall': 'sum',
            'Estimated_Sales': 'sum'
        }).reset_index()
        location_conversion['Conversion_Rate'] = (location_conversion['Estimated_Sales'] / 
                                                location_conversion['FootFall']) * 100
        location_conversion = location_conversion.sort_values('Conversion_Rate', ascending=False)
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(location_conversion['Store Location'], location_conversion['Conversion_Rate'],
                      color='lightblue', alpha=0.8, edgecolor='darkblue')
        
        plt.ylabel('Conversion Rate (%)', fontsize=12, fontweight='bold')
        plt.title('📈 FootFall to Sales Conversion Rate by Location\nHigher is Better', 
                  fontsize=16, fontweight='bold', pad=20)
        
        # Add percentage labels
        for bar, rate in zip(bars, location_conversion['Conversion_Rate']):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_4b_footfall_vs_sales_scatter(self, save_path=None):
        """Graph 4B: FootFall vs Sales Relationship"""
        store_conversion = self.df.groupby(['Store Name', 'Store Location']).agg({
            'FootFall': 'sum',
            'Estimated_Sales': 'sum'
        }).reset_index()
        store_conversion['Conversion_Rate'] = (store_conversion['Estimated_Sales'] / 
                                              store_conversion['FootFall']) * 100
        
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(store_conversion['FootFall'], store_conversion['Estimated_Sales'],
                             s=200, alpha=0.7, c=store_conversion['Conversion_Rate'], 
                             cmap='RdYlGn', edgecolors='black')
        
        # Add trend line
        z = np.polyfit(store_conversion['FootFall'], store_conversion['Estimated_Sales'], 1)
        p = np.poly1d(z)
        plt.plot(store_conversion['FootFall'], p(store_conversion['FootFall']), "r--", alpha=0.8)
        
        plt.xlabel('Total FootFall', fontsize=12, fontweight='bold')
        plt.ylabel('Total Sales', fontsize=12, fontweight='bold')
        plt.title('💡 FootFall vs Sales Efficiency\nColor indicates conversion rate', 
                  fontsize=16, fontweight='bold', pad=20)
        
        plt.colorbar(scatter, label='Conversion Rate (%)')
        
        # Add store labels
        for idx, row in store_conversion.iterrows():
            plt.annotate(f"{row['Store Name'][:8]}\n{row['Store Location']}", 
                        (row['FootFall'], row['Estimated_Sales']),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_4c_store_conversion_rankings(self, save_path=None):
        """Graph 4C: Store Conversion Rate Rankings"""
        store_conversion = self.df.groupby(['Store Name', 'Store Location']).agg({
            'FootFall': 'sum',
            'Estimated_Sales': 'sum'
        }).reset_index()
        store_conversion['Conversion_Rate'] = (store_conversion['Estimated_Sales'] / 
                                              store_conversion['FootFall']) * 100
        store_conversion['Store_Label'] = (store_conversion['Store Name'] + '\n(' + 
                                         store_conversion['Store Location'] + ')')
        store_conversion = store_conversion.sort_values('Conversion_Rate', ascending=True)
        
        plt.figure(figsize=(12, 8))
        colors = ['lightcoral' if x < store_conversion['Conversion_Rate'].median() else 'lightgreen' 
                 for x in store_conversion['Conversion_Rate']]
        
        bars = plt.barh(store_conversion['Store_Label'], store_conversion['Conversion_Rate'],
                       color=colors, alpha=0.8, edgecolor='black')
        
        plt.xlabel('Conversion Rate (%)', fontsize=12, fontweight='bold')
        plt.title('🏆 Store Conversion Rate Rankings\nGreen = Above Average, Red = Below Average', 
                  fontsize=16, fontweight='bold', pad=20)
        
        # Add percentage labels
        for bar, rate in zip(bars, store_conversion['Conversion_Rate']):
            plt.text(rate + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{rate:.1f}%', va='center', fontweight='bold', fontsize=10)
        
        # Add median line
        median_rate = store_conversion['Conversion_Rate'].median()
        plt.axvline(x=median_rate, color='blue', linestyle='--', alpha=0.7, 
                   label=f'Median: {median_rate:.1f}%')
        plt.legend()
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def graph_4d_conversion_improvement_potential(self, save_path=None):
        """Graph 4D: Conversion Improvement Opportunities"""
        store_conversion = self.df.groupby(['Store Name', 'Store Location']).agg({
            'FootFall': 'sum',
            'Estimated_Sales': 'sum'
        }).reset_index()
        store_conversion['Conversion_Rate'] = (store_conversion['Estimated_Sales'] / 
                                              store_conversion['FootFall']) * 100
        
        best_rate = store_conversion['Conversion_Rate'].max()
        store_conversion['Improvement_Potential'] = best_rate - store_conversion['Conversion_Rate']
        store_conversion['Store_Label'] = (store_conversion['Store Name'] + '\n(' + 
                                         store_conversion['Store Location'] + ')')
        
        # Only show stores with improvement potential > 1%
        improvement_data = store_conversion[store_conversion['Improvement_Potential'] > 1.0].copy()
        improvement_data = improvement_data.sort_values('Improvement_Potential', ascending=True)
        
        if len(improvement_data) == 0:
            print("No significant improvement opportunities found!")
            return
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(improvement_data['Store_Label'], improvement_data['Improvement_Potential'],
                       color='orange', alpha=0.8, edgecolor='darkorange')
        
        plt.xlabel('Conversion Rate Improvement Potential (%)', fontsize=12, fontweight='bold')
        plt.title('🎯 Store Conversion Improvement Opportunities\nGap from Best Performer', 
                  fontsize=16, fontweight='bold', pad=20)
        
        # Add percentage labels
        for bar, potential in zip(bars, improvement_data['Improvement_Potential']):
            plt.text(potential + 0.2, bar.get_y() + bar.get_height()/2,
                    f'+{potential:.1f}%', va='center', fontweight='bold')
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

# =============================================================================
# RUNNER FUNCTIONS FOR INDIVIDUAL COMPONENTS
# =============================================================================

def run_all_graph_1_components():
    """Run all Graph 1 components"""
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv")
    print("🔍 GRAPH 1 COMPONENTS: Supply vs Demand Analysis")
    viz.graph_1a_supply_demand_overview()
    input("Press Enter for next component...")
    viz.graph_1b_critical_understocked()
    input("Press Enter for next component...")
    viz.graph_1c_overstocked_items()

def run_all_graph_2_components():
    """Run all Graph 2 components"""
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv")
    print("🏪 GRAPH 2 COMPONENTS: Aggregate Performance Analysis")
    viz.graph_2a_marketplace_totals()
    input("Press Enter for next component...")
    viz.graph_2b_location_performance()
    input("Press Enter for next component...")
    viz.graph_2c_store_rankings()
    input("Press Enter for next component...")
    viz.graph_2d_market_share()

def run_all_graph_3_components():
    """Run all Graph 3 components"""
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv")
    print("📦 GRAPH 3 COMPONENTS: Product Performance Analysis")
    viz.graph_3a_product_location_heatmap()
    input("Press Enter for next component...")
    viz.graph_3b_best_locations_per_product()
    input("Press Enter for next component...")
    viz.graph_3c_product_store_heatmap()
    input("Press Enter for next component...")
    viz.graph_3d_overall_product_rankings()

def run_all_graph_4_components():
    """Run all Graph 4 components"""
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv")
    print("💹 GRAPH 4 COMPONENTS: FootFall Conversion Analysis")
    viz.graph_4a_location_conversion_rates()
    input("Press Enter for next component...")
    viz.graph_4b_footfall_vs_sales_scatter()
    input("Press Enter for next component...")
    viz.graph_4c_store_conversion_rankings()
    input("Press Enter for next component...")
    viz.graph_4d_conversion_improvement_potential()

# Individual component runners
def run_graph_1a(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_1a_supply_demand_overview()
def run_graph_1b(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_1b_critical_understocked()
def run_graph_1c(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_1c_overstocked_items()

def run_graph_2a(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_2a_marketplace_totals()
def run_graph_2b(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_2b_location_performance()
def run_graph_2c(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_2c_store_rankings()
def run_graph_2d(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_2d_market_share()

def run_graph_3a(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_3a_product_location_heatmap()
def run_graph_3b(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_3b_best_locations_per_product()
def run_graph_3c(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_3c_product_store_heatmap()
def run_graph_3d(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_3d_overall_product_rankings()

def run_graph_4a(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_4a_location_conversion_rates()
def run_graph_4b(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_4b_footfall_vs_sales_scatter()
def run_graph_4c(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_4c_store_conversion_rankings()
def run_graph_4d(): 
    viz = MarketplaceVisualizer(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv"); viz.graph_4d_conversion_improvement_potential()

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🎯 MARKETPLACE VISUALIZATION SUITE - INDIVIDUAL COMPONENTS")
    print("=" * 80)
    print("\n📊 GRAPH 1 COMPONENTS - Supply vs Demand:")
    print("  run_graph_1a() - Supply vs Demand Overview")
    print("  run_graph_1b() - Critical Understocked Items") 
    print("  run_graph_1c() - Overstocked Items")
    print("  run_all_graph_1_components() - All Graph 1 components")
    
    print("\n🏪 GRAPH 2 COMPONENTS - Aggregate Performance:")
    print("  run_graph_2a() - Marketplace Totals")
    print("  run_graph_2b() - Location Performance")
    print("  run_graph_2c() - Store Rankings") 
    print("  run_graph_2d() - Market Share")
    print("  run_all_graph_2_components() - All Graph 2 components")
    
    print("\n📦 GRAPH 3 COMPONENTS - Product Performance:")
    print("  run_graph_3a() - Product-Location Heatmap")
    print("  run_graph_3b() - Best Locations per Product")
    print("  run_graph_3c() - Product-Store Heatmap")
    print("  run_graph_3d() - Overall Product Rankings")
    print("  run_all_graph_3_components() - All Graph 3 components")
    
    print("\n💹 GRAPH 4 COMPONENTS - Conversion Analysis:")
    print("  run_graph_4a() - Location Conversion Rates")
    print("  run_graph_4b() - FootFall vs Sales Scatter")
    print("  run_graph_4c() - Store Conversion Rankings")
    print("  run_graph_4d() - Improvement Opportunities")
    print("  run_all_graph_4_components() - All Graph 4 components")
    print("=" * 80)
    
    # Uncomment to run specific components:
    run_graph_1a()
    run_graph_1b()
    run_graph_1c()

    run_graph_2a()
    run_graph_2b()
    run_graph_2c()
    run_graph_2d()

    run_graph_3a()
    run_graph_3b()
    run_graph_3c()
    run_graph_3d()

    run_graph_4a()
    run_graph_4b()
    run_graph_4c()
    run_graph_4d()
    # run_all_graph_1_components()