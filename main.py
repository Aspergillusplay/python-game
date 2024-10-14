import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the window title
pygame.display.set_caption('Shooter')

# Set up the clock for managing the frame rate
clock = pygame.time.Clock()
FPS = 60

pygame.font.init()
font = pygame.font.Font(None, 36)  # Use default font and size 36

grenade_img = pygame.image.load('img/player/grenade.png')
# Background color
BG = (144, 201, 120)

def draw_ammo(ammo):
    ammo_text = font.render(f'Ammo: {ammo}', True, (0, 0, 0))  # Render text in black color
    screen.blit(ammo_text, (10, SCREEN_HEIGHT - 40))  # Position text in the bottom left corner

# Function to draw the background
def draw_bg():
    screen.fill(BG)

# Class representing a soldier character
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.jump_list = []
        self.static_list = []
        self.death_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.jumping = False
        self.in_air = True
        self.vel_y = 0
        self.alive = True
        self.ammo = 30
        self.health = 100
        self.max_health = self.health
        self.death_animation_played = False
        self.grenades = 3  # Initialize with 3 grenades

        # Load all images for the running animation
        img = pygame.image.load(f'img/{self.char_type}/run.png')
        for i in range(10):
            frame = img.subsurface(pygame.Rect(i * img.get_width() // 10, 0, img.get_width() // 10, img.get_height()))
            frame = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))
            self.animation_list.append(frame)

        # Load all images for the jumping animation (only for player)
        if self.char_type == 'player':
            img = pygame.image.load(f'img/{self.char_type}/jump.png')
            for i in range(9):
                frame = img.subsurface(pygame.Rect(i * img.get_width() // 9, 0, img.get_width() // 9, img.get_height()))
                frame = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))
                self.jump_list.append(frame)

        # Load all images for the static animation (only for player)
        if self.char_type == 'player':
            img = pygame.image.load(f'img/{self.char_type}/static.png')
            for i in range(5):
                frame = img.subsurface(pygame.Rect(i * img.get_width() // 5, 0, img.get_width() // 5, img.get_height()))
                frame = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))
                self.static_list.append(frame)
            self.image = self.static_list[self.frame_index]
        else:
            self.static_image = pygame.image.load(f'img/{self.char_type}/static.png')
            self.static_image = pygame.transform.scale(self.static_image, (int(self.static_image.get_width() * scale), int(self.static_image.get_height() * scale)))
            self.image = self.static_image

        # Load all images for the death animation
        if self.char_type == 'player':
            img = pygame.image.load(f'img/{self.char_type}/death.png')
            for i in range(10):
                frame = img.subsurface(pygame.Rect(i * img.get_width() // 10, 0, img.get_width() // 10, img.get_height()))
                frame = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))
                self.death_list.append(frame)
        else:
            img = pygame.image.load(f'img/{self.char_type}/death.png')
            for i in range(12):
                frame = img.subsurface(pygame.Rect(i * img.get_width() // 12, 0, img.get_width() // 12, img.get_height()))
                frame = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))
                self.death_list.append(frame)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    # Update the animation of the soldier
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.alive:
                if self.jumping:
                    if self.frame_index >= len(self.jump_list):
                        self.frame_index = 0
                    self.image = self.jump_list[self.frame_index]
                elif self.char_type == 'player' and not self.jumping and not self.in_air and not (moving_left or moving_right):
                    if self.frame_index >= len(self.static_list):
                        self.frame_index = 0
                    self.image = self.static_list[self.frame_index]
                else:
                    if self.frame_index >= len(self.animation_list):
                        self.frame_index = 0
                    self.image = self.animation_list[self.frame_index]
            else:
                if self.frame_index >= len(self.death_list):
                    self.death_animation_played = True
                    self.rect = pygame.Rect(0, 0, 0, 0)  # Remove hitbox
                else:
                    self.image = self.death_list[self.frame_index]

    # Move the soldier
    def move(self, moving_left, moving_right, jumping):
        if self.alive:
            dx = 0
            dy = 0
            GRAVITY = 0.75

            if self.char_type == 'player':
                if moving_left or moving_right:
                    if moving_left:
                        dx = -self.speed
                        self.flip = True
                        self.direction = -1
                    if moving_right:
                        dx = self.speed
                        self.flip = False
                        self.direction = 1
                    if not self.jumping:
                        self.update_animation()
                else:
                    if not self.jumping:
                        self.update_animation()

                if jumping and not self.jumping and not self.in_air:
                    self.jumping = True
                    self.in_air = True
                    self.vel_y = -15
                    self.frame_index = 0
                    self.update_time = pygame.time.get_ticks()

            self.vel_y += GRAVITY
            dy += self.vel_y

            if self.rect.bottom + dy > SCREEN_HEIGHT - 50:
                dy = SCREEN_HEIGHT - 50 - self.rect.bottom
                self.in_air = False
                self.jumping = False

            self.rect.x += dx
            self.rect.y += dy

            if self.jumping:
                self.update_animation()

    # Draw the soldier on the screen
    def draw(self):
        if self.alive or not self.death_animation_played:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            # Draw a rectangle to visualize the hitbox
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    # Reduce the soldier's health
    def take_damage(self, amount):
        if self.alive:
            self.health -= amount
            print(f"{self.char_type.capitalize()} health: {self.health}")
            if self.health <= 0:
                self.health = 0
                self.alive = False
                self.frame_index = 0
                self.update_time = pygame.time.get_ticks()

# Class representing a bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, direction, scale):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.direction = direction
        self.speed = 10
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # Load all images for the bullet animation
        img = pygame.image.load(f'img/{self.char_type}/bullet.png')
        for i in range(7):
            frame = img.subsurface(pygame.Rect(i * img.get_width() // 7, 0, img.get_width() // 7, img.get_height()))
            frame = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))
            self.animation_list.append(frame)

        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # Move the bullet
        self.rect.x += self.direction * self.speed

        # Check if the bullet is off the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # Update animation
        ANIMATION_COOLDOWN = 50
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
            self.image = self.animation_list[self.frame_index]

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # Apply gravity
        self.vel_y += 0.75
        dx = self.direction * self.speed
        dy = self.vel_y

        # Check for collision with the ground
        if self.rect.bottom + dy > SCREEN_HEIGHT - 50:
            dy = SCREEN_HEIGHT - 50 - self.rect.bottom
            self.speed = 0

        # Update grenade position
        self.rect.x += dx
        self.rect.y += dy

        # Countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            explosion_group.add(explosion)
            # Check for collision with player or enemy
            if pygame.sprite.collide_rect(self, player):
                player.take_damage(100)
            if pygame.sprite.collide_rect(self, enemy):
                enemy.take_damage(100)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png')
            img = pygame.transform.scale(img, (100, 100))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

# Create player and enemy soldiers
player = Soldier('player', 200, 200, 3, 5)
enemy = Soldier('enemy', 400, 200, 3, 5)

# Group to manage bullets
bullet_group = pygame.sprite.Group()

# Movement flags
moving_left = False
moving_right = False
jumping = False
# Group to manage grenades
grenade_group = pygame.sprite.Group()
# Group to manage explosions
explosion_group = pygame.sprite.Group()
# Main game loop
run = True
while run:
    clock.tick(FPS)
    draw_bg()
    player.draw()
    enemy.draw()
    player.move(moving_left, moving_right, jumping)
    enemy.move(False, False, False)  # Move the enemy

    # Update and draw bullets
    bullet_group.update()
    bullet_group.draw(screen)

    # Update and draw grenades
    grenade_group.update()
    grenade_group.draw(screen)

    # Update and draw explosions
    explosion_group.update()
    explosion_group.draw(screen)

    # Check for bullet collisions
    for bullet in bullet_group:
        if bullet.char_type == 'player':
            if pygame.sprite.collide_rect(bullet, enemy):
                print(f"Bullet hit enemy: {bullet.rect}")
                enemy.take_damage(10)
                bullet.kill()
        elif bullet.char_type == 'enemy':
            if pygame.sprite.collide_rect(bullet, player):
                print(f"Bullet hit player: {bullet.rect}")
                player.take_damage(10)
                bullet.kill()

    # Update player and enemy animations
    player.update_animation()
    enemy.update_animation()

    # Draw ammo count
    draw_ammo(player.ammo)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                jumping = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_g and player.grenades > 0:
                grenade = Grenade(player.rect.centerx, player.rect.centery, player.direction)
                grenade_group.add(grenade)
                player.grenades -= 1
                print(f"Grenade thrown: {grenade.rect}")

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                jumping = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.alive and player.ammo > 0:
            bullet_x = player.rect.centerx + (25 if player.direction == 1 else -25)
            bullet = Bullet('player', bullet_x, player.rect.centery + 12, player.direction, 1.5)
            bullet_group.add(bullet)
            player.ammo -= 1
            print(f"Bullet created at: {bullet.rect}")

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()