import pygame
import math

# Initialize Pygame and screen dimensions
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors and textures
TEXTURE_SIZE = 64
textures = [pygame.transform.scale(pygame.image.load(f'texture_{i}.png'), (TEXTURE_SIZE, TEXTURE_SIZE)) for i in range(1, 5)]

# Map layout (0 = empty, 1 = wall)
world_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Player attributes
player_pos = [1.5, 1.5]
player_angle = 0.

def cast_rays():
    for ray in range(0, WIDTH):
        # Calculate angle for the ray
        angle = player_angle - (math.pi / 6) + (ray / WIDTH) * (math.pi / 3)
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        # Ray casting logic
        for depth in range(0, 20):
            x = player_pos[0] + cos_a * depth
            y = player_pos[1] + sin_a * depth
            if int(x) < len(world_map) and int(y) < len(world_map[0]) and world_map[int(y)][int(x)] == 1:
                depth_proj = depth * math.cos(player_angle - angle)
                height = int(HEIGHT / (depth_proj + 0.0001))
                color = (255, 255, 255)  # Wall color (change as needed)
                texture = textures[0]  # Assuming wall texture 0 for demonstration
                # Wall rendering
                pygame.draw.rect(screen, color, (ray, HEIGHT // 2 - height // 2, 1, height))
                break

def main():
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        cast_rays()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()