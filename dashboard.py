import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="HHS Unaccompanied Alien Children Program Dashboard", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: #05060f;
        color: #F5F7FA;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .stApp::before {
        content: "";
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 55%;
        background:
            radial-gradient(ellipse 80% 50% at 50% 100%, rgba(0, 220, 255, 0.05) 0%, transparent 70%),
            repeating-linear-gradient(0deg, transparent 0px, transparent 29px, rgba(0, 220, 255, 0.08) 29px, rgba(0, 220, 255, 0.08) 30px),
            repeating-linear-gradient(0deg, transparent 0px, transparent 59px, rgba(0, 220, 255, 0.04) 59px, rgba(0, 220, 255, 0.04) 60px),
            repeating-linear-gradient(90deg, transparent 0px, transparent 39px, rgba(0, 220, 255, 0.06) 39px, rgba(0, 220, 255, 0.06) 40px);
        transform: perspective(800px) rotateX(50deg);
        transform-origin: bottom center;
        pointer-events: none;
        z-index: -2;
        -webkit-mask-image: linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 55%);
        mask-image: linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 55%);
    }

    .stApp::after {
        content: "";
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background:
            radial-gradient(ellipse 40% 35% at 50% 100%, rgba(0, 255, 255, 0.04) 0%, transparent 70%),
            linear-gradient(to top, rgba(0, 255, 255, 0.25), transparent 50%),
            linear-gradient(to top, rgba(0, 255, 255, 0.2), transparent 45%),
            linear-gradient(to top, rgba(0, 255, 255, 0.3), transparent 55%),
            linear-gradient(to top, rgba(0, 255, 255, 0.15), transparent 45%),
            linear-gradient(to top, rgba(0, 255, 255, 0.22), transparent 52%);
        background-size: 100% 100%, 2px 45%, 3px 35%, 4px 50%, 2px 40%, 3px 48%;
        background-position: 50% 100%, 20% 0, 35% 0, 50% 0, 65% 0, 80% 0;
        background-repeat: no-repeat;
        opacity: 0.45;
        filter: blur(1.5px);
        pointer-events: none;
        z-index: -2;
        -webkit-mask-image: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 50%);
        mask-image: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 50%);
    }

    .main {
        background: transparent;
        color: #F5F7FA;
    }

    .stMetric {
        background: rgba(10, 12, 22, 0.82);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(0, 220, 255, 0.12);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45), 0 0 20px rgba(0, 220, 255, 0.03);
    }

    .stHeader {
        color: #FFFFFF;
        text-shadow: 0 0 0px transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(10, 12, 22, 0.75);
        border-radius: 8px 8px 0 0;
        color: #CBD5E1;
        padding: 10px 20px;
        border: 1px solid rgba(0, 220, 255, 0.08);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 220, 255, 0.1);
        color: #FFFFFF;
        border-bottom: 2px solid rgba(0, 220, 255, 0.8);
    }

    .stDataFrame {
        background-color: rgba(10, 12, 22, 0.8);
        border-radius: 8px;
        border: 1px solid rgba(0, 220, 255, 0.08);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    h1, h2, h3 {
        color: #FFFFFF;
        text-shadow: 0 0 0px transparent;
    }
    p, li {
        color: #CBD5E1;
    }

    .stPlotlyChart, .stChart, .stMatplotlib {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏠 HHS Unaccompanied Alien Children Program Dashboard")
st.markdown("---")

st.header(" Dataset Description")
st.markdown("""
This dashboard analyzes daily time-series data on the **HHS Unaccompanied Alien Children (UAC) Program** from 2023–2025. 
The dataset tracks the flow of unaccompanied children through the **CBP custody** and **HHS care** systems, including apprehensions, 
transfers, discharges, and care capacity metrics. It is designed to support healthcare staffing, shelter planning, and 
humanitarian response evaluation by translating raw counts into structured capacity insights.
""")

st.markdown("---")

with st.expander(" Column Definitions"):
    col_defs = {
        "Date": "Reporting date",
        "Children apprehended and placed in CBP custody*": "New children entering CBP custody",
        "Children in CBP custody": "Current children held by CBP",
        "Children transferred out of CBP custody": "Children moved from CBP to HHS care",
        "Children in HHS Care": "Children currently in HHS care facilities",
        "Children discharged from HHS Care": "Children released from HHS care"
    }
    st.dataframe(pd.DataFrame(list(col_defs.items()), columns=["Column", "Description"]), use_container_width=True)

st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_csv("HHS_Unaccompanied_Alien_Children_Program.csv")
    for col in df.columns[1:]:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    return df

df = load_data()

st.sidebar.header("Filters")
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
    df_filtered = df[mask].copy()
else:
    df_filtered = df.copy()

st.header(" Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    latest_apprehended = int(df_filtered.iloc[-1]['Children apprehended and placed in CBP custody*']) if len(df_filtered) > 0 else 0
    st.metric("Latest Apprehended", latest_apprehended)

with col2:
    latest_cbp = int(df_filtered.iloc[-1]['Children in CBP custody']) if len(df_filtered) > 0 else 0
    st.metric("Latest in CBP Custody", latest_cbp)

with col3:
    latest_transferred = int(df_filtered.iloc[-1]['Children transferred out of CBP custody']) if len(df_filtered) > 0 else 0
    st.metric("Latest Transferred Out", latest_transferred)

with col4:
    latest_hhs = int(df_filtered.iloc[-1]['Children in HHS Care']) if len(df_filtered) > 0 else 0
    st.metric("Latest in HHS Care", latest_hhs)

with col5:
    latest_discharged = int(df_filtered.iloc[-1]['Children discharged from HHS Care']) if len(df_filtered) > 0 else 0
    st.metric("Latest Discharged", latest_discharged)

st.markdown("---")

st.header(" Time Series Analysis")
tab1, tab2, tab3 = st.tabs(["CBP Metrics", "HHS Care", "All Trends"])

with tab1:
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    axes[0].plot(df_filtered['Date'], df_filtered['Children apprehended and placed in CBP custody*'], marker='o', color='tab:blue')
    axes[0].set_title('Children Apprehended and Placed in CBP Custody')
    axes[0].set_ylabel('Count')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(df_filtered['Date'], df_filtered['Children in CBP custody'], marker='o', color='tab:orange')
    axes[1].set_title('Children in CBP Custody')
    axes[1].set_ylabel('Count')
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(df_filtered['Date'], df_filtered['Children transferred out of CBP custody'], marker='o', color='tab:red')
    axes[2].set_title('Children Transferred Out of CBP Custody')
    axes[2].set_ylabel('Count')
    axes[2].set_xlabel('Date')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with tab2:
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    axes[0].plot(df_filtered['Date'], df_filtered['Children in HHS Care'], marker='o', color='tab:green')
    axes[0].set_title('Children in HHS Care')
    axes[0].set_ylabel('Count')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(df_filtered['Date'], df_filtered['Children discharged from HHS Care'], marker='o', color='tab:purple')
    axes[1].set_title('Children Discharged from HHS Care')
    axes[1].set_ylabel('Count')
    axes[1].set_xlabel('Date')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with tab3:
    fig, ax = plt.subplots(figsize=(14, 6))
    for col in df_filtered.columns[1:]:
        ax.plot(df_filtered['Date'], df_filtered[col], marker='o', label=col, alpha=0.8)
    ax.set_title('All Metrics Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Count')
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

st.header("📦 Daily & Cumulative Care Load")

df_cum = df_filtered.copy()
df_cum['Cumulative_Apprehended'] = df_cum['Children apprehended and placed in CBP custody*'].cumsum()
df_cum['Cumulative_Transferred'] = df_cum['Children transferred out of CBP custody'].cumsum()
df_cum['Cumulative_HHS_Admissions'] = df_cum['Children transferred out of CBP custody'].cumsum()
df_cum['Cumulative_Discharged'] = df_cum['Children discharged from HHS Care'].cumsum()
df_cum['Cumulative_CBP_Custody'] = df_cum['Children in CBP custody'].cumsum()
df_cum['Cumulative_HHS_Care'] = df_cum['Children in HHS Care'].cumsum()
df_cum['Total_Cumulative_System_Load'] = df_cum['Cumulative_CBP_Custody'] + df_cum['Cumulative_HHS_Care']

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Apprehended (Cumulative)", int(df_cum['Cumulative_Apprehended'].iloc[-1]) if len(df_cum) > 0 else 0)
with col2:
    st.metric("Total Transferred to HHS (Cumulative)", int(df_cum['Cumulative_Transferred'].iloc[-1]) if len(df_cum) > 0 else 0)
with col3:
    st.metric("Total Discharged (Cumulative)", int(df_cum['Cumulative_Discharged'].iloc[-1]) if len(df_cum) > 0 else 0)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

axes[0, 0].plot(df_cum['Date'], df_cum['Children in CBP custody'], marker='o', color='tab:blue', alpha=0.7, label='Daily')
axes[0, 0].plot(df_cum['Date'], df_cum['Cumulative_CBP_Custody'], color='tab:blue', linewidth=2, linestyle='--', label='Cumulative')
axes[0, 0].set_title('CBP Custody: Daily vs Cumulative')
axes[0, 0].set_ylabel('Count')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].plot(df_cum['Date'], df_cum['Children in HHS Care'], marker='o', color='tab:green', alpha=0.7, label='Daily')
axes[0, 1].plot(df_cum['Date'], df_cum['Cumulative_HHS_Care'], color='tab:green', linewidth=2, linestyle='--', label='Cumulative')
axes[0, 1].set_title('HHS Care: Daily vs Cumulative')
axes[0, 1].set_ylabel('Count')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].plot(df_cum['Date'], df_cum['Cumulative_Transferred'], color='tab:orange', linewidth=2, label='Cumulative Transfers')
axes[1, 0].plot(df_cum['Date'], df_cum['Cumulative_Discharged'], color='tab:purple', linewidth=2, label='Cumulative Discharges')
axes[1, 0].set_title('Cumulative Flow: Transfers vs Discharges')
axes[1, 0].set_ylabel('Count')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].plot(df_cum['Date'], df_cum['Total_Cumulative_System_Load'], color='tab:red', linewidth=2)
axes[1, 1].set_title('Total Cumulative System Load (CBP + HHS)')
axes[1, 1].set_ylabel('Count')
axes[1, 1].set_xlabel('Date')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.subheader(" Daily-to-Cumulative Load Ratios")
df_cum['CBP_Daily_to_Cum'] = df_cum['Children in CBP custody'] / df_cum['Cumulative_CBP_Custody'].replace(0, np.nan)
df_cum['HHS_Daily_to_Cum'] = df_cum['Children in HHS Care'] / df_cum['Cumulative_HHS_Care'].replace(0, np.nan)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df_cum['Date'], df_cum['CBP_Daily_to_Cum'], marker='o', color='tab:blue', alpha=0.7, label='CBP Daily/Cumulative')
ax.plot(df_cum['Date'], df_cum['HHS_Daily_to_Cum'], marker='s', color='tab:green', alpha=0.7, label='HHS Daily/Cumulative')
ax.set_title('Daily to Cumulative Load Ratio')
ax.set_ylabel('Ratio')
ax.set_xlabel('Date')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

st.header("⚖️ Capacity Strain & Relief Periods")

df_strain = df_filtered.copy()
df_strain['Total_System_Load'] = df_strain['Children in CBP custody'] + df_strain['Children in HHS Care']
df_strain['Strain_Index'] = df_strain['Total_System_Load'] / df_strain['Total_System_Load'].rolling(window=14, min_periods=1).mean()
df_strain['Relief_Index'] = 1 / df_strain['Strain_Index'].replace(0, np.nan)

strain_threshold = 1.2
relief_threshold = 0.85

df_strain['Strain_Period'] = df_strain['Strain_Index'] > strain_threshold
df_strain['Relief_Period'] = df_strain['Strain_Index'] < relief_threshold

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Latest Total System Load", int(df_strain.iloc[-1]['Total_System_Load']) if len(df_strain) > 0 else 0)
with col2:
    st.metric("Latest Strain Index", f"{df_strain.iloc[-1]['Strain_Index']:.2f}" if len(df_strain) > 0 else "N/A")
with col3:
    st.metric("Strain Days (>1.2x avg)", int(df_strain['Strain_Period'].sum()))
with col4:
    st.metric("Relief Days (<0.85x avg)", int(df_strain['Relief_Period'].sum()))

fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

axes[0].plot(df_strain['Date'], df_strain['Total_System_Load'], marker='o', color='tab:red', alpha=0.6, label='Total System Load')
axes[0].plot(df_strain['Date'], df_strain['Total_System_Load'].rolling(window=14, min_periods=1).mean(), color='tab:blue', linewidth=2, label='14-Day Moving Avg')
axes[0].set_title('Total System Load with 14-Day Moving Average')
axes[0].set_ylabel('Count')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(df_strain['Date'], df_strain['Strain_Index'], marker='o', color='tab:orange', alpha=0.7)
axes[1].axhline(strain_threshold, color='red', linestyle='--', alpha=0.7, label=f'Strain Threshold ({strain_threshold})')
axes[1].axhline(relief_threshold, color='green', linestyle='--', alpha=0.7, label=f'Relief Threshold ({relief_threshold})')
axes[1].axhline(1.0, color='black', linestyle='-', alpha=0.3)
axes[1].set_title('Strain Index (Daily Load / 14-Day Avg)')
axes[1].set_ylabel('Index')
axes[1].set_xlabel('Date')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close()

strain_dates = df_strain[df_strain['Strain_Period']]['Date'].tolist()
relief_dates = df_strain[df_strain['Relief_Period']]['Date'].tolist()

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"🔴 Strain Periods ({len(strain_dates)} days)")
    if strain_dates:
        st.dataframe(pd.DataFrame({'Date': strain_dates}).reset_index(drop=True))
    else:
        st.info("No strain periods detected.")
with col2:
    st.subheader(f"🟢 Relief Periods ({len(relief_dates)} days)")
    if relief_dates:
        st.dataframe(pd.DataFrame({'Date': relief_dates}).reset_index(drop=True))
    else:
        st.info("No relief periods detected.")

st.markdown("---")

st.header("🔗 Intake, Transfer & Discharge Balance")

df_balance = df_filtered.copy()
df_balance['CBP_Balance'] = df_balance['Children in CBP custody'] - df_balance['Children transferred out of CBP custody']
df_balance['HHS_Balance'] = df_balance['Children in HHS Care'] - df_balance['Children discharged from HHS Care']
df_balance['System_Balance'] = df_balance['CBP_Balance'] + df_balance['HHS_Balance']

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("CBP Net Balance", int(df_balance['CBP_Balance'].sum()))
with col2:
    st.metric("HHS Net Balance", int(df_balance['HHS_Balance'].sum()))
with col3:
    st.metric("System Net Balance", int(df_balance['System_Balance'].sum()))

fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

axes[0].bar(df_balance['Date'], df_balance['CBP_Balance'], color='tab:blue', alpha=0.7)
axes[0].axhline(0, color='black', linestyle='-', linewidth=0.8)
axes[0].set_title('CBP Daily Balance (In Custody - Transferred Out)')
axes[0].set_ylabel('Net Count')
axes[0].grid(True, alpha=0.3, axis='y')

axes[1].bar(df_balance['Date'], df_balance['HHS_Balance'], color='tab:green', alpha=0.7)
axes[1].axhline(0, color='black', linestyle='-', linewidth=0.8)
axes[1].set_title('HHS Daily Balance (In Care - Discharged)')
axes[1].set_ylabel('Net Count')
axes[1].grid(True, alpha=0.3, axis='y')

axes[2].bar(df_balance['Date'], df_balance['System_Balance'], color='tab:purple', alpha=0.7)
axes[2].axhline(0, color='black', linestyle='-', linewidth=0.8)
axes[2].set_title('System-Wide Daily Balance (CBP + HHS)')
axes[2].set_ylabel('Net Count')
axes[2].set_xlabel('Date')
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
st.pyplot(fig)
plt.close()

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df_balance['Date'], df_balance['CBP_Balance'].cumsum(), color='tab:blue', linewidth=2, label='CBP Cumulative Balance')
ax.plot(df_balance['Date'], df_balance['HHS_Balance'].cumsum(), color='tab:green', linewidth=2, label='HHS Cumulative Balance')
ax.plot(df_balance['Date'], df_balance['System_Balance'].cumsum(), color='tab:red', linewidth=2, label='System Cumulative Balance')
ax.axhline(0, color='black', linestyle='--', alpha=0.5)
ax.set_title('Cumulative Balance Over Time')
ax.set_ylabel('Cumulative Net Count')
ax.set_xlabel('Date')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

st.header("🏥 Healthcare Staffing & Shelter Planning Insights")

df_plan = df_filtered.copy()
df_plan['HHS_7d_MA'] = df_plan['Children in HHS Care'].rolling(window=7, min_periods=1).mean()
df_plan['HHS_14d_MA'] = df_plan['Children in HHS Care'].rolling(window=14, min_periods=1).mean()
df_plan['Projected_7d'] = df_plan['HHS_7d_MA']
df_plan['Projected_14d'] = df_plan['HHS_14d_MA']

capacity_threshold = df_plan['Children in HHS Care'].quantile(0.85)
df_plan['Capacity_Warning'] = df_plan['Children in HHS Care'] > capacity_threshold

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Latest HHS Care Count", int(df_plan.iloc[-1]['Children in HHS Care']) if len(df_plan) > 0 else 0)
with col2:
    st.metric("7-Day Projection", f"{df_plan.iloc[-1]['Projected_7d']:.1f}" if len(df_plan) > 0 else "N/A")
with col3:
    st.metric("14-Day Projection", f"{df_plan.iloc[-1]['Projected_14d']:.1f}" if len(df_plan) > 0 else "N/A")
with col4:
    st.metric("85th Percentile Threshold", f"{capacity_threshold:.0f}")

fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

axes[0].plot(df_plan['Date'], df_plan['Children in HHS Care'], marker='o', color='tab:green', alpha=0.5, label='Daily HHS Care')
axes[0].plot(df_plan['Date'], df_plan['HHS_7d_MA'], color='tab:blue', linewidth=2, label='7-Day MA')
axes[0].plot(df_plan['Date'], df_plan['HHS_14d_MA'], color='tab:orange', linewidth=2, label='14-Day MA')
axes[0].axhline(capacity_threshold, color='red', linestyle='--', alpha=0.7, label=f'85th Percentile ({capacity_threshold:.0f})')
axes[0].set_title('HHS Care Load with Projections')
axes[0].set_ylabel('Count')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

warning_days = df_plan[df_plan['Capacity_Warning']]
axes[1].plot(df_plan['Date'], df_plan['Children in HHS Care'], marker='o', color='tab:green', alpha=0.5, label='Daily HHS Care')
axes[1].axhline(capacity_threshold, color='red', linestyle='--', alpha=0.7, label='Capacity Warning Threshold')
axes[1].scatter(warning_days['Date'], warning_days['Children in HHS Care'], color='red', s=50, zorder=5, label='Above Threshold')
axes[1].set_title('Capacity Warning Days')
axes[1].set_ylabel('Count')
axes[1].set_xlabel('Date')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.subheader(" Planning Summary")
planning_summary = {
    'Metric': [
        'Peak HHS Care Count',
        'Average HHS Care Count',
        'Days Above 85th Percentile',
        'Avg 7-Day Projection',
        'Avg 14-Day Projection',
        'Max CBP Custody Count',
        'Avg CBP Custody Count',
        'Max Daily Transfers',
        'Avg Daily Transfers',
        'Max Daily Discharges',
        'Avg Daily Discharges'
    ],
    'Value': [
        int(df_plan['Children in HHS Care'].max()),
        f"{df_plan['Children in HHS Care'].mean():.1f}",
        int(df_plan['Capacity_Warning'].sum()),
        f"{df_plan['Projected_7d'].mean():.1f}",
        f"{df_plan['Projected_14d'].mean():.1f}",
        int(df_plan['Children in CBP custody'].max()),
        f"{df_plan['Children in CBP custody'].mean():.1f}",
        int(df_plan['Children transferred out of CBP custody'].max()),
        f"{df_plan['Children transferred out of CBP custody'].mean():.1f}",
        int(df_plan['Children discharged from HHS Care'].max()),
        f"{df_plan['Children discharged from HHS Care'].mean():.1f}"
    ],
    'Planning Implication': [
        'Maximum shelter capacity required',
        'Baseline staffing and resource level',
        'Days requiring surge capacity',
        'Short-term staffing forecast',
        'Medium-term resource planning',
        'Maximum CBP holding capacity needed',
        'Baseline CBP operational level',
        'Maximum daily transfer throughput',
        'Average daily transfer throughput',
        'Maximum daily discharge capacity',
        'Average daily discharge throughput'
    ]
}
st.dataframe(pd.DataFrame(planning_summary), use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Daily Counts")
    avg_counts = df_filtered.iloc[:, 1:].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(avg_counts.index, avg_counts.values, color=['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c', '#9467bd'])
    ax.set_xlabel('Average Count')
    ax.set_title('Average Daily Counts by Category')
    for bar, val in zip(bars, avg_counts.values):
        ax.text(val + max(avg_counts.values)*0.01, bar.get_y() + bar.get_height()/2, f'{val:.1f}', va='center', fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("Total Counts Over Selected Period")
    total_counts = df_filtered.iloc[:, 1:].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(total_counts.index, total_counts.values, color=['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c', '#9467bd'])
    ax.set_xlabel('Total Count')
    ax.set_title('Total Counts by Category (Selected Period)')
    for bar, val in zip(bars, total_counts.values):
        ax.text(val + max(total_counts.values)*0.01, bar.get_y() + bar.get_height()/2, f'{int(val)}', va='center', fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

st.header("📋 Statistical Summary")
st.dataframe(df_filtered.iloc[:, 1:].describe().round(2).reset_index().rename(columns={'index': 'Statistic'}))

st.markdown("---")

st.header(" Policy-Aligned Healthcare Analytics Framework")
st.markdown("""
This section translates raw operational counts into **structured capacity insights** aligned with federal child care service delivery mandates. 
It empowers stakeholders to evaluate system performance, identify resource gaps, and ensure compliance with care standards.
""")

df_policy = df_filtered.copy()

df_policy['Capacity_Utilization_CBP'] = (df_policy['Children in CBP custody'] / 
                                         (df_policy['Children in CBP custody'] + df_policy['Children transferred out of CBP custody']).replace(0, np.nan) * 100)
df_policy['Capacity_Utilization_HHS'] = (df_policy['Children in HHS Care'] / 
                                         (df_policy['Children in HHS Care'] + df_policy['Children discharged from HHS Care']).replace(0, np.nan) * 100)

df_policy['System_Throughput'] = df_policy['Children transferred out of CBP custody'] + df_policy['Children discharged from HHS Care']
df_policy['Net_System_Flow'] = df_policy['Children apprehended and placed in CBP custody*'] - df_policy['Children discharged from HHS Care']

df_policy['Care_Efficiency_Ratio'] = df_policy['Children discharged from HHS Care'] / df_policy['Children in HHS Care'].replace(0, np.nan)

df_policy['CBP_Processing_Load'] = df_policy['Children in CBP custody'] / df_policy['Children apprehended and placed in CBP custody*'].replace(0, np.nan)
df_policy['HHS_Placement_Load'] = df_policy['Children transferred out of CBP custody'] / df_policy['Children in HHS Care'].replace(0, np.nan)

st.subheader("📊 System Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    latest_util_cbp = df_policy.iloc[-1]['Capacity_Utilization_CBP']
    st.metric("CBP Capacity Utilization", f"{latest_util_cbp:.1f}%" if pd.notna(latest_util_cbp) else "N/A")

with col2:
    latest_util_hhs = df_policy.iloc[-1]['Capacity_Utilization_HHS']
    st.metric("HHS Capacity Utilization", f"{latest_util_hhs:.1f}%" if pd.notna(latest_util_hhs) else "N/A")

with col3:
    latest_throughput = int(df_policy.iloc[-1]['System_Throughput']) if len(df_policy) > 0 else 0
    st.metric("System Throughput", latest_throughput)

with col4:
    latest_efficiency = df_policy.iloc[-1]['Care_Efficiency_Ratio']
    st.metric("Care Efficiency Ratio", f"{latest_efficiency:.2f}" if pd.notna(latest_efficiency) else "N/A")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

axes[0, 0].plot(df_policy['Date'], df_policy['Capacity_Utilization_CBP'], marker='o', color='tab:blue', alpha=0.7)
axes[0, 0].axhline(80, color='red', linestyle='--', alpha=0.5, label='High Utilization (80%)')
axes[0, 0].set_title('CBP Custody Capacity Utilization (%)')
axes[0, 0].set_ylabel('Utilization %')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].plot(df_policy['Date'], df_policy['Capacity_Utilization_HHS'], marker='o', color='tab:green', alpha=0.7)
axes[0, 1].axhline(80, color='red', linestyle='--', alpha=0.5, label='High Utilization (80%)')
axes[0, 1].set_title('HHS Care Capacity Utilization (%)')
axes[0, 1].set_ylabel('Utilization %')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].plot(df_policy['Date'], df_policy['System_Throughput'], marker='o', color='tab:orange', alpha=0.7)
axes[1, 0].set_title('System Throughput (Transfers + Discharges)')
axes[1, 0].set_ylabel('Count')
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].plot(df_policy['Date'], df_policy['Care_Efficiency_Ratio'], marker='o', color='tab:purple', alpha=0.7)
axes[1, 1].axhline(1.0, color='red', linestyle='--', alpha=0.5, label='Break-even (1.0)')
axes[1, 1].set_title('Care Efficiency Ratio (Discharges / In Care)')
axes[1, 1].set_ylabel('Ratio')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.subheader("📈 Resource Allocation & Flow Analysis")

tab_flow1, tab_flow2 = st.tabs(["Net System Flow", "Processing Load Trends"])

with tab_flow1:
    fig, ax = plt.subplots(figsize=(14, 6))
    colors = ['green' if x >= 0 else 'red' for x in df_policy['Net_System_Flow']]
    ax.bar(df_policy['Date'], df_policy['Net_System_Flow'], color=colors, alpha=0.7)
    ax.axhline(0, color='black', linestyle='-', linewidth=0.8)
    ax.set_title('Net System Flow (Apprehensions - Discharges)')
    ax.set_ylabel('Net Count')
    ax.set_xlabel('Date')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    positive_days = (df_policy['Net_System_Flow'] > 0).sum()
    negative_days = (df_policy['Net_System_Flow'] < 0).sum()
    neutral_days = (df_policy['Net_System_Flow'] == 0).sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Surplus Days (Net > 0)", positive_days)
    col2.metric("Deficit Days (Net < 0)", negative_days)
    col3.metric("Balanced Days (Net = 0)", neutral_days)

with tab_flow2:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df_policy['Date'], df_policy['CBP_Processing_Load'], marker='o', color='tab:blue', label='CBP Processing Load', alpha=0.8)
    ax.plot(df_policy['Date'], df_policy['HHS_Placement_Load'], marker='s', color='tab:green', label='HHS Placement Load', alpha=0.8)
    ax.set_title('Processing Load Indicators')
    ax.set_ylabel('Ratio')
    ax.set_xlabel('Date')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.subheader("📋 Policy Compliance Summary")

compliance_data = {
    'Metric': [
        'Avg CBP Capacity Utilization',
        'Avg HHS Capacity Utilization',
        'Avg System Throughput',
        'Avg Care Efficiency Ratio',
        'Total Surplus Days',
        'Total Deficit Days',
        'High Utilization Days (CBP >80%)',
        'High Utilization Days (HHS >80%)'
    ],
    'Value': [
        f"{df_policy['Capacity_Utilization_CBP'].mean():.1f}%",
        f"{df_policy['Capacity_Utilization_HHS'].mean():.1f}%",
        f"{df_policy['System_Throughput'].mean():.1f}",
        f"{df_policy['Care_Efficiency_Ratio'].mean():.2f}",
        int((df_policy['Net_System_Flow'] > 0).sum()),
        int((df_policy['Net_System_Flow'] < 0).sum()),
        int((df_policy['Capacity_Utilization_CBP'] > 80).sum()),
        int((df_policy['Capacity_Utilization_HHS'] > 80).sum())
    ],
    'Policy Interpretation': [
        'Moderate to high CBP facility usage',
        'Moderate to high HHS facility usage',
        'Average daily children processed through system',
        'Ratio >1.0 indicates net discharges exceeding current care load',
        'Days where incoming > outgoing (system growing)',
        'Days where outgoing > incoming (system shrinking)',
        'Days exceeding recommended utilization threshold',
        'Days exceeding recommended utilization threshold'
    ]
}

st.dataframe(pd.DataFrame(compliance_data), use_container_width=True)

st.markdown("---")

st.header("🔍 Raw Data Preview")
st.dataframe(df_filtered.tail(100))

st.markdown("---")

st.header("🛡️ Data Quality & Validation")

full_dates = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='D')
missing_dates = full_dates.difference(df['Date'])
dup_count = df['Date'].duplicated().sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Records", len(df))
with col2:
    st.metric("Missing Dates", len(missing_dates))
with col3:
    st.metric("Duplicate Dates", int(dup_count))

if len(missing_dates) > 0:
    st.warning(f"Missing dates detected: {missing_dates.strftime('%Y-%m-%d').tolist()}")
else:
    st.success("No missing dates found in the dataset.")

if dup_count > 0:
    st.warning(f"Duplicate dates detected: {dup_count} duplicate(s).")
else:
    st.success("No duplicate dates found.")

st.subheader("Logical Constraint Validation")
df_valid = df_filtered.copy()
df_valid['Transfer_Check'] = df_valid['Children transferred out of CBP custody'] <= df_valid['Children in CBP custody']
df_valid['Discharge_Check'] = df_valid['Children discharged from HHS Care'] <= df_valid['Children in HHS Care']

transfer_violations = df_valid[~df_valid['Transfer_Check']]
discharge_violations = df_valid[~df_valid['Discharge_Check']]

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Transfers ≤ CBP Custody violations:** {len(transfer_violations)}")
    if len(transfer_violations) > 0:
        st.dataframe(transfer_violations[['Date', 'Children transferred out of CBP custody', 'Children in CBP custody']])
with col2:
    st.write(f"**Discharges ≤ HHS Care violations:** {len(discharge_violations)}")
    if len(discharge_violations) > 0:
        st.dataframe(discharge_violations[['Date', 'Children discharged from HHS Care', 'Children in HHS Care']])

if len(transfer_violations) == 0 and len(discharge_violations) == 0:
    st.success("All logical constraints satisfied.")

st.markdown("---")

st.header("🏥 Derived Healthcare Capacity Metrics")

df_metrics = df_filtered.copy()
df_metrics['Total System Load'] = df_metrics['Children in CBP custody'] + df_metrics['Children in HHS Care']
df_metrics['Net Daily Intake'] = df_metrics['Children transferred out of CBP custody'] - df_metrics['Children discharged from HHS Care']
df_metrics['Care Load Growth Rate (%)'] = df_metrics['Children in HHS Care'].pct_change() * 100
df_metrics['Backlog Indicator'] = (df_metrics['Net Daily Intake'] > 0).astype(int)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Latest Total System Load", int(df_metrics.iloc[-1]['Total System Load']) if len(df_metrics) > 0 else 0)
with col2:
    st.metric("Latest Net Daily Intake", int(df_metrics.iloc[-1]['Net Daily Intake']) if len(df_metrics) > 0 else 0)
with col3:
    latest_growth = df_metrics.iloc[-1]['Care Load Growth Rate (%)']
    st.metric("Latest Care Load Growth", f"{latest_growth:.2f}%" if pd.notna(latest_growth) else "N/A")
with col4:
    backlog_days = int(df_metrics['Backlog Indicator'].sum())
    st.metric("Backlog Days (Net Intake > 0)", backlog_days)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

axes[0, 0].plot(df_metrics['Date'], df_metrics['Total System Load'], marker='o', color='tab:blue')
axes[0, 0].set_title('Total System Load (CBP + HHS)')
axes[0, 0].set_ylabel('Count')
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].plot(df_metrics['Date'], df_metrics['Net Daily Intake'], marker='o', color='tab:orange')
axes[0, 1].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[0, 1].set_title('Net Daily Intake (Transfers - Discharges)')
axes[0, 1].set_ylabel('Count')
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].plot(df_metrics['Date'], df_metrics['Care Load Growth Rate (%)'], marker='o', color='tab:green')
axes[1, 0].axhline(0, color='red', linestyle='--', alpha=0.5)
axes[1, 0].set_title('Care Load Growth Rate (%)')
axes[1, 0].set_ylabel('Percentage')
axes[1, 0].set_xlabel('Date')
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].plot(df_metrics['Date'], df_metrics['Backlog Indicator'], marker='o', color='tab:red', linestyle='-', linewidth=2)
axes[1, 1].set_title('Backlog Indicator (1 = Positive Net Intake)')
axes[1, 1].set_ylabel('Indicator')
axes[1, 1].set_xlabel('Date')
axes[1, 1].set_yticks([0, 1])
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

st.header("📈 Trend & Temporal Analysis")

tab_trend1, tab_trend2, tab_trend3 = st.tabs(["Daily/Weekly/Monthly Trends", "High-Load Periods", "Calendar Period Comparison"])

with tab_trend1:
    df_trend = df_filtered.copy()
    df_trend['Week'] = df_trend['Date'].dt.to_period('W').dt.start_time
    df_trend['Month'] = df_trend['Date'].dt.to_period('M').dt.start_time
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=False)
    
    daily_hhs = df_trend.groupby('Date')['Children in HHS Care'].mean()
    axes[0].plot(daily_hhs.index, daily_hhs.values, marker='o', color='tab:green', alpha=0.7)
    axes[0].set_title('Daily HHS Care Load')
    axes[0].set_ylabel('Average Count')
    axes[0].grid(True, alpha=0.3)
    
    weekly_hhs = df_trend.groupby('Week')['Children in HHS Care'].mean()
    axes[1].plot(weekly_hhs.index, weekly_hhs.values, marker='o', color='tab:blue', linewidth=2)
    axes[1].set_title('Weekly Average HHS Care Load')
    axes[1].set_ylabel('Average Count')
    axes[1].grid(True, alpha=0.3)
    
    monthly_hhs = df_trend.groupby('Month')['Children in HHS Care'].mean()
    axes[2].plot(monthly_hhs.index, monthly_hhs.values, marker='o', color='tab:red', linewidth=2)
    axes[2].set_title('Monthly Average HHS Care Load')
    axes[2].set_ylabel('Average Count')
    axes[2].set_xlabel('Date')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with tab_trend2:
    df_high = df_filtered.copy()
    hhs_threshold = df_high['Children in HHS Care'].quantile(0.9)
    high_load_days = df_high[df_high['Children in HHS Care'] >= hhs_threshold]
    
    st.subheader(f"Sustained High-Load Periods (Top 10% threshold: {hhs_threshold:.0f} children)")
    if len(high_load_days) > 0:
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(df_high['Date'], df_high['Children in HHS Care'], marker='o', color='tab:green', alpha=0.5, label='Daily HHS Care')
        ax.axhline(hhs_threshold, color='red', linestyle='--', label=f'90th Percentile ({hhs_threshold:.0f})')
        ax.scatter(high_load_days['Date'], high_load_days['Children in HHS Care'], color='red', s=50, zorder=5, label='High Load Days')
        ax.set_title('High-Load Periods in HHS Care')
        ax.set_ylabel('Children in HHS Care')
        ax.set_xlabel('Date')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.write(f"**High-load days identified:** {len(high_load_days)}")
        st.dataframe(high_load_days[['Date', 'Children in HHS Care', 'Children in CBP custody']].reset_index(drop=True))
    else:
        st.info("No high-load days identified.")

with tab_trend3:
    df_compare = df_filtered.copy()
    df_compare['Year'] = df_compare['Date'].dt.year
    df_compare['Half'] = df_compare['Date'].dt.month.apply(lambda x: 'H1' if x <= 6 else 'H2')
    
    yearly_avg = df_compare.groupby('Year')['Children in HHS Care'].mean().reset_index()
    halfyear_avg = df_compare.groupby(['Year', 'Half'])['Children in HHS Care'].mean().reset_index()
    halfyear_avg['Period'] = halfyear_avg['Year'].astype(str) + ' ' + halfyear_avg['Half']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].bar(yearly_avg['Year'].astype(str), yearly_avg['Children in HHS Care'], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    axes[0].set_title('Average HHS Care by Year')
    axes[0].set_ylabel('Average Count')
    axes[0].grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(yearly_avg['Children in HHS Care']):
        axes[0].text(i, v + max(yearly_avg['Children in HHS Care'])*0.01, f'{v:.1f}', ha='center', fontsize=10)
    
    axes[1].bar(halfyear_avg['Period'], halfyear_avg['Children in HHS Care'], color=['#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22'])
    axes[1].set_title('Average HHS Care by Half-Year')
    axes[1].set_ylabel('Average Count')
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].tick_params(axis='x', rotation=45)
    for i, v in enumerate(halfyear_avg['Children in HHS Care']):
        axes[1].text(i, v + max(halfyear_avg['Children in HHS Care'])*0.01, f'{v:.1f}', ha='center', fontsize=9)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

st.header("Pressure & Stress Identification")

df_stress = df_filtered.copy()
df_stress['HHS_7d_MA'] = df_stress['Children in HHS Care'].rolling(window=7, min_periods=1).mean()
df_stress['HHS_14d_MA'] = df_stress['Children in HHS Care'].rolling(window=14, min_periods=1).mean()
df_stress['HHS_7d_std'] = df_stress['Children in HHS Care'].rolling(window=7, min_periods=1).std()
df_stress['Coefficient_of_Variation'] = df_stress['HHS_7d_std'] / df_stress['HHS_7d_MA']
df_stress['Strain_Window'] = (df_stress['Children in HHS Care'] > df_stress['HHS_14d_MA']).astype(int)
prolonged_strain = df_stress['Strain_Window'].rolling(window=7, min_periods=1).sum() >= 5

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Latest 7-Day MA (HHS)", f"{df_stress.iloc[-1]['HHS_7d_MA']:.1f}" if len(df_stress) > 0 else "N/A")
with col2:
    st.metric("Latest 14-Day MA (HHS)", f"{df_stress.iloc[-1]['HHS_14d_MA']:.1f}" if len(df_stress) > 0 else "N/A")
with col3:
    st.metric("Prolonged Strain Days", int(prolonged_strain.sum()))

fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

axes[0].plot(df_stress['Date'], df_stress['Children in HHS Care'], marker='o', color='tab:green', alpha=0.5, label='Daily HHS Care')
axes[0].plot(df_stress['Date'], df_stress['HHS_7d_MA'], color='tab:blue', linewidth=2, label='7-Day Moving Avg')
axes[0].plot(df_stress['Date'], df_stress['HHS_14d_MA'], color='tab:red', linewidth=2, label='14-Day Moving Avg')
axes[0].set_title('HHS Care Load with Rolling Averages')
axes[0].set_ylabel('Count')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(df_stress['Date'], df_stress['Coefficient_of_Variation'], marker='o', color='tab:purple', alpha=0.7)
axes[1].axhline(0.1, color='orange', linestyle='--', alpha=0.5, label='Low Variability Threshold')
axes[1].axhline(0.3, color='red', linestyle='--', alpha=0.5, label='High Variability Threshold')
axes[1].set_title('Variability Analysis (7-Day CV)')
axes[1].set_ylabel('Coefficient of Variation')
axes[1].set_xlabel('Date')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.subheader("Prolonged Strain Windows")
strain_dates = df_stress[prolonged_strain]['Date'].tolist()
if len(strain_dates) > 0:
    st.write(f"Detected **{len(strain_dates)}** days of prolonged strain (5+ of last 7 days above 14-day MA).")
    st.dataframe(pd.DataFrame({'Date': strain_dates}).reset_index(drop=True))
else:
    st.success("No prolonged strain windows detected in the selected period.")

st.markdown("---")

st.markdown("""
<style>
    .footer {
        margin-top: 60px;
        padding: 30px 40px;
        background: rgba(10, 12, 22, 0.85);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(0, 220, 255, 0.12);
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 220, 255, 0.03);
    }
    .footer-title {
        color: #22D3EE;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .footer-text {
        color: #CBD5E1;
        font-size: 14px;
        line-height: 1.6;
    }
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 18px;
    }
    .footer-item {
        padding: 12px;
        background: rgba(5, 6, 15, 0.6);
        border: 1px solid rgba(0, 220, 255, 0.08);
        border-radius: 8px;
    }
    .footer-item-label {
        color: #22D3EE;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .footer-item-value {
        color: #F5F7FA;
        font-size: 13px;
        line-height: 1.5;
    }
    .footer-bottom {
        margin-top: 18px;
        padding-top: 14px;
        border-top: 1px solid rgba(0, 220, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #CBD5E1;
        font-size: 12px;
    }
    .footer-tag {
        color: #22D3EE;
        font-weight: 600;
    }
    @media (max-width: 768px) {
        .footer-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <div class="footer-title">🏛️ UAC Care Analytics Platform</div>
    <div class="footer-text">
        A policy-aligned healthcare analytics framework for monitoring the Unaccompanied Children Program.
        This dashboard transforms raw operational data into structured capacity insights, supporting data-driven
        decision-making for federal child care service delivery.
    </div>
    <div class="footer-grid">
        <div class="footer-item">
            <div class="footer-item-label">Mission</div>
            <div class="footer-item-value">Improve situational awareness and humanitarian response evaluation through quantitative care load analysis.</div>
        </div>
        <div class="footer-item">
            <div class="footer-item-label">Use Cases</div>
            <div class="footer-item-value">Healthcare staffing · Shelter planning · Capacity strain detection · Policy compliance review.</div>
        </div>
        <div class="footer-item">
            <div class="footer-item-label">Data Source</div>
            <div class="footer-item-value">HHS Unaccompanied Alien Children Program · Daily operational reporting 2023–2025.</div>
        </div>
    </div>
    <div class="footer-bottom">
        <span>Built with <span class="footer-tag">Streamlit</span> · Powered by <span class="footer-tag">Python</span> · Visualized with <span class="footer-tag">Matplotlib</span></span>
        <span>© 2025 UAC Care Analytics · All insights derived from public operational data</span>
    </div>
</div>
""", unsafe_allow_html=True)

