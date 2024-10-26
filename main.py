import pygame
import random

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
font = pygame.font.Font(None, 36)

# Load grenade image
grenade_img = pygame.image.load('img/player/grenade.png')

health_box_img = pygame.image.load('img/icons/health_box.png')
health_box_img = pygame.transform.scale(health_box_img, (health_box_img.get_width() // 1.5, health_box_img.get_height() // 1.5))

grenade_box_img = pygame.image.load('img/icons/grenade_box.png')
grenade_box_img = pygame.transform.scale(grenade_box_img, (grenade_box_img.get_width() // 1.5, grenade_box_img.get_height() // 1.5))

ammo_box_img = pygame.image.load('img/icons/ammo_box.png')
ammo_box_img = pygame.transform.scale(ammo_box_img, (ammo_box_img.get_width() // 1.5, ammo_box_img.get_height() // 1.5))

item_boxes = {
    'Health': health_box_img,
    'Grenade': grenade_box_img,
    'Ammo': ammo_box_img
}

# Background color
BG = (144, 201, 120)

# Load images
bullet_img = pygame.image.load('img/icons/bullet.png')
bullet_img = pygame.transform.scale(bullet_img, (bullet_img.get_width() * 2, bullet_img.get_height() * 2))
bullet_img_transparent = bullet_img.copy()
bullet_img_transparent.set_alpha(100)

grenade_img = pygame.image.load('img/icons/grenade.png')
grenade_img = pygame.transform.scale(grenade_img, (grenade_img.get_width() * 1.5, grenade_img.get_height() * 1.5))
grenade_img_transparent = grenade_img.copy()
grenade_img_transparent.set_alpha(100)

def draw_ammo(ammo, max_ammo):
    for i in range(max_ammo):
        if i < ammo:
            screen.blit(bullet_img, (10 + i * (bullet_img.get_width() - 2), 10))
        else:
            screen.blit(bullet_img_transparent, (10 + i * (bullet_img.get_width() - 2), 10))

def draw_grenades(grenades, max_grenades):
    for i in range(max_grenades):
        if i < grenades:
            screen.blit(grenade_img, (10 + i * (grenade_img.get_width() + 5), 35))
        else:
            screen.blit(grenade_img_transparent, (10 + i * (grenade_img.get_width() + 5), 35))

# Function to draw the background
def draw_bg():
    screen.fill(BG)


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.shoot_cooldown = 0
        self.char_type = char_type
        self.speed = speed / 3 if char_type == 'enemy' else speed
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.jump_list = []
        self.static_list = []
        self.shoot_list = []
        self.death_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.jumping = False
        self.in_air = True
        self.vel_y = 0
        self.alive = True
        self.ammo = 20
        self.max_ammo = 20
        self.health = 100
        self.max_health = self.health
        self.death_animation_played = False
        self.grenades = 3
        self.max_grenades = 3
        self.idling = False
        self.idling_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.move_limit = 100
        self.last_dropped_item = None

        # Параметры патрулирования
        self.patrol_start = x - 200
        self.patrol_end = x + 200
        self.patrol_direction = 1

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
            self.image = self.animation_list[self.frame_index]

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

        # Load all images for the shooting animation
        img = pygame.image.load(f'img/{self.char_type}/shooting.png')
        for i in range(2):
            frame = img.subsurface(pygame.Rect(i * img.get_width() // 2, 0, img.get_width() // 2, img.get_height()))
            frame = pygame.transform.scale(frame, (int(frame.get_width() * scale), int(frame.get_height() * scale)))
            self.shoot_list.append(frame)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20  # Cooldown period before the next shot
            bullet_x = self.rect.centerx + (0.5 * self.rect.size[0] * self.direction)  # Adjust the bullet's x position
            bullet_y = self.rect.centery + 12  # Adjust the bullet's y position
            bullet = Bullet(self.char_type, bullet_x, bullet_y, self.direction, 0.5)
            bullet_group.add(bullet)
            self.ammo -= 1
            self.frame_index = 0
            self.action = 1  # Set action to shooting
            self.update_animation()

    def ai(self):
        if self.alive and player.alive:
            self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

            if self.vision.colliderect(player.rect):
                self.shoot()
            else:
                if not self.idling and random.randint(1, 200) == 1:
                    self.idling = True
                    self.idling_counter = 50

                if not self.idling:
                    if self.rect.left <= self.patrol_start:
                        self.patrol_direction = 1
                    elif self.rect.right >= self.patrol_end:
                        self.patrol_direction = -1

                    moving_left = self.patrol_direction == -1
                    moving_right = self.patrol_direction == 1

                    self.move(moving_left, moving_right, False)  # Pass movement state

                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

            if self.alive:
                if self.action == 1:  # Shooting action
                    if self.frame_index >= len(self.shoot_list):
                        self.frame_index = 0
                        self.action = 0  # Reset to default action after shooting
                    self.image = self.shoot_list[self.frame_index]

                elif self.jumping:
                    if self.frame_index >= len(self.jump_list):
                        self.frame_index = 0
                    self.image = self.jump_list[self.frame_index]

                elif self.moving_left or self.moving_right:
                    if self.frame_index >= len(self.animation_list):
                        self.frame_index = 0
                    self.image = self.animation_list[self.frame_index]
                else:
                    if self.frame_index >= len(self.static_list):
                        self.frame_index = 0
                    self.image = self.static_list[self.frame_index]

            else:  # Enemy is dead
                if self.frame_index >= len(self.death_list):
                    self.death_animation_played = True
                    self.rect = pygame.Rect(0, 0, 0, 0)  # Remove hitbox
                else:
                    self.image = self.death_list[self.frame_index]

    def move(self, moving_left, moving_right, jumping):
        if self.alive:
            dx = 0
            dy = 0
            GRAVITY = 0.75

            self.moving_left = moving_left
            self.moving_right = moving_right

            if moving_left or moving_right:
                if moving_left:
                    dx = -self.speed
                    self.flip = True
                    self.direction = -1
                    self.update_animation()  # Update animation when moving left
                if moving_right:
                    dx = self.speed
                    self.flip = False
                    self.direction = 1
                    self.update_animation()  # Update animation when moving right

            else:
                self.update_animation()  # Update animation if standing still

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


    def draw(self):
        if self.alive or not self.death_animation_played:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            # Draw a rectangle to visualize the hitbox
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def take_damage(self, amount):
        if self.alive:
            self.health -= amount
            print(f"{self.char_type.capitalize()} health: {self.health}")
            if self.health <= 0:
                self.health = 0
                self.alive = False
                self.frame_index = 0
                self.update_time = pygame.time.get_ticks()

                # Drop a random item box upon death
                if self.char_type == 'enemy':
                    possible_items = ['Health', 'Ammo', 'Grenade']
                    if self.last_dropped_item in possible_items:
                        possible_items.remove(self.last_dropped_item)
                    item_type = random.choice(possible_items)
                    self.last_dropped_item = item_type
                    item_box = ItemBox(item_type, self.rect.centerx, self.rect.centery)
                    item_box_group.add(item_box)



class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, SCREEN_HEIGHT - 50 - self.image.get_height())  # Drop on the ground

    def update(self):
        # Check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                if player.health < player.max_health:
                    player.health += 25
                    if player.health > player.max_health:
                        player.health = player.max_health
                    self.kill()
            elif self.item_type == 'Grenade':
                if player.grenades < player.max_grenades:
                    player.grenades += 3
                    if player.grenades > player.max_grenades:
                        player.grenades = player.max_grenades
                    self.kill()
            elif self.item_type == 'Ammo':
                if player.ammo < player.max_ammo:
                    player.ammo += 20
                    if player.ammo > player.max_ammo:
                        player.ammo = player.max_ammo
                    self.kill()

class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        # Draw health bar
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, (0, 0, 0), (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 150 * ratio, 20))


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
            if self.char_type == 'enemy':
                frame = pygame.transform.scale(frame, (int(frame.get_width() * scale * 5), int(frame.get_height() * scale * 5)))
            else:
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
        self.bounce = 0.35


    def update(self):
        # Grenade movement
        self.vel_y += 0.75
        dx = self.direction * self.speed
        dy = self.vel_y

        # Check for collision with the ground
        if self.rect.bottom + dy > SCREEN_HEIGHT - 50:
            dy = SCREEN_HEIGHT - 50 - self.rect.bottom
            self.vel_y = -self.vel_y * self.bounce
            self.speed *= self.bounce

        # Check for collision with the walls
        self.rect.x += dx
        self.rect.y += dy

        # Reduce the timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            explosion_group.add(explosion)
            # Deal damage to anyone who is nearby
            if pygame.sprite.spritecollide(self, [player], False, collided=lambda s1, s2: pygame.Rect(s1.rect.x - 75, s1.rect.y - 75, s1.rect.width + 150, s1.rect.height + 150).colliderect(s2.rect)):
                player.take_damage(50)
            if pygame.sprite.spritecollide(self, [enemy], False, collided=lambda s1, s2: pygame.Rect(s1.rect.x - 75, s1.rect.y - 75, s1.rect.width + 150, s1.rect.height + 150).colliderect(s2.rect)):
                enemy.take_damage(100)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png')
            img = pygame.transform.scale(img, (150, 150))
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


# Create a group for enemies
enemy_group = pygame.sprite.Group()

# Create player and enemy soldiers
player = Soldier('player', 200, 200, 3, 5)
enemy1 = Soldier('enemy', 300, 200, 3, 5)
enemy2 = Soldier('enemy', 400, 200, 3, 5)
enemy3 = Soldier('enemy', 500, 200, 3, 5)
enemy4 = Soldier('enemy', 600, 200, 3, 5)

# Add enemies to the group
enemy_group.add(enemy1)
enemy_group.add(enemy2)
enemy_group.add(enemy3)
enemy_group.add(enemy4)

health_bar = HealthBar(10, 65, player.health, player.max_health)

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
# Group to manage
item_box_group = pygame.sprite.Group()

#temp - create item
item_box = ItemBox('Health', 400, SCREEN_HEIGHT - 130)
item_box_group.add(item_box)
item_box = ItemBox('Grenade', 300, SCREEN_HEIGHT - 130)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 200, SCREEN_HEIGHT - 130)
item_box_group.add(item_box)

# Main game loop
run = True
while run:
    clock.tick(FPS)
    draw_bg()

    # Draw health bar
    health_bar.draw(player.health)
    player.draw()
    player.move(moving_left, moving_right, jumping)

    # Update and draw enemies
    for enemy in enemy_group:
        enemy.ai()
        enemy.update_animation()
        enemy.draw()
        enemy.update()

    # Update and draw bullets
    bullet_group.update()
    bullet_group.draw(screen)

    # Update and draw grenades
    grenade_group.update()
    grenade_group.draw(screen)

    # Update and draw explosions
    explosion_group.update()
    explosion_group.draw(screen)

    # Update and draw item boxes
    item_box_group.update()
    item_box_group.draw(screen)

    # Check for bullet collisions
    for bullet in bullet_group:
        if bullet.char_type == 'player':
            for enemy in enemy_group:
                if pygame.sprite.collide_rect(bullet, enemy):
                    print(f"Bullet hit enemy: {bullet.rect}")
                    enemy.take_damage(35)
                    bullet.kill()
        elif bullet.char_type == 'enemy':
            if pygame.sprite.collide_rect(bullet, player):
                print(f"Bullet hit player: {bullet.rect}")
                player.take_damage(10)
                bullet.kill()

    # Update player animation
    player.update_animation()

    # Draw ammo and grenade count
    draw_ammo(player.ammo, player.max_ammo)
    draw_grenades(player.grenades, player.max_grenades)

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