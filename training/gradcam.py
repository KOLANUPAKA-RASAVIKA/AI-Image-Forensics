import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model


# ============================================================
# AI IMAGE FORENSICS
# RESNET50 GRAD-CAM
# ============================================================

print("=" * 60)
print("AI IMAGE FORENSICS")
print("RESNET50 GRAD-CAM")
print("=" * 60)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = r"models\resnet_model.keras"

IMAGE_PATH = r"dataset\test\AI_GENERATED\car_11.png"

OUTPUT_DIR = "gradcam_results"

IMAGE_SIZE = (128, 128)

CLASS_NAMES = [
    "AI_GENERATED",
    "AUTHENTIC",
    "MANIPULATED"
]


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

model = load_model(MODEL_PATH)

print("Model loaded successfully!")


# ============================================================
# DISPLAY MODEL LAYERS
# ============================================================

print("\nModel layers:")

for layer in model.layers:
    print(
        f"{layer.name:30s} "
        f"{str(layer.output.shape)}"
    )


# ============================================================
# GET RESNET50 BACKBONE
# ============================================================

print("\nSearching for ResNet50 backbone...")

backbone = model.get_layer("resnet50")

print("ResNet50 backbone found:")
print(backbone.name)


# ============================================================
# FIND LAST CONVOLUTIONAL LAYER
# ============================================================

last_conv = None

for layer in reversed(backbone.layers):

    if isinstance(
        layer,
        tf.keras.layers.Conv2D
    ):
        last_conv = layer
        break


if last_conv is None:

    raise RuntimeError(
        "Could not find convolutional layer."
    )


print("\nLast convolutional layer:")
print(last_conv.name)

print("Output shape:")
print(last_conv.output.shape)


# ============================================================
# GET CLASSIFICATION HEAD
# ============================================================

gap_layer = model.get_layer(
    "global_average_pooling"
)

dropout_layer = model.get_layer(
    "dropout"
)

feature_dense = model.get_layer(
    "feature_dense"
)

feature_dropout = model.get_layer(
    "feature_dropout"
)

prediction_layer = model.get_layer(
    "forensic_prediction"
)


# ============================================================
# BUILD GRAD-CAM BACKBONE MODEL
# ============================================================

print("\nBuilding Grad-CAM model...")

grad_backbone = tf.keras.models.Model(
    inputs=backbone.input,
    outputs=[
        last_conv.output,
        backbone.output
    ]
)

print("Grad-CAM backbone created successfully!")


# ============================================================
# LOAD IMAGE
# ============================================================

print("\nLoading image...")

image = cv2.imread(IMAGE_PATH)

if image is None:

    raise FileNotFoundError(
        f"Could not load image:\n{IMAGE_PATH}"
    )


# OpenCV loads BGR
# Convert to RGB

image_rgb = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2RGB
)


# Keep original image for overlay

original_image = image_rgb.copy()


# Resize

resized = cv2.resize(
    image_rgb,
    IMAGE_SIZE
)


# ============================================================
# PREPROCESS IMAGE
# ============================================================

img_array = resized.astype(
    np.float32
)


# IMPORTANT:
# Your training uses ResNet50 preprocessing.
# ResNet50 preprocess_input converts RGB to BGR
# and performs the required mean subtraction.

img_array = tf.keras.applications.resnet50.preprocess_input(
    img_array
)


# Add batch dimension

img_array = np.expand_dims(
    img_array,
    axis=0
)


print("Image prepared successfully.")


# ============================================================
# NORMAL MODEL PREDICTION
# ============================================================

print("\nRunning prediction...")

predictions = model(
    img_array,
    training=False
).numpy()


predicted_class = int(
    np.argmax(predictions[0])
)


confidence = float(
    predictions[0][predicted_class]
)


print("\nPrediction:")
print(
    f"Class       : "
    f"{CLASS_NAMES[predicted_class]}"
)

print(
    f"Confidence  : "
    f"{confidence * 100:.2f}%"
)


print("\nClass probabilities:")

for i, class_name in enumerate(
    CLASS_NAMES
):

    print(
        f"{class_name:15s}: "
        f"{predictions[0][i] * 100:.2f}%"
    )


# ============================================================
# GENERATE GRAD-CAM
# ============================================================

print("\nGenerating Grad-CAM...")


with tf.GradientTape() as tape:

    # Run through ResNet50 backbone
    conv_outputs, backbone_features = grad_backbone(
        img_array,
        training=False
    )

    # Reproduce classification head
    x = gap_layer(
        backbone_features
    )

    x = dropout_layer(
        x,
        training=False
    )

    x = feature_dense(
        x
    )

    x = feature_dropout(
        x,
        training=False
    )

    preds = prediction_layer(
        x
    )

    # Score for predicted class
    class_score = preds[:, predicted_class]


# ============================================================
# CALCULATE GRADIENTS
# ============================================================

grads = tape.gradient(
    class_score,
    conv_outputs
)


if grads is None:

    raise RuntimeError(
        "Gradients were not generated."
    )


# Remove batch dimension

conv_outputs = conv_outputs[0]

grads = grads[0]


# ============================================================
# GLOBAL AVERAGE POOLING OF GRADIENTS
# ============================================================

weights = tf.reduce_mean(
    grads,
    axis=(0, 1)
)


# ============================================================
# WEIGHT CONVOLUTIONAL FEATURES
# ============================================================

cam = tf.reduce_sum(
    conv_outputs * weights,
    axis=-1
)


# ============================================================
# RELU
# ============================================================

cam = tf.maximum(
    cam,
    0
)


# Convert to NumPy

cam = cam.numpy()


# ============================================================
# NORMALIZE CAM
# ============================================================

if np.max(cam) != 0:

    cam = cam / np.max(cam)


# ============================================================
# RESIZE HEATMAP
# ============================================================

cam = cv2.resize(
    cam,
    (
        original_image.shape[1],
        original_image.shape[0]
    )
)


# Convert to 0-255

heatmap = np.uint8(
    255 * cam
)


# Apply OpenCV color map

heatmap = cv2.applyColorMap(
    heatmap,
    cv2.COLORMAP_JET
)


# Convert BGR -> RGB

heatmap = cv2.cvtColor(
    heatmap,
    cv2.COLOR_BGR2RGB
)


# ============================================================
# CREATE OVERLAY
# ============================================================

overlay = cv2.addWeighted(
    original_image,
    0.60,
    heatmap,
    0.40,
    0
)


# ============================================================
# ADD PREDICTION TEXT
# ============================================================

overlay_bgr = cv2.cvtColor(
    overlay,
    cv2.COLOR_RGB2BGR
)


text = (
    f"{CLASS_NAMES[predicted_class]} "
    f"({confidence * 100:.2f}%)"
)


cv2.putText(
    overlay_bgr,
    text,
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (255, 255, 255),
    2,
    cv2.LINE_AA
)


# ============================================================
# SAVE FILES
# ============================================================

base_name = os.path.splitext(
    os.path.basename(IMAGE_PATH)
)[0]


heatmap_path = os.path.join(
    OUTPUT_DIR,
    f"{base_name}_heatmap.jpg"
)


overlay_path = os.path.join(
    OUTPUT_DIR,
    f"{base_name}_gradcam.jpg"
)


original_path = os.path.join(
    OUTPUT_DIR,
    f"{base_name}_original.jpg"
)


# Save original

cv2.imwrite(
    original_path,
    cv2.cvtColor(
        original_image,
        cv2.COLOR_RGB2BGR
    )
)


# Save heatmap

cv2.imwrite(
    heatmap_path,
    cv2.cvtColor(
        heatmap,
        cv2.COLOR_RGB2BGR
    )
)


# Save overlay

cv2.imwrite(
    overlay_path,
    overlay_bgr
)


# ============================================================
# SUCCESS
# ============================================================

print("\n" + "=" * 60)
print("GRAD-CAM COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nPrediction:")
print(
    f"Class      : "
    f"{CLASS_NAMES[predicted_class]}"
)

print(
    f"Confidence : "
    f"{confidence * 100:.2f}%"
)

print("\nFiles saved:")

print(
    f"Original   : {original_path}"
)

print(
    f"Heatmap    : {heatmap_path}"
)

print(
    f"Grad-CAM   : {overlay_path}"
)

print("\nOpen the Grad-CAM image to see")
print("which regions influenced the prediction.")