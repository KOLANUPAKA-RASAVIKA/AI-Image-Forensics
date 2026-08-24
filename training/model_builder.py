"""
=========================================================
AI Image Forensics
Model Builder
=========================================================

ResNet50-based 3-class classifier.

Classes:

0 -> AI_GENERATED
1 -> AUTHENTIC
2 -> MANIPULATED
=========================================================
"""

import logging

import tensorflow as tf

from tensorflow.keras.applications import ResNet50

from config import Config


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)


# =========================================================
# MODEL BUILDER
# =========================================================

class ModelBuilder:

    def __init__(self):

        logger.info(
            "Initializing Model Builder..."
        )

        self.input_shape = Config.INPUT_SHAPE

        self.num_classes = Config.NUM_CLASSES

        self.learning_rate = Config.LEARNING_RATE

        self.base_model = None

        self.model = None

        self.load_base_model()

        logger.info(
            "Model Builder Initialized Successfully."
        )


    # =====================================================
    # LOAD RESNET50
    # =====================================================

    def load_base_model(self):

        logger.info(
            "Loading pretrained ResNet50..."
        )

        self.base_model = ResNet50(

            weights="imagenet",

            include_top=False,

            input_shape=self.input_shape

        )

        # -------------------------------------------------
        # Freeze pretrained layers initially
        # -------------------------------------------------

        self.base_model.trainable = False

        logger.info(
            "ResNet50 loaded successfully."
        )

        logger.info(
            f"ResNet50 input shape: "
            f"{self.input_shape}"
        )


    # =====================================================
    # BUILD NETWORK
    # =====================================================

    def build_network(self):

        logger.info(
            "Building classification network..."
        )

        # -------------------------------------------------
        # INPUT
        # -------------------------------------------------

        inputs = tf.keras.Input(

            shape=self.input_shape,

            name="image_input"

        )

        # -------------------------------------------------
        # RESNET50
        # -------------------------------------------------

        x = self.base_model(

            inputs,

            training=False

        )

        # -------------------------------------------------
        # GLOBAL AVERAGE POOLING
        # -------------------------------------------------

        x = tf.keras.layers.GlobalAveragePooling2D(

            name="global_average_pooling"

        )(x)

        # -------------------------------------------------
        # DROPOUT
        # -------------------------------------------------

        x = tf.keras.layers.Dropout(

            0.4,

            name="dropout"

        )(x)

        # -------------------------------------------------
        # DENSE FEATURE LAYER
        # -------------------------------------------------

        x = tf.keras.layers.Dense(

            256,

            activation="relu",

            name="feature_dense"

        )(x)

        # -------------------------------------------------
        # SECOND DROPOUT
        # -------------------------------------------------

        x = tf.keras.layers.Dropout(

            0.3,

            name="feature_dropout"

        )(x)

        # -------------------------------------------------
        # 3 CLASS OUTPUT
        # -------------------------------------------------

        outputs = tf.keras.layers.Dense(

            self.num_classes,

            activation="softmax",

            name="forensic_prediction"

        )(x)

        # -------------------------------------------------
        # CREATE MODEL
        # -------------------------------------------------

        self.model = tf.keras.Model(

            inputs=inputs,

            outputs=outputs,

            name="ImageForensicsResNet50"

        )

        logger.info(
            "Classification network created."
        )

        logger.info(
            f"Number of output classes: "
            f"{self.num_classes}"
        )


    # =====================================================
    # COMPILE
    # =====================================================

    def compile_model(self):

        logger.info(
            "Compiling model..."
        )

        self.model.compile(

            optimizer=tf.keras.optimizers.Adam(

                learning_rate=self.learning_rate

            ),

            loss="categorical_crossentropy",

            metrics=[

                "accuracy"

            ]

        )

        logger.info(
            "Model compiled successfully."
        )


    # =====================================================
    # FREEZE BASE MODEL
    # =====================================================

    def freeze_base_model(self):

        self.base_model.trainable = False

        logger.info(
            "ResNet50 base model frozen."
        )


    # =====================================================
    # FINE TUNING
    # =====================================================

    def unfreeze_last_layers(

        self,

        num_layers=30

    ):

        logger.info(
            f"Unfreezing last "
            f"{num_layers} ResNet50 layers..."
        )

        self.base_model.trainable = True

        # -------------------------------------------------
        # Freeze earlier layers
        # -------------------------------------------------

        for layer in self.base_model.layers[

            :-num_layers

        ]:

            layer.trainable = False

        # -------------------------------------------------
        # Keep BatchNormalization frozen
        # -------------------------------------------------

        for layer in self.base_model.layers:

            if isinstance(

                layer,

                tf.keras.layers.BatchNormalization

            ):

                layer.trainable = False

        logger.info(
            "Fine-tuning configuration completed."
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        logger.info("=" * 60)

        logger.info(
            "MODEL SUMMARY"
        )

        logger.info("=" * 60)

        self.model.summary()

        logger.info("=" * 60)


    # =====================================================
    # BUILD COMPLETE MODEL
    # =====================================================

    def build(self):

        self.build_network()

        self.compile_model()

        self.summary()

        return self.model


# =========================================================
# PUBLIC FUNCTION
# =========================================================

def build_model():

    builder = ModelBuilder()

    return builder.build()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    logger.info("=" * 60)

    logger.info(
        "TESTING MODEL BUILDER"
    )

    logger.info("=" * 60)

    model = build_model()

    logger.info(
        f"Input Shape: "
        f"{model.input_shape}"
    )

    logger.info(
        f"Output Shape: "
        f"{model.output_shape}"
    )

    logger.info(
        f"Number of Classes: "
        f"{Config.NUM_CLASSES}"
    )

    logger.info(
        "Class Mapping:"
    )

    logger.info(
        "0 -> AI_GENERATED"
    )

    logger.info(
        "1 -> AUTHENTIC"
    )

    logger.info(
        "2 -> MANIPULATED"
    )

    logger.info("=" * 60)

    logger.info(
        "MODEL BUILDER TEST COMPLETED"
    )