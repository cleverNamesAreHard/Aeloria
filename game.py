import pygame
import sys
import json
import math

from res.character import load_character_by_name, Character, evaluate_expression
from res.enemies import enemy_take_turn

from utils.draw import (
    draw_grid,
    draw_battle_log,
    draw_ui_buttons,
    render_skill_buttons,
    draw_game_over_screen,
    draw_victory_screen,
    draw_units,
    highlight_movement_tiles,
    draw_choose_player_character,
    run_main_menu
)

from utils.game_engine import (
    move_character,
    get_character_at,
    roll_initiative,
    handle_ko,
    advance_turn,
    resolve_attack
)

pygame.init()

BASE_WIDTH = 1920
BASE_HEIGHT = 1080
DISPLAY_INFO = pygame.display.Info()
SCALE_X = DISPLAY_INFO.current_w / BASE_WIDTH
SCALE_Y = DISPLAY_INFO.current_h / BASE_HEIGHT
SCALE = min(SCALE_X, SCALE_Y)

TILE_SIZE = int(40 * SCALE)
GRID_WIDTH = 16
GRID_HEIGHT = 16
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT
MOVE_RANGE = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tactical RPG")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, int(24 * SCALE))
log_font = pygame.font.SysFont(None, int(16 * SCALE))

with open("res/skills.json") as f:
    attacks_data = json.load(f)

mode = "idle"
selected_attack = None
battle_log = []

def add_to_log(text):
    battle_log.append(text)
    if len(battle_log) > 5:
        battle_log.pop(0)

def load_starter_characters():
    with open("characters/characters.json") as f:
        characters = json.load(f)
    return [c for c in characters if c.get("is_starter")]

def generate_skill_buttons(attacker, skills_data):
    skill_buttons = {}
    base_x = 10
    base_y = SCREEN_HEIGHT - 120
    button_height = 30
    button_width = 180
    padding = 5

    filtered_skills = []
    for sid in attacker.attack_ids:
        skill = skills_data.get(str(sid))
        if not skill:
            continue
        if skill.get("category") == mode:
            filtered_skills.append(str(sid))

    if mode == "attack":
        all_skills = ["weapon_attack"] + filtered_skills
        weapon = attacker.equipment.weapon
        skills_data["weapon_attack"] = {
            "name": "Weapon Attack",
            "category": "attack",
            "target": "enemy",
            "range": getattr(weapon, "range", 1) if weapon else 1,
            "damage": getattr(weapon, "atk_roll", "0"),
        }
    else:
        all_skills = filtered_skills

    for i, skill_id in enumerate(all_skills):
        rect = pygame.Rect(
            base_x,
            base_y - ((len(all_skills) - i) * (button_height + padding)),
            button_width,
            button_height
        )
        skills_data[skill_id]["__rect"] = rect
        skills_data[skill_id]["__id"] = skill_id
        skill_buttons[skill_id] = rect

    print(f"[SKILL BUTTONS] Loaded: {list(skill_buttons.keys())}")
    return skill_buttons

def initialize_characters():
    starter_characters = load_starter_characters()
    party = []

    for idx, data in enumerate(starter_characters):
        ch = load_character_by_name(data["name"])
        ch.team = "player"
        ch.x = 2 + idx
        ch.y = 2
        ch.has_moved = False
        party.append(ch)

    chosen_name = draw_choose_player_character(
        screen,
        pygame.font.SysFont(None, int(32 * SCALE)),
        starter_characters,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        SCALE,
        WHITE,
        BLACK
    )

    player_character = load_character_by_name(chosen_name)

    enemy = load_character_by_name("Vaelith the Hollow")
    enemy.team = "enemy"
    enemy.role = "enemy_hero"
    enemy.x = 8
    enemy.y = 8
    enemy.has_moved = False

    goblin = load_character_by_name("Goblin Grunt")
    goblin.team = "enemy"
    goblin.role = "enemy"
    goblin.x = 9
    goblin.y = 9
    goblin.has_moved = False

    all_units = party + [enemy, goblin]
    turn_order = sorted(all_units, key=roll_initiative, reverse=True)
    return all_units, turn_order, party, player_character

def move_enemy_wrapper(character, x, y):
    return move_character(all_units, character, x, y)

def get_character_wrapper(x, y):
    return get_character_at(all_units, x, y)

# Main Menu
selection = run_main_menu(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT)

# Game state setup
all_units = []
turn_order = []
party = []
player_character = None
turn_index = 0
selected_character = None
running = False
skill_buttons = {}
last_mode = None
game_over = False
victory = False

if selection == "new_game":
    all_units, turn_order, party, player_character = initialize_characters()
    turn_index = 0
    selected_character = turn_order[turn_index]
    selected_character.has_moved = False
    selected_character.ready_to_move = False
    running = True
else:
    pygame.quit()
    sys.exit()

while running:
    if game_over:
        quit_btn = draw_game_over_screen(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if quit_btn.collidepoint(mx, my):
                    running = False
        continue

    if victory:
        save_btn, next_btn, quit_btn = draw_victory_screen(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if quit_btn.collidepoint(mx, my):
                    running = False
                elif save_btn.collidepoint(mx, my):
                    print("[VICTORY] Save clicked! (stub)")
                elif next_btn.collidepoint(mx, my):
                    print("[VICTORY] Next clicked! (stub)")
        continue

    screen.fill(WHITE)

    if mode != last_mode:
        if selected_character.team == "player" and mode in ["attack", "magic"]:
            skill_buttons = generate_skill_buttons(selected_character, attacks_data)
        else:
            skill_buttons = {}
        last_mode = mode

    draw_grid(screen, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)
    name_surface = font.render(f"Active: {selected_character.name}", True, BLACK)
    screen.blit(name_surface, (10, SCREEN_HEIGHT - 100))

    move_btn, end_btn, action_buttons = draw_ui_buttons(screen, font, SCREEN_HEIGHT, mode)
    draw_battle_log(screen, log_font, battle_log, SCREEN_WIDTH, SCREEN_HEIGHT)

    if mode in ["attack", "magic"]:
        render_skill_buttons(screen, font, attacks_data, skill_buttons, selected_attack)

    if selected_character.current_hp <= 0:
        print(f"[SKIP] {selected_character.name} is KO'd — skipping turn")
        turn_index, selected_character = advance_turn(turn_order, turn_index)
        if selected_character is None:
            game_over = True
        continue

    if selected_character.team != "player" and selected_character.role in ["enemy", "enemy_hero"]:
        print(f"\n[ENEMY TURN] {selected_character.name}")
        result = enemy_take_turn(
            selected_character,
            all_units,
            attacks_data,
            move_enemy_wrapper,
            get_character_wrapper
        )
        if not result:
            print(f"{selected_character.name} had no valid action.")
        elif result.get("action") == "move":
            print(f"[ENEMY MOVE] {result['attacker'].name} moved toward {result['target'].name}")
        elif result.get("action") == "none":
            print(f"{result['attacker'].name} could not act this turn.")
        else:
            attacker = result["attacker"]
            target = result["target"]
            skill_id = result["attack_id"]
            skill = attacks_data[str(skill_id)]
            category = result["type"]

            combat_result = resolve_attack(attacker, target, skill, category, turn_order, all_units, add_to_log)
            for line in combat_result["log"]:
                print(f"[ENEMY LOG] {line}")
            add_to_log("\n".join(combat_result["log"]))
            if combat_result["victory"]:
                victory = True

        selected_character.has_moved = False
        selected_character.ready_to_move = False
        mode = "idle"
        selected_attack = None
        turn_index, selected_character = advance_turn(turn_order, turn_index)
        if selected_character is None:
            game_over = True
        continue

    if selected_character.team == "player" and mode == "move" and not selected_character.has_moved:
        highlight_movement_tiles(screen, selected_character, GRID_WIDTH, GRID_HEIGHT, MOVE_RANGE, TILE_SIZE)

    if mode in ["attack", "magic"] and selected_attack:
        atk_range = attacks_data[str(selected_attack)]["range"]
        for target in all_units:
            if target.team != selected_character.team:
                dx = target.x - selected_character.x
                dy = target.y - selected_character.y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist <= atk_range:
                    pygame.draw.rect(screen, RED, (target.x * TILE_SIZE, target.y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

    draw_units(screen, font, all_units, selected_character, TILE_SIZE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if selected_character.team != "player":
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()

            skill_clicked = False
            if mode in ["attack", "magic"] and not selected_attack:
                for skill_id, rect in skill_buttons.items():
                    if rect.collidepoint(mx, my):
                        selected_attack = skill_id
                        print(f"[{mode.upper()} SELECTED] {attacks_data[skill_id]['name']}")
                        skill_clicked = True
                        break
                if skill_clicked:
                    continue

            for action_name, btn in action_buttons.items():
                if btn.collidepoint(mx, my):
                    if mode == action_name:
                        print(f"[CANCEL] {action_name} mode canceled")
                        mode = "idle"
                        selected_attack = None
                    else:
                        mode = action_name
                        selected_attack = None
                        print(f"[{action_name.upper()} MODE] {selected_character.name} is choosing a {action_name} skill.")
                    break

            if move_btn.collidepoint(mx, my):
                mode = "move"
                selected_character.ready_to_move = True
                print(f"[MOVE MODE] {selected_character.name} is preparing to move.")

            elif end_btn.collidepoint(mx, my):
                selected_character.has_moved = False
                selected_character.ready_to_move = False
                mode = "idle"
                selected_attack = None
                turn_index, selected_character = advance_turn(turn_order, turn_index)
                if selected_character is None:
                    game_over = True
                print(f"[TURN ENDED] Switching to {selected_character.name if selected_character else 'None'}")
                continue

            elif mode == "move" and not selected_character.has_moved:
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                moved = move_character(all_units, selected_character, gx, gy)
                if moved:
                    selected_character.has_moved = True
                    mode = "idle"

            elif mode in ["attack", "magic"] and selected_attack:
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                target = get_character_at(all_units, gx, gy)

                if target and target.team != selected_character.team:
                    dx = target.x - selected_character.x
                    dy = target.y - selected_character.y
                    dist = math.sqrt(dx ** 2 + dy ** 2)

                    if selected_attack == "weapon_attack":
                        weapon = selected_character.equipment.weapon
                        if not weapon:
                            print(f"[FAIL] {selected_character.name} has no weapon.")
                            continue

                        if dist > 1:
                            print("Target out of weapon range")
                            continue

                        skill = {
                            "name": "Weapon Attack",
                            "damage": weapon.atk_roll
                        }
                        combat_result = resolve_attack(selected_character, target, skill, "attack", turn_order, all_units, add_to_log)

                    else:
                        atk = attacks_data[str(selected_attack)]
                        if dist > atk["range"]:
                            print("Target out of range for skill.")
                            continue

                        skill_type = atk.get("category", "attack")
                        combat_result = resolve_attack(selected_character, target, atk, skill_type, turn_order, all_units, add_to_log)

                    for line in combat_result["log"]:
                        print(f"[PLAYER LOG] {line}")
                    add_to_log("\n".join(combat_result["log"]))
                    if combat_result["victory"]:
                        victory = True

                    selected_character.has_moved = True
                    selected_attack = None
                    mode = "idle"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
