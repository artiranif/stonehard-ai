import pyautogui
import time
import cv2
import numpy as np
import os

# Tes coordonnées de personnage (BBox)
X_MIN, Y_MIN, W, H = 657, 358, 48, 47

# Création des dossiers de dataset
for folder in ['data/passable', 'data/obstacle']:
    if not os.path.exists(folder): os.makedirs(folder)

def capturer_zone():
    img = pyautogui.screenshot(region=(X_MIN, Y_MIN, W, H))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def images_identiques(img1, img2, seuil=5):
    # Calcule la différence moyenne entre deux captures
    diff = cv2.absdiff(img1, img2)
    score = np.mean(diff)
    return score < seuil

def tenter_mouvement(touche):
    # 1. Capture l'état AVANT
    vue_avant = capturer_zone()
    
    # 2. Tente de bouger
    pyautogui.press(touche)
    time.sleep(0.3) # Temps pour que l'animation se termine
    
    # 3. Capture l'état APRÈS
    vue_apres = capturer_zone()
    
    # 4. Analyse du résultat
    timestamp = int(time.time())
    
    if images_identiques(vue_avant, vue_apres):
        print(f"❌ BLOCAGE détecté en allant vers {touche}")
        cv2.imwrite(f"data/obstacle/obs_{timestamp}.png", vue_avant)
        return False
    else:
        print(f"✅ MOUVEMENT réussi vers {touche}")
        cv2.imwrite(f"data/passable/pass_{timestamp}.png", vue_avant)
        return True