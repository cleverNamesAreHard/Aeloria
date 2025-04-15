import math
import pygame
import sys
from res.character import evaluate_expression


MOVE_RANGE = 3  # Imported in game.py too for UI purposes

def get_character_at(units, x, y):
    for c in units:
        if c.x == x and c.y == y:
            return c
    return None

def move_character(units, character, target_x, target_y):
    dx = target_x - character.x
    dy = target_y - character.y
    distance = math.sqrt(dx**2 + dy**2)
    if distance <= MOVE_RANGE and not get_character_at(units, target_x, target_y):
        character.x = target_x
        character.y = target_y
        return True
    return False

def roll_initiative(character):
    base_roll, breakdown = evaluate_expression("1d20")
    total = base_roll + character.initiative
    print(f"[INIT] {character.name} rolls {breakdown} + {character.initiative} = {total}")
    return total

def handle_ko(target, turn_order, all_units, log_callback):
    if target.current_hp > 0:
        return

    print(f"[DEFEATED] {target.name} is defeated")
    log_callback(f"{target.name} defeated")

    if target in turn_order:
        turn_order.remove(target)
    if target in all_units:
        all_units.remove(target)

    if all(u.team != "enemy" for u in all_units):
        return True  # Indicates victory
    return False

def advance_turn(turn_order, current_index):
    for _ in range(len(turn_order)):
        current_index = (current_index + 1) % len(turn_order)
        unit = turn_order[current_index]
        if unit.current_hp > 0:
            print(f"[TURN] It's now {unit.name}'s turn")
            return current_index, unit
        else:
            print(f"[SKIP] {unit.name} is KO'd — skipping turn")
    return None, None

def resolve_attack(attacker, target, skill, skill_type, turn_order, all_units, log_callback):
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
                if handle_ko(target, turn_order, all_units, log_callback):
                    log_lines.append("Victory!")
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
                if handle_ko(target, turn_order, all_units, log_callback):
                    log_lines.append("Victory!")

    return {
        "log": log_lines,
        "victory": any("Victory!" in line for line in log_lines)
    }

def draw_main_menu(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT, title="Tactical RPG"):
    menu_items = ["New Game", "Load Game", "Options", "Quit"]
    buttons = []

    title_font = pygame.font.SysFont(None, int(64))
    title_surface = title_font.render(title, True, (0, 0, 0))
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    button_width = 250
    button_height = 50
    spacing = 20
    start_y = SCREEN_HEIGHT // 2 - ((button_height + spacing) * len(menu_items)) // 2

    for i, label in enumerate(menu_items):
        rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            start_y + i * (button_height + spacing),
            button_width,
            button_height
        )
        buttons.append((label, rect))

    screen.fill((255, 255, 255))
    screen.blit(title_surface, title_rect)

    for label, rect in buttons:
        pygame.draw.rect(screen, (200, 200, 200), rect)
        text = font.render(label, True, (0, 0, 0))
        screen.blit(text, (rect.x + 20, rect.y + 12))

    pygame.display.flip()
    return buttons

def run_main_menu(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT):
    while True:
        buttons = draw_main_menu(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for label, rect in buttons:
                    if rect.collidepoint(mx, my):
                        if label == "New Game":
                            return "new_game"
                        elif label == "Quit":
                            pygame.quit()
                            sys.exit()
                        else:
                            print(f"[STUB] {label} is not implemented yet.")
