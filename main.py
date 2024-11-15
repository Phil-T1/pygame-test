import pygame
import math
import os
import random

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 80
PLAYER_SPEED = 5
JUMP_FORCE = -15
GRAVITY = 0.8

# Projectile settings
PROJECTILE_SPEED = 15
PROJECTILE_SIZE = 5

# Sound effects
class GameSounds:
    def __init__(self):
        # Load sound effects
        self.fire = pygame.mixer.Sound('sounds/fire.mp3')
        self.reload = pygame.mixer.Sound('sounds/reload.mp3')
        self.thump = pygame.mixer.Sound('sounds/thump.mp3')
        
        # Set volume
        self.fire.set_volume(0.3)
        self.reload.set_volume(0.4)
        self.thump.set_volume(1.2)
    
    def play_fire(self):
        self.fire.stop()  # Stop any currently playing fire sound
        self.fire.play()
    
    def play_reload(self):
        self.reload.stop()  # Stop any currently playing reload sound
        self.reload.play()
    
    def play_thump(self):
        self.thump.stop()  # Stop any currently playing thump sound
        self.thump.play()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, sounds):
        super().__init__()
        self.image = pygame.Surface([PROJECTILE_SIZE, PROJECTILE_SIZE])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.sounds = sounds
        
        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        self.velocity_x = (dx / distance) * PROJECTILE_SPEED
        self.velocity_y = (dy / distance) * PROJECTILE_SPEED
        
        # Store position as float for precise movement
        self.float_x = float(x)
        self.float_y = float(y)
        
        # Track previous position for ground collision
        self.prev_y = y

    def update(self):
        # Store previous position
        self.prev_y = self.rect.bottom
        
        # Update position using float values for smooth movement
        self.float_x += self.velocity_x
        self.float_y += self.velocity_y
        
        # Store old position for collision check
        old_bottom = self.rect.bottom
        
        # Update rect position
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)
        
        # Check for ground collision
        if self.rect.bottom >= WINDOW_HEIGHT - 50:
            # Only play sound if we just hit the ground this frame
            if old_bottom < WINDOW_HEIGHT - 50:
                self.sounds.play_thump()
            self.kill()
        # Check for other boundaries
        elif (self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or 
              self.rect.bottom < 0):
            self.kill()

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
        
        # Load images
        self.sun = pygame.image.load('images/sun.png')
        self.sun = pygame.transform.scale(self.sun, (100, 100))
        self.trees = [
            pygame.image.load('images/tree-1.png'),
            pygame.image.load('images/tree-2.png'),
            pygame.image.load('images/tree-3.png')
        ]
        
        # Position sun in top right corner
        self.sun_rect = self.sun.get_rect()
        self.sun_rect.topright = (WINDOW_WIDTH - 20, 20)
        
        # Store tree positions and variants
        self.tree_positions = []
        for i in range(-1, WINDOW_WIDTH // 100 + 2):
            self.tree_positions.append({
                'x': i * 100,
                'variant': random.randint(0, 2)
            })
        
        # Initialize sounds
        self.sounds = GameSounds()

        # Create sprites
        self.player = Player(WINDOW_WIDTH // 4, WINDOW_HEIGHT - 80)
        self.gun = Gun()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
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
            mouse_x, mouse_y = pygame.mouse.get_pos()
            projectile = Projectile(self.gun.rect.centerx, self.gun.rect.centery, 
                                  mouse_x, mouse_y, self.sounds)
            self.projectiles.add(projectile)
            self.all_sprites.add(projectile)
            self.sounds.play_fire()

    def reload(self):
        self.gun.ammo = self.gun.max_ammo
        self.sounds.play_reload()

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_a]:
            self.player.rect.x -= PLAYER_SPEED
            self.player.direction = "left"
            self.background_x += 1
            # Update tree positions
            for tree in self.tree_positions:
                tree['x'] += 1
        if keys[pygame.K_d]:
            self.player.rect.x += PLAYER_SPEED
            self.player.direction = "right"
            self.background_x -= 1
            # Update tree positions
            for tree in self.tree_positions:
                tree['x'] -= 1

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
        
        # Add new trees as needed
        while self.tree_positions[0]['x'] + 100 < 0:
            self.tree_positions.pop(0)
            new_x = self.tree_positions[-1]['x'] + 100
            self.tree_positions.append({
                'x': new_x,
                'variant': random.randint(0, 2)
            })
        while self.tree_positions[-1]['x'] > WINDOW_WIDTH:
            self.tree_positions.pop()
            new_x = self.tree_positions[0]['x'] - 100
            self.tree_positions.insert(0, {
                'x': new_x,
                'variant': random.randint(0, 2)
            })

    def draw(self):
        self.screen.fill((100, 100, 255))  # Sky blue background
        
        # Draw sun (fixed position)
        self.screen.blit(self.sun, self.sun_rect)

        # Draw scrolling ground
        ground_color = (50, 150, 50)  # Green ground
        pygame.draw.rect(self.screen, ground_color, 
                        (0, WINDOW_HEIGHT - 55, WINDOW_WIDTH, 50))

        # Draw trees with different variants
        for tree in self.tree_positions:
            x = tree['x']
            variant = tree['variant']
            self.screen.blit(self.trees[variant], (x, WINDOW_HEIGHT - 180))

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
