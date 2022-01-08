import sys
import pygame
pygame.init()

screenX = 1280
screenY = 704
game_screen = pygame.display.set_mode((screenX, screenY))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        for i in range(1, 5):
            image = pygame.image.load("player right " + str(i) + ".png")
            self.images.append(image)

        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()

        self.move_x = 0
        self.move_y = 0

        self.is_jumping = False
        self.is_falling = False
        self.velocity = 9
        self.mass = 1
        self.force = 0

        self.health = 5
        self.damage = 0

    def jump(self):
        if self.is_jumping == False:
            self.is_jumping = True

    def move(self, stepsX, stepsY):
        self.move_x += stepsX

    def updateLocation(self):
        # move image right
        if self.move_x > 0:
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0
            self.image = self.images[self.image_index]

        # move image left
        elif self.move_x < 0:
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0
            self.image = pygame.transform.flip(
                self.images[self.image_index], True, False)

        if self.is_jumping:
            #force = (1/2) * (mass) * (velocity^2)
            self.force = (1/2) * self.mass * (self.velocity ** 2)
            self.move_y -= self.force
            self.velocity -= 1
            if self.velocity < 0:
                self.mass = -1

            #update the player's rect
            self.rect.y += self.move_y

            # if the player hits the ground, stop moving
            if self.rect.y >= (screenY - 64 - 72):
                # if self.rect.bottom == g.rect.top:
                self.is_jumping = False
                self.velocity = 9
                self.mass = 1
                
        ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False)
        platform_hit_list = pygame.sprite.spritecollide(self, platform_list, False)
        
        #landing on / hitting a platform
        for platform in platform_hit_list:
            if self.is_jumping:
                # approach from bottom
                if self.mass > 0:
                    if (self.rect.y < platform.rect.y + platform.rect.height) and (self.rect.y > platform.rect.y):
                        self.rect.y = platform.rect.y + platform.rect.height
                        self.mass = -1
                        self.velocity = 9
                        self.is_jumping = True
                        break
                # approaching from top
                elif self.mass < 0:
                    if self.rect.y + self.rect.height > platform.rect.y:
                        self.rect.y = platform.rect.y - self.rect.height + 2
                        self.is_jumping = False
                        self.velocity = 9
                        self.mass = 1

        #fall down from platform
        if len(platform_hit_list) == 0 and (self.is_jumping == False) and (self.rect.y < (screenY - 64 - 72 - 1)):
            self.velocity = 9
            self.mass = -1
            self.is_jumping = True

        # update player's rect
        self.rect.x += self.move_x

        # screen boundaries
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > (screenX - self.rect.width):
            self.rect.x = screenX - self.rect.width
            
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > (screenY - 64 - self.rect.height):
            self.rect.y = screenY - 64 - self.rect.height

        #reset move counters
        self.move_x = 0
        self.move_y = 0

    def enemy_collision(self):
        enemy_hit_list = pygame.sprite.spritecollide(self, enemy_list, False)
        
        # if the player and enemy are currently touching
        if self.damage == 0:
            for enemy in enemy_hit_list:
                if not self.rect.contains(enemy):
                    self.damage = self.rect.colliderect(enemy)
        if self.damage == 1:
            touching = self.rect.collidelist(enemy_hit_list)
            if touching == -1:
                self.damage = 0
                self.health -= 1
                print(self.health)

    def coin_collision(self):
        coin_hit_list = pygame.sprite.spritecollide(self, coin_list, False)
        for coin in coin_hit_list:
            coin_list.remove(coin)

    def final(self):
        key_hit_list = pygame.sprite.spritecollide(self, key_list, False)
        for key in key_hit_list:
            key_list.remove(key)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, l_boundary, r_boundary):
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        for i in range(1, 3):
            image = pygame.image.load("enemy " + str(i) + ".png")
            self.images.append(image)

        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.l_boundary = l_boundary
        self.r_boundary = r_boundary

        self.speed = 3
        # start off on a platform facing left
        self.facing_left = True

    def move(self):
        # move left
        if self.facing_left:
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0
            self.image = self.images[self.image_index]
            self.rect.x -= self.speed
            if self.rect.x < self.l_boundary:
                self.rect.x = self.l_boundary
                self.facing_left = False

        # move right
        else:
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0
            self.image = pygame.transform.flip(
                self.images[self.image_index], True, False)
            self.rect.x += self.speed
            if self.rect.x > self.r_boundary:
                self.rect.x = self.r_boundary
                self.facing_left = True

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Game:
    def enemy():
        enemy_list = pygame.sprite.Group()
        i = 0
        enemy_locations = []

        # locations (x, y) and the enemy's left and right boundary to make sure they
        #don't fall off their platform
        enemy_locations.append((160, 80, 0, 160))
        enemy_locations.append((224, 368, 64, 224))
        enemy_locations.append((1120, 188, 960, 1120))
        enemy_locations.append((1248, 592, 0, 1248))

        while i < len(enemy_locations):
            enemy = Enemy(enemy_locations[i][0], enemy_locations[i][1], enemy_locations[i][2],
                          enemy_locations[i][3])
            enemy_list.add(enemy)
            i += 1

        return enemy_list

    def ground(location_x, x, y):
        ground_list = pygame.sprite.Group()
        i = 0
        while i < len(location_x):
            ground = Platform(location_x[i], screenY - y, x, y, "tile 3.png")
            ground_list.add(ground)
            i += 1
        return ground_list

    def platform(x, y):
        platform_list = pygame.sprite.Group()
        platform_locations = []
        i = 0

        # locations (x, y) and tile type of each tile
        platform_locations.append((0, 2 * y, "8"))
        platform_locations.append((x, 2 * y, "8"))
        platform_locations.append((2 * x, 2 * y, "10"))

        platform_locations.append((3 * x, 3 * y + 80, "9"))
        platform_locations.append((4 * x, 3 * y + 80, "8"))
        platform_locations.append((5 * x, 3 * y + 80, "8"))
        platform_locations.append((6 * x, 3 * y + 80, "8"))
        platform_locations.append((7 * x, 3 * y + 80, "10"))

        platform_locations.append((x, (4 * y) + (2 * 80), "9"))
        platform_locations.append((2 * x, (4 * y) + (2 * 80), "8"))
        platform_locations.append((3 * x, (4 * y) + (2 * 80), "10"))

        platform_locations.append((5 * x, (5 * y) + (2 * 80) + 20, "9"))
        platform_locations.append((6 * x, (5 * y) + (2 * 80) + 20, "8"))
        platform_locations.append((7 * x, (5 * y) + (2 * 80) + 20, "8"))
        platform_locations.append((8 * x, (5 * y) + (2 * 80) + 20, "8"))
        platform_locations.append((9 * x, (5 * y) + (2 * 80) + 20, "10"))

        platform_locations.append((9 * x + 15, 4 * y - 20, "11"))

        platform_locations.append((11 * x, 3 * y - 40, "11"))

        platform_locations.append((13 * x, 3 * y - 40, "11"))

        platform_locations.append((15 * x, 4 * y - 20, "9"))
        platform_locations.append((16 * x, 4 * y - 20, "8"))
        platform_locations.append((17 * x, 4 * y - 20, "10"))

        platform_locations.append((screenX - x - 30, 2 * y, "11"))

        platform_locations.append((screenX - (4 * x), (5 * y) + (2 * 80) + 20, "9"))
        platform_locations.append((screenX - (3 * x), (5 * y) + (2 * 80) + 20, "8"))
        platform_locations.append((screenX - (2 * x), (5 * y) + (2 * 80) + 20, "8"))
        platform_locations.append((screenX - x, (5 * y) + (2 * 80) + 20, "8"))

        platform_locations.append((screenX - (3 * x), (3 * y) + (2 * 80) + 20, "9"))
        platform_locations.append((screenX - (2 * x), (3 * y) + (2 * 80) + 20, "10"))

        while i < len(platform_locations):
            platform = Platform(
                platform_locations[i][0], platform_locations[i][1], x, y, "tile " +
                platform_locations[i][2] + ".png")
            platform_list.add(platform)
            i += 1

        return platform_list

    def hearts():       
        empty_heart_list = pygame.sprite.Group()
        
        for i in range(1, 6):
            heart = Platform(5 + (45 * (i - 1)) + (3 * (i - 1)), 5, 45, 42, "heart 2.png")
            empty_heart_list.add(heart)

        return empty_heart_list

    def coins():
        coin_list = pygame.sprite.Group()
        coin = Platform(screenX - 64 - 23, 2 * 64 - 48, 48, 48, "coin.png")
        coin_list.add(coin)
        coin = Platform(777, 30, 48, 48, "coin.png")
        coin_list.add(coin)
        coin = Platform(5, 75, 48, 48, "coin.png")
        coin_list.add(coin)
        coin = Platform(750, 370, 48, 48, "coin.png")
        coin_list.add(coin)
        coin = Platform(840, 370, 48, 48, "coin.png")
        coin_list.add(coin)
        return coin_list

    def key():
        key_list = pygame.sprite.Group()
        key = Platform(600, 604, 84, 36, "key.png")
        key_list.add(key)
        return key_list

player = Player()
player_group = pygame.sprite.Group(player)
player.rect.x = 0
player.rect.y = screenY - 64 - player.rect.height
health = 5

ground_locations = []
tileX = 64
tileY = 64
i = 0
while i <= (screenX / tileX) + tileX:
    ground_locations.append(i * tileX)
    i += 1

filled_heart_list = []
for i in range(1, 6):
    filled_heart = pygame.image.load("heart 1.png")
    filled_heart_list.append(filled_heart)
hearts = pygame.image.load("heart 1.png")
        
ground_list = Game.ground(ground_locations, tileX, tileY)
platform_list = Game.platform(tileX, tileY)
enemy_list = Game.enemy()
empty_heart_list = Game.hearts()
coin_list = Game.coins()
key_list = Game.key()

coin = pygame.image.load("side coin.png")
coin_counter_list = []
heart_counter_list = []
for i in range(0, 6):
    counter = pygame.image.load("x" + str(i) + ".png")
    coin_counter_list.append(counter)
    heart_counter_list.append(counter)
coins_left = 5

background = pygame.image.load("background.png")
background_rect = background.get_rect()

game_over_background = pygame.image.load("game over back.png")
gameover = pygame.image.load("game over.png")
play = True
in_game = True
game_over = False
steps = 10
health = 5

#main loop
while play:
    pygame.event.clear()
    while in_game:
        pygame.event.clear()
        pygame.event.get()

        game_screen.blit(background, (0, 0))
        keys = pygame.key.get_pressed()

        # press ESCAPE key to exit the game
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            in_game = False
            sys.exit()

        # press RIGHT arrow key to move right
        if keys[pygame.K_RIGHT]:
            player.move(steps, 0)

        # press LEFT arrow key to move left
        if keys[pygame.K_LEFT]:
            player.move(-steps, 0)

        # press SPACE bar to jump
        if keys[pygame.K_SPACE]:
            player.jump()

        player.updateLocation()

        # draw everything onto the game screen
        player_group.draw(game_screen)
        game_screen.blit(coin_counter_list[5 - len(coin_list)], (308, 15))
        game_screen.blit(coin, (260, 5))
        ground_list.draw(game_screen)
        platform_list.draw(game_screen)
        coin_list.draw(game_screen)
        enemy_list.draw(game_screen)
        empty_heart_list.draw(game_screen)
        player.enemy_collision()
        player.coin_collision()
        
        if player.health < health:
            del filled_heart_list[-1]
            
        for f in filled_heart_list:
            i = filled_heart_list.index(f)
            game_screen.blit(f, (5 + (45 * i) + (3 * i), 5))

        for e in enemy_list:
            e.move()
            
        if player.health == 0:
            game_over = True
            in_game = False
            
        if len(coin_list) == 0:
            key_list.draw(game_screen)
            player.final()

        if len(key_list) == 0:
            game_over = True
            in_game = False
        
        health = player.health
        
        pygame.display.update()
        pygame.time.delay(20)

    while game_over:
        pygame.event.clear()
        game_screen.blit(game_over_background, (0, 0))
        game_screen.blit(gameover, (410, 234))
        
        pygame.event.get()
        keys = pygame.key.get_pressed()

        # press ESCAPE key to exit the game
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            game_over = False
            play = False
            sys.exit()

        game_screen.blit(coin_counter_list[5 - len(coin_list)], (633, 315))
        game_screen.blit(coin, (585, 305))
        game_screen.blit(hearts, (585, 400))
        game_screen.blit(heart_counter_list[player.health], (633, 405))
        
        pygame.display.update()
        pygame.time.delay(10)

    pygame.display.update()
    pygame.time.delay(10)
        

