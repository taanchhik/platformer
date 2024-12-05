import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer") #название игры

WIDTH, HEIGHT = 800, 600 #ширина и высота окна игры
FPS = 60 #кадры в секунду
PLAYER_VEL = 5 #скорость игрока

window = pygame.display.set_mode((WIDTH, HEIGHT)) #окно игры

def flip(sprites): #эта функция переворачивает изображение
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites] #True - да, перевернуть по оси x, False - нет, не переворачивать по оси y

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join('assets', dir1, dir2) #путь к загружаемым изображениям
    images = [f for f in listdir(path) if isfile(join(path, f))] #эта строка будет загружать изображения из каталога (dyrectory) по очереди
        
    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() #convert_alpha() - получение прозрачного фона

        sprites = []
        for i in range(sprite_sheet.get_width() // width): #делим ширину каталога картинок на ширину одной картинки в каталоге
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32) #pygame.Surface - поверхность игровой точки
                                                                           #pygame.SRCALPHA - позволяет загружать прозрачные изображения
                                                                           #32 - глубина
            rect = pygame.Rect(i * width, 0, width, height) #место, на котором хотим получить новое изображение
            surface.blit(sprite_sheet, (0,0), rect) #рисуем на этом месте только тот кадр, который нужен в этот момент
            sprites.append(pygame.transform.scale2x(surface)) #scale2x - масштабирование по X
            
        if direction: #если нужна смена направления
            all_sprites[image.replace('.png', '') + '_right'] = sprites
            all_sprites[image.replace('.png', '') + '_left'] = flip(sprites) #переворачиваем
        else:
            all_sprites[image.replace('.png', '')] = sprites
            

            
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets(dir1, dir2, width, height)
        
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0 #скорость по горизонтали
        self.y_vel = 0 #скорость по вертикали
        self.mask = None
        self.direction = 'left' #эта переменная нужна, чтобы отслеживать, в каком направлении смотрит игрок
        self.animation_count = 0 #будем сбрасывать значение до нуля, когда будем менять направление,
                                 #чтобы анимация не выглядела шатко при движении слева направо.
                                 #self.animation_count - это счётчик кадров анимации
        self.fall_count = 0 #как долго персонаж падает

    def move(self, dx, dy): #dx - смещение по оси x, аналогично для y
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel): #помним, что в нашем случае ось x направлена вправо, ось y - ВНИЗ!!!
        self.x_vel = -vel
        if self.direction != 'left':
            self.direction = 'left'
            self.animation_count = 0
            
    def move_right(self, vel): 
        self.x_vel = vel
        if self.direction != 'right':
            self.direction = 'right'
            self.animation_count = 0

    def loop(self, fps):
        self.move(self.x_vel, self.y_vel)
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)

        self.fall_count += 1

    def draw(self, win): #функция, обрабатывающая рисование на экране
        pygame.draw.rect(win, self.COLOR, self.rect)
        



def get_background(name):
    image = pygame.image.load(join('assets', 'Background', name)) #задали картинку с неким названием
    _, _, width, height = image.get_rect() #первые 2 переменные - это x и y; нас не интересуют их значения, поэтому ставим '_'
    tiles = [] #плитки для фона

    for i in range(WIDTH // width + 1): #WIDTH // width + 1 - количество необходимых плиток для фона по ширине
        for j in range(HEIGHT // height + 1): #аналогично по высоте
            pos = (i * width, j * height) #заняли позицию
            tiles.append(pos) #добавили в список позицию для плитки

    return tiles, image




def draw(window, background, bg_image, player):
    for tile in background:
        window.blit(bg_image, tile)

    player.draw(window)
    
    pygame.display.update() #обновление окна


def handle_move(player): #клавиши, которые будут нажиматься для управления игроком
    keys = pygame.key.get_pressed() #показывает, какие клавиши нажаты в данный момент

    player.x_vel = 0 #зануляем, чтобы игрок не продолжал двигаться, пока не будет нажата другая клавиша
    if keys[pygame.K_LEFT]: #если нажата клавиша "стрелка влево"
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT]: #если нажата клавиша "стрелка вправо"
        player.move_right(PLAYER_VEL)
        
    

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background('Yellow.png')

    player = Player(100, 100, 50, 50)
    
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #выход пользователя из игры
                run = False
                break
        
        player.loop(FPS)    
        handle_move(player)
        draw(window, background, bg_image, player) #отрисовываем все объекты
        
    pygame.quit()
    quit()




if __name__ == "__main__":
    main(window)
