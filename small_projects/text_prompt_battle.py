import random as r


player_health = 100
enemy_health = 100
# Each move stores a tuple which represents changes in health to the user [0] and the target [1]
moves = {"normal": (0, -20), 
         "special": (5, -10), 
         "heal": (15, 0), 
         "last stand": (-15, -30)}
moves_keys = list(moves.keys()) # So we can access keys with indices later


def report(player_health, enemy_health):
    print(f"""
    Player health: {player_health}
    Enemy health: {enemy_health}
    """)


def check_game_over(player_health, enemy_health):
    if player_health <= 0 and enemy_health > 0:
        print("GAME OVER: Enemy wins.")
        return False
    elif enemy_health <= 0 and player_health > 0:
        print("GAME OVER: Player wins.")
        return False
    elif enemy_health <= 0 and player_health <= 0:
        print("DRAW.")
        return False
    else:
        return True


current_turn = 1
# Game loop
running = True

while running:
    # Player turn
    if current_turn == 1:
        print("PLAYER TURN")
        valid_input = False
        while valid_input == False: # Check that player move input is valid
            player_input = input("Select move... \n")
            valid_input = player_input.lower() in moves_keys or player_input.lower() == 'quit'
            if not valid_input:
                print("Invalid move. Try again.")
        # Allow player to quit the game.
        if player_input.lower() == 'quit':
            running = False
            break
        selected = moves[player_input.lower()]
        print("You selected: ", player_input)
        player_health += selected[0] # Adjust player and enemy health based on selected move
        enemy_health += selected[1]
        report(player_health, enemy_health)
        running = check_game_over(player_health, enemy_health)
    # Enemy turn
    elif current_turn == -1:
        print("ENEMY TURN")
        enemy_input = r.randint(0, 3)
        selected = moves[moves_keys[enemy_input]] # Get element at index
        print("Enemy selected: ", moves_keys[enemy_input])
        enemy_health += selected[0]
        player_health += selected[1]
        report(player_health, enemy_health)
        running = check_game_over(player_health, enemy_health)
    # Turn swap
    current_turn *= -1
