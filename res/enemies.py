import math
from res.character import evaluate_expression


def enemy_take_turn(enemy, all_units, attacks_data, move_fn, get_fn):
    target = get_closest_enemy(enemy, all_units)
    
    # 💥 Bail if no living enemy found
    if not target or target.current_hp <= 0:
        print(f"[AI] {enemy.name} found no valid living targets.")
        return None

    dx = target.x - enemy.x
    dy = target.y - enemy.y
    distance = math.sqrt(dx**2 + dy**2)

    # Try to use a skill
    for attack_id in enemy.attack_ids:
        atk = attacks_data[str(attack_id)]
        if distance <= atk["range"]:
            return {
                "attacker": enemy,
                "target": target,
                "attack_id": attack_id,
                "type": atk.get("category", "attack")
            }

    # Try to move toward target
    moved = move_towards(enemy, target, move_fn, get_fn)
    if moved:
        print(f"[AI] {enemy.name} moved toward {target.name}")
        return {"action": "move", "attacker": enemy, "target": target}

    print(f"[AI] {enemy.name} could not act this turn.")
    return {"action": "none", "attacker": enemy}

def get_closest_enemy(enemy, units):
    opponents = [u for u in units if u.team != enemy.team]
    if not opponents:
        return None
    return min(opponents, key=lambda u: (u.x - enemy.x) ** 2 + (u.y - enemy.y) ** 2)

def move_towards(enemy, target, move_fn, get_fn):
    MOVE_RANGE = 3

    best_dist = float("inf")
    best_pos = None

    for dx in range(-MOVE_RANGE, MOVE_RANGE + 1):
        for dy in range(-MOVE_RANGE, MOVE_RANGE + 1):
            if dx == 0 and dy == 0:
                continue

            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance > MOVE_RANGE:
                continue

            tx = enemy.x + dx
            ty = enemy.y + dy

            if not (0 <= tx < 16 and 0 <= ty < 16):
                continue

            if get_fn(tx, ty):
                continue

            dist_to_target = math.sqrt((tx - target.x) ** 2 + (ty - target.y) ** 2)
            if dist_to_target < best_dist:
                best_dist = dist_to_target
                best_pos = (tx, ty)

    if best_pos:
        print(f"[AI] {enemy.name} moving from ({enemy.x},{enemy.y}) to {best_pos}")
        return move_fn(enemy, *best_pos)  # Only move once, here.

    return False
