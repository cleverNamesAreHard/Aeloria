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

with open("res/skills.json") as f:
    attacks_data = json.load(f)

mode = "idle"
selected_attack = None
battle_log = []

def add_to_log(text):
    battle_log.append(text)
    if len(battle_log) > 5:
        battle_log.pop(0)

def draw_battle_log():
    log_width = 165
    log_height = 170
    x = SCREEN_WIDTH - log_width - 10
    y = SCREEN_HEIGHT - log_height - 10

    log_surface = pygame.Surface((log_width, log_height), pygame.SRCALPHA)
    log_surface.fill((200, 200, 200, 180))
    screen.blit(log_surface, (x, y))

    line_y = y + 5
    inner_line_spacing = 9       # spacing between lines inside a message
    between_entries_spacing = 6  # extra spacing between entries
    total_used = 0

    for entry in battle_log:
        lines = entry.split("\n")
        block_height = len(lines) * inner_line_spacing + between_entries_spacing

        if total_used + block_height > log_height:
            break

        for i, line in enumerate(lines):
            text = log_font.render(line, True, BLACK)
            screen.blit(text, (x + 3, line_y + total_used + i * inner_line_spacing))

        total_used += block_height

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

def render_skill_buttons(skills_data, skill_buttons):
    for skill_id, rect in skill_buttons.items():
        skill = skills_data.get(skill_id)
        if not skill:
            continue
        is_selected = (skill_id == selected_attack)
        bg_color = YELLOW if is_selected else GRAY
        pygame.draw.rect(screen, bg_color, rect)
        label = skill["name"]
        text = font.render(label, True, BLACK)
        screen.blit(text, (rect.x + 5, rect.y + 5))

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
    action_buttons = {}
    action_types = ["attack", "magic", "item"]
    for i, action_type in enumerate(action_types):
        btn = pygame.Rect(10 + (110 * i), SCREEN_HEIGHT - 180, 100, 40)
        color = YELLOW if mode == action_type else GRAY
        pygame.draw.rect(screen, color, btn)
        label = font.render(action_type.capitalize(), True, BLACK)
        screen.blit(label, (btn.x + 10, btn.y + 10))
        action_buttons[action_type] = btn

    move_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 100, 50)
    end_turn_button = pygame.Rect(120, SCREEN_HEIGHT - 60, 100, 50)
    pygame.draw.rect(screen, GRAY, move_button)
    pygame.draw.rect(screen, GRAY, end_turn_button)
    screen.blit(font.render("Move", True, BLACK), (move_button.x + 10, move_button.y + 10))
    screen.blit(font.render("End Turn", True, BLACK), (end_turn_button.x + 10, end_turn_button.y + 10))

    return move_button, end_turn_button, action_buttons

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
                    
def roll_initiative(character):
    base_roll, breakdown = evaluate_expression("1d20")
    total = base_roll + character.initiative
    print(f"[INIT] {character.name} rolls {breakdown} + {character.initiative} = {total}")
    return total

def handle_ko(target, turn_order, all_units):
    if target.current_hp > 0:
        return

    print(f"[DEFEATED] {target.name} is defeated")
    add_to_log(f"{target.name} defeated")

    if target in turn_order:
        turn_order.remove(target)
    if target in all_units:
        all_units.remove(target)
    if all(u.team != "enemy" for u in all_units):
        global victory
        victory = True


def advance_turn(turn_order, turn_index):
    for _ in range(len(turn_order)):
        turn_index = (turn_index + 1) % len(turn_order)
        selected_character = turn_order[turn_index]
        if selected_character.current_hp > 0:
            print(f"[TURN] It's now {selected_character.name}'s turn")
            return turn_index, selected_character
        else:
            print(f"[SKIP] {selected_character.name} is KO'd — skipping turn")
    return None, None  # Indicates game over

def draw_game_over_screen():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    game_over_text = font.render("Game Over", True, RED)
    quit_text = font.render("Quit", True, BLACK)

    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2, 120, 50)

    pygame.draw.rect(screen, GRAY, quit_button)
    screen.blit(game_over_text, text_rect)
    screen.blit(quit_text, (quit_button.x + 30, quit_button.y + 10))

    return quit_button

def draw_victory_screen():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    congrats_text = font.render("Victory!", True, GREEN)
    save_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 100, 50)
    next_btn = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2, 100, 50)
    quit_btn = pygame.Rect(SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2, 100, 50)

    pygame.draw.rect(screen, GRAY, save_btn)
    pygame.draw.rect(screen, GRAY, next_btn)
    pygame.draw.rect(screen, GRAY, quit_btn)

    screen.blit(congrats_text, congrats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))
    screen.blit(font.render("Save", True, BLACK), (save_btn.x + 25, save_btn.y + 15))
    screen.blit(font.render("Next", True, BLACK), (next_btn.x + 25, next_btn.y + 15))
    screen.blit(font.render("Quit", True, BLACK), (quit_btn.x + 25, quit_btn.y + 15))

    return save_btn, next_btn, quit_btn

def resolve_attack(attacker, target, skill, skill_type):
    log_lines = [f"{attacker.name} used {skill['name']} on {target.name}"]

    if skill_type == "attack":
        atk_roll, atk_break = evaluate_expression("1d20")
        bonus = getattr(attacker, "attack_bonus", 2)
        atk_total = atk_roll + bonus
        log_lines.append(f"Attack Roll: 1d20+{bonus} -> {atk_total}")

        if atk_roll == 1:
            log_lines.append("MISS (Critical Fail)")
        elif atk_roll == 20 or atk_total >= target.ac:
            dmg_total, dmg_breakdown = evaluate_expression(skill["damage"])
            log_lines.append(f"HIT\nDamage Roll: {skill['damage']} -> {dmg_total} ({dmg_breakdown})")
            target.current_hp = max(0, target.current_hp - dmg_total)
            if target.current_hp == 0:
                log_lines.append(f"{target.name} was defeated!")
                handle_ko(target, turn_order, all_units)
        else:
            log_lines.append("MISS")

    elif skill_type == "magic":
        dc = getattr(attacker, "save_dc", 8)
        save_roll, save_break = evaluate_expression("1d20")
        save_bonus = getattr(target, "save_bonus", 0)
        save_total = save_roll + save_bonus
        log_lines.append(f"Save DC: {dc} — {target.name} rolled {save_break} + {save_bonus} = {save_total}")

        if save_total >= dc:
            log_lines.append("SAVE SUCCESS — No damage")
        else:
            dmg_total, dmg_breakdown = evaluate_expression(skill["damage"])
            log_lines.append(f"FAILED SAVE\nDamage Roll: {skill['damage']} -> {dmg_total} ({dmg_breakdown})")
            target.current_hp = max(0, target.current_hp - dmg_total)
            if target.current_hp == 0:
                log_lines.append(f"{target.name} was defeated!")
                handle_ko(target, turn_order, all_units)

    return log_lines

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

goblin = load_character_by_name("Goblin Grunt")
goblin.team = "enemy"
goblin.role = "enemy"
goblin.x = 9
goblin.y = 9
goblin.has_moved = False

all_units = party + [enemy, goblin]
turn_order = sorted(all_units, key=roll_initiative, reverse=True)
turn_index = 0
selected_character = turn_order[turn_index]
selected_character.has_moved = False
selected_character.ready_to_move = False

running = True
skill_buttons = {}
last_mode = None
game_over = False
victory = False

while running:
    if game_over:
        quit_btn = draw_game_over_screen()
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
        save_btn, next_btn, quit_btn = draw_victory_screen()
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

    draw_grid()
    name_surface = font.render(f"Active: {selected_character.name}", True, BLACK)
    screen.blit(name_surface, (10, SCREEN_HEIGHT - 100))

    move_btn, end_btn, action_buttons = draw_ui_buttons()
    draw_battle_log()

    if mode in ["attack", "magic"]:
        render_skill_buttons(attacks_data, skill_buttons)

    if selected_character.current_hp <= 0:
        print(f"[SKIP] {selected_character.name} is KO'd — skipping turn")
        turn_index, selected_character = advance_turn(turn_order, turn_index)
        if selected_character is None:
            game_over = True
            continue

    if selected_character.team != "player" and selected_character.role in ["enemy", "enemy_hero"]:
        print(f"\n[ENEMY TURN] {selected_character.name}")
        result = enemy_take_turn(selected_character, all_units, attacks_data, move_character, get_character_at)

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

            log_lines = resolve_attack(attacker, target, skill, category)
            for line in log_lines:
                print(f"[ENEMY LOG] {line}")
            add_to_log("\n".join(log_lines))

        selected_character.has_moved = False
        selected_character.ready_to_move = False
        mode = "idle"
        selected_attack = None
        turn_index, selected_character = advance_turn(turn_order, turn_index)
        if selected_character is None:
            game_over = True
        continue

    if selected_character.team == "player" and mode == "move" and not selected_character.has_moved:
        highlight_movement_tiles(selected_character)

    if mode in ["attack", "magic"] and selected_attack:
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
        hp_text = font.render(f"{c.current_hp}/{c.hp}", True, BLACK)
        screen.blit(hp_text, (rect.x, rect.y - 12))

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
                moved = move_character(selected_character, gx, gy)
                if moved:
                    selected_character.has_moved = True
                    mode = "idle"

            elif mode in ["attack", "magic"] and selected_attack:
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

                        skill = {
                            "name": "Weapon Attack",
                            "damage": weapon.atk_roll
                        }
                        log_lines = resolve_attack(selected_character, target, skill, "attack")

                    else:
                        atk = attacks_data[str(selected_attack)]
                        if dist > atk["range"]:
                            print("Target out of range for skill.")
                            continue

                        skill_type = atk.get("category", "attack")
                        log_lines = resolve_attack(selected_character, target, atk, skill_type)

                    for line in log_lines:
                        print(f"[PLAYER LOG] {line}")
                    add_to_log("\n".join(log_lines))

                    selected_character.has_moved = True
                    selected_attack = None
                    mode = "idle"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

