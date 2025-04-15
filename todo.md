## MVP Features

### Combat System
- [x] Turn-based grid movement and combat loop
- [x] Initiative tracking and active turn handling
- [x] Skill and attack usage system
- [x] Battle log with support for multiline and overflow
- [ ] Add item usage system (e.g., healing potions, utility items)
- [ ] Expand skill targeting (AOEs, allies, self)

### Game Logic
- [ ] Save/load system for game state
- [ ] Scene-to-scene navigation system
- [ ] Campaign metadata system (e.g., name, author, description)
- [ ] Campaign selection screen
- [ ] Reorganize all game data into campaigns/%campaign_name%/
- [ ] Scene engine (dialogue scenes, transitions)
- [ ] Add title page and chapter splash support

### Story and Scene Support
- [ ] JSON structure for scenes and events
- [ ] Basic scene scripting engine (text and simple triggers)
- [ ] Load and play linear story sequences
- [ ] Character selection and assignment to player

### Developer Experience
- [ ] Rebase game logic to support a rules.json system
- [ ] Start migrating hardcoded rules into rule definitions
- [ ] Basic JSON validation for all core files
- [ ] Error handling for bad data

## Future Features and Expansion

### Toolkit Suite
- [ ] Drag-and-drop scene builder GUI
- [ ] Map/tile editor for combat maps
- [ ] Character builder (stat input, equipment, portrait)
- [ ] Visual scripting editor for cutscenes and battle triggers
- [ ] Skill/item builder tool

### Campaign and Engine Separation
- [ ] Fully modular engine/campaign design
- [ ] Multiple ruleset support (5e, Pathfinder, homebrew)
- [ ] Ruleset visual editor
- [ ] Rule validator and previewer

### DM Mode and Multiplayer
- [ ] Add game server module (host/join functionality)
- [ ] Support for DM to inject narrative and control enemies
- [ ] Player login with one character per player
- [ ] Server saves and session handoffs

### Packaging and Distribution
- [ ] CLI tools for building distributable games from campaigns
- [ ] PyInstaller packaging scripts (Windows/macOS/Linux)
- [ ] Packaged asset bundling
- [ ] Campaign zip or pkg export format

### Art and Assets
- [ ] Drop-in asset support per campaign
- [ ] Fallback to base assets when no override exists
- [ ] Define asset directory structure
- [ ] Commission base assets (5 tilesets, sprite sheets)
- [ ] Music/audio loader with campaign override support

### Cutscenes and Animation Scripting
- [ ] Add support for animation scripting in scenes
- [ ] Script format: move characters, trigger dialogue, set flags
- [ ] Fade/pan support, music triggers
- [ ] Camera targeting and cutscene-style events

### Documentation and Mod Support
- [ ] Write and generate full documentation
- [ ] Autogenerate docs from JSON schemas
- [ ] Developer/modder guide (how to add a campaign, skill, etc.)
- [ ] Storyteller tutorial and sample campaign
- [ ] License clarification and .mailmap support

### Community and Showcase
- [ ] Itch.io page
- [ ] GitHub README GIF demo and example
- [ ] Public v1 release milestone
- [ ] Outreach to artists, writers, and TTRPG creators

## Stretch Goals and Long-Term Plans

- [ ] AI scripting editor for NPCs/enemies
- [ ] Online campaign browser and downloader
- [ ] Player-made rule conversion tools
- [ ] Web-based toolkit suite (run in browser)
- [ ] Visual logic builder for rolls and stat interactions
- [ ] In-game mod manager
- [ ] Cross-campaign shared world support
