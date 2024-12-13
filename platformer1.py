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

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#шрифт
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font_level_complete = pygame.font.SysFont('Bauhaus 93', 50)

tile_size = 50
game_over = 0
main_menu = True
level_select = False
level = 1
level_completed = False
total_transformations_left = 2

#цвета
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
    '''Графический вывод текста на экран

    :param text: Строка, которую нужно вывести на экран
    :type text: str
    :param font: Шрифт строки
    :type font: pygame.font.Font
    :param text_col: Цвет строки
    :param x: Координата x (в пикселях) левого верхнего угла текста на экране
    :type x: int
    :param y: Координата y (в пикселях) левого верхнего угла текста на экране
    :type y: int
    :returns: None
    :rtype: None
    :raises AttributeError: Если font не является допустимым объектом
    :raises TypeError: Если text_col не является 3-элементным кортежем целых чисел
    '''
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_level(level):
    '''Сбрасывает уровень игры до указанного

    :param level: Номер уровня
    :type level: int
    :returns: Объект World, представляющий собой загруженный уровень
    :rtype: World
    :raises FileNotFoundError: Если файла с данными уровня ('level{level}_data') не существует
    :raises EOFError: Если файл с данными уровня пуст или повреждён
    :raises pickle.UnpicklingError: Если произошла ошибка во время распаковки файла с данными уровня
    '''
    player.reset(850, screen_height - 120)
    player2.reset(100, screen_height - 120)
    blob_group.empty()
    platform_group.empty()
    lava_group.empty()
    exit_group.empty()
    total_transformations_left = 2 if level == 1 else 1
    '''Файлы level{level}_data были созданы с помощью заимствованного файла level_editor.py, взятого из проекта игры-платформера, процесс выполнения которого был представлен на общедоступной платформе YouTube'''
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    return world


class Button():
    '''Это класс интерактивных кнопок

    Обрабатывает отрисовку изображения кнопки и обнаружение щелчков мыши
    '''
    def __init__(self, x, y, image):
        '''Инициализирует объект Button

        :param x: Координата x левого верхнего угла кнопки
        :type x: int
        :param y: Координата y левого верхнего угла кнопки
        :type y: int
        :param image:  Изображение кнопки (pygame.Surface)
        :returns: None
        :rtype: None
        :raises TypeError: Если тип image не является pygame.Surface
        '''
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
        
    def draw(self):
        '''Отрисовывает кнопку на экране и проверяет нажатия

        :returns: True, если кнопка была нажата, и False в противном случае
        :rtype: bool
        :raises TypeError: Если screen (поверхность) не является объектом pygame.Surface
        :raises AttributeError: Может быть выброшено, если self.image или self.rect не являются валидными объектами Pygame
        '''
        action = False
        pos = pygame.mouse.get_pos() #позиция курсора мыши
        if self.rect.collidepoint(pos): #условие наведения курсора мыши и нажатия на кнопку
            if pygame.mouse.get_pressed()[0] == 1 and not(self.clicked):
                action = True
                print('CLICKED')
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, self.rect) #нарисуем кнопку
        return action


class Player():
    '''Это класс первого игрового персонажа

    Загружает и управляет спрайтами пресонажа, а также инициализирует его позицию
    '''
    def __init__(self, x, y):
        '''Инициализирует объект Player

        :param x: Начальная координата x персонажа
        :type x: int
        :param y: Начальная координата y персонажа
        :type y: int
        :returns: None
        :rtype: None
        :raises KeyError: Если ключ self.current_parameter не существует в словаре self.parameters
        :raises FileNotFoundError: Если файлы спрайтов (изображения) не найдены по указанным путям
        '''
        self.reset(x, y)
        self.parameters = {
            "normal": {"jump_height": 15, "sprite_sheet": "pinky"},
            "super": {"jump_height": 25, "sprite_sheet": "frogpinky"}
        }
        self.current_parameter = "normal"
        self.load_sprites()

    def load_sprites(self):
        '''Загружает и подготавливает спрайты персонажа из файлов изображений

        :returns: None
        :rtype: None
        :raises FileNotFoundError: Если файл изображения, указанный в строке f'img/{sprite_sheet_prefix}{num}.png', не найден
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
        self.images_right = []
        self.images_left = []
        sprite_sheet_prefix = self.parameters[self.current_parameter]["sprite_sheet"]
        for num in range(1, 5): 
            img_right = pygame.image.load(f'img/{sprite_sheet_prefix}{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 70))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

    def update(self, game_over):
        '''Обновляет позицию игрока, обрабатывает столкновения и управляет анимацией на основе пользовательского ввода и состояния игры

        :param game_over: Целое число, преставляющее состояние игры (0 - игра запущена, -1 - игра окончена)
        :type game_over: int
        :returns: Целое число, представляющее обновленное состояние игры (0 - игра запущена, -1 - игра окончена)
        :rtype: int
        :raises TypeError: Если типы данных переменных, используемых в вычислениях или сравнениях, не соответствуют ожидаемым
        :raises IndexError: Если self.index выходит за пределы допустимого диапазона индексов в списке self.images_right или self.images_left
        :raises AttributeError: Если у объекта self, world, platform, blob_group, или lava_group отсутствует необходимый атрибут или метод
        :raises pygame.error: Если произошла ошибка при отрисовке изображения
        '''
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20
        if game_over == 0:
            #управление игроком
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and not(self.jumped) and not(self.in_air):
                jump_fx.play()
                self.vel_y = -self.parameters[self.current_parameter]["jump_height"]
                self.jumped = True
            if not(key[pygame.K_UP]):
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if not(key[pygame.K_LEFT]) and not(key[pygame.K_RIGHT]):
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
            #проверка на столкновение с платформой
            for platform in platform_group:
                #столкновения по оси X
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #столкновения по оси Y
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #проверка, есть ли над игроком платформа
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #проверка, есть ли под игроком платформа
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
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
        '''Сбрасывает состояние игрока до начальных значений: загружает спрайты, устанавливает начальную позицию и сбрасывает переменные анимации

        :param x: Начальная координата x игрока
        :type x: int
        :param y: Начальная координата y игрока
        :type y: int
        :returns: None
        :rtype: None
        :raises FileNotFoundError: Если файлы изображений 'img/pinky{num}.png' и 'img/ghost.png' не найдены по указанным путям
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/pinky{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 70))
            img_left = pygame.transform.flip(img_right, True, False)
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
        self.current_parameter = "normal"

    def draw(self, surface):
        '''Рисует игрока на заданной поверхности

        :param surface: Поверхность, на которой будет нарисован игрок
        :type surface: pygame.Surface
        :returns: None
        :rtype: None
        :raises TypeError: Если поверхность не является объектом pygame.Surface, если self.image и self.rect не являются валидными объектами Pygame
        '''
        surface.blit(self.image, self.rect)


class Player2():
    '''Это класс второго игрового персонажа

    Загружает и управляет спрайтами пресонажа, а также инициализирует его позицию
    '''
    def __init__(self, x, y):
        '''Инициализирует объект Player2

        :param x: Начальная координата x персонажа
        :type x: int
        :param y: Начальная координата y персонажа
        :type y: int
        :returns: None
        :rtype: None
        :raises KeyError: Если ключ self.current_parameter не существует в словаре self.parameters
        :raises FileNotFoundError: Если файлы спрайтов (изображения) не найдены по указанным путям
        '''
        self.reset(x, y)
        self.parameters = {
            "normal": {"jump_height": 15, "sprite_sheet": "greeny"},
            "super": {"jump_height": 25, "sprite_sheet": "froggreeny"}
        }
        self.current_parameter = "normal"
        self.load_sprites()

    def load_sprites(self):
        '''Загружает и подготавливает спрайты персонажа из файлов изображений

        :returns: None
        :rtype: None
        :raises FileNotFoundError: Если файл изображения, указанный в строке f'img/{sprite_sheet_prefix}{num}.png', не найден
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
        self.images_right = []
        self.images_left = []
        sprite_sheet_prefix = self.parameters[self.current_parameter]["sprite_sheet"]
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/{sprite_sheet_prefix}{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 70))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

    def update(self, game_over):
        '''Обновляет позицию игрока, обрабатывает столкновения и управляет анимацией на основе пользовательского ввода и состояния игры

        :param game_over: Целое число, преставляющее состояние игры
        :type game_over: int
        :returns: Целое число, представляющее обновленное состояние игры
        :rtype: int
        :raises TypeError: Если типы данных переменных, используемых в вычислениях или сравнениях, не соответствуют ожидаемым
        :raises IndexError: Если self.index выходит за пределы допустимого диапазона индексов в списке self.images_right или self.images_left
        :raises AttributeError: Если у объекта self, world, platform, blob_group, или lava_group отсутствует необходимый атрибут или метод
        :raises pygame.error: Если произошла ошибка при отрисовке изображения
        '''
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20
        if game_over == 0:
            #управление игроком 2
            key = pygame.key.get_pressed()
            if key[pygame.K_w] and not(self.jumped) and not(self.in_air):
                jump_fx.play()
                self.vel_y = -self.parameters[self.current_parameter]["jump_height"]
                self.jumped = True
            if not(key[pygame.K_w]):
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_d]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if not(key[pygame.K_a]) and not(key[pygame.K_d]):
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
            #проверка на столкновение с платформой
            for platform in platform_group:
                #столкновения по оси X
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #столкновения по оси Y
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #проверка, есть ли над игроком платформа
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #проверка, есть ли под игроком платформа
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
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
        '''Сбрасывает состояние игрока до начальных значений: загружает спрайты, устанавливает начальную позицию и сбрасывает переменные анимации

        :param x: Начальная координата x игрока
        :type x: int
        :param y: Начальная координата y игрока
        :type y: int
        :returns: None
        :rtype: None
        :raises FileNotFoundError: Если файлы изображений 'img/greeny{num}.png' и 'img/ghost.png' не найдены по указанным путям
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
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
        self.current_parameter = "normal"

    def draw(self, surface):
        '''Рисует игрока на заданной поверхности

        :param surface: Поверхность, на которой будет нарисован игрок
        :type surface: pygame.Surface
        :returns: None
        :rtype: None
        :raises TypeError: Если поверхность не является объектом pygame.Surface
        '''
        surface.blit(self.image, self.rect)


class World():
    '''Этот класс представляет игровой мир, включая плитки, врагов и платформы

    Загружает и управляет элементами мира на основе предоставленных данных
    '''
    def __init__(self, data):
        '''Инициализирует объект World

        :param data: Файл со списком, представляющим союой структуру уровня. Каждый элемент в списке соответствует типу плитки
        :type data: pickle file
        :returns: None
        :rtype: None
        :raises FileNotFoundError: если файлы изображений не найдены
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
        self.tile_list = []
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
        '''Этот метод перебирает список плиток и отрисовывает каждое изображение плитки на экране (отрисовывает мир)

        :returns: None
        :rtype: None
        :raises TypeError: Если элементы списка self.tile_list не являются кортежами длиной 2
        '''
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    '''Представляет врага в игре

    Наследуется от pygame.sprite.Sprite. Враг движется горизонтально взад и вперёд
    '''
    def __init__(self, x, y):
        '''Инициализирует объект Enemy

        :param x: Начальная координата x врага
        :type x: int
        :param y: Начальная координата y врага
        :type y: int
        :raises FileNotFoundError: Если файл изображения 'img/blob.png' не найден
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        '''Обновляет позицию врага на каждом кадре

        :returns: None
        :rtype: None
        :raises: None
        '''
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
    '''Представляет движущуюся платформу в игре.

    Наследуется от pygame.sprite.Sprite. Платформа движется горизонтально и/или вертикально взад и вперёд.
    '''
    def __init__(self, x, y, move_x, move_y):
        '''Инициализирует объект Platform

        :param x: Начальная координата x платформы
        :type x: int
        :param y: Начальная координата y платформы
        :type y: int
        :param move_x: Горизонтальная скорость движения платформы (пикселей за кадр)
        :type move_x: int
        :param move_y: Вертикальная скорость движения платформы (пикселей за кадр)
        :type move_y: int
        :raises FileNotFoundError: Если файл изображения 'img/platform.png' не найден
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
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
        '''Обновляет позицию платформы на каждом кадре

        :returns: None
        :rtype: None
        :raises: None
        '''
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    '''Представляет элемент лавы в игре

    Наследуется от pygame.sprite.Sprite
    '''
    def __init__(self, x, y):
        '''Инициализирует объект Lava

        :param x: Начальная координата x лавы
        :type x: int
        :param y: Начальная координата y лавы
        :type y: int
        :raises FileNotFoundError: Если файл изображения 'img/lava.png' не найден.
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        

class Exit(pygame.sprite.Sprite):
    '''Представляет элемент-выход в игре

    Наследуется от pygame.sprite.Sprite
    '''
    def __init__(self, x, y):
        '''Инициализирует объект Exit
        
        :param x: Начальная координата x выхода
        :type x: int
        :param y: Начальная координата y выхода
        :type y: int
        :raises TypeError: Если координаты не являются целыми числами
        :raises FileNotFoundError: Если файл изображения 'img/exit.png' не найден
        :raises pygame.error: Если произошла ошибка при загрузке или масштабировании изображения
        '''
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(850, screen_height - 120) #70 + 50 = 120
player2 = Player2(100, screen_height - 120)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

save_file = "save_game.dat"

def load_progress():
    '''Загружает прогресс игрока из файла для сохранения прогресса

    :returns: Сохранённый уровень (целое число) или 0, если файл сохранения не найден или повреждён
    :rtype: int
    :raises FileNotFoundError: Если файл, указанный в переменной save_file, не существует
    :raises EOFError: Если файл существует, но пустой (достигнут конец файла до начала чтения данных)
    '''
    try:
        with open(save_file, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return 0

def save_progress(level):
    '''Сохраняет прогресс игрока в файл

    :param level: Текущий уровень, который нужно сохранить
    :type level: int
    :raises TypeError: Если уровень не является целым числом
    '''
    if not isinstance(level, int):
        raise TypeError("Уровень должен быть целым числом")
    with open(save_file, "wb") as f:
        pickle.dump(level, f)

highest_level = load_progress()

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

run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    if main_menu and not(level_select):
        if exit_button.draw() == True:
            run = False
        if start_button.draw() == True:
            main_menu = False
            level_select = True
    elif level_select and not(main_menu):
        if exit2_button.draw() == True:
            run = False
        if level1_btn.draw() == True:
            level = 1
            world_data = []
            world = reset_level(level)
            run = True
            level_select = False
            level_completed = False
            total_transformations_left = 2
        if level2_btn.draw() == True and highest_level >= 1:
            level = 2
            world_data = []
            world = reset_level(level)
            run = True
            level_select = False
            level_completed = False
            total_transformations_left = 1
    else:
        world.draw()
        if game_over == 0:
            blob_group.update()
            platform_group.update()
            draw_text(f"Transforms: {total_transformations_left}", font_score, white, 10, 10)
        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        game_over = player.update(game_over)
        game_over = player2.update(game_over)
        player.draw(screen)
        player2.draw(screen)
        if restart_button.draw():
            total_transformations_left = 2 if level == 1 else 1
            player.current_parameter = "normal"
            player2.current_parameter = "normal"
            world = reset_level(level)
            game_over = 0
            level_completed = False
        if menu_button.draw():
            level_completed = False
            level_select = True
            main_menu = False
            game_over = 0
        if pygame.sprite.spritecollide(player, exit_group, False) and pygame.sprite.spritecollide(player2, exit_group, False) and not(level_completed):
            level_completed = True
            game_over = 1
        if game_over == -1:
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
        if level_completed:
            if level > highest_level:
                highest_level = level
                save_progress(highest_level)
            if level == 1:
                draw_text('LEVEL 1 COMPLETED!', font_level_complete, blue, (screen_width // 2) - 250, screen_height // 2 - 50)
            elif level == 2:
                draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
            else:
                draw_text('LEVEL ' + str(level) + ' COMPLETED!', font_level_complete, blue, (screen_width // 2) - 250, screen_height // 2 - 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and total_transformations_left > 0:
                player.current_parameter = "super"
                player.load_sprites()
                total_transformations_left -= 1
            elif event.key == pygame.K_0 and total_transformations_left > 0:
                player2.current_parameter = "super"
                player2.load_sprites()
                total_transformations_left -= 1
    pygame.display.update()
    
pygame.quit()
