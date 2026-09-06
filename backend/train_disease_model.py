import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
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

# Freeze pretrained layers
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
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# =========================
# 9. Train
# =========================

EPOCHS = 10

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=EPOCHS
)

# =========================
# 10. Save Model
# =========================

model.save(MODEL_PATH)

print("\nModel saved successfully!")
print("Model:", MODEL_PATH)
print("Classes:", class_names)