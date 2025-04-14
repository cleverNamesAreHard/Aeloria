import pygame
import os
import sys
import json
import math
from res.character import load_character_by_name, Character, evaluate_expression
from res.enemies import enemy_take_turn


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
GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tactical RPG")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, int(24 * SCALE))
log_font = pygame.font.SysFont(None, int(16 * SCALE))

with open("res/attacks.json") as f:
    attacks_data = json.load(f)

mode = "idle"
selected_attack = None
battle_log = []

def add_to_log(text):
    battle_log.append(text)
    if len(battle_log) > 5:
        battle_log.pop(0)

def draw_battle_log():
    start_x = SCREEN_WIDTH - 300
    start_y = SCREEN_HEIGHT - 120
    for i, log_entry in enumerate(battle_log):
        line = log_font.render(log_entry, True, BLACK)
        screen.blit(line, (start_x, start_y + i * 18))

def draw_attack_buttons(attacker, attacks_data):
    attack_buttons = []
    base_x = 10
    base_y = SCREEN_HEIGHT - 120
    button_height = 30
    button_width = 180
    padding = 5

    # Create list in display order: weapon attack first (top), others after
    all_attacks = ["weapon_attack"] + [str(aid) for aid in attacker.attack_ids]

    for i, attack_id in enumerate(all_attacks):
        # Stack buttons top to bottom
        rect = pygame.Rect(
            base_x,
            base_y - ((len(all_attacks) - i) * (button_height + padding)),
            button_width,
            button_height
        )

        if attack_id == "weapon_attack":
            attacks_data["weapon_attack"] = {
                "name": "Weapon Attack",
                "range": 1,
                "damage": attacker.equipment.weapon.atk_roll if attacker.equipment.weapon else "0",
                "__rect": rect,
                "__id": "weapon_attack"
            }
            label = "Weapon Attack"
        else:
            attack = attacks_data[attack_id]
            attack["__rect"] = rect
            attack["__id"] = attack_id
            label = attack["name"]

        pygame.draw.rect(screen, GRAY, rect)
        text = font.render(label, True, BLACK)
        screen.blit(text, (rect.x + 5, rect.y + 5))

    return attack_buttons

def get_character_at(x, y):
    for c in all_units:
        if c.x == x and c.y == y:
            return c
    return None

def move_character(character, target_x, target_y):
    dx = target_x - character.x
    dy = target_y - character.y
    distance = math.sqrt(dx**2 + dy**2)
    if distance <= MOVE_RANGE and not get_character_at(target_x, target_y):
        character.x = target_x
        character.y = target_y
        return True
    return False

def highlight_movement_tiles(character):
    for dx in range(-MOVE_RANGE, MOVE_RANGE + 1):
        for dy in range(-MOVE_RANGE, MOVE_RANGE + 1):
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= MOVE_RANGE:
                tx = character.x + dx
                ty = character.y + dy
                if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                    pygame.draw.rect(screen, YELLOW, (tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

def draw_grid():
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def draw_ui_buttons():
    move_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 100, 50)
    attack_button = pygame.Rect(120, SCREEN_HEIGHT - 60, 100, 50)
    end_turn_button = pygame.Rect(230, SCREEN_HEIGHT - 60, 100, 50)
    pygame.draw.rect(screen, GRAY, move_button)
    pygame.draw.rect(screen, GRAY, attack_button)
    pygame.draw.rect(screen, GRAY, end_turn_button)
    screen.blit(font.render("Move", True, BLACK), (move_button.x + 10, move_button.y + 10))
    screen.blit(font.render("Attack", True, BLACK), (attack_button.x + 10, attack_button.y + 10))
    screen.blit(font.render("End Turn", True, BLACK), (end_turn_button.x + 10, end_turn_button.y + 10))
    return move_button, attack_button, end_turn_button

def load_starter_characters():
    with open("characters/characters.json") as f:
        characters = json.load(f)
    return [c for c in characters if c.get("is_starter")]

def choose_player_character():
    starters = load_starter_characters()
    font = pygame.font.SysFont(None, int(32 * SCALE))
    button_height = int(50 * SCALE)
    spacing = int(20 * SCALE)
    buttons = []

    for index, character_data in enumerate(starters):
        rect = pygame.Rect(
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 4 + index * (button_height + spacing),
            SCREEN_WIDTH // 2,
            button_height
        )
        buttons.append((rect, character_data))

    selecting = True
    while selecting:
        screen.fill(WHITE)
        for rect, character_data in buttons:
            pygame.draw.rect(screen, GRAY, rect)
            text_surface = font.render(character_data["name"], True, BLACK)
            screen.blit(text_surface, (rect.x + 10, rect.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for rect, character_data in buttons:
                    if rect.collidepoint(mx, my):
                        return load_character_by_name(character_data["name"])

starter_characters = load_starter_characters()
party = []
player_character = None

for idx, data in enumerate(starter_characters):
    ch = load_character_by_name(data["name"])
    ch.team = "player"
    ch.x = 2 + idx
    ch.y = 2
    ch.has_moved = False
    party.append(ch)

chosen_name = choose_player_character().name
for ch in party:
    if ch.name == chosen_name:
        player_character = ch
        break

enemy = load_character_by_name("Vaelith the Hollow")
enemy.team = "enemy"
enemy.role = "enemy_hero"
enemy.x = 8
enemy.y = 8
enemy.has_moved = False

all_units = party + [enemy]
turn_order = all_units.copy()
turn_index = 0
selected_character = turn_order[turn_index]
selected_character.has_moved = False
selected_character.ready_to_move = False

running = True
while running:
    screen.fill(WHITE)
    draw_grid()

    name_surface = font.render(f"Active: {selected_character.name}", True, BLACK)
    screen.blit(name_surface, (10, SCREEN_HEIGHT - 100))

    move_btn, attack_btn, end_btn = draw_ui_buttons()
    draw_battle_log()

    if mode == "attack" and selected_character.team == "player":
        draw_attack_buttons(selected_character, attacks_data)

    if selected_character.team != "player" and selected_character.role in ["enemy", "enemy_hero"]:
        print(f"\n[ENEMY TURN] {selected_character.name}")
        acted = enemy_take_turn(selected_character, all_units, attacks_data, move_character)
        if acted:
            selected_character.has_moved = False
            selected_character.ready_to_move = False
            mode = "idle"
            selected_attack = None
            turn_index = (turn_index + 1) % len(turn_order)
            selected_character = turn_order[turn_index]
            continue

    if selected_character.team == "player" and mode == "move" and not selected_character.has_moved:
        highlight_movement_tiles(selected_character)

    if mode == "attack" and selected_attack:
        atk_range = attacks_data[str(selected_attack)]["range"]
        for target in all_units:
            if target.team != selected_character.team:
                dx = target.x - selected_character.x
                dy = target.y - selected_character.y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist <= atk_range:
                    pygame.draw.rect(screen, RED, (target.x * TILE_SIZE, target.y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

    for c in all_units:
        color = BLUE if c.team == "player" else RED
        rect = pygame.Rect(c.x * TILE_SIZE, c.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, color, rect)
        if c == selected_character:
            pygame.draw.rect(screen, GREEN, rect, 3)
        letter = font.render(c.name[0].upper(), True, WHITE)
        screen.blit(letter, (rect.x + 10, rect.y + 5))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if selected_character.team != "player":
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()

            if move_btn.collidepoint(mx, my):
                mode = "move"
                selected_character.ready_to_move = True
                print(f"[MOVE MODE] {selected_character.name} is preparing to move.")

            elif attack_btn.collidepoint(mx, my):
                mode = "attack"
                selected_attack = None
                print(f"[ATTACK MODE] {selected_character.name} is choosing an attack.")

            elif end_btn.collidepoint(mx, my):
                selected_character.has_moved = False
                selected_character.ready_to_move = False
                mode = "idle"
                selected_attack = None
                turn_index = (turn_index + 1) % len(turn_order)
                selected_character = turn_order[turn_index]
                print(f"[TURN ENDED] Switching to {selected_character.name}")
                continue

            elif mode == "move" and not selected_character.has_moved:
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                moved = move_character(selected_character, gx, gy)
                if moved:
                    print(f"[MOVED] {selected_character.name} moved to ({gx}, {gy})")
                    add_to_log(f"{selected_character.name} moved")
                    selected_character.has_moved = True
                    mode = "idle"

            elif mode == "attack" and not selected_attack:
                for atk_id, atk_data in attacks_data.items():
                    if "__rect" in atk_data and atk_data["__rect"].collidepoint(mx, my):
                        selected_attack = atk_data["__id"]
                        print(f"[ATTACK SELECTED] {atk_data['name']}")
                        break

                # Check for weapon attack button
                if "weapon_attack" in attacks_data:
                    rect = attacks_data["weapon_attack"]["__rect"]
                    if rect.collidepoint(mx, my):
                        selected_attack = "weapon_attack"
                        print("[ATTACK SELECTED] Weapon Attack")

            elif mode == "attack" and selected_attack:
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                target = get_character_at(gx, gy)

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

                        base_roll, roll_breakdown = evaluate_expression("1d20")
                        bonus = weapon.attack_bonus
                        attack_total = base_roll + bonus

                        print(f"[ATTACK ROLL] {selected_character.name} rolled {roll_breakdown} + {bonus} = {attack_total} vs AC {target.ac}")

                        if base_roll == 1:
                            print("[MISS] Critical Fail")
                            add_to_log(f"{selected_character.name[0]} MISS")
                        elif base_roll == 20 or attack_total >= target.ac:
                            damage_total, dmg_breakdown = evaluate_expression(weapon.atk_roll)
                            if base_roll == 20:
                                print(f"[CRIT] {selected_character.name} crits {target.name} for {damage_total} ({dmg_breakdown})")
                                add_to_log(f"{selected_character.name[0]} CRIT {target.name[0]} ({damage_total})")
                            else:
                                print(f"[HIT] {selected_character.name} hits {target.name} for {damage_total} ({dmg_breakdown})")
                                add_to_log(f"{selected_character.name[0]}->{target.name[0]} ({damage_total})")
                        else:
                            print("[MISS] Attack missed")
                            add_to_log(f"{selected_character.name[0]} MISS")

                    else:
                        atk = attacks_data[str(selected_attack)]
                        if dist <= atk["range"]:
                            total, breakdown = evaluate_expression(atk["damage"])
                            print(f"[SPELL] {selected_character.name} uses {atk['name']} on {target.name}")
                            print(f"[ROLL] {breakdown} = {total}")
                            add_to_log(f"{selected_character.name[0]}->{target.name[0]} ({total})")

                    selected_character.has_moved = True
                    selected_attack = None
                    mode = "idle"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
