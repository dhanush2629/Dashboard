# app.py
"""
Data Dashboard (Streamlit)
Features:
- Upload CSV or use sample data
- Animated KPI counters (JS)
- Animated time-series (Plotly) with play/slider
- Animated bar race (Plotly)
- Donut charts (Plotly)
- World map visualization (Plotly scatter_geo)
- Responsive layout (CSS)
- Download filtered data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="expanded")

NEON_BG = "#0b1320"
NEON_FONT = "#ffffff"
NEON_GRID = "rgba(0,209,255,0.14)"
NEON_COLORWAY = ["#00d1ff","#9a6cff","#00ffc6","#ff7c70","#f9e12b","#8de05f"]

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor=NEON_BG,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=NEON_FONT),
        title_font_color=NEON_FONT,
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=NEON_FONT)),
        xaxis=dict(gridcolor=NEON_GRID, tickfont=dict(color=NEON_FONT), title_font=dict(color=NEON_FONT)),
        yaxis=dict(gridcolor=NEON_GRID, tickfont=dict(color=NEON_FONT), title_font=dict(color=NEON_FONT)),
        colorway=NEON_COLORWAY,
    )
    return fig

# -------------------------
# Utility: sample data
# -------------------------
@st.cache_data
def make_sample_data(n_days=240):
    np.random.seed(42)
    start = datetime(2024, 1, 1)
    products = ['Laptop','Phone','Headset','Keyboard','Monitor','Tablet']
    regions = ['North','South','East','West']
    cities = [
        ("New Delhi", 28.6139, 77.2090), ("Mumbai", 19.0760, 72.8777), ("Bengaluru", 12.9716, 77.5946),
        ("Chennai",13.0827,80.2707), ("Kolkata",22.5726,88.3639), ("Hyderabad",17.3850,78.4867),
        ("London",51.5074,-0.1278), ("New York",40.7128,-74.0060), ("San Francisco",37.7749,-122.4194)
    ]
    rows=[]
    for d in range(n_days):
        date = start + timedelta(days=int(d))
        for p in products:
            qty = np.random.poisson(2)
            base_price = {'Laptop':900,'Phone':600,'Headset':80,'Keyboard':70,'Monitor':220,'Tablet':350}[p]
            price = base_price * (1 + np.random.normal(0,0.06))
            sales = max(0, round(qty * price,2))
            city, lat, lon = cities[np.random.randint(0, len(cities))]
            rows.append({
                'order_date': date,
                'product': p,
                'region': np.random.choice(regions, p=[0.3,0.25,0.25,0.2]),
                'quantity': int(qty),
                'unit_price': round(price,2),
                'sales': sales,
                'city': city,
                'latitude': lat + np.random.normal(0,0.02),
                'longitude': lon + np.random.normal(0,0.02)
            })
    df = pd.DataFrame(rows)
    return df

# -------------------------
# Sidebar: data input & filters
# -------------------------
st.sidebar.header("Data")
uploaded = st.sidebar.file_uploader("Upload CSV with columns: order_date, product, region, quantity, unit_price, sales, latitude, longitude (optional)", type=['csv','xlsx'])
use_sample = st.sidebar.checkbox("Use sample data", value=True)

@st.cache_data
def load_data(uploaded_file, use_sample_flag):
    if uploaded_file:
        try:
            if str(uploaded_file).lower().endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")
            return pd.DataFrame()
    elif use_sample_flag:
        df = make_sample_data()
    else:
        df = pd.DataFrame()
    if not df.empty and 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'])
    return df

df = load_data(uploaded, use_sample)
if df.empty:
    st.warning("No data loaded — upload a CSV or enable sample data in the sidebar.")
    st.stop()

# default filters
st.sidebar.markdown("---")
st.sidebar.header("Filters")
min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()
date_range = st.sidebar.date_input("Order date range", [min_date, max_date])
regions = st.sidebar.multiselect("Region", sorted(df['region'].unique()), default=sorted(df['region'].unique()))
products = st.sidebar.multiselect("Product", sorted(df['product'].unique()), default=sorted(df['product'].unique()))

# apply filters
start_dt = pd.to_datetime(date_range[0])
end_dt = pd.to_datetime(date_range[1])
df_filtered = df[
    (df['order_date'] >= start_dt) &
    (df['order_date'] <= end_dt) &
    (df['region'].isin(regions)) &
    (df['product'].isin(products))
].copy()

# -------------------------
# Responsive CSS + KPI animation JS
# -------------------------
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#071a28 0%, #0a0f1f 100%); color:#ffffff; }
section[data-testid="stSidebar"], div[data-testid="stSidebar"], aside[data-testid="stSidebar"] { color:#ffffff !important; background: linear-gradient(180deg,#071a28 0%, #0a0f1f 100%); }
section[data-testid="stSidebar"] *, div[data-testid="stSidebar"] *, aside[data-testid="stSidebar"] * { color:#ffffff !important; }
section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] select, section[data-testid="stSidebar"] textarea { color:#ffffff !important; background-color: rgba(255,255,255,0.05) !important; }
section[data-testid="stSidebar"] input::placeholder, section[data-testid="stSidebar"] textarea::placeholder { color:#e0e0e0 !important; }
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown, .stText { color:#ffffff !important; }
    .grid-2 { display:grid; grid-template-columns: 1fr 1fr; gap:16px; }
    @media (max-width: 760px) { .grid-2 { grid-template-columns: 1fr; } }
    .card { background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); padding:12px; border-radius:10px; box-shadow: 0 10px 30px rgba(2,6,18,0.6); border:1px solid rgba(0,209,255,0.25); }
    .kpi-row { display:flex; gap:12px; flex-wrap:wrap; }
    .kpi { background: rgba(8,20,38,0.45); padding:12px;border-radius:8px; min-width:140px; text-align:center; }
    .kpi .lbl { color:#ffffff !important; font-size:12px; margin-top:6px; }
    .dataframe tbody tr:hover { background: rgba(255,255,255,0.02) !important; }
    .stApp button, section[data-testid="stSidebar"] button, div[data-testid="stSidebar"] button, aside[data-testid="stSidebar"] button { background-color:#0908c3 !important; color:#ffffff !important; border:1px solid #0908c3 !important; }
    [data-testid="stDownloadButton"] > button, div[data-testid="baseButton-secondary"] > button, div[data-testid="baseButton-primary"] > button { background-color:#0908c3 !important; color:#ffffff !important; border-color:#0908c3 !important; }
    .stApp button:hover, .stApp button:focus, .stApp button:active, section[data-testid="stSidebar"] button:hover, section[data-testid="stSidebar"] button:focus, section[data-testid="stSidebar"] button:active { background-color:#07079d !important; border-color:#07079d !important; }
    header[data-testid="stHeader"], div[data-testid="stToolbar"] { background-color:#080738 !important; }
    div[role="menu"], div[role="menu"] * {  color:#ffffff !important; }
    div[role="listbox"], div[role="option"] {  color:#ffffff !important; }
    .modebar 
    .modebar-btn { color:#ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# JS function to animate numbers (runs in an iframe via components.html)
kpi_js = """
<script>
function animateNumber(elId, endVal, duration=1200) {
  const el = document.getElementById(elId);
  if(!el) return;
  const start = 0;
  const range = endVal - start;
  let startTime = null;
  function step(timestamp) {
    if (!startTime) startTime = timestamp;
    const progress = Math.min((timestamp - startTime) / duration, 1);
    const value = Math.floor(progress * range + start);
    el.innerText = value.toLocaleString();
    if (progress < 1) {
      window.requestAnimationFrame(step);
    } else {
      el.innerText = endVal.toLocaleString();
    }
  }
  window.requestAnimationFrame(step);
}
</script>
"""

# -------------------------
# Top: title + Lottie (optional) + KPIs
# -------------------------
st.title("📊 Data Dashboard")

st.components.v1.html(kpi_js, height=0)  # inject JS

# Compute KPIs
total_sales = int(df_filtered['sales'].sum())
total_orders = int(df_filtered.shape[0])
total_qty = int(df_filtered['quantity'].sum())
unique_products = int(df_filtered['product'].nunique())

kpi_html = """
<style>
  .lbl { color:#ffffff !important; }
</style>
<div class="kpi-row">
  <div class="kpi card"><div style="font-size:18px; color:#ffffff; font-weight:700;"><span id='k_sale'>0</span></div><div class='lbl'>Total Sales (USD)</div></div>
  <div class="kpi card"><div style="font-size:18px; color:#ffffff; font-weight:700;"><span id='k_orders'>0</span></div><div class='lbl'>Transactions</div></div>
  <div class="kpi card"><div style="font-size:18px; color:#ffffff; font-weight:700;"><span id='k_qty'>0</span></div><div class='lbl'>Total Quantity</div></div>
  <div class="kpi card"><div style="font-size:18px; color:#ffffff; font-weight:700;"><span id='k_prod'>0</span></div><div class='lbl'>Products</div></div>
</div>

<script>
setTimeout(()=>{ animateNumber('k_sale', %d, 1400); animateNumber('k_orders', %d, 1200); animateNumber('k_qty', %d, 1200); animateNumber('k_prod', %d, 1000); }, 200);
</script>
""" % (total_sales, total_orders, total_qty, unique_products)

st.components.v1.html(kpi_html, height=140)

# -------------------------
# Layout: charts
# -------------------------
# Prepare timeseries
ts = df_filtered.groupby('order_date')['sales'].sum().reset_index().sort_values('order_date')
ts['sales_smooth'] = ts['sales'].rolling(7, min_periods=1).mean()

# Animated timeseries: create frames by month for a "play" feel
ts['month'] = ts['order_date'].dt.to_period('M').dt.to_timestamp()
months = sorted(ts['month'].unique())
fig_ts = px.line(ts, x='order_date', y='sales_smooth', title='Sales (7-day rolling)', template='plotly_dark')
# create frames manually (cumulative)
frames = []
for m in months:
    m_ts = pd.to_datetime(m)
    dframe = ts[ts['month'] <= m_ts]
    frames.append(dict(name=m_ts.strftime('%Y-%m'), data=[dict(x=dframe['order_date'].dt.strftime('%Y-%m-%d'), y=dframe['sales_smooth'])]))
fig_ts.frames = frames
style_fig(fig_ts)
fig_ts.update_layout(
    updatemenus=[dict(type="buttons", showactive=False, y=1.05, x=1.02, xanchor="right",
                      buttons=[dict(label="Play", method="animate",
                                    args=[None, {"frame": {"duration": 300, "redraw": True}, "fromcurrent": True}])])],
    sliders=[dict(steps=[dict(method='animate', args=[[pd.to_datetime(m).strftime('%Y-%m')], {"frame":{"duration":300,"redraw":True}}], label=pd.to_datetime(m).strftime('%Y-%m')) for m in months], active=0)]
)

# Bar race: monthly product sales
prod_month = df_filtered.groupby([df_filtered['order_date'].dt.to_period('M').dt.to_timestamp(), 'product'])['sales'].sum().reset_index()
prod_month.columns = ['month','product','sales']
prod_month = prod_month.sort_values(['month','sales'], ascending=[True, False])
prod_month['month_str'] = prod_month['month'].dt.strftime('%Y-%m')

fig_bar = px.bar(prod_month, x='sales', y='product', color='product', orientation='h',
                 animation_frame='month_str', range_x=[0, prod_month['sales'].max()*1.2],
                 title='Sales by Product (Month-wise)', template='plotly_dark', height=480)
fig_bar.update_layout(showlegend=False)
style_fig(fig_bar)

# Donut charts: product share & region share (current filtered window)
prod_share = df_filtered.groupby('product')['sales'].sum().reset_index()
reg_share = df_filtered.groupby('region')['sales'].sum().reset_index()

fig_donut_prod = px.pie(prod_share, names='product', values='sales', hole=0.55,
                       title='Product Sales Share', template='plotly_dark')
fig_donut_prod.update_traces(textposition='inside', textinfo='percent+label')
style_fig(fig_donut_prod)

fig_donut_reg = px.pie(reg_share, names='region', values='sales', hole=0.55,
                      title='Region Sales Share', template='plotly_dark')
fig_donut_reg.update_traces(textposition='inside', textinfo='percent+label')
style_fig(fig_donut_reg)

# World map: if latitude/longitude available use scatter_geo, else try to aggregate by city then plot by sample coords
has_geo = ('latitude' in df_filtered.columns) and ('longitude' in df_filtered.columns)
if has_geo:
    map_df = df_filtered.groupby(['city','latitude','longitude'])['sales'].sum().reset_index()
    fig_map = px.scatter_geo(map_df, lat='latitude', lon='longitude', size='sales',
                             hover_name='city', projection='natural earth',
                             title='Sales by Location (geo)', template='plotly_dark')
else:
    # fallback: aggregate by city column if available, else by product create fake coords for visualization
    if 'city' in df_filtered.columns:
        # use the mean lat/lon per city if present in data
        if 'latitude' in df_filtered.columns and 'longitude' in df_filtered.columns:
            map_df = df_filtered.groupby(['city'])[['latitude','longitude','sales']].agg({'latitude':'mean','longitude':'mean','sales':'sum'}).reset_index()
            fig_map = px.scatter_geo(map_df, lat='latitude', lon='longitude', size='sales',
                                     hover_name='city', projection='natural earth', title='Sales by Location', template='plotly_dark')
        else:
            # use a small set of known cities with coords for demo
            city_coords = {
                'New Delhi': (28.6139,77.2090), 'Mumbai':(19.0760,72.8777), 'Bengaluru':(12.9716,77.5946),
                'London':(51.5074,-0.1278), 'New York':(40.7128,-74.0060), 'San Francisco':(37.7749,-122.4194)
            }
            agg = df_filtered.groupby('city')['sales'].sum().reset_index()
            agg['latitude'] = agg['city'].map(lambda c: city_coords.get(c, (0,0))[0])
            agg['longitude'] = agg['city'].map(lambda c: city_coords.get(c, (0,0))[1])
            fig_map = px.scatter_geo(agg, lat='latitude', lon='longitude', size='sales', hover_name='city', projection='natural earth', title='Sales by City (approx)', template='plotly_dark')
    else:
        # fallback: product-based geo demo (random coords)
        demo = df_filtered.groupby('product')['sales'].sum().reset_index()
        rng = np.random.RandomState(0)
        demo['latitude'] = rng.uniform(-40,60, size=len(demo))
        demo['longitude'] = rng.uniform(-120,120, size=len(demo))
        fig_map = px.scatter_geo(demo, lat='latitude', lon='longitude', size='sales', hover_name='product', projection='natural earth', title='Demo Geo (no coordinates provided)', template='plotly_dark')

style_fig(fig_map)
# -------------------------
# Render charts in responsive grid
# -------------------------
st.markdown("<div class='grid-2'>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_ts, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Second row: donuts + map
st.markdown("<div class='grid-2' style='margin-top:16px;'>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_donut_prod, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='card' style='margin-top:12px;'>", unsafe_allow_html=True)
    st.plotly_chart(fig_donut_reg, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Data table and download
# -------------------------
st.markdown("---")
st.subheader("Filtered Data")
st.dataframe(df_filtered.sort_values('order_date', ascending=False).reset_index(drop=True))

def to_csv_bytes(df_in):
    return df_in.to_csv(index=False).encode('utf-8')

col1, col2 = st.columns(2)
with col1:
    st.download_button("Download CSV", to_csv_bytes(df_filtered), "filtered_data.csv", "text/csv")
with col2:
    buffer = BytesIO()
    df_filtered.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button("Download Excel", data=buffer, file_name="filtered_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# -------------------------
# Footer
# -------------------------
st.markdown("<hr><div style='opacity:0.6;font-size:12px;'>Built with Streamlit • Plotly • Responsive layout • Animated KPIs</div>", unsafe_allow_html=True)
