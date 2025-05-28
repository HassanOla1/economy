# frontend/app.py
import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# Set page config FIRST
st.set_page_config(page_title="Islamic Digital Economy Dashboard", layout="wide")

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")

def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

# Skip backend check for testing
# if not check_backend():
#     st.error("⚠️ Backend service not available. Please check if the backend container is running.")
#     st.stop()

# Sidebar filters
st.sidebar.image("https://via.placeholder.com/200x100?text=Islamic+Economy+Dashboard ")
st.sidebar.markdown("## 🌍 Filters")

# Country selector
try:
    response = requests.get(f"{BACKEND_URL}/query/halal_ecommerce")
    countries = list(set(row["country"] for row in response.json())) if response.status_code == 200 else ["Malaysia", "Indonesia", "Saudi Arabia"]
except:
    countries = ["Malaysia", "Indonesia", "Saudi Arabia"]

selected_countries = st.sidebar.multiselect("Select Countries", options=countries, default=countries)
selected_year = st.sidebar.slider("Select Year", min_value=2015, max_value=2025, value=2020)

# ✅ MAIN TITLE (Now using Streamlit defaults)
st.title("📊 Islamic Digital Economy Dashboard")
st.markdown("Explore trends in halal e-commerce, fintech, and digital economy metrics across Muslim-majority countries")

# Navigation menu
selected = option_menu(
    menu_title=None,
    options=["Halal E-commerce", "ICT & Fintech", "AI Insights", "Data Explorer"],
    icons=["shop", "graph-up-arrow", "robot", "table"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

# Tab: Halal E-commerce
if selected == "Halal E-commerce":
    st.header("🛒 Halal E-commerce Growth")
    rev_response = requests.get(
        f"{BACKEND_URL}/aggregation/halal_ecommerce",
        params={"metric": "revenue_usd", "group_by": "country"}
    )
    if rev_response.status_code == 200:
        rev_data = rev_response.json()
        rev_df = pd.DataFrame(rev_data if isinstance(rev_data, list) else [rev_data])
        if not rev_df.empty:
            fig = px.bar(
                rev_df,
                x="country",
                y="total",
                title="Total Revenue by Country",
                color="country",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig, use_container_width=True)

# Tab: ICT & Fintech
elif selected == "ICT & Fintech":
    col1, col2 = st.columns(2)
    with col1:
        ict_response = requests.get(
            f"{BACKEND_URL}/aggregation/ict_services",
            params={"metric": "gross_output", "group_by": "country"}
        )
        if ict_response.status_code == 200:
            ict_data = ict_response.json()
            ict_df = pd.DataFrame(ict_data if isinstance(ict_data, list) else [ict_data])
            if not ict_df.empty:
                st.markdown("## 📶 ICT Services Output")
                ict_fig = px.area(
                    ict_df,
                    x="country",
                    y="total",
                    title="Gross Output by Country",
                    color="country",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                st.plotly_chart(ict_fig, use_container_width=True)
    with col2:
        penetration_response = requests.get(f"{BACKEND_URL}/query/internet_penetration")
        if penetration_response.status_code == 200:
            penetration_data = penetration_response.json()
            penetration_df = pd.DataFrame(penetration_data if isinstance(penetration_data, list) else [penetration_data])
            if not penetration_df.empty:
                penetration_df["internet_penetration"] = penetration_df["internet_penetration"].str.replace("%", "").astype(float)
                penetration_fig = px.bar(
                    penetration_df,
                    x="country",
                    y="internet_penetration",
                    title="Internet Penetration Rate",
                    color="country",
                    range_y=[0, 100],
                    color_discrete_sequence=px.colors.qualitative.Set1
                )
                st.plotly_chart(penetration_fig, use_container_width=True)

# Tab: AI Insights
elif selected == "AI Insights":
    st.header("🤖 AI-Powered Analysis")
    user_query = st.text_input("Ask a question about the data")
    if st.button("Get AI Analysis") and user_query.strip():
        ai_response = requests.post(f"{BACKEND_URL}/ai_query", json={"question": user_query})
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            st.markdown("### 🤖 AI Analysis")
            st.markdown(ai_data.get("answer", "No answer returned."))
            if "result" in ai_data:
                ai_df = pd.DataFrame(ai_data["result"])
                st.markdown("### 📊 Query Results")
                st.dataframe(ai_df)
        else:
            st.error(f"AI Query Failed: {ai_response.text}")

# Tab: Data Explorer
elif selected == "Data Explorer":
    st.header("🔍 Explore Raw Data")
    data_type = st.selectbox("Select Dataset", ["halal_ecommerce", "ict_services", "internet_penetration", "islamic_fintech"])
    filter_country = st.multiselect("Filter by Country", options=countries, default=countries)
    data_response = requests.get(f"{BACKEND_URL}/query/{data_type}", params={"countries": filter_country})
    if data_response.status_code == 200:
        raw_data = data_response.json()
        df = pd.DataFrame(raw_data if isinstance(raw_data, list) else [raw_data])
        st.dataframe(df)
    else:
        st.warning("No data available for this selection.")

# Summary metrics
st.markdown("## 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    response = requests.get(f"{BACKEND_URL}/summary/halal_ecommerce")
    data = response.json() if response.status_code == 200 else {"count": 0, "avg_growth_rate": 0}
    st.metric("Total Halal Revenue", f"${data.get('count', 0) * 1_000_000:,.0f} USD")

with col2:
    response = requests.get(f"{BACKEND_URL}/summary/islamic_fintech")
    data = response.json() if response.status_code == 200 else {"count": 0}
    st.metric("Total Fintech Transactions", f"${data.get('count', 0) * 1_000_000:,.0f} USD")

with col3:
    response = requests.get(f"{BACKEND_URL}/summary/ict_services")
    data = response.json() if response.status_code == 200 else {"count": 0}
    st.metric("Total ICT Output", f"${data.get('count', 0) * 1_000_000:,.0f} USD")

with col4:
    response = requests.get(f"{BACKEND_URL}/summary/household_ict")
    data = response.json() if response.status_code == 200 else {"avg_growth_rate": 75.4}
    st.metric("Average Internet Usage", f"{data.get('avg_growth_rate', 75.4):.1f}%")

# Country profile tool
st.markdown("## 🌏 Country Profile Tool")
country_profile = st.selectbox("Select Country for Detailed Analysis", countries)

if country_profile:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {country_profile} - Halal E-commerce")
        response = requests.get(f"{BACKEND_URL}/query/halal_ecommerce", params={"countries": [country_profile]})
        df = pd.DataFrame(response.json() if response.status_code == 200 else [])
        st.dataframe(df)
    with col2:
        st.markdown(f"### {country_profile} - Fintech")
        fintech_response = requests.get(f"{BACKEND_URL}/query/islamic_fintech", params={"countries": [country_profile]})
        fintech_df = pd.DataFrame(fintech_response.json() if fintech_response.status_code == 200 else [])
        st.dataframe(fintech_df)

# Country comparison
st.markdown("## 🌐 Country-wise Total Comparison Across Sectors")
metrics = {
    "Halal E-commerce": "halal_ecommerce",
    "Islamic Fintech": "islamic_fintech",
    "ICT Services": "ict_services"
}
country_totals = {}

for label, endpoint in metrics.items():
    try:
        response = requests.get(f"{BACKEND_URL}/aggregation/{endpoint}", params={"metric": "count", "group_by": "country"})
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data if isinstance(data, list) else [data])
            for _, row in df.iterrows():
                country = row["country"]
                total = row["total"] * 1_000_000
                if country not in country_totals:
                    country_totals[country] = {}
                country_totals[country][label] = total
    except Exception as e:
        continue

if country_totals:
    comparison_df = pd.DataFrame.from_dict(country_totals, orient="index").fillna(0).reset_index().rename(columns={"index": "Country"})
    melted_df = comparison_df.melt(id_vars="Country", var_name="Sector", value_name="Total (USD)")
    compare_fig = px.bar(
        melted_df,
        x="Country",
        y="Total (USD)",
        color="Sector",
        title="Total Digital Economy Metrics by Country and Sector",
        barmode="group",
        text_auto='.2s',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(compare_fig, use_container_width=True)

# Download section
st.sidebar.markdown("---")
st.sidebar.markdown("## 📥 Download Reports")
available_reports = ["halal_ecommerce", "ict_services", "internet_penetration", "islamic_fintech"]
selected_report = st.sidebar.selectbox("Select report to download", available_reports)

try:
    download_response = requests.get(f"{BACKEND_URL}/download/{selected_report}")
    if download_response.status_code == 200:
        st.sidebar.download_button(
            label="Download CSV",
            data=download_response.content,
            file_name=f"{selected_report}.csv",
            mime="text/csv"
        )
    else:
        st.sidebar.info("Report not available for download.")
except Exception as e:
    st.sidebar.error(f"Error downloading report: {e}")