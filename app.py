import streamlit as st
import pandas as pd
import hashlib
import os
import plotly.express as px

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    else:
        return pd.DataFrame(columns=["username", "password"])

def save_user(username, password):
    users = load_users()
    hashed_pw = hash_password(password)

    new_user = pd.DataFrame([[username, hashed_pw]], columns=["username", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv("users.csv", index=False)

#authentication function
def authenticate(username, password):
    users = load_users()
    hashed_pw = hash_password(password)

    user = users[
        (users["username"] == username) &
        (users["password"] == hashed_pw)
    ]

    return not user.empty

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"


# Signup Page
def signup():
    st.title("ScoutPro Analytics Sign Up")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        users = load_users()

        if new_user in users["username"].values:
            st.error("Username already exists")
        else:
            save_user(new_user, new_pass)
            st.success("Account created! You can now Login!.")
            st.session_state.page = "login"

    if st.button("Go to Login"):
        st.session_state.page = "login"


# Login Page
def login():
    st.title("ScoutPro Analytics Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {username}")
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Create Account"):
        st.session_state.page = "signup"


# Logout function
def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()


if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login()
    else:
        signup()
    st.stop()

#Sidebar info 
st.sidebar.success(f"Logged in as: {st.session_state.username}")
logout()

# Page configuration
st.set_page_config(page_title="ScoutPro Analytics Dashboard", layout="wide")


# Page Title
st.title("ScoutPro Dashboard")

# Sidebar
st.sidebar.header("Filters")

# load data from CSV
@st.cache_data
def load_data():
    df = pd.read_csv('scout_dataset.csv')
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
    col1, col2, col3, col4, col5 = st.columns(5)
    
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

    with col5:
        totaltransfer_value = filtered_df['Transfer_Value'].sum()
        st.metric("Total Transfer Value", str(totaltransfer_value))
    
    st.markdown("---")

    # Charts section
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Top Performers", "Statistics", 'Player Analysis', 'League Analysis', "Player List", "Search Player"])
    
    with tab1:
        st.subheader("Top Performers")
        col1, col2 = st.columns(2)
        
        with col1:
            # Top scorers bar chart
            st.markdown("#### Top 10 Scorers")
            top_scorers = filtered_df.nlargest(10, 'Goals')[['Name', 'Goals', 'Position', 'Club', 'Age']]
            
            fig1 = px.bar(
                top_scorers, 
                x='Name', 
                y='Goals',
                color='Goals',
                hover_data=['Position', 'Club', 'Age'],
                title="Top Goal Scorers",
                color_continuous_scale='Reds'
            )
            fig1.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Top assists bar chart
            st.markdown("#### Top 10 Assist Providers")
            top_assists = filtered_df.nlargest(10, 'Assists')[['Name', 'Assists', 'Position', 'Club', 'Age']]
            
            fig2 = px.bar(
                top_assists, 
                x='Name', 
                y='Assists',
                color='Assists',
                hover_data=['Position', 'Club', 'Age'],
                title="Top Assist Providers",
                color_continuous_scale='Blues',
                text='Assists'
            )
            fig2.update_layout(xaxis_tickangle=-45, showlegend=False)
            fig2.update_traces(textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)
       
        with col1:
            st.markdown("#### Top 10 Dribblers")
            top_dribblers = filtered_df.nlargest(10, 'Dribbles')[['Name', 'Dribbles', 'Position', 'Club', 'Age']]
            fig_dribble = px.bar(
                top_dribblers,
                x='Name',
                y='Dribbles',
                color='Dribbles',
                hover_data=['Position', 'Club','Age'],
                title="Top Dribblers",
                color_continuous_scale='Purples'
            )
            fig_dribble.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_dribble, use_container_width=True)

        with col2:
            st.markdown("#### Top 10 Tacklers")
            top_tacklers = filtered_df.nlargest(10, 'Tck_Won')[['Name', 'Tck_Won', 'Position', 'Club', 'Age']]
            fig_tackle = px.bar(
                top_tacklers,
                x='Name',
                y='Tck_Won',
                color='Tck_Won',
                hover_data=['Position', 'Club', 'Age'],
                title="Top Tacklers",
                color_continuous_scale='Greens'
            )
            fig_tackle.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_tackle, use_container_width=True)

        with col1:
            # Most appearances chart
            st.markdown("#### Most Appearances")
            top_apps = filtered_df.nlargest(10, 'Apps')[['Name', 'Apps', 'Position', 'Club', 'Age']]
            fig3 = px.bar(
                top_apps, 
                y='Name',  
                x='Apps',  
                orientation='h',  
                color='Apps',
                hover_data=['Position', 'Club', 'Age'],
                title="Most Game Time",
                color_continuous_scale='Oranges',
                text='Apps'
            )
            fig3.update_layout(
                yaxis={'categoryorder': 'total ascending'},  # Sort by value
                showlegend=False,
                height=400
            )
            fig3.update_traces(textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            # Goals per appearance ratio
            st.markdown("#### Goals Per Game (Min 5 Apps)")
            filtered_df['Goals_Per_Game'] = filtered_df['Goals'] / filtered_df['Apps']
            qualified = filtered_df[filtered_df['Apps'] >= 5].nlargest(15, 'Goals_Per_Game')
            
            fig4_ratio = px.bar(
                qualified,
                x='Name',
                y='Goals_Per_Game',
                color='Goals_Per_Game',
                hover_data=['Goals', 'Apps', 'Position', 'Club'],
                title='Most Clinical Finishers',
                color_continuous_scale='Reds'
            )
            fig4_ratio.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig4_ratio, use_container_width=True)


        with col1:
             # Position distribution pie chart
             st.markdown("#### Players by Position")
             position_counts = filtered_df['Position'].value_counts()
             fig5 = px.pie(
                 values=position_counts.values,
                 names=position_counts.index,
                 title="Position Distribution",
                 hole=0.4
            )
             st.plotly_chart(fig5, use_container_width=True)

        with col2:
            # League distribution bar chart
            st.markdown("#### Players by League")
            league_counts = filtered_df['League'].value_counts()
            fig6 = px.bar(
                x=league_counts.index,
                y=league_counts.values,
                labels={'x': 'League', 'y': 'Number of Players'},
                title="Players per League",
                color=league_counts.values,
                color_continuous_scale='Sunset'
            )
            fig6.update_layout(xaxis_tickangle=-50)
            st.plotly_chart(fig6, use_container_width=True)





    with tab2:
        st.subheader("Statistical Analysis")
        col1, col2 = st.columns(2)
            
        with col1:
            fig7 = px.scatter(
                filtered_df,
                x='Goals',
                y='Assists',
                color='Position',
                size='Apps',
                hover_data=['Name', 'Club', 'Age'],
                title="Player Performance: Goals vs Assists"
            )
            st.plotly_chart(fig7, use_container_width=True)

        with col2:
            # Age distribution histogram
            st.markdown("#### Age Distribution")
            
            fig8 = px.histogram(
                filtered_df,
                x='Age',
                nbins=20,
                title="Player Age Distribution",
                color_discrete_sequence=["#2D486A"]
            )
            st.plotly_chart(fig8, use_container_width=True)

        with col1:
            # Dribbling stats
            st.markdown("#### Best Dribblers")
            top_dribblers = filtered_df.nlargest(10, 'Dribbles')[['Name', 'Dribbles', 'Position', 'Club', 'Age']]
            
            fig9 = px.bar(
                top_dribblers,
                x='Name',
                y='Dribbles',
                color='Dribbles',
                hover_data=['Position', 'Club', 'Age'],
                title="Dribbling Leaders",
                color_continuous_scale='Plasma',
                text='Dribbles'
            )
            fig9.update_layout(xaxis_tickangle=-45, showlegend=False)
            fig9.update_traces(textposition='outside')
            st.plotly_chart(fig9, use_container_width=True)


        with col2:
            # Tackles Stats
            st.markdown("#### Defensive Leaders (Tackles Won)")
            top_tacklers = filtered_df.nlargest(10, 'Tck_Won')[['Name', 'Tck_Won', 'Position', 'Club']]

            fig10 = px.scatter(
                top_tacklers,
                x='Tck_Won',
                y='Name',
                size='Tck_Won',
                color='Position',
                hover_data=['Club'],
                title="Top Tacklers Overview"
            )
            fig10.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig10, use_container_width=True)


        with col1:
            # Key Passes Stats
            st.markdown("#### Creative Players (Key Passes)")
            top_creators = filtered_df.nlargest(10, 'Key_Passes')[['Name', 'Key_Passes', 'Assists', 'Position', 'Club']]
            
            fig11 = px.bar(
                top_creators,
                x='Name',
                y='Key_Passes',
                color='Assists',
                hover_data=['Position', 'Club'],
                title="Most Creative Players",
                color_continuous_scale='Teal',
                text='Key_Passes'
            )
            fig11.update_layout(xaxis_tickangle=-45, showlegend=False)
            fig11.update_traces(textposition='outside')
            st.plotly_chart(fig11, use_container_width=True)

            with col2:
                st.markdown("#### Key Passes vs Assists")
                
                fig_creativity = px.scatter(
                    filtered_df,
                    x='Key_Passes',
                    y='Assists',
                    color='Position',
                    size='Apps',
                    hover_data=['Name', 'Club'],
                    title="Creativity Analysis"
                )
                st.plotly_chart(fig_creativity, use_container_width=True)

            with col1:
                st.markdown("#### Transfer Value vs Goals")
                
                fig_value_goals = px.scatter(
                    filtered_df,
                    x='Transfer_Value',
                    y='Goals',
                    color='Position',
                    size='Apps',
                    hover_data=['Name', 'Club', 'Age'],
                    title="Transfer Value vs Goal Output"
                    )
                
                st.plotly_chart(fig_value_goals, use_container_width=True)

    




    with tab3:
        # Player analysis
        st.subheader("Player Analysis")
        col1, col2 = st.columns(2)
            
        with col1:
            st.markdown("Players by Position")
            position_counts = filtered_df['Position'].value_counts()
            
            fig12 = px.pie(
                values=position_counts.values,
                names=position_counts.index,
                title="Position Distribution",
                hole=0.4,
            )
            fig12.update_traces(textposition='inside', textinfo='label+percent')
            st.plotly_chart(fig12, use_container_width=True)

            
        with col2:
            # League distribution chart
            st.markdown("####  Players by League")
            league_counts = filtered_df['League'].value_counts()
            
            fig13 = px.bar(
                x=league_counts.index,
                y=league_counts.values,
                labels={'x': 'League', 'y': 'Number of Players'},
                title="League Distribution",
                color=league_counts.values,
                color_continuous_scale='fall',
                text=league_counts.values
            )
            fig13.update_layout(xaxis_tickangle=-45, showlegend=False)
            fig13.update_traces(textposition='outside')
            st.plotly_chart(fig13, use_container_width=True)

        with col1:
            # Nationality distribution chart
            st.markdown("#### Top 10 Nationalities")
            nationality_counts = filtered_df['Nationality'].value_counts().head(10)
            
            fig14 = px.bar(
                y=nationality_counts.index,
                x=nationality_counts.values,
                orientation='h',
                labels={'x': 'Number of Players', 'y': 'Nationality'},
                title="Most Represented Nationalities",
                color=nationality_counts.values,
                color_continuous_scale='Rainbow',
                text=nationality_counts.values
            )
            fig14.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            fig14.update_traces(textposition='outside')
            st.plotly_chart(fig14, use_container_width=True)

        with col2:
            # Preferred foot chart
            st.markdown("#### Preferred Foot Distribution")
            foot_counts = filtered_df['Preferred_foot'].value_counts()
            
            fig15 = px.pie(
                values=foot_counts.values,
                names=foot_counts.index,
                title="Foot Preference",
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#95E1D3']
            )
            fig15.update_traces(textposition='inside', textinfo='label+percent+value')
            st.plotly_chart(fig15, use_container_width=True)

        with col1:
            # Age vs Goals scatter plot
            st.markdown("#### Age vs Goals Scored")
            fig16 = px.scatter(
                filtered_df,
                x='Age',
                y='Goals',
                size='Apps',
                color='Position',
                hover_data=['Name', 'Club'],
                title="Performance by Age",
                opacity=0.6
            )
            st.plotly_chart(fig16, use_container_width=True)

        with col2:
            # Clean sheets records chart
            st.markdown("#### Defensive Records (Clean Sheets)")
            defensive_positions = filtered_df[filtered_df['Position'].isin(['GK', 'CB', 'LB', 'RB', 'RWB', 'LWB'])]
            top_defenders = defensive_positions.nlargest(10, 'Clean_sheets')[['Name', 'Clean_sheets', 'Position', 'Club']]
            
            if len(top_defenders) > 0:
                fig17 = px.bar(
                    top_defenders,
                    x='Name',
                    y='Clean_sheets',
                    color='Position',
                    hover_data=['Club'],
                    title="Most Clean Sheets (Defenders/GK)",
                    text='Clean_sheets'
                )
                fig17.update_layout(xaxis_tickangle=-45)
                fig17.update_traces(textposition='outside')
                st.plotly_chart(fig17, use_container_width=True)
            else:
                st.info("No defensive players in filtered results")
                


    with tab4:
        st.subheader("League Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Average age by league
            st.markdown("#### Average Age by League")
            league_age = filtered_df.groupby('League')['Age'].mean().sort_values(ascending=False)
            
            fig18 = px.bar(
                x=league_age.index,
                y=league_age.values,
                labels={'x': 'League', 'y': 'Average Age'},
                title="Player Age Profile by League",
                color=league_age.values,
                color_continuous_scale='Blues',
                text=league_age.values
            )
            fig18.update_layout(xaxis_tickangle=-45, showlegend=False)
            fig18.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            st.plotly_chart(fig18, use_container_width=True)
        

        with col2:
            # Average appearances by league
            st.markdown("#### Average Appearances by League")
            league_apps = filtered_df.groupby('League')['Apps'].mean().sort_values(ascending=False)
            
            fig19 = px.bar(
                x=league_apps.index,
                y=league_apps.values,
                labels={'x': 'League', 'y': 'Average Apps'},
                title="Playing Time by League",
                color=league_apps.values,
                color_continuous_scale='Oranges',
                text=league_apps.values
            )
            fig19.update_layout(xaxis_tickangle=-45, showlegend=False)
            fig19.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            st.plotly_chart(fig19, use_container_width=True)
        

        with col1:
            # Average goals
            st.markdown("#### Average Goals by League")
            league_goals = filtered_df.groupby('League')['Goals'].mean().sort_values(ascending=False)
            
            fig20 = px.bar(
                x=league_goals.index,
                y=league_goals.values,
                labels={'x': 'League', 'y': 'Average Goals'},
                title="Goal Scoring by League",
                color=league_goals.values,
                color_continuous_scale='tempo',
                text=league_goals.values
            )
            fig20.update_layout(xaxis_tickangle=-45, showlegend=False)
            fig20.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            st.plotly_chart(fig20, use_container_width=True)

        with col2:
            #League strength analysis
            st.markdown("#### League Strength")
            league_strength = filtered_df.groupby('League')['Goals'].mean().sort_values(ascending=False)
            
            fig_league_strength = px.bar(
                 x=league_strength.index,
                 y=league_strength.values,
                 labels={'x': 'League', 'y': 'Avg Goals'},
                 title="Average Goals per League",
                 color=league_strength.values,
            )
            fig_league_strength.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_league_strength, use_container_width=True)
        

   

    with tab5:
        # Player list
        st.subheader("Player Database")
        display_columns = ['Name', 'Age', 'Position', 'Nationality', 'Club', 'League', 
            'Goals', 'Assists', 'Apps', 'Height', 'Transfer_Value', 'Preferred_foot'
        ]
            
        st.dataframe(
            filtered_df[display_columns].sort_values('Goals', ascending=False),
            use_container_width=True,
            height=600
        )
            
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
        label="Download Filtered Dataset",
        data=csv,
        file_name='filtered_players.csv',
        mime='text/csv',
        )

        # Summary statistics
        st.markdown("### Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Oldest Player", int(filtered_df['Age'].max()))
            st.metric("Youngest Player", int(filtered_df['Age'].min()))
        
        with col2:
            st.metric("Total Clubs", filtered_df['Club'].nunique())
            st.metric("Total Leagues", filtered_df['League'].nunique())



    with tab6:
            
        st.subheader("Search for Specific Player")
        search_name = st.text_input("Enter player name:")
        
        if search_name:
            search_results = filtered_df[
            filtered_df['Name'].str.contains(search_name, case=False, na=False)
        ]
            
            if len(search_results) > 0:
                st.success(f"Found {len(search_results)} player(s)")
                for idx, player in search_results.iterrows():
                    
                    with st.expander(f"{player['Name']} - {player['Position']}"):
                        col1, col2, col3 = st.columns(3)
                            
                        with col1:
                            st.markdown("**Basic Info**")
                            st.write(f"**Age:** {player['Age']}")
                            st.write(f"**Nationality:** {player['Nationality']}")
                            st.write(f"**Position:** {player['Position']}")
                            st.write(f"**Height:** {player['Height']}")
                            st.write(f"**Preferred Foot:** {player['Preferred_foot']}")
                                
                        with col2:
                            st.markdown("**Club Info**")
                            st.write(f"**Club:** {player['Club']}")
                            st.write(f"**League:** {player['League']}")
                            st.write(f"**Apps:** {player['Apps']}")
                            st.write(f"**Starts:** {player['Starts']}")
                            st.write(f"**Mins:** {player['Mins']}")
                                
                        with col3:
                            st.markdown("**Performance**")
                            st.write(f"**Goals:** {player['Goals']}")
                            st.write(f"**Assists:** {player['Assists']}")
                            st.write(f"**Shots:** {player['Shots']}")
                            st.write(f"**Key Passes:** {player['Key_Passes']}")
                            st.write(f"**Dribbles:** {player['Dribbles']}%")
                            st.write(f"**xG:** {player['xG']}%")  
                            st.write(f"**xA:** {player['xA']}%")
                            st.write(f"**Transfer Value:** {player['Transfer_Value']}")
                                
                else:
                    st.warning("No players found with that name")
                    
    st.markdown("#### Best Player per League")
    top_league_players = filtered_df.loc[
        filtered_df.groupby('League')['Goals'].idxmax()
        ]
    st.dataframe(
        top_league_players[['Name', 'League', 'Goals', 'Assists', 'Dribbles', 'Shots','Sprints_90', 'Distance_km','Pens','xG','xA', 'Club']],
        use_container_width=True
        )

         
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Make sure 'scout_dataset.csv' is in the same folder as app.py")
    
   
