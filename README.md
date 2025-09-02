# 2025 FinServ NFL Survivor Pool

Welcome to the **2025 FinServ NFL Survivor Pool**! This is a web application built with **Streamlit** and **Snowflake** that allows users to participate in a weekly NFL survivor pool. Users select one team each week to “survive,” with restrictions based on previous picks and eliminations.

---

## Features

### Player Workflow
- Select your name from a dropdown.  
- The app checks if you’ve been **eliminated** and displays a message if so.  
- Choose a team to pick for the current week from **available teams you haven’t picked yet**.  
- Submit your pick — the app **updates or inserts** your pick in Snowflake.  
- See your **current pick** updated immediately after submission.  

### Rules & Instructions
- Only **one team can be picked per week**. Ties are not considered wins.  
- You **cannot pick the same team twice**.  
- Picks must be submitted **before the first game of each week** (usually Thursday night).  
- If it’s too early or too late to pick, the app displays appropriate messages.  

### Standings
- After the first game of the week has started, users can view a **table of all players’ picks** for the current week.  
- Only **player names and team picks** are shown, maintaining privacy while providing visibility into ongoing picks.  

### App Structure
- **Tabs** separate functionality:
  - **Make a Pick** → select player, choose team, submit pick.  
  - **Standings** → view picks for the current week (only visible after first game).  
  - **Other Info / Rules** → displays rules and instructions.  
- Built with `st.tabs` for a clean user experience.  

---

## Technology Stack

- **Frontend & UI**: [Streamlit](https://streamlit.io)  
- **Backend & Database**: [Snowflake](https://www.snowflake.com)  
- **Python Libraries**:
  - `snowflake-snowpark-python` — query and manipulate Snowflake tables  
  - `pandas` — convert Snowflake results to DataFrames for display  
  - `datetime` — handle date/time comparisons  
  - `streamlit` — interactive web app  

---

## Snowflake Tables

- **PLAYERS** — stores player information (`PLAYER_ID`, `NAME`)  
- **GAMES** — stores NFL games with `GAME_DATE`, `WEEK`, `HOME_TEAM`, `AWAY_TEAM`  
- **PICKS** — stores submitted picks (`PLAYER_ID`, `TEAM`, `WEEK`, `CREATED_AT`, `GAME_ID`)  
- **ELIMINATIONS** — stores eliminated players (`PLAYER_ID`)  

---

## Installation & Deployment

1. Clone the repo:  
```bash
git clone https://github.com/yourusername/nfl-survivor-pool.git
