import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Football Player Scouting Dashboard", layout="wide")


# Page Title
st.title("Digital Football Scouting Dashboard")

# Sidebar
st.sidebar.header("Filters")

# load data from CSV
@st.cache_data
def load_data():
    df = pd.read_csv('scout_dataset1.csv')
    return df


try:
    df = load_data()
    
    st.sidebar.success(f"Loaded {len(df)} players")
    st.sidebar.subheader("Filter Players")
    
    positions = ["All"] + sorted(df['Position'].dropna().unique().tolist())
    selected_position = st.sidebar.selectbox("Position", positions)

    min_age = int(df['Age'].min())
    max_age = int(df['Age'].max())
    age_range = st.sidebar.slider(
        "Age Range", 
        min_age, 
        max_age, 
        (min_age, max_age)
    )

    leagues = ["All"] + sorted(df['League'].dropna().unique().tolist())
    selected_league = st.sidebar.selectbox("League", leagues)
    
    
    nationalities = ["All"] + sorted(df['Nationality'].dropna().unique().tolist())
    selected_nationality = st.sidebar.selectbox("Nationality", nationalities)
    
    
    clubs = ["All"] + sorted(df['Club'].dropna().unique().tolist())
    selected_club = st.sidebar.selectbox("Club", clubs)
    
    filtered_df = df.copy()

    if selected_position != "All":
        filtered_df = filtered_df[filtered_df['Position'] == selected_position]
    
    filtered_df = filtered_df[
        (filtered_df['Age'] >= age_range[0]) & 
        (filtered_df['Age'] <= age_range[1])
    ]
    
    if selected_league != "All":
          filtered_df = filtered_df[filtered_df['League'] == selected_league]
    
    if selected_nationality != "All":
        filtered_df = filtered_df[filtered_df['Nationality'] == selected_nationality]
    
    if selected_club != "All":
        filtered_df = filtered_df[filtered_df['Club'] == selected_club]

    st.sidebar.markdown("---")
    st.sidebar.info(f"**Showing {len(filtered_df)} players**")

    # Main Dashboard Section
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", len(filtered_df))
    
    with col2:
        avg_age = filtered_df['Age'].mean()
        st.metric("Average Age", f"{avg_age:.1f}")
    
    with col3:
        total_goals = filtered_df['Goals'].sum()
        st.metric("Total Goals", int(total_goals))
    
    with col4:
        total_assists = filtered_df['Assists'].sum()
        st.metric("Total Assists", int(total_assists))
    
    st.markdown("---")

    # Charts section
    tab1, tab2, tab3, tab4 = st.tabs(["Top Performers", "Statistics", "Player List", "Search Player"])
    
    with tab1:
        st.subheader("Top Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top scorers bar chart
            st.markdown("#### Top 10 Scorers")
            top_scorers = filtered_df.nlargest(10, 'Goals')[['Name', 'Goals', 'Position', 'Club']]
            
            fig1 = px.bar(
                top_scorers, 
                x='Name', 
                y='Goals',
                color='Goals',
                hover_data=['Position', 'Club'],
                title="Top Goal Scorers",
                color_continuous_scale='Reds'
            )
            fig1.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)




except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    
   