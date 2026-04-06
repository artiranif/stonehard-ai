import cv2
import numpy as np
import os
import tensorflow as tf

MODEL_PATH = 'model/obstacle_classifier.h5'
IMG_W, IMG_H = 48, 47  # doit correspondre à la taille des tuiles capturées

def charger_modele():
    """Charge le modèle Keras entraîné depuis MODEL_PATH."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_PATH}\n"
            "Lance d'abord l'entraînement avec : python train-model.py"
        )
    print(f"✅ Modèle chargé depuis {MODEL_PATH}")
    return tf.keras.models.load_model(MODEL_PATH)

def predire_obstacle(modele, tuile):
    """Retourne True si le modèle prédit que la tuile est un obstacle."""
    img = cv2.resize(tuile, (IMG_W, IMG_H)).astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)  # (1, H, W, 3)
    prediction = modele.predict(img, verbose=0)[0][0]
    return prediction > 0.5  # True = obstacle, False = passable
