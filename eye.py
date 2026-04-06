import pyautogui
import cv2
import numpy as np
import os

# Paramètres à ajuster selon votre écran
CENTER_X, CENTER_Y = 657, 358 # Centre de l'écran (votre perso)
TILE_SIZE = 49  # Taille approximative d'une case en pixels

# Dossier pour stocker nos références
if not os.path.exists('tiles_ref'):
    os.makedirs('tiles_ref')

def capturer_cases_adjacentes():
    # Décalages pour les 8 directions (Isométrie)
    directions = {
        "nord": (0, -TILE_SIZE),
        "sud": (0, TILE_SIZE),
        "est": (TILE_SIZE, 0),
        "ouest": (-TILE_SIZE, 0),
        "nord_est": (TILE_SIZE//2, -TILE_SIZE//2),
        "sud_ouest": (-TILE_SIZE//2, TILE_SIZE//2),
        # Ajoutez les autres diagonales ici
    }

    screenshot = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    for nom, offset in directions.items():
        x = CENTER_X + offset[0]
        y = CENTER_Y + offset[1]
        
        # On découpe une petite zone de 32x32 pixels autour du point
        tile = frame[y-16:y+16, x-16:x+16]
        cv2.imwrite(f'tiles_ref/check_{nom}.png', tile)
        print(f"Case {nom} capturée.")

import time

print("Focus le jeu dans 5 secondes...")
time.sleep(5)
# Exécutez ceci en étant bien positionné dans le jeu
capturer_cases_adjacentes()