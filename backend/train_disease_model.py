import tensorflow as tf
import numpy as np

from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from pathlib import Path


# =========================
# 1. Paths
# =========================

DATASET_DIR = Path(
    r"C:\Users\thiru\OneDrive\Documents\potato_dataset\Potato Leaf Disease Dataset in Uncontrolled Environment"
)

MODEL_PATH = Path("disease_mobilenetv2.keras")


# =========================
# 2. Settings
# =========================

IMG_SIZE = (224, 224)
BATCH_SIZE = 16
SEED = 42


# =========================
# 3. Load Dataset
# =========================

train_dataset = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)


class_names = train_dataset.class_names

print("\nClasses:")
for i, name in enumerate(class_names):
    print(i, "->", name)


# =========================
# 3A. Class Weights
# =========================

class_counts = {}

for class_name in class_names:
    class_dir = DATASET_DIR / class_name

    image_files = [
        file for file in class_dir.iterdir()
        if file.is_file()
    ]

    class_counts[class_name] = len(image_files)


total_samples = sum(class_counts.values())
num_classes = len(class_names)

class_weights = {}

for i, class_name in enumerate(class_names):
    class_weights[i] = (
        total_samples /
        (num_classes * class_counts[class_name])
    )


print("\nClass Counts:")
for class_name, count in class_counts.items():
    print(class_name, "->", count)


print("\nClass Weights:")
for i, weight in class_weights.items():
    print(class_names[i], "->", round(weight, 2))


# =========================
# 4. Improve Dataset Performance
# =========================

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(AUTOTUNE)
validation_dataset = validation_dataset.prefetch(AUTOTUNE)


# =========================
# 5. Data Augmentation
# =========================

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])


# =========================
# 6. MobileNetV2 Base Model
# =========================

base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

# Initially freeze pretrained layers
base_model.trainable = False


# =========================
# 7. Build Model
# =========================

inputs = layers.Input(shape=(224, 224, 3))

x = data_augmentation(inputs)

x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

x = base_model(x, training=False)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(0.3)(x)

outputs = layers.Dense(
    len(class_names),
    activation="softmax"
)(x)

model = models.Model(inputs, outputs)


# =========================
# 8. Compile
# =========================

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


model.summary()


# =========================
# 9. Callbacks
# =========================

early_stopping = EarlyStopping(
    monitor="val_accuracy",
    patience=3,
    restore_best_weights=True
)

checkpoint = ModelCheckpoint(
    MODEL_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)


# =========================
# 10. Initial Training
# =========================

print("\n==============================")
print("Starting Initial Training")
print("==============================")

EPOCHS = 15

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=EPOCHS,
    class_weight=class_weights,
    callbacks=[
        early_stopping,
        checkpoint
    ]
)


# =========================
# 11. Fine-Tuning
# =========================

print("\n==============================")
print("Starting Fine-Tuning")
print("==============================")


# Unfreeze MobileNetV2
base_model.trainable = True


# Freeze most layers
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
    restore_best_weights=True
)


fine_tune_checkpoint = ModelCheckpoint(
    MODEL_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)


FINE_TUNE_EPOCHS = 10

history_fine = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=FINE_TUNE_EPOCHS,
    class_weight=class_weights,
    callbacks=[
        fine_tune_early_stopping,
        fine_tune_checkpoint
    ]
)


# =========================
# 12. Save Final Model
# =========================

model.save(MODEL_PATH)

print("\n================================")
print("Model saved successfully!")
print("================================")

print("Model:", MODEL_PATH)
print("Classes:", class_names)