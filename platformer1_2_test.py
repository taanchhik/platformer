import unittest
import pygame
from unittest.mock import patch, MagicMock

class Player:
    def __init__(self, x, y):
        self.parameters = {
            "normal": {"jump_height": 15, "sprite_sheet": "pinky"},
            "super": {"jump_height": 25, "sprite_sheet": "frogpinky"}
        }
        self.current_parameter = "normal"
        self.load_sprites()

    def load_sprites(self):
        self.images_right = []
        self.images_left = []
        sprite_sheet_prefix = self.parameters[self.current_parameter]["sprite_sheet"]
        for num in range(1, 5):
            img_right = pygame.image.load(f'img/{sprite_sheet_prefix}{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 70))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

   
class TestLoadSprites(unittest.TestCase):

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
        player = Player(0,0)  # Инициализируем Player, чтобы вызвать load_sprites
        self.assertEqual(len(player.images_right), 4)
        self.assertEqual(len(player.images_left), 4)
        mock_load.assert_called() #проверим, что load вызывался
        mock_scale.assert_called() #проверим, что scale вызывался
        mock_flip.assert_called() #проверим, что flip вызывался

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


if __name__ == '__main__':
    pygame.init()  # Необходимо инициализировать pygame для использования pygame.error
    unittest.main()
    pygame.quit()
