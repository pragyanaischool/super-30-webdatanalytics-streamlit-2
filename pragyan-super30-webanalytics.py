import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import date, timedelta
from urllib.parse import unquote

# --- Configuration for Simulated NYC Road Traffic Data ---
LAT_MIN, LAT_MAX = 40.70, 40.80
LON_MIN, LON_MAX = -74.02, -73.93

# --- Functions for Simulated Road Traffic Analytics ---

def generate_simulated_traffic_data():
    """Generates a DataFrame of random traffic data for a small area in NYC."""
    lat_vals = np.linspace(LAT_MIN, LAT_MAX, 15)
    lon_vals = np.linspace(LON_MIN, LON_MAX, 15)
    records = []
    for lat in lat_vals:
        for lon in lon_vals:
            records.append({
                "lat": lat,
                "lon": lon,
                "currentSpeed": np.random.uniform(10, 60),
                "freeFlowSpeed": np.random.uniform(40, 70),
                "jamFactor": np.random.uniform(0, 10),
                "confidence": np.random.uniform(0.5, 1)
            })
    return pd.DataFrame(records)

def display_road_traffic_analytics():
    """Displays maps and charts for the simulated road traffic data."""
    st.markdown("## Simulated NYC Road Traffic Analytics")
    st.info("This section displays randomly generated traffic data for a sample area in New York City.")
    
    df = generate_simulated_traffic_data()
    st.dataframe(df.head(10))

    st.markdown("### Traffic Jam Factor Heatmap")
    fig_map = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="jamFactor",
        size="jamFactor",
        size_max=15,
        color_continuous_scale=px.colors.sequential.OrRd,
        hover_name="currentSpeed",
        hover_data={"currentSpeed": True, "freeFlowSpeed": True, "jamFactor": True},
        zoom=12,
        height=500,
        title="Higher 'Jam Factor' indicates worse traffic conditions",
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0, "t":40, "l":0, "b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Traffic Speed Analysis")
        fig_speed = px.line(
            df.sort_values(by="lat"),
            x="lat",
            y=["currentSpeed", "freeFlowSpeed"],
            title="Current Speed vs Free Flow Speed",
            labels={"value": "Speed (km/h)", "lat": "Latitude"}
        )
        st.plotly_chart(fig_speed, use_container_width=True)

    with col2:
        st.markdown("### Jam Factor Distribution")
        fig_jam = px.histogram(
            df,
            x="jamFactor",
            nbins=20,
            title="Distribution of Traffic Jam Factor",
            labels={"jamFactor": "Jam Factor"}
        )
        st.plotly_chart(fig_jam, use_container_width=True)

    avg_speed = df["currentSpeed"].mean()
    avg_free_speed = df["freeFlowSpeed"].mean()
    avg_jam = df["jamFactor"].mean()
    max_jam = df["jamFactor"].max()

    st.markdown("### Aggregate Traffic Insights")
    st.markdown(f"- Average Current Speed: **{avg_speed:.2f} km/h**")
    st.markdown(f"- Average Free Flow Speed: **{avg_free_speed:.2f} km/h**")
    st.markdown(f"- Average Jam Factor: **{avg_jam:.2f}**")
    st.markdown(f"- Maximum Jam Factor: **{max_jam:.2f}**")

# --- Functions for Wikipedia Article Traffic Analytics ---

def fetch_wikipedia_pageviews(article, start_date, end_date):
    headers = {'User-Agent': 'StreamlitApp/1.0 (https://your-app-url.com; your-email@example.com)'}
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    article_formatted = article.replace(' ', '_')
    url = (
        f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia/all-access/user/{article_formatted}/daily/{start_str}/{end_str}"
    )
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            st.error(f"Article '{article}' not found on Wikipedia.")
            return None
        response.raise_for_status()
        data = response.json()
        if 'items' in data:
            df = pd.DataFrame(data['items'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d00')
            df = df.rename(columns={'views': 'pageviews', 'timestamp': 'date'})
            return df[['date', 'pageviews']]
        else:
            return None
    except requests.RequestException as e:
        st.error(f"API request failed: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

def display_wikipedia_analytics():
    st.markdown("## Wikipedia Article Traffic Analytics")
    st.info("Analyze daily pageviews for English Wikipedia articles using the free Wikimedia API.")
    article_input = st.text_input("Enter Wikipedia Article Title or URL", "Streamlit")
    today = date.today()
    last_month = today - timedelta(days=30)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", last_month, max_value=today)
    with col2:
        end_date = st.date_input("End Date", today, max_value=today)

    if st.button("Get Article Analytics"):
        if not article_input:
            st.warning("Please enter an article title or URL.")
            return

        article_title = article_input
        if "en.wikipedia.org/wiki/" in article_input:
            article_title = unquote(article_input.split('/')[-1]).replace('_', ' ')

        if start_date > end_date:
            st.warning("Start date cannot be after end date.")
            return

        with st.spinner(f"Fetching pageviews for '{article_title}'..."):
            views_df = fetch_wikipedia_pageviews(article_title, start_date, end_date)

        if views_df is not None and not views_df.empty:
            st.success(f"Data retrieved for '{article_title}'!")
            total_views = views_df['pageviews'].sum()
            avg_views = views_df['pageviews'].mean()
            max_views_row = views_df.loc[views_df['pageviews'].idxmax()]

            st.markdown("### Key Metrics")
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Pageviews", f"{total_views:,}")
            kpi2.metric("Average Daily Views", f"{avg_views:.0f}")
            kpi3.metric("Peak Views", f"{max_views_row['pageviews']:,}", max_views_row['date'].strftime('%b %d, %Y'))

            st.markdown("### Daily Pageviews Over Time")
            fig = px.line(
                views_df,
                x='date',
                y='pageviews',
                title=f"Daily Traffic for '{article_title}'",
                labels={'pageviews': 'Pageviews', 'date': 'Date'}
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Show Raw Data"):
                st.dataframe(views_df)
        else:
            st.error(f"No data available for '{article_title}'.")

# --- Functions for Website SEO & Traffic Analytics ---

def fetch_website_seo_data(api_key, domain):
    url = "https://api.seoreviewtools.com/website-traffic-v2"
    params = {"key": api_key, "domain": domain}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

def display_website_seo_analytics():
    st.markdown("## Website SEO & Traffic Analytics")
    st.info("Provide a free API key from SEO Review Tools and a website domain to get traffic & SEO info.")

    api_key = st.text_input("API Key", type="password")
    domain = st.text_input("Website Domain (e.g., streamlit.io)")

    if st.button("Get Website Analytics"):
        if not api_key or not domain:
            st.warning("API key and domain are required.")
            return

        with st.spinner(f"Analyzing {domain}..."):
            data = fetch_website_seo_data(api_key, domain)

        if data and data.get('success', False):
            st.success(f"Data retrieved for {domain}!")

            metrics = data.get('data', {})

            st.markdown("### Key Metrics & Engagement")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Global Rank", f"#{metrics.get('global_rank', 'N/A'):,}")
            kpi2.metric("Monthly Visits", f"{metrics.get('visits', 0):,}")
            bounce_rate = metrics.get('bounce_rate')
            kpi3.metric("Bounce Rate", f"{bounce_rate:.1%}" if bounce_rate is not None else "N/A")
            duration = metrics.get('avg_session_duration')
            if duration is not None:
                mins, secs = divmod(int(duration), 60)
                kpi4.metric("Avg. Session", f"{mins}m {secs}s")
            else:
                kpi4.metric("Avg. Session", "N/A")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Traffic by Country")
                country_data = metrics.get('traffic_country', [])
                if country_data:
                    country_df = pd.DataFrame(country_data)
                    fig_map = px.choropleth(
                        country_df,
                        locations="country_code",
                        color="traffic_percentage",
                        hover_name="country_name",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title="Top Countries by Traffic"
                    )
                    st.plotly_chart(fig_map, use_container_width=True)
                else:
                    st.info("No geographic data available.")

            with col2:
                st.markdown("### Traffic by Device")
                device_data = metrics.get('traffic_device_split', {})
                if device_data:
                    device_df = pd.DataFrame(list(device_data.items()), columns=['Device', 'Percentage'])
                    fig_device_pie = px.pie(
                        device_df,
                        values='Percentage',
                        names='Device',
                        title="Traffic Distribution by Device"
                    )
                    st.plotly_chart(fig_device_pie, use_container_width=True)
                else:
                    st.info("No device data available.")

            st.markdown("### Traffic Sources")
            sources_data = metrics.get('traffic_sources', {})
            if sources_data:
                sources_df = pd.DataFrame(list(sources_data.items()), columns=['Source', 'Percentage'])
                fig_sources_pie = px.pie(
                    sources_df,
                    values='Percentage',
                    names='Source',
                    title="Traffic Distribution by Source"
                )
                st.plotly_chart(fig_sources_pie, use_container_width=True)
            else:
                st.info("No traffic source data available.")

            with st.expander("Show Raw API Response"):
                st.json(data)
        elif data:
            st.error(f"API error: {data.get('message','Unknown error')}")
        else:
            st.error("Failed to retrieve data. Check API key and domain.")

# --- Main App ---

st.set_page_config(page_title="Analytics Dashboard", layout="wide")
st.title("Traffic & Website Analytics Dashboard")

st.sidebar.header("Choose Analytics Type")
option = st.sidebar.radio(
    "Select a view:",
    ["Simulated NYC Road Traffic", "Wikipedia Article Traffic", "Website SEO & Traffic"]
)

if option == "Simulated NYC Road Traffic":
    display_road_traffic_analytics()
elif option == "Wikipedia Article Traffic":
    display_wikipedia_analytics()
else:
    display_website_seo_analytics()
