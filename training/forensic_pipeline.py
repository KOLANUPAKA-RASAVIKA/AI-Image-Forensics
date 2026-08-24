import os
import sys
import cv2
import numpy as np
import tensorflow as tf
import tkinter as tk

from tkinter import filedialog
from tensorflow.keras.preprocessing import image


# ============================================================
# AI IMAGE FORENSICS
# COMPLETE FORENSIC PIPELINE
# ResNet50 + ELA + Grad-CAM
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

RESULTS_DIR = "forensic_results"

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("AI IMAGE FORENSICS")
print("COMPLETE FORENSIC PIPELINE")
print("=" * 60)


# ============================================================
# SELECT IMAGE FROM COMPUTER
# ============================================================

print("\nOpening image selector...")

root = tk.Tk()
root.withdraw()

IMAGE_PATH = filedialog.askopenfilename(
    title="Select an image for forensic analysis",
    filetypes=[
        (
            "Image files",
            "*.jpg *.jpeg *.png *.tif *.tiff *.bmp"
        ),
        (
            "JPEG files",
            "*.jpg *.jpeg"
        ),
        (
            "PNG files",
            "*.png"
        ),
        (
            "TIFF files",
            "*.tif *.tiff"
        ),
        (
            "All files",
            "*.*"
        )
    ]
)

root.destroy()


# ============================================================
# CHECK IMAGE SELECTION
# ============================================================

if not IMAGE_PATH:

    print("\nNo image selected.")

    print("\nProgram stopped.")

    sys.exit(0)


print("\nSelected image:")
print(IMAGE_PATH)


# ============================================================
# CHECK MODEL
# ============================================================

if not os.path.exists(MODEL_PATH):

    print("\nERROR: ResNet50 model not found!")

    print(
        "\nExpected model:"
    )

    print(
        os.path.abspath(MODEL_PATH)
    )

    print(
        "\nMake sure this file exists:"
    )

    print(
        "models\\resnet_model.keras"
    )

    sys.exit(1)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading ResNet50 model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)

print("Model loaded successfully!")


# ============================================================
# LOAD ORIGINAL IMAGE
# ============================================================

print("\nLoading image...")

original_image = cv2.imread(
    IMAGE_PATH
)

if original_image is None:

    print(
        "\nERROR: Could not read selected image."
    )

    sys.exit(1)


original_height, original_width = (
    original_image.shape[:2]
)

print(
    f"Original size: "
    f"{original_width} x {original_height}"
)


# ============================================================
# PREPARE IMAGE
# ============================================================

print("\nPreparing image for ResNet50...")

img = image.load_img(
    IMAGE_PATH,
    target_size=IMG_SIZE
)

img_array = image.img_to_array(
    img
)

img_array = np.expand_dims(
    img_array,
    axis=0
)

img_array = tf.keras.applications.resnet50.preprocess_input(
    img_array
)

print("Image prepared successfully!")


# ============================================================
# RESNET50 PREDICTION
# ============================================================

print("\nRunning ResNet50 prediction...")

predictions = model.predict(
    img_array,
    verbose=0
)

probabilities = predictions[0]

predicted_index = int(
    np.argmax(probabilities)
)

predicted_class = CLASS_NAMES[
    predicted_index
]

confidence = (
    float(probabilities[predicted_index])
    * 100
)


# ============================================================
# DISPLAY PREDICTION
# ============================================================

print("\n" + "=" * 60)
print("RESNET50 PREDICTION")
print("=" * 60)

print(
    f"\nPrediction : {predicted_class}"
)

print(
    f"Confidence : {confidence:.2f}%"
)

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
# ELA
# ============================================================

print("\n" + "=" * 60)
print("ERROR LEVEL ANALYSIS")
print("=" * 60)

print("\nRunning Error Level Analysis...")

base_name = os.path.splitext(
    os.path.basename(IMAGE_PATH)
)[0]

ela_path = os.path.join(
    RESULTS_DIR,
    base_name + "_ela.jpg"
)

try:

    # JPEG compression quality
    quality = 90

    encode_params = [
        cv2.IMWRITE_JPEG_QUALITY,
        quality
    ]

    success, encoded_image = cv2.imencode(
        ".jpg",
        original_image,
        encode_params
    )

    if not success:

        raise Exception(
            "Could not encode image."
        )

    compressed_image = cv2.imdecode(
        encoded_image,
        cv2.IMREAD_COLOR
    )

    difference = cv2.absdiff(
        original_image,
        compressed_image
    )

    max_difference = int(
        np.max(difference)
    )

    print(
        f"Maximum pixel difference: "
        f"{max_difference}"
    )

    ela_image = cv2.convertScaleAbs(
        difference,
        alpha=10,
        beta=0
    )

    cv2.imwrite(
        ela_path,
        ela_image
    )

    print(
        "\nELA completed successfully!"
    )

    print(
        "ELA saved:"
    )

    print(
        os.path.abspath(ela_path)
    )

except Exception as e:

    print(
        "\nELA failed:"
    )

    print(str(e))

    ela_path = None


# ============================================================
# GRAD-CAM
# ============================================================

print("\n" + "=" * 60)
print("GRAD-CAM ANALYSIS")
print("=" * 60)

gradcam_path = os.path.join(
    RESULTS_DIR,
    base_name + "_gradcam.jpg"
)

heatmap_path = os.path.join(
    RESULTS_DIR,
    base_name + "_heatmap.jpg"
)


try:

    print("\nSearching for ResNet50 backbone...")

    resnet_backbone = model.get_layer(
        "resnet50"
    )

    print(
        "ResNet50 backbone found:"
    )

    print(
        resnet_backbone.name
    )

    # --------------------------------------------------------
    # Last convolutional layer
    # --------------------------------------------------------

    last_conv_layer = resnet_backbone.get_layer(
        "conv5_block3_3_conv"
    )

    print(
        "\nLast convolutional layer:"
    )

    print(
        last_conv_layer.name
    )

    # --------------------------------------------------------
    # Build Grad-CAM model
    # --------------------------------------------------------

    print(
        "\nBuilding Grad-CAM model..."
    )

    grad_model = tf.keras.models.Model(
        inputs=resnet_backbone.input,
        outputs=[
            last_conv_layer.output,
            resnet_backbone.output
        ]
    )

    # --------------------------------------------------------
    # Calculate gradients
    # --------------------------------------------------------

    print(
        "Generating Grad-CAM..."
    )

    with tf.GradientTape() as tape:

        conv_outputs, backbone_output = grad_model(
            img_array,
            training=False
        )

        # Classification head

        x = model.get_layer(
            "global_average_pooling"
        )(
            backbone_output
        )

        x = model.get_layer(
            "dropout"
        )(
            x,
            training=False
        )

        x = model.get_layer(
            "feature_dense"
        )(
            x
        )

        x = model.get_layer(
            "feature_dropout"
        )(
            x,
            training=False
        )

        predictions_grad = model.get_layer(
            "forensic_prediction"
        )(
            x
        )

        class_score = predictions_grad[
            :,
            predicted_index
        ]

    grads = tape.gradient(
        class_score,
        conv_outputs
    )

    if grads is None:

        raise Exception(
            "Gradients could not be calculated."
        )

    # --------------------------------------------------------
    # Average gradients
    # --------------------------------------------------------

    pooled_grads = tf.reduce_mean(
        grads,
        axis=(0, 1, 2)
    )

    conv_outputs = conv_outputs[0]

    # --------------------------------------------------------
    # Generate heatmap
    # --------------------------------------------------------

    heatmap = tf.reduce_sum(
        conv_outputs * pooled_grads,
        axis=-1
    )

    heatmap = tf.maximum(
        heatmap,
        0
    )

    max_value = tf.reduce_max(
        heatmap
    )

    if float(max_value) > 0:

        heatmap = (
            heatmap / max_value
        )

    heatmap = heatmap.numpy()

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    heatmap = cv2.resize(
        heatmap,
        (
            original_width,
            original_height
        )
    )

    heatmap_uint8 = np.uint8(
        255 * heatmap
    )

    # --------------------------------------------------------
    # Color heatmap
    # --------------------------------------------------------

    heatmap_color = cv2.applyColorMap(
        heatmap_uint8,
        cv2.COLORMAP_JET
    )

    # --------------------------------------------------------
    # Save heatmap
    # --------------------------------------------------------

    cv2.imwrite(
        heatmap_path,
        heatmap_color
    )

    # --------------------------------------------------------
    # Overlay
    # --------------------------------------------------------

    gradcam_image = cv2.addWeighted(
        original_image,
        0.6,
        heatmap_color,
        0.4,
        0
    )

    cv2.imwrite(
        gradcam_path,
        gradcam_image
    )

    print(
        "\nGrad-CAM completed successfully!"
    )

    print(
        "Heatmap:"
    )

    print(
        os.path.abspath(heatmap_path)
    )

    print(
        "\nGrad-CAM:"
    )

    print(
        os.path.abspath(gradcam_path)
    )

except Exception as e:

    print(
        "\nGrad-CAM failed:"
    )

    print(str(e))

    gradcam_path = None
    heatmap_path = None


# ============================================================
# FINAL FORENSIC REPORT
# ============================================================

print("\n" + "=" * 60)
print("FINAL FORENSIC REPORT")
print("=" * 60)

print(
    "\nImage:"
)

print(
    os.path.abspath(IMAGE_PATH)
)

print(
    f"\nPrediction  : {predicted_class}"
)

print(
    f"Confidence  : {confidence:.2f}%"
)

print(
    "\nClass probabilities:"
)

for class_name, probability in zip(
    CLASS_NAMES,
    probabilities
):

    print(
        f"{class_name:<15}: "
        f"{probability * 100:.2f}%"
    )

print(
    "\nELA:"
)

if ela_path:

    print(
        os.path.abspath(ela_path)
    )

else:

    print(
        "Failed"
    )

print(
    "\nGrad-CAM:"
)

if gradcam_path:

    print(
        os.path.abspath(gradcam_path)
    )

    print(
        "\nHeatmap:"
    )

    print(
        os.path.abspath(heatmap_path)
    )

else:

    print(
        "Failed"
    )

print(
    "\n" + "=" * 60
)

print(
    "FORENSIC ANALYSIS COMPLETED"
)

print(
    "=" * 60
)