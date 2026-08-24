"""
=========================================================
AI IMAGE FORENSICS
Grad-CAM Explainability
=========================================================

Model architecture:

    Input
      ↓
    ResNet50
      ↓
    GlobalAveragePooling2D
      ↓
    Dense
      ↓
    Dropout
      ↓
    Dense / Softmax
      ↓
    AI_GENERATED
    AUTHENTIC
    MANIPULATED

IMPORTANT:
The trained model uses:

    224 x 224 input

and:

    ResNet50 preprocess_input()

Grad-CAM must use the SAME preprocessing.
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import os
import logging

import cv2
import numpy as np
import tensorflow as tf

from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import (
    preprocess_input
)

import config as Config


# =========================================================
# LOGGING
# =========================================================

logger = logging.getLogger(__name__)


# =========================================================
# MODEL CONFIGURATION
# =========================================================

MODEL_PATH = Config.MODEL_PATH

CLASS_NAMES = list(
    Config.CLASS_NAMES
)

NUM_CLASSES = int(
    Config.NUM_CLASSES
)


# =========================================================
# IMPORTANT MODEL INPUT SIZE
# MUST MATCH THE TRAINED MODEL
# =========================================================

IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224

IMAGE_SIZE = (
    IMAGE_WIDTH,
    IMAGE_HEIGHT
)


# =========================================================
# GRAD-CAM GENERATOR
# =========================================================

class GradCAMGenerator:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        logger.info(
            "Initializing Grad-CAM Generator..."
        )

        logger.info(
            "Loading trained model..."
        )

        logger.info(
            "Model path: %s",
            MODEL_PATH
        )


        # -------------------------------------------------
        # Check model
        # -------------------------------------------------

        if not os.path.exists(
            MODEL_PATH
        ):

            raise FileNotFoundError(
                "Grad-CAM model not found:\n"
                f"{MODEL_PATH}"
            )


        # -------------------------------------------------
        # Load model
        # -------------------------------------------------

        try:

            self.model = (
                tf.keras.models.load_model(
                    MODEL_PATH
                )
            )

        except Exception as exc:

            logger.exception(
                "Failed to load model for Grad-CAM."
            )

            raise RuntimeError(
                f"Unable to load Grad-CAM model:\n{exc}"
            )


        logger.info(
            "Model loaded successfully: %s",
            MODEL_PATH
        )


        # -------------------------------------------------
        # Validate model input
        # -------------------------------------------------

        logger.info(
            "Model input shape: %s",
            self.model.input_shape
        )

        logger.info(
            "Model output shape: %s",
            self.model.output_shape
        )


        expected_input = (
            None,
            IMAGE_HEIGHT,
            IMAGE_WIDTH,
            3
        )


        if tuple(
            self.model.input_shape
        ) != expected_input:

            raise ValueError(
                "\n"
                "Grad-CAM model input mismatch.\n"
                f"Expected: {expected_input}\n"
                f"Actual:   {self.model.input_shape}"
            )


        # -------------------------------------------------
        # Validate output classes
        # -------------------------------------------------

        output_classes = (
            self.model.output_shape[-1]
        )


        if output_classes != NUM_CLASSES:

            raise ValueError(
                "\n"
                "Grad-CAM class mismatch.\n"
                f"Expected: {NUM_CLASSES}\n"
                f"Actual:   {output_classes}\n"
            )


        # -------------------------------------------------
        # Find ResNet50 backbone
        # -------------------------------------------------

        self.backbone = (
            self.get_resnet_model()
        )


        logger.info(
            "ResNet50 backbone found: %s",
            self.backbone.name
        )


        # -------------------------------------------------
        # Find last convolution layer
        # -------------------------------------------------

        self.last_conv_layer = (
            self.find_last_conv_layer(
                self.backbone
            )
        )


        logger.info(
            "Grad-CAM target layer: %s",
            self.last_conv_layer.name
        )


        logger.info(
            "Grad-CAM Generator Ready."
        )


    # =====================================================
    # GET RESNET MODEL
    # =====================================================

    def get_resnet_model(self):

        """
        Find the nested ResNet50 model inside the
        trained forensic model.
        """

        for layer in self.model.layers:

            if isinstance(
                layer,
                tf.keras.Model
            ):

                # ResNet50 is usually the first nested model.
                if (
                    "resnet"
                    in layer.name.lower()
                ):

                    return layer


        # -------------------------------------------------
        # Fallback:
        # find any nested model
        # -------------------------------------------------

        for layer in self.model.layers:

            if isinstance(
                layer,
                tf.keras.Model
            ):

                return layer


        raise ValueError(
            "Could not find nested ResNet50 model."
        )


    # =====================================================
    # FIND LAST CONVOLUTION LAYER
    # =====================================================

    def find_last_conv_layer(
        self,
        backbone
    ):

        """
        Find the deepest convolution layer inside
        ResNet50.

        This works without hard-coding a specific
        ResNet50 layer name.
        """

        candidate_layers = []


        for layer in backbone.layers:

            try:

                output_shape = (
                    layer.output.shape
                )

            except Exception:

                continue


            # -------------------------------------------------
            # Conv layers normally have:
            # (None, height, width, channels)
            # -------------------------------------------------

            if (
                len(output_shape) == 4
                and
                isinstance(
                    layer,
                    (
                        tf.keras.layers.Conv2D,
                        tf.keras.layers.SeparableConv2D
                    )
                )
            ):

                candidate_layers.append(
                    layer
                )


        if not candidate_layers:

            raise ValueError(
                "No convolution layer found inside ResNet50."
            )


        return candidate_layers[-1]


    # =====================================================
    # PREPROCESS IMAGE
    # =====================================================

    def preprocess_image(
        self,
        image_path
    ):

        """
        Prepare image exactly like training.

        Input:
            original image

        Resize:
            224 x 224

        Preprocessing:
            ResNet50 preprocess_input

        Output:
            (1, 224, 224, 3)
        """

        # -------------------------------------------------
        # Check image
        # -------------------------------------------------

        if not os.path.exists(
            image_path
        ):

            raise FileNotFoundError(
                f"Image not found:\n{image_path}"
            )


        logger.info(
            "Preprocessing image for Grad-CAM: %s",
            image_path
        )


        # -------------------------------------------------
        # Load image
        # -------------------------------------------------

        img = image.load_img(
            image_path,
            target_size=IMAGE_SIZE,
            color_mode="rgb"
        )


        # -------------------------------------------------
        # Convert to numpy
        # -------------------------------------------------

        img_array = image.img_to_array(
            img
        )


        # -------------------------------------------------
        # ResNet50 preprocessing
        # IMPORTANT
        # -------------------------------------------------

        img_array = preprocess_input(
            img_array
        )


        # -------------------------------------------------
        # Add batch dimension
        # -------------------------------------------------

        img_array = np.expand_dims(
            img_array,
            axis=0
        )


        logger.info(
            "Grad-CAM preprocessed image shape: %s",
            img_array.shape
        )


        # -------------------------------------------------
        # Safety validation
        # -------------------------------------------------

        expected_shape = (
            1,
            IMAGE_HEIGHT,
            IMAGE_WIDTH,
            3
        )


        if img_array.shape != expected_shape:

            raise ValueError(
                "\n"
                "Grad-CAM preprocessing shape mismatch.\n"
                f"Expected: {expected_shape}\n"
                f"Actual:   {img_array.shape}"
            )


        return img_array


    # =====================================================
    # BUILD GRAD-CAM MODEL
    # =====================================================

    def build_gradcam_model(
        self
    ):

        """
        Create the Grad-CAM graph.

        Because ResNet50 is nested inside the forensic
        model, we calculate gradients through:

            ResNet50
                ↓
            GAP
                ↓
            Dense
                ↓
            Dropout
                ↓
            Output
        """

        # -------------------------------------------------
        # Backbone Grad-CAM model
        # -------------------------------------------------

        backbone_grad_model = tf.keras.models.Model(

            inputs=self.backbone.input,

            outputs=[
                self.last_conv_layer.output,
                self.backbone.output
            ]

        )


        return backbone_grad_model


    # =====================================================
    # APPLY CLASSIFIER HEAD
    # =====================================================

    def apply_classifier_head(
        self,
        backbone_output
    ):

        """
        Pass ResNet50 output through the remaining layers
        of the forensic model.

        Expected architecture:

            ResNet50
            GAP
            Dense
            Dropout
            Dense
        """

        x = backbone_output


        # -------------------------------------------------
        # Find backbone index
        # -------------------------------------------------

        backbone_index = (
            self.model.layers.index(
                self.backbone
            )
        )


        # -------------------------------------------------
        # Apply layers after ResNet50
        # -------------------------------------------------

        for layer in self.model.layers[
            backbone_index + 1:
        ]:

            # Ignore input layers
            if isinstance(
                layer,
                tf.keras.layers.InputLayer
            ):

                continue


            x = layer(
                x,
                training=False
            )


        return x


    # =====================================================
    # GENERATE HEATMAP
    # =====================================================

    def generate_heatmap(
        self,
        image_path
    ):

        """
        Generate Grad-CAM heatmap.

        Returns:

            heatmap
            predicted_class
            confidence
        """

        logger.info(
            "Generating Grad-CAM heatmap..."
        )


        # =================================================
        # PREPROCESS
        # =================================================

        img_array = (
            self.preprocess_image(
                image_path
            )
        )


        # =================================================
        # BUILD GRAPH
        # =================================================

        grad_model = (
            self.build_gradcam_model()
        )


        # =================================================
        # GRADIENT CALCULATION
        # =================================================

        img_tensor = tf.convert_to_tensor(
            img_array,
            dtype=tf.float32
        )


        with tf.GradientTape() as tape:

            # ---------------------------------------------
            # ResNet backbone
            # ---------------------------------------------

            conv_outputs, backbone_output = (
                grad_model(
                    img_tensor,
                    training=False
                )
            )


            # ---------------------------------------------
            # Apply forensic classifier head
            # ---------------------------------------------

            predictions = (
                self.apply_classifier_head(
                    backbone_output
                )
            )


            # ---------------------------------------------
            # Predicted class
            # ---------------------------------------------

            predicted_class = tf.argmax(
                predictions[0]
            )


            # ---------------------------------------------
            # Predicted probability
            # ---------------------------------------------

            predicted_score = predictions[
                0,
                predicted_class
            ]


        # =================================================
        # GRADIENTS
        # =================================================

        gradients = tape.gradient(
            predicted_score,
            conv_outputs
        )


        if gradients is None:

            raise ValueError(
                "Gradients could not be generated."
            )


        # =================================================
        # GLOBAL AVERAGE GRADIENTS
        # =================================================

        pooled_gradients = tf.reduce_mean(
            gradients,
            axis=(
                0,
                1,
                2
            )
        )


        # =================================================
        # REMOVE BATCH DIMENSION
        # =================================================

        conv_outputs = conv_outputs[0]


        # =================================================
        # WEIGHT FEATURE MAPS
        # =================================================

        heatmap = tf.reduce_sum(
            conv_outputs *
            pooled_gradients,
            axis=-1
        )


        # =================================================
        # RELU
        # =================================================

        heatmap = tf.maximum(
            heatmap,
            0
        )


        # =================================================
        # NORMALIZE
        # =================================================

        heatmap_max = tf.reduce_max(
            heatmap
        )


        if float(
            heatmap_max
        ) > 0:

            heatmap = (
                heatmap /
                heatmap_max
            )


        # =================================================
        # NUMPY
        # =================================================

        heatmap = heatmap.numpy()


        logger.info(
            "Heatmap shape: %s",
            heatmap.shape
        )


        logger.info(
            "Predicted class: %s",
            CLASS_NAMES[
                int(predicted_class)
            ]
        )


        logger.info(
            "Grad-CAM confidence: %.4f",
            float(predicted_score)
        )


        return (
            heatmap,
            int(predicted_class),
            float(predicted_score)
        )


    # =====================================================
    # SAVE GRAD-CAM
    # =====================================================

    def save_gradcam(
        self,
        image_path
    ):

        """
        Generate and save Grad-CAM overlay.

        The final output is resized to the ORIGINAL
        image dimensions, not forced to 224 x 224.
        """

        # -------------------------------------------------
        # Generate heatmap
        # -------------------------------------------------

        (
            heatmap,
            predicted_class,
            confidence
        ) = self.generate_heatmap(
            image_path
        )


        # -------------------------------------------------
        # Read original image
        # -------------------------------------------------

        original = cv2.imread(
            image_path
        )


        if original is None:

            raise ValueError(
                f"Could not read original image:\n"
                f"{image_path}"
            )


        # -------------------------------------------------
        # Original dimensions
        # -------------------------------------------------

        original_height, original_width = (
            original.shape[:2]
        )


        # -------------------------------------------------
        # Resize heatmap to original image size
        # -------------------------------------------------

        heatmap = cv2.resize(
            heatmap,
            (
                original_width,
                original_height
            )
        )


        # -------------------------------------------------
        # Convert heatmap to uint8
        # -------------------------------------------------

        heatmap_uint8 = np.uint8(
            255 * heatmap
        )


        # -------------------------------------------------
        # Apply color map
        # -------------------------------------------------

        heatmap_color = cv2.applyColorMap(
            heatmap_uint8,
            cv2.COLORMAP_JET
        )


        # -------------------------------------------------
        # Overlay
        # -------------------------------------------------

        overlay = cv2.addWeighted(
            original,
            0.60,
            heatmap_color,
            0.40,
            0
        )


        # =================================================
        # OUTPUT FOLDER
        # =================================================

        output_folder = (
            Config.OUTPUT_FOLDER
        )


        # Create output directory
        os.makedirs(
            output_folder,
            exist_ok=True
        )


        # -------------------------------------------------
        # Filename
        # -------------------------------------------------

        output_filename = (
            "gradcam_result.jpg"
        )


        output_path = os.path.join(
            output_folder,
            output_filename
        )


        # -------------------------------------------------
        # Save
        # -------------------------------------------------

        success = cv2.imwrite(
            output_path,
            overlay
        )


        if not success:

            raise IOError(
                "Failed to save Grad-CAM image:\n"
                f"{output_path}"
            )


        logger.info(
            "Grad-CAM saved: %s",
            output_path
        )


        return output_path


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AI IMAGE FORENSICS - GRAD-CAM TEST")
    print("=" * 70)

    print(
        "Model:",
        MODEL_PATH
    )

    print(
        "Model input:",
        GradCAMGenerator.__name__
    )

    print(
        "Image size:",
        IMAGE_SIZE
    )

    print(
        "Classes:",
        CLASS_NAMES
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
            "Image does not exist:"
        )

        print(
            test_image
        )

    else:

        try:

            generator = (
                GradCAMGenerator()
            )


            output = (
                generator.save_gradcam(
                    test_image
                )
            )


            print()
            print("=" * 70)

            print(
                "Grad-CAM generated successfully:"
            )

            print(
                output
            )

            print("=" * 70)

        except Exception as exc:

            logger.exception(
                "Grad-CAM test failed."
            )

            print()
            print(
                "Grad-CAM failed:"
            )

            print(
                str(exc)
            )