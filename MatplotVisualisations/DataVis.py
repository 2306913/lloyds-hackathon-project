import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

class MarketplaceVisualizer:
    def __init__(self, csv_file_path):
        """Initialize with CSV data"""
        self.df = pd.read_csv(r"C:\University\lloyds\lloyds-hackathon-project\MatplotVisualisations\product_data(in).csv")
        self.df.columns = self.df.columns.str.strip()  # Clean column names
        
    def visualization_1_supply_demand_gap(self, save_path=None):
        """
        1. SUPPLY VS DEMAND GAP ANALYSIS
        Most Critical: Shows over/under-stocked items for inventory optimization
        """
        plt.figure(figsize=(12, 8))
        
        # Create supply-demand ratio
        self.df['Supply_Demand_Ratio'] = self.df['Quantity'] / self.df['Demand']
        
        # Color coding: Red = understocked, Green = well-stocked, Blue = overstocked
        colors = []
        for ratio in self.df['Supply_Demand_Ratio']:
            if ratio < 0.8:
                colors.append('red')      # Understocked
            elif ratio > 1.5:
                colors.append('blue')     # Overstocked
            else:
                colors.append('green')    # Well-stocked
        
        scatter = plt.scatter(self.df['Demand'], self.df['Quantity'], 
                            c=colors, alpha=0.7, s=self.df['FootFall']*2)
        
        # Add diagonal line for perfect supply-demand balance
        max_val = max(self.df['Demand'].max(), self.df['Quantity'].max())
        plt.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Perfect Balance')
        
        plt.xlabel('Demand', fontsize=12)
        plt.ylabel('Quantity in Stock', fontsize=12)
        plt.title('Supply vs Demand Gap Analysis\n(Bubble size = FootFall, Colors: Red=Understocked, Green=Balanced, Blue=Overstocked)', 
                  fontsize=14, pad=20)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', label='Understocked (<80% demand)'),
            Patch(facecolor='green', label='Well-stocked (80-150% demand)'),
            Patch(facecolor='blue', label='Overstocked (>150% demand)'),
            plt.Line2D([0], [0], color='k', linestyle='--', label='Perfect Balance')
        ]
        plt.legend(handles=legend_elements, loc='upper left')
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return self._get_insights_supply_demand()
    
    def visualization_2_store_performance(self, save_path=None):
        """
        2. STORE PERFORMANCE COMPARISON
        Essential: Compare stores across all key metrics
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Store Performance Dashboard', fontsize=16, y=0.98)
        
        # Group by store
        store_metrics = self.df.groupby('Store Name').agg({
            'Quantity': 'sum',
            'Demand': 'sum', 
            'FootFall': 'mean'
        }).reset_index()
        store_metrics['Sales_Potential'] = store_metrics['Demand'] * store_metrics['FootFall'] / 100
        
        # 1. Total Inventory by Store
        bars1 = axes[0,0].bar(store_metrics['Store Name'], store_metrics['Quantity'], 
                             color='skyblue', edgecolor='navy', alpha=0.7)
        axes[0,0].set_title('Total Inventory by Store', fontweight='bold')
        axes[0,0].set_ylabel('Total Quantity')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            axes[0,0].text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(height)}', ha='center', va='bottom')
        
        # 2. Total Demand by Store
        bars2 = axes[0,1].bar(store_metrics['Store Name'], store_metrics['Demand'], 
                             color='lightcoral', edgecolor='darkred', alpha=0.7)
        axes[0,1].set_title('Total Demand by Store', fontweight='bold')
        axes[0,1].set_ylabel('Total Demand')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        for bar in bars2:
            height = bar.get_height()
            axes[0,1].text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(height)}', ha='center', va='bottom')
        
        # 3. Average FootFall by Store
        bars3 = axes[1,0].bar(store_metrics['Store Name'], store_metrics['FootFall'], 
                             color='lightgreen', edgecolor='darkgreen', alpha=0.7)
        axes[1,0].set_title('Average FootFall by Store', fontweight='bold')
        axes[1,0].set_ylabel('Average FootFall')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        for bar in bars3:
            height = bar.get_height()
            axes[1,0].text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(height)}', ha='center', va='bottom')
        
        # 4. Sales Potential Score
        bars4 = axes[1,1].bar(store_metrics['Store Name'], store_metrics['Sales_Potential'], 
                             color='gold', edgecolor='orange', alpha=0.7)
        axes[1,1].set_title('Sales Potential Score', fontweight='bold')
        axes[1,1].set_ylabel('Potential Score')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        for bar in bars4:
            height = bar.get_height()
            axes[1,1].text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return self._get_insights_store_performance(store_metrics)
    
    def visualization_3_category_performance(self, save_path=None):
        """
        3. PRODUCT CATEGORY PERFORMANCE MATRIX
        Strategic: Shows which categories drive the business
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Group by category
        category_metrics = self.df.groupby('Product Category').agg({
            'Quantity': 'sum',
            'Demand': 'sum',
            'FootFall': 'mean'
        }).reset_index()
        
        # 1. Category Performance Bars
        x_pos = np.arange(len(category_metrics))
        width = 0.25
        
        bars1 = ax1.bar(x_pos - width, category_metrics['Quantity'], width, 
                       label='Total Inventory', color='skyblue', alpha=0.8)
        bars2 = ax1.bar(x_pos, category_metrics['Demand'], width, 
                       label='Total Demand', color='lightcoral', alpha=0.8)
        bars3 = ax1.bar(x_pos + width, category_metrics['FootFall'], width, 
                       label='Avg FootFall', color='lightgreen', alpha=0.8)
        
        ax1.set_xlabel('Product Category')
        ax1.set_ylabel('Values')
        ax1.set_title('Category Performance Comparison', fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(category_metrics['Product Category'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Category Market Share (Demand-based)
        wedges, texts, autotexts = ax2.pie(category_metrics['Demand'], 
                                          labels=category_metrics['Product Category'],
                                          autopct='%1.1f%%', startangle=90,
                                          colors=plt.cm.Set3.colors)
        ax2.set_title('Market Share by Demand', fontweight='bold')
        
        # Beautify pie chart
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return self._get_insights_category_performance(category_metrics)
    
    def visualization_4_inventory_heatmap(self, save_path=None):
        """
        4. INVENTORY OPTIMIZATION HEATMAP
        Operational: Shows exactly which products need attention by store
        """
        plt.figure(figsize=(14, 8))
        
        # Create pivot table for heatmap
        pivot_data = self.df.pivot_table(
            values='Supply_Demand_Ratio', 
            index='Product Name', 
            columns='Store Name', 
            aggfunc='mean'
        ).fillna(0)
        
        # Create custom colormap: Red (understocked) -> Yellow (balanced) -> Blue (overstocked)
        from matplotlib.colors import LinearSegmentedColormap
        colors = ['darkred', 'red', 'yellow', 'lightblue', 'darkblue']
        cmap = LinearSegmentedColormap.from_list('inventory', colors, N=100)
        
        # Create heatmap
        sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap=cmap, center=1.0,
                   cbar_kws={'label': 'Supply/Demand Ratio'}, 
                   linewidths=0.5, linecolor='white')
        
        plt.title('Inventory Optimization Heatmap by Store and Product\n(Red = Understocked, Yellow = Balanced, Blue = Overstocked)', 
                  fontsize=14, pad=20)
        plt.xlabel('Store Name', fontsize=12)
        plt.ylabel('Product Name', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # Add text box with interpretation
        textstr = 'Ratio Guide:\n< 0.8 = Understocked\n0.8-1.5 = Well-stocked\n> 1.5 = Overstocked'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return self._get_insights_inventory_heatmap(pivot_data)
    
    def visualization_5_top_products_demand(self, save_path=None):
        """
        5. TOP PRODUCTS BY DEMAND RANKING
        Sales Focus: Identifies best-selling and high-potential products
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Group by product and sum demand
        product_demand = self.df.groupby('Product Name').agg({
            'Demand': 'sum',
            'FootFall': 'mean',
            'Quantity': 'sum'
        }).reset_index().sort_values('Demand', ascending=True)
        
        # 1. Top Products by Total Demand
        bars1 = ax1.barh(product_demand['Product Name'], product_demand['Demand'], 
                        color='coral', alpha=0.8, edgecolor='darkred')
        ax1.set_xlabel('Total Demand')
        ax1.set_title('Top Products by Total Demand', fontweight='bold', pad=20)
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars1, product_demand['Demand'])):
            ax1.text(value + 1, bar.get_y() + bar.get_height()/2, 
                    f'{int(value)}', va='center', fontweight='bold')
        
        # 2. Products by FootFall Potential
        product_footfall = product_demand.sort_values('FootFall', ascending=True)
        bars2 = ax2.barh(product_footfall['Product Name'], product_footfall['FootFall'], 
                        color='lightblue', alpha=0.8, edgecolor='darkblue')
        ax2.set_xlabel('Average FootFall')
        ax2.set_title('Products by FootFall Attraction', fontweight='bold', pad=20)
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars2, product_footfall['FootFall'])):
            ax2.text(value + 1, bar.get_y() + bar.get_height()/2, 
                    f'{int(value)}', va='center', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return self._get_insights_top_products(product_demand)
    
    def generate_all_visualizations(self, save_directory=None):
        """Generate all 5 visualizations at once"""
        insights = {}
        
        print("Generating Visualization 1: Supply vs Demand Gap Analysis...")
        insights['supply_demand'] = self.visualization_1_supply_demand_gap(
            f"{save_directory}/1_supply_demand_gap.png" if save_directory else None)
        
        print("\nGenerating Visualization 2: Store Performance Comparison...")
        insights['store_performance'] = self.visualization_2_store_performance(
            f"{save_directory}/2_store_performance.png" if save_directory else None)
        
        print("\nGenerating Visualization 3: Category Performance Matrix...")
        insights['category_performance'] = self.visualization_3_category_performance(
            f"{save_directory}/3_category_performance.png" if save_directory else None)
        
        print("\nGenerating Visualization 4: Inventory Optimization Heatmap...")
        insights['inventory_heatmap'] = self.visualization_4_inventory_heatmap(
            f"{save_directory}/4_inventory_heatmap.png" if save_directory else None)
        
        print("\nGenerating Visualization 5: Top Products by Demand...")
        insights['top_products'] = self.visualization_5_top_products_demand(
            f"{save_directory}/5_top_products.png" if save_directory else None)
        
        return insights
    
    # Helper methods for insights
    def _get_insights_supply_demand(self):
        understocked = self.df[self.df['Supply_Demand_Ratio'] < 0.8]
        overstocked = self.df[self.df['Supply_Demand_Ratio'] > 1.5]
        
        return {
            'understocked_items': len(understocked),
            'overstocked_items': len(overstocked),
            'critical_understocked': understocked.nsmallest(3, 'Supply_Demand_Ratio')[['Product Name', 'Store Name']].to_dict('records')
        }
    
    def _get_insights_store_performance(self, store_metrics):
        best_store = store_metrics.loc[store_metrics['Sales_Potential'].idxmax(), 'Store Name']
        worst_store = store_metrics.loc[store_metrics['Sales_Potential'].idxmin(), 'Store Name']
        
        return {
            'best_performing_store': best_store,
            'worst_performing_store': worst_store,
            'store_rankings': store_metrics.sort_values('Sales_Potential', ascending=False)['Store Name'].tolist()
        }
    
    def _get_insights_category_performance(self, category_metrics):
        top_category = category_metrics.loc[category_metrics['Demand'].idxmax(), 'Product Category']
        
        return {
            'top_category_by_demand': top_category,
            'category_rankings': category_metrics.sort_values('Demand', ascending=False)['Product Category'].tolist()
        }
    
    def _get_insights_inventory_heatmap(self, pivot_data):
        critical_cells = []
        for product in pivot_data.index:
            for store in pivot_data.columns:
                ratio = pivot_data.loc[product, store]
                if ratio < 0.8 and ratio > 0:
                    critical_cells.append(f"{product} at {store}")
        
        return {
            'critical_inventory_issues': critical_cells[:5]  # Top 5 issues
        }
    
    def _get_insights_top_products(self, product_demand):
        return {
            'top_demand_product': product_demand.iloc[-1]['Product Name'],
            'top_footfall_product': product_demand.loc[product_demand['FootFall'].idxmax(), 'Product Name'],
            'product_rankings_by_demand': product_demand.sort_values('Demand', ascending=False)['Product Name'].tolist()
        }

# USAGE EXAMPLE:
if __name__ == "__main__":
    # Initialize the visualizer
    viz = MarketplaceVisualizer('product_datain.csv')
    
    # Generate all visualizations and get insights
    print("=== MARKETPLACE VISUALIZATION SUITE ===\n")
    insights = viz.generate_all_visualizations()
    
    # Print key insights
    print("\n=== KEY INSIGHTS ===")
    print(f"Critical understocked items: {insights['supply_demand']['understocked_items']}")
    print(f"Best performing store: {insights['store_performance']['best_performing_store']}")
    print(f"Top category by demand: {insights['category_performance']['top_category_by_demand']}")
    print(f"Top product by demand: {insights['top_products']['top_demand_product']}")