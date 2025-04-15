# Tactical RPG – D&D Campaign Conversion

This is a personal project to convert a custom Dungeons & Dragons campaign into a tactical RPG. The goal is to make the world and story more accessible outside of traditional tabletop sessions, and to give players a way to experience the campaign on their own.

![Aeloria Chronicles Banner](https://i.imgur.com/cPiu7S1.png)

## Project Goals

- Build a turn-based tactical RPG similar to Final Fantasy Tactics
- Use a grid-based movement and combat system
- Allow players to control a party of characters through missions tied to a larger narrative
- Capture the tone and structure of a tabletop D&D campaign in a playable game format

## What the Game Will Include

- A party system with allies and enemies taking turns
- Grid-based maps where movement and positioning matter
- A branching story with scripted missions and narrative progression
- Character stats, leveling, and abilities (based on D&D mechanics)
- Encounters adapted directly from sessions in the original campaign

## Setup

To get the game running locally:

1. Make sure you're using **Python 3.13.2**
   - You can download it from [python.org](https://www.python.org/downloads/release/python-3132/)
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Once everything’s installed, run the game with:

```bash
python game.py
```

## Why This Exists

This is meant to be a playable version of a homebrew campaign setting, so others can experience it without needing to be at the table. It also makes it easier to revisit the story or try out different decisions without relying on memory or group availability.

## Current Status

Got some backend stats, some basic gameplay, init, combat UI.  Next is to get "scenes" or "stages" created so I can start the story somewhere, move it along, and create some kind of save state.  Then I can make a main menu, and it's dialogue dialogue dialogue while I work on finding a tileset and way to represent it on a semi-topdown way.  Not sure how I'm gonna do that yet.

This is a work in progress in the most literal sense of the phrase.
