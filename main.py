import os
from typing import Any

os.environ["DISPLAY"] = ":0"
os.environ["XAUTHORITY"] = "/run/user/1000/gdm/Xauthority"

import threading

from controls import Controls
from snake import Snake


class Main:
    def __call__(self, *args: Any, **kwds: Any) -> Any:

        snake = Snake()
        thread = threading.Thread(target=snake.gameloop)
        thread.start()

        controls = Controls()
        controls.main()


if __name__ == "__main__":
    game = Main()
    game()
