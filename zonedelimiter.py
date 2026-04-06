import pyautogui
import cv2
import numpy as np
from pynput import mouse
import time
import os
from datetime import datetime

# --- TES COORDONNÉES ---
X1, Y1 = 657, 358
X2, Y2 = 705, 405
W, H = X2 - X1, Y2 - Y1
mode_show = False # decide si on affiche les captures ou pas

print("--- MODE VALIDATION DE ZONE ---")
print("1. Bascule sur Stoneshard.")
print("2. Fais un CLIC GAUCHE là où tu veux déclencher la capture.")
print("-" * 30)

def effectuer_capture(x_clic=None, y_clic=None):
    print(f"\n📸 Clic détecté à ({x_clic}, {y_clic}). Capture en cours...")
    
    # Un minuscule délai pour éviter de capturer le curseur de sélection si Windows l'affiche
    time.sleep(0.2)
    
    # 1. Prendre la capture
    screenshot = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 2. Dessiner le rectangle de la zone de ton IA (Rouge)
    cv2.rectangle(frame, (X1, Y1), (X2, Y2), (0, 0, 255), 2)
    
    # 3. Dessiner un cercle là où tu as cliqué (Vert) pour vérifier le décalage
    if x_clic is not None and y_clic is not None:
        cv2.circle(frame, (int(x_clic), int(y_clic)), 5, (0, 255, 0), -1)
    
    # 4. Ajouter les labels
    cv2.putText(frame, "ZONE IA", (X1, Y1 - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    if x_clic is not None and y_clic is not None:
        cv2.putText(frame, "VOTRE CLIC", (int(x_clic) + 10, int(y_clic)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # 5. Sauvegarder et Afficher
    output_dir = os.path.join("data", "verifzone")
    os.makedirs(output_dir, exist_ok=True)
    filename = "zone_delimiter_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f") + ".png"
    output = os.path.join(output_dir, filename)
    cv2.imwrite(output, frame)
    print(f"✅ Image enregistrée : {output}")
    print("Vérifie si le carré rouge entoure bien ton personnage.")
    
    # Optionnel : Essayer d'ouvrir l'image
    if mode_show:
        if os.name == 'posix': # Linux/Mac
            import subprocess
            subprocess.Popen(["xdg-open", output])
        else: # Windows
            os.startfile(output)

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        effectuer_capture(x, y)
        return False # Arrête l'écouteur après le premier clic

if __name__ == "__main__":
    # Lancement de l'écouteur
    mode_show = True  # Affiche la capture après le clic
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()