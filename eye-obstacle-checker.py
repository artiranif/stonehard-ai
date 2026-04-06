import pyautogui
import cv2
import numpy as np
import time
import os
from pynput import mouse

from movement import move_square
from movement import DOWN, UP, LEFT, RIGHT
from zonedelimiter import effectuer_capture
from model_utils import charger_modele, predire_obstacle, MODEL_PATH

# --- CONFIGURATION ---
# Ta zone (BBox) du personnage
X1, Y1, X2, Y2 = 657, 358, 705, 405
W, H = X2 - X1, Y2 - Y1

# Mode : False = collecte de données, True = utilise le modèle entraîné
MODE_PROD = False
# Le cas echeant on peut utiliser les deux modes
# Si PROD = True et ceci est aussi True, alors on enregistre les captures et on s'arrete quand le modele decide, par contre on peut pas se fier au modele pour enregistrer les captures d'obstacles, on doit se fier a la MSE pour ça
# Si PROD = True et MODE_DOUBLE = False, alors on se fie uniquement au collecteur de données pour arrêter le test
# Si Prod = False mais MODE_DOUBLE = True, on continue la collecte mais et on teste la prediction voir si elle a raison, seul le collecteur de données décide d'arrêter le test, le modele est juste là pour nous donner une idée de sa performance en temps réel
MODE_DOUBLE = True

# Dossiers de données
for d in ['data/passable', 'data/obstacle']:
    if not os.path.exists(d): 
        os.makedirs(d)

def obtenir_tuile(direction=None):
    """Prend une capture de la zone de l'IA."""
    # on doit utilier des coordonees qui correspondent a la direction du mouvement pour capturer la bonne tuile
    # la valeur d'ajout et de soustracition est 48 pixel
    if direction == UP:
        y_offset = -48
        x_offset = 0
    elif direction == DOWN:
        y_offset = 48
        x_offset = 0
    elif direction == LEFT:
        y_offset = 0
        x_offset = -48
    elif direction == RIGHT:
        y_offset = 0
        x_offset = 48
    else:
        y_offset = 0
        x_offset = 0
    screenshot = pyautogui.screenshot(region=(X1 + x_offset, Y1 + y_offset, W, H))
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def _mse_mouvement(direction, avant):
    """Bouge dans la direction et retourne (est_obstacle, erreur)."""
    move_square(direction)
    time.sleep(0.5)
    apres = obtenir_tuile(direction)
    erreur = np.mean((avant.astype("float") - apres.astype("float")) ** 2)
    return erreur < 2.0, erreur

def _sauvegarder_tuile(avant, timestamp, est_obstacle):
    """Sauvegarde la tuile dans le bon dossier selon le label."""
    path = f"data/obstacle/obs_{timestamp}.png" if est_obstacle else f"data/passable/pass_{timestamp}.png"
    cv2.imwrite(path, avant)

def _log_mse(compteur, est_obstacle, erreur, obstacle_predit=None):
    """Affiche le résultat MSE, avec comparaison modèle si disponible."""
    emoji = "🛑" if est_obstacle else "✅"
    label = "OBSTACLE" if est_obstacle else "PASSABLE"
    msg = f"[{compteur}] {emoji} {label} (MSE: {erreur:.2f})"
    if obstacle_predit is not None:
        accord = "✅ accord" if obstacle_predit == est_obstacle else "⚠️ désaccord modèle/MSE"
        label_mod = "obstacle" if obstacle_predit else "passable"
        msg += f" | Modèle: {label_mod} [{accord}]"
    print(msg)

def lancer_test_collision():
    print("\n▶️ Test de collision à DROITE lancé.")
    print("L'IA va s'arrêter dès qu'elle touche un obstacle.")

    use_model = MODE_PROD or MODE_DOUBLE
    modele = charger_modele() if use_model else None
    compteur = 0

    while True:
        compteur += 1
        # 1. Capture de la tuile de destination (à droite du joueur)
        avant = obtenir_tuile(RIGHT)
        timestamp = int(time.time() * 1000)

        # Prédiction du modèle si disponible
        obstacle_predit = predire_obstacle(modele, avant) if use_model else False

        if MODE_PROD and not MODE_DOUBLE:
            # Modèle seul — prédit avant de bouger, pas de sauvegarde
            if obstacle_predit:
                print(f"[{compteur}] 🛑 [PROD] OBSTACLE PRÉDIT ! Arrêt.")
                break
            print(f"[{compteur}] ✅ [PROD] Passable — déplacement.")
            move_square('right')
            time.sleep(0.5)

        elif MODE_PROD and MODE_DOUBLE:
            # MSE labellise et sauvegarde, modèle décide l'arrêt
            est_obstacle, erreur = _mse_mouvement(RIGHT, avant)
            _sauvegarder_tuile(avant, timestamp, est_obstacle)
            _log_mse(compteur, est_obstacle, erreur, obstacle_predit)
            if obstacle_predit:
                print(f"[{compteur}] 🛑 [PROD+DOUBLE] Arrêt décidé par le modèle.")
                break

        elif not MODE_PROD and MODE_DOUBLE:
            # MSE décide tout (arrêt + label + sauvegarde), modèle en monitoring
            est_obstacle, erreur = _mse_mouvement('right', avant)
            _log_mse(compteur, est_obstacle, erreur, obstacle_predit)
            _sauvegarder_tuile(avant, timestamp, est_obstacle)
            if est_obstacle:
                break

        else:
            # Collecte pure — MSE seule
            est_obstacle, erreur = _mse_mouvement('right', avant)
            _log_mse(compteur, est_obstacle, erreur)
            _sauvegarder_tuile(avant, timestamp, est_obstacle)
            if est_obstacle:
                break

        time.sleep(0.1)

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.right:
        print(f"🖱️ Clic droit à ({x}, {y}) : Démarrage du test...")
        lancer_test_collision()
        return False # Arrête l'écouteur après le déclenchement

if __name__ == "__main__":
    if MODE_PROD:
        print("--- MODE PROD : TEST DU MODÈLE ---")
        print(f"Modèle utilisé : {MODEL_PATH}")
    else:
        print("--- MODE COLLECTE : APPRENTISSAGE STONESHARD ---")
        print("Les captures seront sauvegardées dans data/passable et data/obstacle.")
    print("1. Va dans le jeu.")
    print("2. Fais un CLIC DROIT pour commencer à marcher vers la droite.")

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    print("\n✅ Session terminée.")