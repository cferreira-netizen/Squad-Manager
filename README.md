# ⚽ Squad Manager

A data-driven soccer team management web app built with Python and Streamlit.

## Description

Squad Manager lets you build and maintain a soccer team roster, track player fitness and availability, pick starting lineups with an AI-powered recommender, log match results, and view season statistics — all in one interactive dashboard.

## Features

- **Squad roster** — add, edit, and remove players with position, fitness, and availability tracking
- **Lineup picker** — select your starting XI and substitutes from available players
- **"Who should start?" recommender** — ranks players by recent form (goals, assists, wins) and fitness
- **Match log** — record opponents, scores, scorers, and assists for each game
- **Season stats** — points table, W/D/L summary, goals, and per-player stats (apps, goals, assists)
- **Save/load** — all data persists across restarts via local JSON files

## How to run

```bash
# Install dependencies
pip install streamlit pandas

# Run development version
streamlit run src/main.py

# Run production version (graded)
streamlit run dist/main.py
```

## File structure

```
squad-manager/
├── README.md           
├── demo.mp4            
├── src/                 
│   ├── data/
│   │   ├── squad.json      
│   │   └── matches.json    
│   └── main.py         
└── dist/               
    ├── data/
    │   ├── squad.json
    │   └── matches.json
    └── main.py
```

## User instructions

1. Go to the **Squad** tab to add your players (name, position, fitness, availability)
2. Go to **Pick Lineup** to select your starting 11 — use the recommender for suggestions
3. After a match, go to **Log Match** to record the result, scorers, and assisters
4. Check **Season Stats** for a full breakdown of your team's performance

## AI use statement

This project used AI (Claude) to help write and format the README. Claude was also used occasionally to help fix errors in the code. 