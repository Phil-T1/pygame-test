import pygame
import math
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 80
PLAYER_SPEED = 5
JUMP_FORCE = -15
GRAVITY = 0.8

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.is_jumping = False
        self.is_crouching = False
        self.direction = "right"

    def update(self):
        # Gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Ground collision
        if self.rect.bottom > WINDOW_HEIGHT - 50:  # Ground level
            self.rect.bottom = WINDOW_HEIGHT - 50
            self.velocity_y = 0
            self.is_jumping = False

        # Handle crouching
        if self.is_crouching and not self.is_jumping:
            self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT // 2])
            self.image.fill(RED)
        else:
            self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
            self.image.fill(RED)

class Gun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([30, 10])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.angle = 0
        self.ammo = 30
        self.max_ammo = 30

    def update(self):
        # Position gun relative to player
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        self.angle = math.degrees(math.atan2(-dy, dx))

        # Rotate gun image
        self.image = pygame.transform.rotate(pygame.Surface([30, 10]), self.angle)
        self.image.fill(BLACK)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pixel Art Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.background_x = 0

        # Create sprites
        self.player = Player(WINDOW_WIDTH // 4, WINDOW_HEIGHT - 130)
        self.gun = Gun()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.gun)

        # Set custom cursor
        pygame.mouse.set_visible(False)
        self.crosshair = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.crosshair, WHITE, (10, 10), 10, 1)
        pygame.draw.line(self.crosshair, WHITE, (0, 10), (20, 10), 1)
        pygame.draw.line(self.crosshair, WHITE, (10, 0), (10, 20), 1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.shoot()
                elif event.button == 3:  # Right click
                    self.reload()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and not self.player.is_jumping:
                    self.player.velocity_y = JUMP_FORCE
                    self.player.is_jumping = True
                elif event.key == pygame.K_s:
                    self.player.is_crouching = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    self.player.is_crouching = False

    def shoot(self):
        if self.gun.ammo > 0:
            self.gun.ammo -= 1
            # Add shooting logic here

    def reload(self):
        self.gun.ammo = self.gun.max_ammo

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_a]:
            self.player.rect.x -= PLAYER_SPEED
            self.player.direction = "left"
            self.background_x += 1
        if keys[pygame.K_d]:
            self.player.rect.x += PLAYER_SPEED
            self.player.direction = "right"
            self.background_x -= 1

        # Keep player in bounds
        if self.player.rect.left < 0:
            self.player.rect.left = 0
        if self.player.rect.right > WINDOW_WIDTH:
            self.player.rect.right = WINDOW_WIDTH

        # Update sprites
        self.all_sprites.update()
        
        # Update gun position to follow player
        self.gun.rect.centerx = self.player.rect.centerx
        self.gun.rect.centery = self.player.rect.centery

    def draw(self):
        self.screen.fill((100, 100, 255))  # Sky blue background

        # Draw scrolling ground
        ground_color = (50, 150, 50)  # Green ground
        pygame.draw.rect(self.screen, ground_color, 
                        (0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, 50))

        # Draw background elements that scroll
        for i in range(-1, WINDOW_WIDTH // 100 + 2):
            x_pos = (i * 100 + self.background_x) % WINDOW_WIDTH
            pygame.draw.rect(self.screen, (70, 40, 0), 
                           (x_pos, WINDOW_HEIGHT - 150, 30, 100))

        self.all_sprites.draw(self.screen)

        # Draw crosshair at mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.screen.blit(self.crosshair, 
                        (mouse_pos[0] - 10, mouse_pos[1] - 10))

        # Draw ammo counter
        font = pygame.font.Font(None, 36)
        ammo_text = font.render(f"Ammo: {self.gun.ammo}/{self.gun.max_ammo}", 
                               True, WHITE)
        self.screen.blit(ammo_text, (10, 10))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
