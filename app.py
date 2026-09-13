import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud

# Load dataset
df = pd.read_csv("social_media_analytics_dataset.csv")

# =========================
# Step 1: Data Cleaning
# =========================

# Handle missing values
for col in ["Likes", "Comments", "Shares", "Reach", "Followers"]:
    df[col] = df[col].fillna(df[col].median())

# Standardize PostDate
df["PostDate"] = pd.to_datetime(df["PostDate"], errors="coerce")

# Remove duplicates
df = df.drop_duplicates()

# =========================
# Step 2: Engagement Analysis
# =========================

# Total & average engagement
df["Engagement"] = df["Likes"] + df["Comments"] + df["Shares"]
total_engagement = df["Engagement"].sum()
avg_engagement = df["Engagement"].mean()

# Top 10 posts by engagement
top_posts = df.nlargest(10, "Engagement")

# Trend analysis
engagement_trend = df.groupby(df["PostDate"].dt.to_period("M"))["Engagement"].sum()

# =========================
# Step 3: Audience Insights
# =========================

# Peak posting time
df["Hour"] = df["PostDate"].dt.hour
peak_time = df.groupby("Hour")["Engagement"].mean()

# Engagement by content type
content_type_perf = df.groupby("ContentType")["Engagement"].mean().sort_values(ascending=False)

# Hashtag analysis
all_hashtags = ", ".join(df["Hashtags"].astype(str).tolist())
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_hashtags)

# =========================
# Step 4: Growth & Influencer Metrics
# =========================

# Engagement rate
df["EngagementRate"] = (df["Engagement"] / df["Followers"]) * 100

# Follower growth
follower_growth = df.groupby(df["PostDate"].dt.to_period("M"))["Followers"].mean()

# Influencer posts
influencer_posts = df.nlargest(5, "EngagementRate")

# =========================
# Step 5: Dashboard (Streamlit)
# =========================

def dashboard():
    st.set_page_config(page_title="📊 Social Media Analytics Dashboard", layout="wide")
    st.title("📊 Social Media Analytics Dashboard")
    st.markdown("---")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        platform_filter = st.multiselect("Select Platform", options=df["Platform"].unique(), default=df["Platform"].unique())
    with col2:
        content_filter = st.multiselect("Select Content Type", options=df["ContentType"].unique(), default=df["ContentType"].unique())
    
    filtered_df = df[(df["Platform"].isin(platform_filter)) & (df["ContentType"].isin(content_filter))]

    # =========================
    # Overall Engagement Metrics
    # =========================
    st.subheader("📌 Overall Engagement")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Engagement", f"{filtered_df['Engagement'].sum():,}")
    with col2:
        st.metric("Average Engagement", f"{filtered_df['Engagement'].mean():.2f}")
    st.markdown("---")

    # =========================
    # Charts Section
    # =========================
    st.subheader("📈 Engagement Trends & Performance")

    col1, col2 = st.columns(2)
    with col1:
        trend_data = filtered_df.groupby(filtered_df["PostDate"].dt.to_period("M"))["Engagement"].sum().reset_index()
        trend_data["PostDate"] = trend_data["PostDate"].astype(str)
        fig1 = px.line(trend_data, x="PostDate", y="Engagement", title="Engagement Trend Over Time")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        follower_data = filtered_df.groupby(filtered_df["PostDate"].dt.to_period("M"))["Followers"].mean().reset_index()
        follower_data["PostDate"] = follower_data["PostDate"].astype(str)
        fig2 = px.line(follower_data, x="PostDate", y="Followers", title="Average Followers Growth")
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig3 = px.bar(top_posts, x="PostID", y="Engagement", color="Platform", title="Top 10 Posts by Engagement")
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        fig4 = px.bar(content_type_perf.reset_index(), x="ContentType", y="Engagement", title="Content Type Performance")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # =========================
    # Hashtags & Influencers
    # =========================
    st.subheader("📌 Hashtags & Influencer Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.image(wordcloud.to_array(), caption="WordCloud of Hashtags", use_container_width=True)
    with col2:
        st.write("### Influencer Posts (Top by Engagement Rate)")
        st.dataframe(influencer_posts[["PostID", "Platform", "EngagementRate"]].reset_index(drop=True))

    st.markdown("---")

    # Export option
    st.download_button(
        "⬇️ Download Filtered Data as CSV", 
        data=filtered_df.to_csv(index=False), 
        file_name="filtered_data.csv", 
        mime="text/csv"
    )

if __name__ == "__main__":
    dashboard()
