import math
from res.character import evaluate_expression

def enemy_take_turn(enemy, all_units, attacks_data, move_fn):
    target = get_closest_enemy(enemy, all_units)
    if not target:
        print(f"{enemy.name} has no valid targets.")
        return True  # No targets = turn over

    dx = target.x - enemy.x
    dy = target.y - enemy.y
    distance = math.sqrt(dx**2 + dy**2)

    # Try to attack first if in range
    for attack_id in enemy.attack_ids:
        attack = attacks_data[str(attack_id)]
        if distance <= attack["range"]:
            total, breakdown = evaluate_expression(attack["damage"])
            print(f"[ENEMY ATTACK] {enemy.name} uses {attack['name']} on {target.name}")
            print(f"[ROLL] {breakdown} = {total}")
            print(f"[LOG] {enemy.name[0]}->{target.name[0]} ({total})")
            return True  # Attack completes the turn

    # Try to move closer if not in range
    moved = move_towards(enemy, target, move_fn)
    if moved:
        print(f"[ENEMY MOVE] {enemy.name} moved toward {target.name}")
        return True  # Moved = turn over

    # If no move or attack was possible
    print(f"[ENEMY STALLED] {enemy.name} could not move or attack")
    return True

def get_closest_enemy(enemy, units):
    opponents = [u for u in units if u.team != enemy.team]
    if not opponents:
        return None
    return min(opponents, key=lambda u: (u.x - enemy.x) ** 2 + (u.y - enemy.y) ** 2)

def move_towards(enemy, target, move_fn):
    best_dist = float("inf")
    best_pos = (enemy.x, enemy.y)

    for dx in range(-3, 4):
        for dy in range(-3, 4):
            tx = enemy.x + dx
            ty = enemy.y + dy
            if tx < 0 or ty < 0 or tx >= 16 or ty >= 16:
                continue
            dist = math.sqrt((tx - target.x) ** 2 + (ty - target.y) ** 2)
            if dist < best_dist and move_fn(enemy, tx, ty):
                return True

    return False
