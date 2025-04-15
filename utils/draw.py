import pygame
import math
import sys


WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

def draw_grid(screen, screen_width, screen_height, tile_size):
    for x in range(0, screen_width, tile_size):
        pygame.draw.line(screen, GRAY, (x, 0), (x, screen_height))
    for y in range(0, screen_height, tile_size):
        pygame.draw.line(screen, GRAY, (0, y), (screen_width, y))

def draw_battle_log(screen, log_font, battle_log, screen_width, screen_height):
    log_width = 165
    log_height = 170
    x = screen_width - log_width - 10
    y = screen_height - log_height - 10

    log_surface = pygame.Surface((log_width, log_height), pygame.SRCALPHA)
    log_surface.fill((200, 200, 200, 180))
    screen.blit(log_surface, (x, y))

    line_y = y + 5
    inner_line_spacing = 9
    between_entries_spacing = 6
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

def highlight_movement_tiles(screen, character, grid_width, grid_height, move_range, tile_size):
    for dx in range(-move_range, move_range + 1):
        for dy in range(-move_range, move_range + 1):
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= move_range:
                tx = character.x + dx
                ty = character.y + dy
                if 0 <= tx < grid_width and 0 <= ty < grid_height:
                    pygame.draw.rect(screen, YELLOW, (tx * tile_size, ty * tile_size, tile_size, tile_size), 2)

def draw_ui_buttons(screen, font, screen_height, mode):
    action_buttons = {}
    action_types = ["attack", "magic", "item"]
    for i, action_type in enumerate(action_types):
        btn = pygame.Rect(10 + (110 * i), screen_height - 180, 100, 40)
        color = YELLOW if mode == action_type else GRAY
        pygame.draw.rect(screen, color, btn)
        label = font.render(action_type.capitalize(), True, BLACK)
        screen.blit(label, (btn.x + 10, btn.y + 10))
        action_buttons[action_type] = btn

    move_button = pygame.Rect(10, screen_height - 60, 100, 50)
    end_turn_button = pygame.Rect(120, screen_height - 60, 100, 50)
    pygame.draw.rect(screen, GRAY, move_button)
    pygame.draw.rect(screen, GRAY, end_turn_button)
    screen.blit(font.render("Move", True, BLACK), (move_button.x + 10, move_button.y + 10))
    screen.blit(font.render("End Turn", True, BLACK), (end_turn_button.x + 10, end_turn_button.y + 10))

    return move_button, end_turn_button, action_buttons

def render_skill_buttons(screen, font, skills_data, skill_buttons, selected_attack):
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

def draw_units(screen, font, all_units, selected_character, tile_size):
    for c in all_units:
        color = BLUE if c.team == "player" else RED
        rect = pygame.Rect(c.x * tile_size, c.y * tile_size, tile_size, tile_size)
        pygame.draw.rect(screen, color, rect)
        if c == selected_character:
            pygame.draw.rect(screen, GREEN, rect, 3)
        letter = font.render(c.name[0].upper(), True, WHITE)
        screen.blit(letter, (rect.x + 10, rect.y + 5))
        hp_text = font.render(f"{c.current_hp}/{c.hp}", True, BLACK)
        screen.blit(hp_text, (rect.x, rect.y - 12))

def draw_game_over_screen(screen, font, screen_width, screen_height):
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    game_over_text = font.render("Game Over", True, RED)
    quit_text = font.render("Quit", True, BLACK)

    text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 3))
    quit_button = pygame.Rect(screen_width // 2 - 60, screen_height // 2, 120, 50)

    pygame.draw.rect(screen, GRAY, quit_button)
    screen.blit(game_over_text, text_rect)
    screen.blit(quit_text, (quit_button.x + 30, quit_button.y + 10))

    return quit_button

def draw_victory_screen(screen, font, screen_width, screen_height):
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    congrats_text = font.render("Victory!", True, GREEN)
    save_btn = pygame.Rect(screen_width // 2 - 150, screen_height // 2, 100, 50)
    next_btn = pygame.Rect(screen_width // 2 - 50, screen_height // 2, 100, 50)
    quit_btn = pygame.Rect(screen_width // 2 + 50, screen_height // 2, 100, 50)

    pygame.draw.rect(screen, GRAY, save_btn)
    pygame.draw.rect(screen, GRAY, next_btn)
    pygame.draw.rect(screen, GRAY, quit_btn)

    screen.blit(congrats_text, congrats_text.get_rect(center=(screen_width // 2, screen_height // 3)))
    screen.blit(font.render("Save", True, BLACK), (save_btn.x + 25, save_btn.y + 15))
    screen.blit(font.render("Next", True, BLACK), (next_btn.x + 25, next_btn.y + 15))
    screen.blit(font.render("Quit", True, BLACK), (quit_btn.x + 25, quit_btn.y + 15))

    return save_btn, next_btn, quit_btn

def draw_choose_player_character(screen, font, starters, SCREEN_WIDTH, SCREEN_HEIGHT, SCALE, WHITE, BLACK):
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

    while True:
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
                        return character_data["name"]

def draw_main_menu(screen, font, screen_width, screen_height, title="Tactical RPG"):
    menu_items = ["New Game", "Load Game", "Options", "Quit"]
    buttons = []

    # Dynamically adjust sizes based on screen height
    title_font_size = max(32, int(screen_height * 0.06))  # scales with window size
    button_width = int(screen_width * 0.5)
    button_height = max(40, int(screen_height * 0.06))
    spacing = max(10, int(screen_height * 0.02))

    title_font = pygame.font.SysFont(None, title_font_size)
    title_surface = title_font.render(title, True, BLACK)
    title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 5))

    total_height = len(menu_items) * (button_height + spacing)
    start_y = title_rect.bottom + spacing * 2

    for i, label in enumerate(menu_items):
        rect = pygame.Rect(
            (screen_width - button_width) // 2,
            start_y + i * (button_height + spacing),
            button_width,
            button_height
        )
        buttons.append((label, rect))

    screen.fill(WHITE)
    screen.blit(title_surface, title_rect)

    for label, rect in buttons:
        pygame.draw.rect(screen, GRAY, rect)
        text = font.render(label, True, BLACK)
        screen.blit(text, (rect.x + 20, rect.y + 12))

    pygame.display.flip()
    return buttons

def run_main_menu(screen, font, screen_width, screen_height):
    while True:
        buttons = draw_main_menu(screen, font, screen_width, screen_height)

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
                        # Load/Options do nothing
