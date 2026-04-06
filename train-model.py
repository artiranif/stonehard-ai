import cv2
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

# --- CONFIGURATION ---
PASSABLE_DIR = 'data/passable'
OBSTACLE_DIR = 'data/obstacle'
MODEL_OUTPUT = 'model/obstacle_classifier.h5'
IMG_W, IMG_H = 48, 47  # taille des tuiles capturées

os.makedirs('model', exist_ok=True)

# --- CHARGEMENT DES DONNÉES ---
def charger_images(dossier, label):
    images, labels = [], []
    for fichier in os.listdir(dossier):
        chemin = os.path.join(dossier, fichier)
        img = cv2.imread(chemin)
        if img is None:
            continue
        img = cv2.resize(img, (IMG_W, IMG_H)).astype('float32') / 255.0
        images.append(img)
        labels.append(label)
    return images, labels

print("📂 Chargement des données...")
imgs_pass, lbls_pass = charger_images(PASSABLE_DIR, 0)   # 0 = passable
imgs_obs,  lbls_obs  = charger_images(OBSTACLE_DIR, 1)   # 1 = obstacle

print(f"  Passable : {len(imgs_pass)} images")
print(f"  Obstacle : {len(imgs_obs)} images")

if len(imgs_pass) == 0 or len(imgs_obs) == 0:
    print("❌ Pas assez de données. Lance d'abord eye-obstacle-checker.py en mode collecte.")
    exit(1)

X = np.array(imgs_pass + imgs_obs)
y = np.array(lbls_pass + lbls_obs)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# --- MODÈLE ---
modele = models.Sequential([
    layers.Input(shape=(IMG_H, IMG_W, 3)),
    layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')   # 0 = passable, 1 = obstacle
])

modele.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
modele.summary()

# --- ENTRAÎNEMENT ---
print("\n🚀 Entraînement en cours...")
historique = modele.fit(
    X_train, y_train,
    epochs=20,
    batch_size=16,
    validation_data=(X_test, y_test)
)

# --- ÉVALUATION ---
loss, acc = modele.evaluate(X_test, y_test, verbose=0)
print(f"\n📊 Précision sur le jeu de test : {acc * 100:.1f}%")

# --- SAUVEGARDE ---
modele.save(MODEL_OUTPUT)
print(f"✅ Modèle sauvegardé : {MODEL_OUTPUT}")
