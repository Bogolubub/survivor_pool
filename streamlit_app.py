import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, avg, current_timestamp, min as sf_min
from datetime import datetime
from snowflake.snowpark import Session
import json

def create_session():
    connection_parameters = {
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "password": st.secrets["snowflake"]["password"],
        "role": st.secrets["snowflake"]["role"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"],
    }
    return Session.builder.configs(connection_parameters).create()

session = create_session()
# --- Assume session is already created ---
# Load players into pandas
player_df = session.table("SURVIVOR_POOL.ENTRY_APP.PLAYERS").select(col("NAME"), col("PLAYER_ID")).to_pandas().sort_values(by="NAME")
player_options = ["-- Select a player --"] + player_df["NAME"].tolist()
#load current week
week = session.table("GAMES").select(avg(col("WEEK"))).collect()[0][0]

#is it before the first game still?
earliest_game_df = session.table("GAMES").select(sf_min(col("GAME_DATE")).alias("EARLIEST_GAME")).collect()
earliest_game = earliest_game_df[0]["EARLIEST_GAME"]

#title
st.title("2025 FinServ NFL Survivor Pool")

tab1, tab2, tab3 = st.tabs(["Rules", "Make a Pick", "Standings"])



#tab 1
with tab1:
    st.header("Welcome to the 2025 FinServ Survivor Pool 👋")
    
    st.markdown(
        """
        ### Rules 📜
        Hi, welcome to the **2025 FinServ Survivor Pool**. The rules are simple:

        1. ✅ You must pick **1 team to win each week**.  
           ⚠️ *Ties are not wins!*  

        2. 🚫 You cannot pick the same team twice.  

        3. ⏰ Picks must be submitted **before the first game of each week**.  
           *Typically this is Thursday night.*  

        ---
        Good luck! 🍀
        """
    )


#tab 2
with tab2:
    if datetime.now() > earliest_game:
        st.write("Oops it's too late to pick, contact louie if you think something is wrong.")
    
    else:
        # --- Player selection ---
        selected_name = st.selectbox("Select your name and make your pick!", player_options)
        
        if selected_name != "-- Select a player --":
            selected_id = player_df.loc[player_df["NAME"] == selected_name, "PLAYER_ID"].iloc[0]
        
            is_eliminated = (
            session.table("ELIMINATIONS")
            .filter(col("PLAYER_ID") == selected_id)
            .select(col("PLAYER_ID"))
            .collect()
            )
        
            if is_eliminated:
                st.error(
                    "Sorry, but you've been eliminated and can't make a pick. "
                    "If you think this is an error, contact Louie."
                )
            else:
            
                existing_pick = (
                    session.table("PICKS")
                    .filter((col("PLAYER_ID") == selected_id) & (col("WEEK") == week))
                    .select(col("TEAM"))
                    .collect()
                )
        
                if existing_pick:
                    st.write(f"Your current pick is: {existing_pick[0]['TEAM']}")
            
                # --- Available teams ---
                available_teams_df = (
                    session.table("NFL_TEAMS")
                    .select(col("NFL_TEAM_NAME"))
                    .filter(
                        ~col("NFL_TEAM_NAME").in_(
                            session.table("PICKS")
                            .select(col("TEAM"))
                            .filter(col("PLAYER_ID") == selected_id)
                        )
                    )
                )
                available_teams_pd = available_teams_df.to_pandas()
                available_teams_options = ["-- Select a team --"] + available_teams_pd["NFL_TEAM_NAME"].tolist()
            
                # --- Team selection ---
                selected_team = st.selectbox("Who is going to win this week?", available_teams_options)
            
                if selected_team != "-- Select a team --":
                    st.write("You chose", selected_team)
            
                    if st.button("Submit Pick"):
                        
            
                        # Check if player already has a pick for this week
                        existing_pick = (
                            session.table("PICKS")
                            .filter((col("PLAYER_ID") == selected_id) & (col("WEEK") == week))
                            .select(col("PICK_ID"))
                            .collect()
                        )
            
                        # Get game_id for selected team
                        game_id = (
                            session.table("GAMES")
                            .filter((col("HOME_TEAM") == selected_team) | (col("AWAY_TEAM") == selected_team))
                            .select(col("GAME_ID"))
                            .limit(1)
                            .collect()[0][0]
                        )
            
                        if existing_pick:
                            # Player has already submitted → UPDATE
                            pick_id = existing_pick[0][0]
                            session.sql(
                                f"""
                                UPDATE PICKS
                                SET TEAM = '{selected_team}', GAME_ID = {game_id}, PICK_TIME = CURRENT_TIMESTAMP
                                WHERE PICK_ID = {pick_id}
                                """
                            ).collect()
                            st.success("Your pick was updated successfully!")
                            existing_pick = selected_team
                            
                        else:
                            # Player has not submitted → INSERT
                            pick_id = session.sql("SELECT picks_sequence.nextval").collect()[0][0]
                            session.sql(
                                f"""
                                INSERT INTO PICKS (PICK_ID, PLAYER_ID, WEEK, TEAM, PICK_TIME, GAME_ID)
                                VALUES ({pick_id}, {selected_id}, {week}, '{selected_team}', CURRENT_TIMESTAMP, {game_id})
                                """
                            ).collect()
                            st.success("Your pick was submitted successfully!")


#tab 3
with tab3:
    st.header("This Week's Picks")

    # Get earliest game time for the current week
    earliest_game_df = (
        session.table("GAMES")
        .select(sf_min(col("GAME_DATE")).alias("EARLIEST_GAME"))
        .collect()
    )

    if earliest_game_df:
        earliest_game_time = earliest_game_df[0]["EARLIEST_GAME"]

        # Get current timestamp (UTC by default, adjust if your GAME_DATE is in another TZ)
        current_time = datetime.utcnow()

        if current_time >= earliest_game_time:
            # Show all picks for the current week
            current_week = (
                session.table("GAMES")
                .select(sf_min(col("WEEK")).alias("CURRENT_WEEK"))
                .collect()[0]["CURRENT_WEEK"]
            )

            current_week_df = session.sql(f"""
            SELECT players.name AS Player, picks.team AS Team
            FROM picks
            JOIN players ON picks.player_id = players.player_id
            WHERE picks.week = {current_week}
            """).to_pandas()

            if current_week_df.empty:
                st.write("No picks have been submitted yet this week.")
            else:
                st.dataframe(current_week_df)
        else:
            st.info("⏰ You cannot see other players' picks until the first game of the week has started.")
    else:
        st.warning("No games found in the schedule.")

                            
