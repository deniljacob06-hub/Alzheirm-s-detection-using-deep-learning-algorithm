"""
Melanoma Classifier (MobileNetV2 Transfer Learning)

Handles extreme class imbalance safely.

Label mapping:
    NM*        -> benign (0)
    SSM*/LMM*  -> melanoma (1)

Proof-of-concept only. NOT for medical use.
"""

import os
import math
import argparse
from glob import glob
import numpy as np
import pandas as pd
from sklearn.utils import class_weight

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models, optimizers

# ---------------- CONFIG ---------------- #

DATA_DIR = os.path.join("images", "dermquest")
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "melanoma_mobilenetv2.h5")

IMG_SIZE = (224, 224)
BATCH = 8
EPOCHS = 6

os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------- LABEL INFERENCE ---------------- #

def infer_label_from_filename(fn):
    base = os.path.basename(fn).upper()
    if base.startswith("NM"):
        return "benign"
    elif base.startswith("SSM") or base.startswith("LMM"):
        return "melanoma"
    else:
        return "benign"

# ---------------- BUILD DATAFRAME ---------------- #

def build_dataframe(data_dir):
    files = sorted(glob(os.path.join(data_dir, "*_orig.jpg")))
    if not files:
        raise RuntimeError("No images found")

    rows = []
    for f in files:
        rows.append({
            "filename": f,
            "label": infer_label_from_filename(f)
        })

    df = pd.DataFrame(rows)

    print("\nDataset Summary:")
    print(df["label"].value_counts())

    if len(df["label"].unique()) < 2:
        raise RuntimeError("Only ONE class detected.")

    return df

# ---------------- BUILD MODEL ---------------- #

def build_model():
    base = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=IMG_SIZE + (3,)
    )
    base.trainable = False

    x = layers.GlobalAveragePooling2D()(base.output)
    x = layers.Dropout(0.3)(x)
    output = layers.Dense(1, activation="sigmoid")(x)

    model = models.Model(base.input, output)

    model.compile(
        optimizer=optimizers.Adam(1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model

# ---------------- SAFE TRAIN ---------------- #

def train(df, epochs):

    benign_df = df[df["label"] == "benign"]
    melanoma_df = df[df["label"] == "melanoma"]

    print("\nClass distribution:")
    print(df["label"].value_counts())

    # Manual safe split for extreme imbalance
    if len(benign_df) < 3:
        print("\n⚠ Extremely imbalanced dataset.")
        print("Using 1 benign sample for validation.")

        benign_train = benign_df.iloc[:-1]
        benign_val = benign_df.iloc[-1:]

        split_index = int(0.8 * len(melanoma_df))
        melanoma_train = melanoma_df.iloc[:split_index]
        melanoma_val = melanoma_df.iloc[split_index:]

        train_df = pd.concat([benign_train, melanoma_train])
        val_df = pd.concat([benign_val, melanoma_val])
    else:
        from sklearn.model_selection import train_test_split
        train_df, val_df = train_test_split(
            df,
            test_size=0.2,
            stratify=df["label"],
            random_state=42
        )

    print("\nTrain classes:")
    print(train_df["label"].value_counts())

    print("\nValidation classes:")
    print(val_df["label"].value_counts())

    # Image generators
    train_gen = ImageDataGenerator(
        rescale=1./255,
        horizontal_flip=True,
        rotation_range=20,
        zoom_range=0.2
    )

    val_gen = ImageDataGenerator(rescale=1./255)

    train_it = train_gen.flow_from_dataframe(
        train_df,
        x_col="filename",
        y_col="label",
        target_size=IMG_SIZE,
        class_mode="binary",
        batch_size=BATCH,
        shuffle=True
    )

    val_it = val_gen.flow_from_dataframe(
        val_df,
        x_col="filename",
        y_col="label",
        target_size=IMG_SIZE,
        class_mode="binary",
        batch_size=BATCH,
        shuffle=False
    )

    # ---- FIXED CLASS WEIGHTS ---- #

    numeric_labels = train_df["label"].map({"benign": 0, "melanoma": 1})

    weights = class_weight.compute_class_weight(
        class_weight="balanced",
        classes=np.array([0, 1]),
        y=numeric_labels
    )

    class_weights = {
        0: weights[0],  # benign
        1: weights[1]   # melanoma
    }

    print("\nClass Weights:", class_weights)

    model = build_model()

    model.fit(
        train_it,
        validation_data=val_it,
        epochs=epochs,
        class_weight=class_weights
    )

    model.save(MODEL_PATH)
    print("\nModel saved successfully.")

    return model

# ---------------- PREDICT ---------------- #

def predict_on_image(model, image_path):
    from tensorflow.keras.preprocessing import image

    img = image.load_img(image_path, target_size=IMG_SIZE)
    arr = image.img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)

    prob = model.predict(arr)[0][0]
    return float(prob)

# ---------------- MAIN ---------------- #

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", "-i", help="Image path")
    parser.add_argument("--epochs", "-e", type=int, default=EPOCHS)
    parser.add_argument("--no-train", action="store_true")
    args = parser.parse_args()

    df = build_dataframe(DATA_DIR)

    if args.no_train and os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Loaded existing model.")
    else:
        model = train(df, epochs=args.epochs)

    if args.image:
        image_path = args.image
    else:
        image_path = input("\nEnter full image path: ").strip()

    if not os.path.exists(image_path):
        raise FileNotFoundError("Image not found.")

    prob = predict_on_image(model, image_path)
    label = "melanoma" if prob >= 0.5 else "benign"

    print("\nPrediction Result:")
    print(f"Melanoma probability: {prob:.4f}")
    print(f"Predicted class: {label}")