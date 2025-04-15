# Elarion Tactical RPG
### A D&D Campaign Conversion Effort

This is a personal project to adapt a custom Dungeons & Dragons campaign into a turn-based tactical RPG. The goal is to make the story and world accessible outside the tabletop setting, giving players a way to experience the campaign solo.

![Elarion Chronicles Banner](https://i.imgur.com/htZ7ohK.png)

## Project Goals

- Build a tactical RPG in the style of Final Fantasy Tactics
- Use a grid-based movement and combat system
- Let players control a party through missions tied to a larger narrative
- Capture the tone and pacing of a D&D campaign in a playable format

## Currently Implemented

- Turn-based combat with initiative order and grid movement
- Character stats (STR/DEX/CON/etc) and equipment that affect gameplay
- A working UI for move, attack, item, and end turn actions
- Skills with different categories (attack, magic, support)
- Enemies with basic AI that take actions based on range and logic
- A battle log system that logs rolls, effects, and outcomes

## In Progress / Planned Features

- Scene scripting and dialogue system for narrative delivery
- A save/load system for campaign progress
- Main menu and game state management
- Visual map tileset and semi-topdown representation
- Drag-and-drop tools for building scenes and maps (editor UI)
- Full campaign conversion from original D&D sessions

## Setup

1. Clone this repository
    ```bash
    git clone https://github.com/cleverNamesAreHard/Elarion.git
    cd Elarion
    ```

2. Make sure you're using [**Python 3.13.2**](https://www.python.org/downloads/release/python-3132/)

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   ```

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

5. Run the game:
   ```bash
   python game.py
   ```

## Notes

This is an active, evolving project. The current version is focused on core combat systems and early engine foundations. The narrative layer and tooling for campaign building are in development.

### License

This project is licensed under the MIT License
