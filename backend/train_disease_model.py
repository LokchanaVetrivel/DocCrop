import tensorflow as tf
import numpy as np
import json

from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from pathlib import Path


# ============================================================
# 1. PATHS
# ============================================================

DATASET_DIR = Path(
    r"C:\Users\Keerthana M\OneDrive\Documents\Plant Disease Detection and Remedy System\dataset\PlantVillage\PlantVillage"
)

TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "val"

MODEL_PATH = Path("disease_mobilenetv2.keras")
CLASS_NAMES_PATH = Path("disease_class_names.json")


# ============================================================
# 2. SETTINGS
# ============================================================

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42


# ============================================================
# 3. CHECK DATASET PATHS
# ============================================================

print("\n========================================")
print("Checking Dataset")
print("========================================")

print("Train directory:", TRAIN_DIR)
print("Validation directory:", VAL_DIR)

if not TRAIN_DIR.exists():
    raise FileNotFoundError(
        f"Training directory not found:\n{TRAIN_DIR}"
    )

if not VAL_DIR.exists():
    raise FileNotFoundError(
        f"Validation directory not found:\n{VAL_DIR}"
    )


# ============================================================
# 4. LOAD TRAINING DATASET
# ============================================================

print("\n========================================")
print("Loading Training Dataset")
print("========================================")

train_dataset = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED
)


# ============================================================
# 5. LOAD VALIDATION DATASET
# ============================================================

print("\n========================================")
print("Loading Validation Dataset")
print("========================================")

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# ============================================================
# 6. CLASS NAMES
# ============================================================

class_names = train_dataset.class_names

print("\n========================================")
print("Classes")
print("========================================")

for i, name in enumerate(class_names):
    print(f"{i:2d} -> {name}")

num_classes = len(class_names)

print("\nTotal Classes:", num_classes)


# ============================================================
# 7. VERIFY TRAIN / VALIDATION CLASSES
# ============================================================

validation_class_names = validation_dataset.class_names

if class_names != validation_class_names:
    raise ValueError(
        "Training and validation classes do not match!"
    )

if num_classes != 38:
    print(
        f"\nWARNING: Expected 38 classes, but found {num_classes}."
    )


# ============================================================
# 8. SAVE CLASS NAMES
# ============================================================

with open(CLASS_NAMES_PATH, "w", encoding="utf-8") as f:
    json.dump(class_names, f, indent=4)

print("\nClass names saved to:", CLASS_NAMES_PATH)


# ============================================================
# 9. DATASET PERFORMANCE
# ============================================================

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(AUTOTUNE)
validation_dataset = validation_dataset.prefetch(AUTOTUNE)


# ============================================================
# 10. DATA AUGMENTATION
# ============================================================

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
    layers.RandomContrast(0.1),
])


# ============================================================
# 11. MOBILE NET V2 BASE MODEL
# ============================================================

print("\n========================================")
print("Loading MobileNetV2")
print("========================================")

base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

# Freeze pretrained layers initially
base_model.trainable = False


# ============================================================
# 12. BUILD MODEL
# ============================================================

inputs = layers.Input(
    shape=(224, 224, 3),
    name="plant_image"
)

x = data_augmentation(inputs)

x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

x = base_model(
    x,
    training=False
)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(0.3)(x)

outputs = layers.Dense(
    num_classes,
    activation="softmax",
    name="disease_prediction"
)(x)

model = models.Model(
    inputs=inputs,
    outputs=outputs
)


# ============================================================
# 13. COMPILE MODEL
# ============================================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


# ============================================================
# 14. MODEL SUMMARY
# ============================================================

model.summary()


# ============================================================
# 15. CALLBACKS
# ============================================================

early_stopping = EarlyStopping(
    monitor="val_accuracy",
    patience=3,
    restore_best_weights=True,
    verbose=1
)

checkpoint = ModelCheckpoint(
    MODEL_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)

reduce_lr = ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.2,
    patience=2,
    min_lr=1e-7,
    verbose=1
)


# ============================================================
# 16. INITIAL TRAINING
# ============================================================

print("\n========================================")
print("STARTING INITIAL TRAINING")
print("========================================")

INITIAL_EPOCHS = 10

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=INITIAL_EPOCHS,
    callbacks=[
        early_stopping,
        checkpoint,
        reduce_lr
    ]
)


# ============================================================
# 17. FINE-TUNING
# ============================================================

print("\n========================================")
print("STARTING FINE-TUNING")
print("========================================")

base_model.trainable = True


# Freeze most MobileNetV2 layers
for layer in base_model.layers[:-30]:
    layer.trainable = False


# Keep BatchNormalization layers frozen
for layer in base_model.layers:
    if isinstance(layer, layers.BatchNormalization):
        layer.trainable = False


# Recompile with smaller learning rate
model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.00001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


fine_tune_early_stopping = EarlyStopping(
    monitor="val_accuracy",
    patience=3,
    restore_best_weights=True,
    verbose=1
)

fine_tune_checkpoint = ModelCheckpoint(
    MODEL_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)

fine_tune_reduce_lr = ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.2,
    patience=2,
    min_lr=1e-8,
    verbose=1
)


FINE_TUNE_EPOCHS = 10

history_fine = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=FINE_TUNE_EPOCHS,
    callbacks=[
        fine_tune_early_stopping,
        fine_tune_checkpoint,
        fine_tune_reduce_lr
    ]
)


# ============================================================
# 18. SAVE FINAL MODEL
# ============================================================

model.save(MODEL_PATH)


# ============================================================
# 19. FINAL INFORMATION
# ============================================================

print("\n========================================")
print("TRAINING COMPLETED")
print("========================================")

print("Model saved:", MODEL_PATH)
print("Class names saved:", CLASS_NAMES_PATH)
print("Number of classes:", num_classes)

print("\nClasses:")

for i, name in enumerate(class_names):
    print(i, "->", name)

print("\n========================================")
print("DONE")
print("========================================")