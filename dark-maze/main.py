import pygame
import random
import sys

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dark Maze")
clock = pygame.time.Clock()

# Load essential assets
ASSETS = {
    "player": pygame.transform.scale(pygame.image.load("assets/sprites/player.png"), (TILE_SIZE, TILE_SIZE)),
    "exit": pygame.transform.scale(pygame.image.load("assets/sprites/exit.png"), (TILE_SIZE, TILE_SIZE)),
    "font": "assets/fonts/PressStart2P-Regular.ttf",
}

font_large = pygame.font.Font(ASSETS["font"], 36)
font_medium = pygame.font.Font(ASSETS["font"], 24)
font_small = pygame.font.Font(ASSETS["font"], 16)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Maze setup
ROWS = HEIGHT // TILE_SIZE
COLS = WIDTH // TILE_SIZE

def generate_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    stack = [(0, 0)]
    maze[0][0] = 0

    while stack:
        r, c = stack[-1]
        directions = [(0,2), (0,-2), (2,0), (-2,0)]
        random.shuffle(directions)
        moved = False
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 1:
                maze[nr][nc] = 0
                maze[r + dr//2][c + dc//2] = 0
                stack.append((nr, nc))
                moved = True
                break
        if not moved:
            stack.pop()
    
    # Ensure the exit is reachable by clearing a path to it
    maze[rows-1][cols-1] = 0
    
    # Clear adjacent cells to ensure accessibility
    if cols > 1:
        maze[rows-1][cols-2] = 0
    if rows > 1:
        maze[rows-2][cols-1] = 0
    
    # If maze dimensions allow, create a small clear area around the exit
    if rows > 2 and cols > 2:
        maze[rows-2][cols-2] = 0
    
    return maze

def draw_menu():
    screen.fill((10, 10, 10))
    
    # Title
    title = font_large.render("DARK MAZE", True, (255, 255, 100))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    
    # How to play section
    instructions = [
        "HOW TO PLAY:",
        "",
        "• Use ARROW KEYS to move",
        "• Navigate through the dark maze",
        "• You can only see nearby tiles",
        "• Reach the EXIT before time runs out",
        "• You have 60 seconds to escape!",
        "",
        "CONTROLS:",
        "↑ ↓ ← → : Move player",
        "R : Restart game"
    ]
    
    y_offset = 180
    for i, instruction in enumerate(instructions):
        if instruction == "HOW TO PLAY:" or instruction == "CONTROLS:":
            text = font_medium.render(instruction, True, (255, 200, 100))
        elif instruction == "":
            y_offset += 10
            continue
        else:
            text = font_small.render(instruction, True, (200, 200, 200))
        
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 25
    
    # Start button
    button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 120, 300, 60)
    pygame.draw.rect(screen, (50, 50, 100), button_rect)
    pygame.draw.rect(screen, (100, 100, 200), button_rect, 3)
    
    start_text = font_medium.render("PRESS SPACE TO START", True, (255, 255, 255))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 105))
    
    return button_rect

def draw_maze(maze, player_pos):
    screen.fill((10, 10, 10))
    pr, pc = player_pos
    for r in range(ROWS):
        for c in range(COLS):
            dist = abs(pr - r) + abs(pc - c)
            if dist <= 4:
                rect = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = (40, 40, 40) if maze[r][c] == 1 else (20, 20, 20)
                pygame.draw.rect(screen, color, rect)

    # Draw player
    screen.blit(ASSETS["player"], (pc * TILE_SIZE, pr * TILE_SIZE))

    # Draw exit (only when close enough to see it)
    exit_dist = abs(pr - (ROWS-1)) + abs(pc - (COLS-1))
    if exit_dist <= 4:
        screen.blit(ASSETS["exit"], ((COLS - 1) * TILE_SIZE, (ROWS - 1) * TILE_SIZE))

def draw_game_over(won):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    msg = "YOU WIN!" if won else "TIME'S UP!"
    text = font_large.render(msg, True, (255, 255, 100) if won else (255, 100, 100))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
    
    sub = font_medium.render("Press R to Restart", True, (255, 255, 255))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))
    
    menu_text = font_small.render("Press M for Menu", True, (200, 200, 200))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 60))

# Game state
game_state = MENU
maze = None
player_pos = [0, 0]
timer = 60
start_ticks = 0
won = False

# Game loop
while True:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    
    if game_state == MENU:
        draw_menu()
        
        if keys[pygame.K_SPACE]:
            game_state = PLAYING
            maze = generate_maze(ROWS, COLS)
            player_pos = [0, 0]
            start_ticks = pygame.time.get_ticks()
            won = False
    
    elif game_state == PLAYING:
        seconds = timer - (pygame.time.get_ticks() - start_ticks) // 1000
        
        # Player movement
        r, c = player_pos
        if keys[pygame.K_UP] and r > 0 and maze[r - 1][c] == 0:
            player_pos[0] -= 1
        if keys[pygame.K_DOWN] and r < ROWS - 1 and maze[r + 1][c] == 0:
            player_pos[0] += 1
        if keys[pygame.K_LEFT] and c > 0 and maze[r][c - 1] == 0:
            player_pos[1] -= 1
        if keys[pygame.K_RIGHT] and c < COLS - 1 and maze[r][c + 1] == 0:
            player_pos[1] += 1

        # Check win/lose conditions
        if player_pos[0] == ROWS - 1 and player_pos[1] == COLS - 1:
            won = True
            game_state = GAME_OVER
        elif seconds <= 0:
            won = False
            game_state = GAME_OVER

        # Draw game
        draw_maze(maze, player_pos)
        
        # Draw timer in top-right corner to avoid overlap
        timer_text = font_medium.render(f"Time: {max(0, seconds)}", True, (255, 255, 255))
        screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 10))
    
    elif game_state == GAME_OVER:
        draw_maze(maze, player_pos)
        
        # Draw timer in top-right corner (frozen)
        final_time = max(0, timer - (pygame.time.get_ticks() - start_ticks) // 1000)
        timer_text = font_medium.render(f"Time: {final_time}", True, (255, 255, 255))
        screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 10))
        
        draw_game_over(won)
        
        if keys[pygame.K_r]:
            game_state = PLAYING
            maze = generate_maze(ROWS, COLS)
            player_pos = [0, 0]
            start_ticks = pygame.time.get_ticks()
            won = False
        elif keys[pygame.K_m]:
            game_state = MENU
    
    pygame.display.flip()