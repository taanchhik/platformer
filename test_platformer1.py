import unittest

import pygame
from pygame.locals import *
from pygame import mixer
import pickle
import platformer1

from os import path
import builtins
from unittest.mock import MagicMock, patch, mock_open
from platformer1 import draw_text, reset_level, Button, Player, Player2, World, Enemy, Platform, Lava, Exit, load_progress, save_progress
pygame.init()

pygame.display.set_mode((1000, 1000))
save_file = "save_game.dat"


class TestGameFunctions(unittest.TestCase):

    @patch('pickle.load')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_reset_level_success(self, mock_open, mock_load):
        mock_load.return_value = [[1, 1, 1]]
        world = reset_level(1)
        self.assertIsNotNone(world)
        mock_open.assert_called_once_with('level1_data', 'rb')
        mock_load.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_reset_level_file_not_found(self, mock_open):
        with self.assertRaises(FileNotFoundError):
            reset_level(1)

    @patch('pickle.load', side_effect=pickle.UnpicklingError)
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_reset_level_unpickling_error(self, mock_open, mock_load):
        with self.assertRaises(pickle.UnpicklingError):
            reset_level(1)

    @patch('pygame.Surface')
    def test_button_init(self, MockSurface):
        button = Button(10, 10, MockSurface.return_value)
        self.assertEqual(button.rect.x, 10)
        self.assertEqual(button.rect.y, 10)
        self.assertFalse(button.clicked)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_progress(self, mock_open):
        save_progress(5)
        mock_open.assert_called_once_with(platformer1.save_file, "wb")
        handle = mock_open()
        handle.write.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_progress_file_not_found(self, mock_open):
        level = load_progress()
        self.assertEqual(level, 0)

    @patch('pickle.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_progress_success(self, mock_file, mock_pickle_dump):
        mock_file.return_value = mock_open().return_value
        mock_pickle_dump.return_value = None
        save_progress(1)
        mock_file.assert_called_once_with(save_file, 'wb')
        mock_pickle_dump.assert_called_once_with(1, mock_file.return_value)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_progress_type_error(self, mock_file):
        mock_file.return_value = mock_open().return_value
        with self.assertRaises(TypeError):
            save_progress('1')

    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    @patch('pygame.transform.flip')
    def test_load_sprites_success(self, mock_flip, mock_scale, mock_load):
        # Создаем мок-изображения
        mock_image = MagicMock()
        mock_image.get_width.return_value = 40
        mock_image.get_height.return_value = 70
        mock_load.return_value = mock_image
        mock_scale.return_value = mock_image
        mock_flip.return_value = mock_image
        player = Player(0,0)
        self.assertEqual(len(player.images_right), 4)
        self.assertEqual(len(player.images_left), 4)
        mock_load.assert_called()
        mock_scale.assert_called()
        mock_flip.assert_called()

    @patch('pygame.image.load', side_effect=FileNotFoundError)
    def test_load_sprites_file_not_found(self, mock_load):
        with self.assertRaises(FileNotFoundError):
            player = Player(0, 0)

    @patch('pygame.image.load')
    @patch('pygame.transform.scale', side_effect=pygame.error)
    def test_load_sprites_scale_error(self, mock_scale, mock_load):
        mock_image = MagicMock()
        mock_load.return_value = mock_image
        with self.assertRaises(pygame.error):
            player = Player(0, 0)

    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    @patch('pygame.transform.flip', side_effect=pygame.error)
    def test_load_sprites_flip_error(self, mock_flip, mock_scale, mock_load):
        mock_image = MagicMock()
        mock_load.return_value = mock_image
        mock_scale.return_value = mock_image
        with self.assertRaises(pygame.error):
            player = Player(0, 0)

    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    @patch('pygame.transform.flip')
    def test_load_sprites_super(self, mock_flip, mock_scale, mock_load):
        #Проверяем загрузку спрайтов в режиме "super"
        mock_image = MagicMock()
        mock_image.get_width.return_value = 40
        mock_image.get_height.return_value = 70
        mock_load.return_value = mock_image
        mock_scale.return_value = mock_image
        mock_flip.return_value = mock_image
        player = Player(0,0)
        player.current_parameter = "super"
        player.load_sprites()
        self.assertEqual(len(player.images_right), 4)
        self.assertEqual(len(player.images_left), 4)

    def setUp(self):
        '''Выполняется перед тестом'''
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 36)

    def tearDown(self):
        '''Выполняется после теста'''
        pygame.font.quit()

    def test_draw_text_negative(self):
        with self.assertRaises(AttributeError):
            draw_text("Test", "not a font", (255, 255, 255), 10, 10)


if __name__ == '__main__':
    pygame.init()
    unittest.main()
    pygame.quit()
