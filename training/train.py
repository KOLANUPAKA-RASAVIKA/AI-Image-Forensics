import os
import json
import shutil
import logging

import numpy as np
import tensorflow as tf

from tensorflow.keras import layers, models
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from tensorflow.keras.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    ReduceLROnPlateau,
    CSVLogger
)

from sklearn.metrics import (
    classification_report,
    confusion_matrix
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

TRAIN_DIR = os.path.join(
    DATASET_DIR,
    "train"
)

VALIDATION_DIR = os.path.join(
    DATASET_DIR,
    "validation"
)

TEST_DIR = os.path.join(
    DATASET_DIR,
    "test"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

# Flask deployment model directory
AI_SERVICE_MODEL_DIR = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "ai-service",
        "model"
    )
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

os.makedirs(
    AI_SERVICE_MODEL_DIR,
    exist_ok=True
)


# ============================================================
# MODEL PATHS
# ============================================================

BEST_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "resnet_model.keras"
)

FINAL_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "resnet_final.keras"
)

DEPLOY_MODEL_PATH = os.path.join(
    AI_SERVICE_MODEL_DIR,
    "resnet_model.h5"
)

DEPLOY_MODEL_KERAS_PATH = os.path.join(
    AI_SERVICE_MODEL_DIR,
    "resnet_model.keras"
)

LOG_PATH = os.path.join(
    MODEL_DIR,
    "training_log.csv"
)

TRAINING_INFO_PATH = os.path.join(
    MODEL_DIR,
    "training_info.json"
)

CONFUSION_MATRIX_PATH = os.path.join(
    MODEL_DIR,
    "confusion_matrix.npy"
)

CLASSIFICATION_REPORT_PATH = os.path.join(
    MODEL_DIR,
    "classification_report.json"
)


# ============================================================
# TRAINING SETTINGS
# ============================================================

IMG_SIZE = (
    224,
    224
)

BATCH_SIZE = 16

HEAD_EPOCHS = 8

FINE_TUNE_EPOCHS = 15

TOTAL_EPOCHS = (
    HEAD_EPOCHS +
    FINE_TUNE_EPOCHS
)

NUM_CLASSES = 3

CLASS_NAMES = [
    "AI_GENERATED",
    "AUTHENTIC",
    "MANIPULATED"
]

SEED = 42


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(
    __name__
)


# ============================================================
# GPU / CPU
# ============================================================

print("=" * 70)
print("AI IMAGE FORENSICS")
print("RESNET50 FORENSIC TRAINING")
print("=" * 70)

gpus = tf.config.list_physical_devices(
    "GPU"
)

if gpus:

    logger.info(
        "GPU detected:"
    )

    for gpu in gpus:
        logger.info(
            str(gpu)
        )

else:

    logger.info(
        "No GPU detected. Training will use CPU."
    )


# ============================================================
# DATASET VALIDATION
# ============================================================

def count_images(folder):

    extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
        ".tif",
        ".tiff"
    )

    count = 0

    if not os.path.exists(folder):
        return 0

    for root, _, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(
                extensions
            ):

                count += 1

    return count


def validate_dataset():

    print()
    print("=" * 70)
    print("VALIDATING DATASET")
    print("=" * 70)

    split_dirs = {
        "train": TRAIN_DIR,
        "validation": VALIDATION_DIR,
        "test": TEST_DIR
    }

    totals = {}

    for split_name, split_dir in split_dirs.items():

        print()
        print(split_name.upper())

        total = 0

        if not os.path.exists(
            split_dir
        ):

            raise FileNotFoundError(
                f"Missing dataset directory:\n{split_dir}"
            )

        for class_name in CLASS_NAMES:

            class_dir = os.path.join(
                split_dir,
                class_name
            )

            count = count_images(
                class_dir
            )

            print(
                f"{class_name:18} : {count}"
            )

            total += count

        totals[split_name] = total

        print(
            f"{'TOTAL':18} : {total}"
        )

    print()
    print("-" * 70)

    # Every class must contain data
    for split_name, split_dir in split_dirs.items():

        for class_name in CLASS_NAMES:

            class_dir = os.path.join(
                split_dir,
                class_name
            )

            count = count_images(
                class_dir
            )

            if count == 0:

                raise ValueError(
                    f"No images found in:\n{class_dir}"
                )

    print(
        "DATASET VALIDATION PASSED"
    )

    return totals


# ============================================================
# DATA GENERATORS
# ============================================================

def create_generators():

    print()
    print("=" * 70)
    print("CREATING DATA GENERATORS")
    print("=" * 70)

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,

        rotation_range=15,

        width_shift_range=0.08,

        height_shift_range=0.08,

        zoom_range=0.12,

        shear_range=0.08,

        horizontal_flip=True,

        brightness_range=(
            0.90,
            1.10
        ),

        fill_mode="nearest"
    )


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validation_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )


    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    test_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )


    # --------------------------------------------------------
    # TRAIN GENERATOR
    # --------------------------------------------------------

    train_generator = train_datagen.flow_from_directory(

        TRAIN_DIR,

        target_size=IMG_SIZE,

        batch_size=BATCH_SIZE,

        class_mode="categorical",

        classes=CLASS_NAMES,

        shuffle=True,

        seed=SEED
    )


    # --------------------------------------------------------
    # VALIDATION GENERATOR
    # --------------------------------------------------------

    validation_generator = validation_datagen.flow_from_directory(

        VALIDATION_DIR,

        target_size=IMG_SIZE,

        batch_size=BATCH_SIZE,

        class_mode="categorical",

        classes=CLASS_NAMES,

        shuffle=False
    )


    # --------------------------------------------------------
    # TEST GENERATOR
    # --------------------------------------------------------

    test_generator = test_datagen.flow_from_directory(

        TEST_DIR,

        target_size=IMG_SIZE,

        batch_size=BATCH_SIZE,

        class_mode="categorical",

        classes=CLASS_NAMES,

        shuffle=False
    )


    print()
    print(
        "Training class mapping:",
        train_generator.class_indices
    )

    print(
        "Validation class mapping:",
        validation_generator.class_indices
    )

    print(
        "Test class mapping:",
        test_generator.class_indices
    )


    expected_mapping = {
        name: index
        for index, name
        in enumerate(CLASS_NAMES)
    }


    if (
        train_generator.class_indices
        != expected_mapping
    ):

        raise ValueError(
            "Training class mapping is incorrect."
        )


    if (
        validation_generator.class_indices
        != expected_mapping
    ):

        raise ValueError(
            "Validation class mapping is incorrect."
        )


    if (
        test_generator.class_indices
        != expected_mapping
    ):

        raise ValueError(
            "Test class mapping is incorrect."
        )


    return (
        train_generator,
        validation_generator,
        test_generator
    )


# ============================================================
# BUILD RESNET50
# ============================================================

def build_model():

    print()
    print("=" * 70)
    print("BUILDING RESNET50 MODEL")
    print("=" * 70)

    logger.info(
        "Loading ImageNet pretrained ResNet50..."
    )


    base_model = ResNet50(

        weights="imagenet",

        include_top=False,

        input_shape=(
            IMG_SIZE[0],
            IMG_SIZE[1],
            3
        )
    )


    # --------------------------------------------------------
    # FREEZE BACKBONE INITIALLY
    # --------------------------------------------------------

    base_model.trainable = False


    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    inputs = layers.Input(
        shape=(
            IMG_SIZE[0],
            IMG_SIZE[1],
            3
        ),
        name="image_input"
    )


    # --------------------------------------------------------
    # BACKBONE
    # --------------------------------------------------------

    x = base_model(
        inputs,
        training=False
    )


    # --------------------------------------------------------
    # GLOBAL AVERAGE POOLING
    # --------------------------------------------------------

    x = layers.GlobalAveragePooling2D(
        name="global_average_pooling"
    )(x)


    # --------------------------------------------------------
    # DENSE FEATURES
    # --------------------------------------------------------

    x = layers.Dense(
        256,
        activation="relu",
        name="feature_dense"
    )(x)


    # --------------------------------------------------------
    # DROPOUT
    # --------------------------------------------------------

    x = layers.Dropout(
        0.35,
        name="feature_dropout"
    )(x)


    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    outputs = layers.Dense(
        NUM_CLASSES,
        activation="softmax",
        name="forensic_prediction"
    )(x)


    model = models.Model(
        inputs=inputs,
        outputs=outputs,
        name="ImageForensicsResNet50"
    )


    return (
        model,
        base_model
    )


# ============================================================
# COMPILE
# ============================================================

def compile_model(
    model,
    learning_rate
):

    model.compile(

        optimizer=tf.keras.optimizers.Adam(
            learning_rate=learning_rate
        ),

        loss="categorical_crossentropy",

        metrics=[
            tf.keras.metrics.CategoricalAccuracy(
                name="accuracy"
            )
        ]
    )


# ============================================================
# CALLBACKS
# ============================================================

def create_callbacks():

    checkpoint = ModelCheckpoint(

        BEST_MODEL_PATH,

        monitor="val_accuracy",

        mode="max",

        save_best_only=True,

        verbose=1
    )


    early_stopping = EarlyStopping(

        monitor="val_accuracy",

        mode="max",

        patience=5,

        restore_best_weights=True,

        verbose=1
    )


    reduce_lr = ReduceLROnPlateau(

        monitor="val_loss",

        factor=0.25,

        patience=2,

        min_lr=1e-7,

        verbose=1
    )


    csv_logger = CSVLogger(
        LOG_PATH,
        append=False
    )


    return [
        checkpoint,
        early_stopping,
        reduce_lr,
        csv_logger
    ]


# ============================================================
# FINE TUNING
# ============================================================

def prepare_fine_tuning(
    base_model
):

    print()
    print("=" * 70)
    print("PREPARING RESNET50 FINE-TUNING")
    print("=" * 70)


    base_model.trainable = True


    # Freeze most layers.
    # Fine-tune the final 40 layers.
    for layer in base_model.layers[:-40]:

        layer.trainable = False


    # BatchNorm should remain frozen.
    for layer in base_model.layers:

        if isinstance(
            layer,
            layers.BatchNormalization
        ):

            layer.trainable = False


    trainable_count = sum(

        1

        for layer
        in base_model.layers

        if layer.trainable
    )


    logger.info(
        "Trainable ResNet50 layers: %s",
        trainable_count
    )


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(
    model,
    test_generator
):

    print()
    print("=" * 70)
    print("FINAL TEST EVALUATION")
    print("=" * 70)


    test_generator.reset()


    test_loss, test_accuracy = (
        model.evaluate(
            test_generator,
            verbose=1
        )
    )


    print()
    print(
        f"Test Loss     : {test_loss:.4f}"
    )

    print(
        f"Test Accuracy : {test_accuracy * 100:.2f}%"
    )


    # --------------------------------------------------------
    # PREDICTIONS
    # --------------------------------------------------------

    test_generator.reset()


    predictions = model.predict(
        test_generator,
        verbose=1
    )


    predicted_indices = np.argmax(
        predictions,
        axis=1
    )


    true_indices = (
        test_generator.classes
    )


    # --------------------------------------------------------
    # CONFUSION MATRIX
    # --------------------------------------------------------

    matrix = confusion_matrix(

        true_indices,

        predicted_indices,

        labels=list(
            range(NUM_CLASSES)
        )
    )


    np.save(
        CONFUSION_MATRIX_PATH,
        matrix
    )


    print()
    print(
        "CONFUSION MATRIX"
    )

    print(
        matrix
    )


    # --------------------------------------------------------
    # CLASSIFICATION REPORT
    # --------------------------------------------------------

    report = classification_report(

        true_indices,

        predicted_indices,

        labels=list(
            range(NUM_CLASSES)
        ),

        target_names=CLASS_NAMES,

        output_dict=True,

        zero_division=0
    )


    with open(
        CLASSIFICATION_REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )


    print()
    print(
        "CLASSIFICATION REPORT"
    )

    print(
        classification_report(

            true_indices,

            predicted_indices,

            labels=list(
                range(NUM_CLASSES)
            ),

            target_names=CLASS_NAMES,

            zero_division=0
        )
    )


    return (
        test_loss,
        test_accuracy,
        matrix,
        report
    )


# ============================================================
# SAVE TRAINING INFORMATION
# ============================================================

def save_training_info(

    history1,

    history2,

    test_loss,

    test_accuracy,

    matrix,

    report
):

    history = {}


    for key, values in (
        history1.history.items()
    ):

        history[key] = [
            float(value)
            for value in values
        ]


    for key, values in (
        history2.history.items()
    ):

        if key not in history:

            history[key] = []


        history[key].extend(

            float(value)

            for value in values
        )


    info = {

        "classes":
            CLASS_NAMES,

        "class_mapping": {
            name: index
            for index, name
            in enumerate(CLASS_NAMES)
        },

        "image_size":
            list(IMG_SIZE),

        "batch_size":
            BATCH_SIZE,

        "head_epochs":
            HEAD_EPOCHS,

        "fine_tune_epochs":
            FINE_TUNE_EPOCHS,

        "test_loss":
            float(test_loss),

        "test_accuracy":
            float(test_accuracy),

        "confusion_matrix":
            matrix.tolist(),

        "classification_report":
            report,

        "history":
            history
    }


    with open(

        TRAINING_INFO_PATH,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            info,

            file,

            indent=4
        )


# ============================================================
# DEPLOY MODEL TO AI SERVICE
# ============================================================

def deploy_model(
    model
):

    print()
    print("=" * 70)
    print("DEPLOYING MODEL TO FLASK AI SERVICE")
    print("=" * 70)


    # --------------------------------------------------------
    # Save native Keras model
    # --------------------------------------------------------

    model.save(
        DEPLOY_MODEL_KERAS_PATH
    )


    logger.info(
        "Keras model deployed to: %s",
        DEPLOY_MODEL_KERAS_PATH
    )


    # --------------------------------------------------------
    # Save H5 model
    # --------------------------------------------------------

    model.save(
        DEPLOY_MODEL_PATH
    )


    logger.info(
        "H5 model deployed to: %s",
        DEPLOY_MODEL_PATH
    )


    print()
    print(
        "DEPLOYMENT COMPLETE"
    )

    print(
        f"Model: {DEPLOY_MODEL_PATH}"
    )


# ============================================================
# MAIN TRAINING
# ============================================================

def main():

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    totals = validate_dataset()


    (
        train_generator,
        validation_generator,
        test_generator
    ) = create_generators()


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model, base_model = build_model()


    print()
    print("=" * 70)
    print("MODEL SUMMARY")
    print("=" * 70)

    model.summary()


    # --------------------------------------------------------
    # CALLBACKS
    # --------------------------------------------------------

    callbacks = create_callbacks()


    # ========================================================
    # STAGE 1
    # ========================================================

    print()
    print("=" * 70)
    print("STAGE 1")
    print("TRAINING CLASSIFICATION HEAD")
    print("=" * 70)


    compile_model(
        model,
        learning_rate=1e-3
    )


    history1 = model.fit(

        train_generator,

        validation_data=
            validation_generator,

        epochs=
            HEAD_EPOCHS,

        callbacks=
            callbacks,

        verbose=1
    )


    # ========================================================
    # STAGE 2
    # ========================================================

    print()
    print("=" * 70)
    print("STAGE 2")
    print("FINE-TUNING RESNET50")
    print("=" * 70)


    prepare_fine_tuning(
        base_model
    )


    compile_model(
        model,
        learning_rate=1e-5
    )


    history2 = model.fit(

        train_generator,

        validation_data=
            validation_generator,

        initial_epoch=
            HEAD_EPOCHS,

        epochs=
            TOTAL_EPOCHS,

        callbacks=
            callbacks,

        verbose=1
    )


    # ========================================================
    # LOAD BEST MODEL
    # ========================================================

    print()
    print("=" * 70)
    print("LOADING BEST MODEL")
    print("=" * 70)


    if not os.path.exists(
        BEST_MODEL_PATH
    ):

        raise FileNotFoundError(
            "Best model was not created:\n"
            f"{BEST_MODEL_PATH}"
        )


    model = tf.keras.models.load_model(
        BEST_MODEL_PATH
    )


    logger.info(
        "Best model loaded successfully."
    )


    # ========================================================
    # TEST
    # ========================================================

    (
        test_loss,
        test_accuracy,
        matrix,
        report
    ) = evaluate_model(

        model,

        test_generator
    )


    # ========================================================
    # SAVE FINAL MODEL
    # ========================================================

    model.save(
        FINAL_MODEL_PATH
    )


    logger.info(
        "Final model saved to: %s",
        FINAL_MODEL_PATH
    )


    # ========================================================
    # SAVE TRAINING INFO
    # ========================================================

    save_training_info(

        history1,

        history2,

        test_loss,

        test_accuracy,

        matrix,

        report
    )


    # ========================================================
    # DEPLOY MODEL
    # ========================================================

    deploy_model(
        model
    )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("TRAINING COMPLETED")
    print("=" * 70)

    print()
    print(
        f"Train images      : {totals['train']}"
    )

    print(
        f"Validation images : {totals['validation']}"
    )

    print(
        f"Test images       : {totals['test']}"
    )

    print()
    print(
        f"Test accuracy     : {test_accuracy * 100:.2f}%"
    )

    print()
    print(
        "Classes:"
    )

    for index, class_name in enumerate(
        CLASS_NAMES
    ):

        print(
            f"  {index} -> {class_name}"
        )

    print()
    print(
        f"Best model:"
    )

    print(
        BEST_MODEL_PATH
    )

    print()
    print(
        "Flask deployment model:"
    )

    print(
        DEPLOY_MODEL_PATH
    )

    print()
    print(
        "Confusion matrix:"
    )

    print(
        CONFUSION_MATRIX_PATH
    )

    print()
    print(
        "Classification report:"
    )

    print(
        CLASSIFICATION_REPORT_PATH
    )

    print()
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()