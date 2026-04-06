from pynput import mouse
import sys

print("--- MODE CAPTURE PAR CLIC ---")
print("1. Clique sur les 4 coins de ton carré dans le jeu.")
print("2. Le script s'arrêtera automatiquement après 4 clics.")
print("-" * 30)

coords = []

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        # On enregistre la position du clic
        ix, iy = int(x), int(y)
        coords.append((ix, iy))
        print(f"✅ Clic {len(coords)}/4 enregistré : X={ix}, Y={iy}")
        
        # Si on a nos 4 points, on arrête l'écouteur
        if len(coords) >= 4:
            return False 

# Lancement de l'écouteur
with mouse.Listener(on_click=on_click) as listener:
    listener.join()

# Calcul automatique de la zone (BBox)
x_min = min(c[0] for c in coords)
x_max = max(c[0] for c in coords)
y_min = min(c[1] for c in coords)
y_max = max(c[1] for c in coords)

print("\n--- RÉSULTATS POUR TON IA ---")
print(f"Coins capturés : {coords}")
print(f"Zone (ROI) : Top-Left({x_min}, {y_min}) | Bottom-Right({x_max}, {y_max})")
print(f"Largeur: {x_max - x_min}px | Hauteur: {y_max - y_min}px")
print("\nTu peux maintenant utiliser ces valeurs pour 'découper' la vue de ton IA.")