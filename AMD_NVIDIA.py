import numpy as np
import pandas as pd
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Setting up the visualization style
sns.set (style="whitegrid")
plt.rcParams["font.family"] = 'sans-serif'
plt.rcParams["font.sans-serif"] = ["Arial"]

#color palette
# Using NVIDIA's official green and AMD's official red
nvidia_color = "#76B900"
amd_color = "#ED1C24"
palette = {"NVIDIA": nvidia_color, "AMD": amd_color}

#Ticker symbols and inintal variables
nvidia = yf.Ticker("NVDA")
amd = yf.Ticker("AMD")

#find quarterly fin data
nvidia_financials = nvidia.quarterly_financials
amd_financials = amd.quarterly_financials

# Isolating just the revenue line from the financial statements
nvidia_revenue = nvidia_financials.loc['Total Revenue']
amd_revenue = amd_financials.loc['Total Revenue']

#make into df for visualisation
nvidia_revenue_df = pd.DataFrame(nvidia_revenue).reset_index()
nvidia_revenue_df.columns = ['Date', 'Revenue']
nvidia_revenue_df['Company'] = 'NVIDIA'

#make int df for visualization
amd_revenue_df = pd.DataFrame(amd_revenue).reset_index()
amd_revenue_df.columns = ['Date', 'Revenue']
amd_revenue_df['Company'] = 'AMD'

# Combining both companies' data into a single df for easier comparison
combo = pd.concat([nvidia_revenue_df,amd_revenue_df])
combo['Date'] = pd.to_datetime(combo['Date'])

#sort by date
combo = combo.sort_values('Date')

# Taking only the last 20 quarters
# Using .copy() to avoid the SettingWithCopyWarning
nvidia_20 = nvidia_revenue_df.tail(20).copy()
amd_20 = amd_revenue_df.tail(20).copy()

#identifiers for each date-company pair to avoid duplicate date issues
# This solves the problem with Seaborn's lineplot when both companies share dates
nvidia_20['Date_Company'] = nvidia_20['Date'].astype(str) + "_NVIDIA"
amd_20['Date_Company'] = amd_20['Date'].astype(str) + "_AMD"

# Combine the dataframes and set the unique identifiers as the index
combo_20 = pd.concat([nvidia_20, amd_20])
combo_20 = combo_20.sort_values('Date')

#revenue in billions for better looks
combo_20['Revenue (Billions)'] = combo_20['Revenue']

#get P/E
nvidia_pe = nvidia.info.get('trailingPE', None)
amd_pe = amd.info.get('trailingPE', None)

#make P/E Df
pe_df = pd.DataFrame({
    'Company': ['NVIDIA', 'AMD'],
    'P/E Ratio': [nvidia_pe, amd_pe]
})

def Billions_format(x, pos):
    return f'${x:.1f}B'

#make fig with subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14,12), height_ratios=[2,1])

# PLOT 1: Quarterly Revenue Comparison

# Split the data by company for separate plotting
nvidia_data = combo_20[combo_20['Company'] == 'NVIDIA']
amd_data = combo_20[combo_20['Company'] == 'AMD']

# Plot each company separately
ax1.plot(nvidia_data['Date'], nvidia_data['Revenue (Billions)'],
         color=nvidia_color, marker='o', markersize=8, linewidth=3, label='NVIDIA')
ax1.plot(amd_data['Date'], amd_data['Revenue (Billions)'],
         color=amd_color, marker='o', markersize=8, linewidth=3, label='AMD')

#enhance q rev plot
ax1.set_title('Quarterly Revenue: NVIDIA vs AMD', fontsize=20, fontweight='bold', pad=20)
ax1.set_xlabel('Quarter', fontsize=14, fontweight='bold')
ax1.set_ylabel('Revenue (Billions)', fontsize=14, fontweight='bold')
ax1.yaxis.set_major_formatter(FuncFormatter(Billions_format))
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.tick_params(axis='both',labelsize=12)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

#plot P/E
sns.barplot(
    data=pe_df,
    x='Company',
    y='P/E Ratio',
    palette=palette,
    ax=ax2
)

#enhance
ax2.set_title('P/E Ratio Comparison', fontsize=20, fontweight='bold', pad=20)
ax2.set_xlabel('Company', fontsize=14, fontweight='bold')
ax2.set_ylabel('P/E Ratio', fontsize=14, fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.tick_params(axis='both',labelsize=12)

#add P/E val ontop of bars
for i, v in enumerate(pe_df['P/E Ratio']):
    if v is not None:
        ax2.text(i, v+2, f"{v:.2f}", ha='center', fontsize=14, fontweight='bold')
    else:
        ax2.text(i, 0, "Data Unavailable", ha='center', fontsize=12)

#adj layout
plt.tight_layout()
plt.subplots_adjust(hspace=0.3)

#Add watermark
fig.text(0.5, 0.01, 'Source: Yahoo Finance | Generated with Matplotlib & Seaborn',
         ha='center', fontsize=10, style='italic', alpha=0.7)

plt.show()