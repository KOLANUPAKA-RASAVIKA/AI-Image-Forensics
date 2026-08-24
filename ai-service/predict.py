"""
=========================================================
AI IMAGE FORENSICS
Prediction Service
=========================================================

Classes:

0 -> AI_GENERATED
1 -> AUTHENTIC
2 -> MANIPULATED

IMPORTANT:
The model was trained using:

    ResNet50 preprocess_input()

and an input size of:

    224 x 224

Prediction MUST use exactly the same preprocessing.
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import os
import logging

import numpy as np
import tensorflow as tf

from PIL import Image

from tensorflow.keras.applications.resnet50 import (
    preprocess_input
)

import config as Config


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# MODEL PATH
# =========================================================

MODEL_PATH = Config.MODEL_PATH


# =========================================================
# IMAGE CONFIGURATION
# IMPORTANT:
# THIS MUST MATCH THE NEW TRAINED MODEL
# =========================================================

IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224

IMAGE_SIZE = (
    IMAGE_WIDTH,
    IMAGE_HEIGHT
)


# =========================================================
# CLASS CONFIGURATION
# =========================================================

CLASS_NAMES = [
    "AI_GENERATED",
    "AUTHENTIC",
    "MANIPULATED"
]

NUM_CLASSES = 3


# =========================================================
# LOAD MODEL
# =========================================================

logger.info(
    "Loading ResNet50 model..."
)

logger.info(
    "Model path: %s",
    MODEL_PATH
)


# ---------------------------------------------------------
# CHECK MODEL EXISTS
# ---------------------------------------------------------

if not os.path.exists(
    MODEL_PATH
):
    raise FileNotFoundError(
        "Model not found at:\n"
        f"{MODEL_PATH}"
    )


# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

try:

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

except Exception as exc:

    logger.exception(
        "Failed to load ResNet50 model."
    )

    raise RuntimeError(
        "Unable to load model:\n"
        f"{exc}"
    )


logger.info(
    "Model loaded successfully."
)


# =========================================================
# MODEL VALIDATION
# =========================================================

logger.info(
    "Model input shape: %s",
    model.input_shape
)

logger.info(
    "Model output shape: %s",
    model.output_shape
)


# ---------------------------------------------------------
# Validate input shape
# ---------------------------------------------------------

expected_input_shape = (
    None,
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
    3
)


if tuple(model.input_shape) != expected_input_shape:

    raise ValueError(
        "\n"
        "MODEL INPUT SHAPE MISMATCH\n"
        f"Expected: {expected_input_shape}\n"
        f"Actual:   {model.input_shape}\n"
    )


# ---------------------------------------------------------
# Validate output classes
# ---------------------------------------------------------

model_output_classes = (
    model.output_shape[-1]
)


if model_output_classes != NUM_CLASSES:

    raise ValueError(
        "\n"
        "MODEL OUTPUT CLASS MISMATCH\n"
        f"Expected classes: {NUM_CLASSES}\n"
        f"Model outputs:    {model_output_classes}\n"
        f"Classes:          {CLASS_NAMES}\n"
    )


logger.info(
    "Model/class configuration validated."
)

logger.info(
    "Classes: %s",
    CLASS_NAMES
)

logger.info(
    "Inference image size: %s",
    IMAGE_SIZE
)

logger.info(
    "Inference preprocessing: ResNet50 preprocess_input"
)


# =========================================================
# PREPROCESS IMAGE
# =========================================================

def preprocess_image(image_path):
    """
    Load and preprocess image exactly like training.

    Training:
        preprocess_input()

    Prediction:
        preprocess_input()

    Input:
        224 x 224 x 3

    Output:
        1 x 224 x 224 x 3
    """

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if not os.path.exists(
        image_path
    ):

        raise FileNotFoundError(
            f"Image not found:\n{image_path}"
        )


    logger.info(
        "Reading image: %s",
        image_path
    )


    # -----------------------------------------------------
    # OPEN IMAGE
    # -----------------------------------------------------

    try:

        image = Image.open(
            image_path
        ).convert("RGB")

    except Exception as exc:

        logger.exception(
            "Unable to open image."
        )

        raise ValueError(
            f"Unable to read image:\n{exc}"
        )


    # -----------------------------------------------------
    # RESIZE TO MODEL INPUT
    # -----------------------------------------------------

    image = image.resize(
        IMAGE_SIZE
    )


    # -----------------------------------------------------
    # CONVERT TO NUMPY
    # -----------------------------------------------------

    image_array = np.array(
        image,
        dtype=np.float32
    )


    # -----------------------------------------------------
    # RESNET50 PREPROCESSING
    # IMPORTANT
    # -----------------------------------------------------

    image_array = preprocess_input(
        image_array
    )


    # -----------------------------------------------------
    # ADD BATCH DIMENSION
    # -----------------------------------------------------

    image_array = np.expand_dims(
        image_array,
        axis=0
    )


    # -----------------------------------------------------
    # LOG SHAPE
    # -----------------------------------------------------

    logger.info(
        "Preprocessed image shape: %s",
        image_array.shape
    )


    # -----------------------------------------------------
    # FINAL SAFETY CHECK
    # -----------------------------------------------------

    expected_shape = (
        1,
        IMAGE_HEIGHT,
        IMAGE_WIDTH,
        3
    )


    if image_array.shape != expected_shape:

        raise ValueError(
            "\n"
            "PREPROCESSED IMAGE SHAPE MISMATCH\n"
            f"Expected: {expected_shape}\n"
            f"Actual:   {image_array.shape}\n"
        )


    return image_array


# =========================================================
# PREDICT IMAGE
# =========================================================

def predict_image(image_path):
    """
    Predict image class.

    Returns:

        {
            predicted_class,
            class_index,
            confidence,
            confidence_percentage,
            probabilities
        }
    """

    logger.info(
        "Running prediction..."
    )


    # =====================================================
    # STEP 1 - PREPROCESS
    # =====================================================

    image = preprocess_image(
        image_path
    )


    logger.info(
        "Image preprocessed successfully."
    )


    # =====================================================
    # STEP 2 - MODEL PREDICTION
    # =====================================================

    try:

        predictions = model.predict(
            image,
            verbose=0
        )

    except Exception as exc:

        logger.exception(
            "Model prediction failed."
        )

        raise RuntimeError(
            f"Model prediction failed:\n{exc}"
        )


    # =====================================================
    # STEP 3 - VALIDATE MODEL OUTPUT
    # =====================================================

    if predictions is None:

        raise ValueError(
            "Model returned no prediction."
        )


    if len(predictions) == 0:

        raise ValueError(
            "Model returned an empty prediction."
        )


    probabilities = np.asarray(
        predictions[0],
        dtype=np.float32
    )


    if len(probabilities) != NUM_CLASSES:

        raise ValueError(
            "\n"
            "PREDICTION OUTPUT MISMATCH\n"
            f"Expected: {NUM_CLASSES} probabilities\n"
            f"Received: {len(probabilities)} probabilities\n"
        )


    if not np.all(
        np.isfinite(probabilities)
    ):

        raise ValueError(
            "Model returned invalid probability values."
        )


    # =====================================================
    # STEP 4 - NORMALIZE IF NECESSARY
    # =====================================================

    probability_sum = float(
        np.sum(probabilities)
    )


    if probability_sum <= 0:

        raise ValueError(
            "Model returned zero probability sum."
        )


    # Softmax should already sum to ~1.
    # Normalize only if necessary.

    if (
        probability_sum < 0.95
        or probability_sum > 1.05
    ):

        probabilities = (
            probabilities /
            probability_sum
        )


    # =====================================================
    # STEP 5 - GET PREDICTED CLASS
    # =====================================================

    predicted_index = int(
        np.argmax(
            probabilities
        )
    )


    if not (
        0 <= predicted_index < NUM_CLASSES
    ):

        raise ValueError(
            "Invalid predicted class index."
        )


    predicted_class = (
        CLASS_NAMES[
            predicted_index
        ]
    )


    # =====================================================
    # STEP 6 - CONFIDENCE
    # =====================================================

    confidence = float(
        probabilities[
            predicted_index
        ]
    )


    confidence_percentage = round(
        confidence * 100,
        2
    )


    # =====================================================
    # STEP 7 - PROBABILITY DICTIONARY
    # =====================================================

    probability_dict = {

        "AI_GENERATED":
            float(probabilities[0]),

        "AUTHENTIC":
            float(probabilities[1]),

        "MANIPULATED":
            float(probabilities[2])
    }


    # =====================================================
    # STEP 8 - LOG RESULT
    # =====================================================

    logger.info(
        "Prediction completed."
    )

    logger.info(
        "Predicted class: %s",
        predicted_class
    )

    logger.info(
        "Class index: %s",
        predicted_index
    )

    logger.info(
        "Confidence: %.6f",
        confidence
    )

    logger.info(
        "Confidence percentage: %.2f%%",
        confidence_percentage
    )

    logger.info(
        "AI_GENERATED: %.6f",
        probability_dict[
            "AI_GENERATED"
        ]
    )

    logger.info(
        "AUTHENTIC: %.6f",
        probability_dict[
            "AUTHENTIC"
        ]
    )

    logger.info(
        "MANIPULATED: %.6f",
        probability_dict[
            "MANIPULATED"
        ]
    )


    # =====================================================
    # STEP 9 - RETURN
    # =====================================================

    return {

        "predicted_class":
            predicted_class,

        "class_index":
            predicted_index,

        "confidence":
            confidence,

        "confidence_percentage":
            confidence_percentage,

        "probabilities":
            probability_dict
    }


# =========================================================
# OPTIONAL DIRECT TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AI IMAGE FORENSICS - PREDICTION TEST")
    print("=" * 70)

    print(
        "Model:",
        MODEL_PATH
    )

    print(
        "Input size:",
        IMAGE_SIZE
    )

    print(
        "Classes:",
        CLASS_NAMES
    )

    print(
        "Preprocessing:",
        "ResNet50 preprocess_input"
    )

    print("=" * 70)


    test_image = input(
        "\nEnter image path: "
    ).strip().strip('"')


    if not test_image:

        print(
            "No image path provided."
        )

    elif not os.path.exists(
        test_image
    ):

        print(
            f"Image does not exist:\n{test_image}"
        )

    else:

        try:

            result = predict_image(
                test_image
            )


            print()
            print("=" * 70)
            print("PREDICTION RESULT")
            print("=" * 70)


            print(
                "Predicted class:",
                result[
                    "predicted_class"
                ]
            )


            print(
                "Class index:",
                result[
                    "class_index"
                ]
            )


            print(
                "Confidence:",
                f"{result['confidence_percentage']:.2f}%"
            )


            print()
            print(
                "Probabilities:"
            )


            for class_name, probability in (
                result[
                    "probabilities"
                ].items()
            ):

                print(
                    f"  {class_name}: "
                    f"{probability * 100:.2f}%"
                )


            print("=" * 70)


        except Exception as exc:

            logger.exception(
                "Prediction test failed."
            )

            print()
            print(
                "Prediction failed:"
            )

            print(
                str(exc)
            )