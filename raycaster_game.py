import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# World map
world_map = [
    '####################',
    '#                  #',
    '#                  #',
    '#                  #',
    '######            #',
    '#                  #',
    '#                  #',
    '####################'
]

# Player settings
player_pos = [5.0, 5.0]
player_angle = 0.0
player_speed = 0.05
player_rot_speed = 0.03

# Function to draw the player
def draw_player(screen, player_pos):
    pygame.draw.circle(screen, WHITE, (int(player_pos[0]*50), int(player_pos[1]*50)), 5)

# Function to cast rays
def cast_rays(screen):
    for ray_angle in range(-30, 30):  # Casting rays in 60 degrees
        ray_angle_rad = math.radians(ray_angle + player_angle)
        for depth in range(1, 20):
            ray_x = player_pos[0] + depth * math.cos(ray_angle_rad)
            ray_y = player_pos[1] + depth * math.sin(ray_angle_rad)
            if world_map[int(ray_y)][int(ray_x)] == '#':
                break
        # Draw the ray
        pygame.draw.line(screen, WHITE, 
                         (int(player_pos[0]*50), int(player_pos[1]*50)), 
                         (int(ray_x*50), int(ray_y*50)), 1)

# Main game loop
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Raycasting Game')
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:  # Move forward
            player_pos[0] += player_speed * math.cos(player_angle)
            player_pos[1] += player_speed * math.sin(player_angle)
        if keys[pygame.K_s]:  # Move backward
            player_pos[0] -= player_speed * math.cos(player_angle)
            player_pos[1] -= player_speed * math.sin(player_angle)
        if keys[pygame.K_a]:  # Rotate left
            player_angle -= player_rot_speed
        if keys[pygame.K_d]:  # Rotate right
            player_angle += player_rot_speed

        cast_rays(screen)
        draw_player(screen, player_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()