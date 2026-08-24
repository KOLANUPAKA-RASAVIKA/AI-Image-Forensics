import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image


# ============================================================
# AI IMAGE FORENSICS
# RESNET50 IMAGE PREDICTION
# ============================================================

MODEL_PATH = os.path.join(
    "models",
    "resnet_model.keras"
)

CLASS_NAMES = [
    "AI_GENERATED",
    "AUTHENTIC",
    "MANIPULATED"
]

IMG_SIZE = (128, 128)


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("AI IMAGE FORENSICS")
print("RESNET50 IMAGE PREDICTION")
print("=" * 60)


# ============================================================
# GET IMAGE PATH
# ============================================================

if len(sys.argv) < 2:

    print("\nERROR: No image path provided!")

    print("\nUsage:")
    print('python predict.py "path_to_image"')

    print("\nExample:")
    print('python predict.py "dataset\\test\\AI_GENERATED\\car_11.png"')

    print("\nOr:")
    print('python predict.py "C:\\Users\\rasav\\Downloads\\image.jpg"')

    sys.exit()


IMAGE_PATH = sys.argv[1]


# ============================================================
# CHECK MODEL
# ============================================================

if not os.path.exists(MODEL_PATH):

    print("\nERROR: Model not found!")

    print("Expected:")
    print(MODEL_PATH)

    sys.exit()


# ============================================================
# CHECK IMAGE
# ============================================================

if not os.path.exists(IMAGE_PATH):

    print("\nERROR: Image not found!")

    print("Image path:")
    print(IMAGE_PATH)

    sys.exit()


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)

print("Model loaded successfully!")


# ============================================================
# IMAGE INFORMATION
# ============================================================

print("\nImage:")
print(os.path.abspath(IMAGE_PATH))


# ============================================================
# LOAD IMAGE
# ============================================================

print("\nLoading image...")

try:

    img = image.load_img(
        IMAGE_PATH,
        target_size=IMG_SIZE
    )

except Exception as e:

    print("\nERROR: Could not load image!")
    print(e)

    sys.exit()


img_array = image.img_to_array(img)


# ============================================================
# ADD BATCH DIMENSION
# ============================================================

img_array = np.expand_dims(
    img_array,
    axis=0
)


# ============================================================
# RESNET50 PREPROCESSING
# ============================================================

img_array = tf.keras.applications.resnet50.preprocess_input(
    img_array
)


# ============================================================
# PREDICTION
# ============================================================

print("\nRunning prediction...")

predictions = model.predict(
    img_array,
    verbose=0
)

probabilities = predictions[0]


# ============================================================
# GET PREDICTED CLASS
# ============================================================

predicted_index = np.argmax(
    probabilities
)

predicted_class = CLASS_NAMES[
    predicted_index
]

confidence = (
    probabilities[predicted_index] * 100
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n" + "=" * 60)
print("PREDICTION RESULT")
print("=" * 60)

print(
    f"\nPrediction : {predicted_class}"
)

print(
    f"Confidence : {confidence:.2f}%"
)


# ============================================================
# CLASS PROBABILITIES
# ============================================================

print("\nClass probabilities:")

for class_name, probability in zip(
    CLASS_NAMES,
    probabilities
):

    print(
        f"{class_name:<15}: "
        f"{probability * 100:.2f}%"
    )


# ============================================================
# END
# ============================================================

print("\n" + "=" * 60)
print("PREDICTION COMPLETED SUCCESSFULLY")
print("=" * 60)