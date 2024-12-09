import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height)) #создание окна
pygame.display.set_caption('Platformer') #название

#шрифт
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font_level_complete = pygame.font.SysFont('Bauhaus 93', 50)

tile_size = 50
game_over = 0
main_menu = True
level_select = False
level = 0
max_levels = 7
score = 0
level_completed = False

#colors
white = (255, 255, 255)
blue = (0, 0, 255)

#загрузка изображений
bg_img = pygame.image.load('img/sky.png')
bg_img = pygame.transform.scale(bg_img, (1000, 1000))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
start_img = pygame.transform.scale(start_img, (300, 100))
exit_img = pygame.image.load('img/exit_btn.png')
exit_img = pygame.transform.scale(exit_img, (300, 100))
level1_img = pygame.image.load('img/level1_btn.png')
level1_img = pygame.transform.scale(level1_img, (200, 200))
level2_img = pygame.image.load('img/level2_btn.png')
level2_img = pygame.transform.scale(level2_img, (200, 200))
menu_img = pygame.image.load('img/menu_btn.png')
exit2_img = pygame.image.load('img/exit_btn.png')
exit2_img = pygame.transform.scale(exit_img, (300, 100))

#загрузка звуков
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


#функция обновления уровня
def reset_level(level):
    player.reset(100, screen_height - 120)
    player2.reset(100, screen_height - 120)
    blob_group.empty()
    platform_group.empty()
    lava_group.empty()
    exit_group.empty()

    #загрузка данных уровня и создание мира
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
        
    def draw(self):
        action = False
        
        #позиция курсора мыши
        pos = pygame.mouse.get_pos()

        #условие наведения курсора мыши и нажатия на кнопку
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                print('CLICKED')
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        #нарисуем кнопку
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):

        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            #управление игроком
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            
            #гравитация
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #анимация
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
                
            #проверка на столкновение
            self.in_air = True
            for tile in world.tile_list:
                #проверка на столконвение по оси X
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #проверка на столконвение по оси Y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #находится ли игрок под землёй (прыжок)
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #находится ли игрок над землёй (падение)
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            #проверка на столкновение с врагами
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()
            
            #проверка на столкновение с лавой
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            #проверка на столкновение с выходом
            #if pygame.sprite.spritecollide(self, exit_group, False):
            #    game_over = 1

            #проверка на столкновение с платформой
            for platform in platform_group:
                #столкновения по оси X
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #столкновения по оси X
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #проверка, есть ли под игроком платформа
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #проверка, есть ли под игроком платформа
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
                        dy = 0
                    #вбок вместе с платформой
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction
                
            #отрегулировать позицию игрока
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5
        
        #нарисуем игрока в окне
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/pinky{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 70))
            img_left = pygame.transform.flip(img_right, True, False) #переворачивание по оси X
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.image = pygame.transform.scale(img_right, (40, 70))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Player2():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            #управление игроком 2
            key = pygame.key.get_pressed()
            if key[pygame.K_w] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_w] == False:
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_d]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
            
            #гравитация
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #анимация
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
                
            #проверка на столкновение
            self.in_air = True
            for tile in world.tile_list:
                #проверка на столконвение по оси X
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #проверка на столконвение по оси Y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #находится ли игрок под землёй (прыжок)
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #находится ли игрок над землёй (падение)
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            #проверка на столкновение с врагами
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()
            
            #проверка на столкновение с лавой
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            #проверка на столкновение с выходом
            #if pygame.sprite.spritecollide(self, exit_group, False):
            #    game_over = 1

            #проверка на столкновение с платформой
            for platform in platform_group:
                #столкновения по оси X
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #столкновения по оси X
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #проверка, есть ли под игроком платформа
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #проверка, есть ли под игроком платформа
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
                        dy = 0
                    #вбок вместе с платформой
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction
                
            #отрегулировать позицию игрока
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5
        
        #нарисуем игрока в окне
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/greeny{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 70))
            img_left = pygame.transform.flip(img_right, True, False) #переворачивание по оси X
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.image = pygame.transform.scale(img_right, (40, 70))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class World():
    def __init__(self, data):
        self.tile_list = []
        
        #загрузка изображений
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1
            
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

'''            
world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
'''

player = Player(100, screen_height - 120) #70 + 50 = 120
player2 = Player2(100, screen_height - 120)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


#загрузка данных уровня и создание мира
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

#создание кнопок
restart_button = Button(screen_width // 2 - 50, screen_height // 2 - 495, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 100, screen_height // 2, exit_img)
exit2_button = Button(screen_width // 2 - 150, screen_height // 2 - 400, exit_img)
level1_btn = Button(screen_width // 2 - 350, screen_height // 2, level1_img)
level2_btn = Button(screen_width // 2 + 100, screen_height // 2, level2_img)
menu_button = Button(screen_width - 125, 5, menu_img)

if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)


run = True
while run:

    clock.tick(fps)
    
    screen.blit(bg_img, (0, 0))
    
    if main_menu == True and level_select == False: #если открыто меню
        if exit_button.draw() == True: #если нажата кнопка exit
            run = False #то выход из игры
        if start_button.draw() == True: #если нажата кнопка старт
            main_menu = False
            level_select = True
    elif level_select == True and main_menu == False:
        #если открыто меню с уровнями
        if exit2_button.draw() == True: #если нажата кнопка exit
            run = False
        if level1_btn.draw() == True: #если нажата кнопка lvl1
            level = 1
            world_data = []
            world = reset_level(level)
            run = True
            level_select = False
            level_completed = False
        if level2_btn.draw() == True: #если нажата кнопка lvl2
            level = 2
            world_data = []
            world = reset_level(level)
            run = True
            level_select = False
            level_completed = False
    else:
        world.draw()

        if pygame.sprite.spritecollide(player, exit_group, False) and pygame.sprite.spritecollide(player2, exit_group, False):
                game_over = 1
                
        if game_over == 0:
            blob_group.update()
            platform_group.update()
            #обновление счёта
            '''
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_fx.play()
            if pygame.sprite.spritecollide(player2, coin_group, True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)'''

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)
        game_over = player2.update(game_over)

        player.draw(screen)
        player2.draw(screen)

        # Always show restart button during gameplay
        if restart_button.draw():
            world = reset_level(level)
            game_over = 0

        # Check for level completion
        if pygame.sprite.spritecollide(player, exit_group, False) and pygame.sprite.spritecollide(player2, exit_group, False) and not level_completed:
            level_completed = True
            game_over = 1
                
        #если игрок умер
        if game_over == -1:
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

        if level_completed:
            if level == 1:
                draw_text('LEVEL 1 COMPLETED!', font_level_complete, blue, (screen_width // 2) - 250, screen_height // 2 - 50)
            elif level == 2:
                draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
            else:
                draw_text('LEVEL ' + str(level) + ' COMPLETED!', font_level_complete, blue, (screen_width // 2) - 250, screen_height // 2 -50)

        # Show menu button to go back to level select
        if menu_button.draw():
            level_completed = False
            level_select = True
            main_menu = False
            game_over = 0
            
        if restart_button.draw():
            world = reset_level(level)
            game_over = 0
            level_completed = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update() #обновление окна
    
pygame.quit()
