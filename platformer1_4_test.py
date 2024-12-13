import pygame
import unittest

screen = pygame.display.set_mode((1000, 1000)) 

def draw_text(text: str, font: pygame.font.Font, text_col: tuple[int, int, int], x: int, y: int):
    """Отрисовывает текст на экране."""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


class TestDrawText(unittest.TestCase):
    
    def setUp(self):
        '''Выполняется перед каждым тестом'''
        pygame.font.init() # инициализируем шрифт pygame, если он ещё не инициализирован
        self.font = pygame.font.SysFont(None, 36) #создаём шрифт

    def tearDown(self):
        '''Выполняется после каждого теста'''
        pygame.font.quit()

    def test_draw_text_positive_1(self):
        """Позитивный тест 1: Отрисовка текста с корректными параметрами."""
        draw_text("Hello", self.font, (255, 255, 255), 10, 10)
        self.assertTrue(True) #Заглушка - тест пройден, если не было исключений

    def test_draw_text_negative_1(self):
        """Отрицательный тест 2: Некорректный объект шрифта."""
        with self.assertRaises(AttributeError):
            draw_text("Test", "not a font", (255, 255, 255), 10, 10) #Шрифт - строка, а не объект


if __name__ == '__main__':
    unittest.main()

