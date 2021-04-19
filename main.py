from typing import Any

import threading

from src.controls import Controls
from src.snake import Snake


class Main:
    def __call__(self, *args: Any, **kwds: Any) -> Any:

        snake = Snake()
        thread = threading.Thread(target=snake.gameloop)
        thread.start()

        controls = Controls()
        controls()


if __name__ == "__main__":
    game = Main()
    game()
