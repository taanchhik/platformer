import unittest
from unittest.mock import patch, Mock, mock_open
import pickle

save_file = "save_game.dat"

def save_progress(level):
    if not isinstance(level, int):
        raise TypeError("Уровень должен быть целым числом")
    with open(save_file, "wb") as f:
        pickle.dump(level, f)


class TestSaveProgress(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
