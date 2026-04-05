
import time

UP = 'up'
RIGHT = 'right'
DOWN = 'down'
LEFT = 'left'

DELAY = 0.1  # Délai entre les appuis de touches (en secondes)
latency_of_game = 1  # Ajustez ce délai en fonction de la latence de votre jeu

def move_keyboard(direction):
    """ if we are using keyboard"""
    import keyboard as controller
    controller.press(direction)
    time.sleep(DELAY)
    controller.release(direction)

def move_autogui(direction):
    import pyautogui as controller
    controller.keyDown(direction)
    time.sleep(DELAY)
    controller.keyUp(direction)

def move_xdotool(direction):
    import subprocess as controller
    # xdotool use uppercase for the first letter of the commande
    if direction in [UP, RIGHT, DOWN, LEFT]:
        direction = direction.capitalize()
    controller.run(["xdotool", "keydown", direction])
    time.sleep(DELAY)
    controller.run(["xdotool", "keyup", direction])

def move_square(direction):
    move = move_autogui
    if direction in [UP, RIGHT, DOWN, LEFT]:
        move(direction)
    else:
        print(f"Direction '{direction}' non reconnue. Utilisez UP, RIGHT, DOWN ou LEFT.")
        return
    print(f"Moved {direction}")
    time.sleep(latency_of_game)


if __name__ == "__main__":
    move_square(UP)
    move_square(RIGHT)
    move_square(DOWN)
    move_square(LEFT)