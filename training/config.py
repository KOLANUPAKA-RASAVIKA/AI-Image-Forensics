import os


class Config:

    # =====================================================
    # PATHS
    # =====================================================

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    PROJECT_DIR = os.path.dirname(BASE_DIR)

    DATASET_DIR = os.path.join(
        BASE_DIR,
        "dataset"
    )

    MODEL_DIR = os.path.join(
        BASE_DIR,
        "models"
    )

    MODEL_PATH = os.path.join(
        MODEL_DIR,
        "resnet_model.h5"
    )

    HISTORY_DIR = os.path.join(
        BASE_DIR,
        "history"
    )

    # =====================================================
    # IMAGE
    # =====================================================

    IMAGE_WIDTH = 128
    IMAGE_HEIGHT = 128
    CHANNELS = 3

    IMAGE_SIZE = (
        IMAGE_WIDTH,
        IMAGE_HEIGHT
    )

    INPUT_SHAPE = (
        IMAGE_HEIGHT,
        IMAGE_WIDTH,
        CHANNELS
    )

    # =====================================================
    # CLASSES
    # =====================================================

    CLASS_NAMES = [
        "AI_GENERATED",
        "AUTHENTIC",
        "MANIPULATED"
    ]

    NUM_CLASSES = len(CLASS_NAMES)

    CLASS_MODE = "categorical"

    # =====================================================
    # TRAINING
    # =====================================================

    BATCH_SIZE = 32
    EPOCHS = 20

    LEARNING_RATE = 0.0001

    RANDOM_SEED = 42

    VERBOSE = 1

    # =====================================================
    # DATA AUGMENTATION
    # =====================================================

    ROTATION_RANGE = 15

    WIDTH_SHIFT = 0.10

    HEIGHT_SHIFT = 0.10

    SHEAR_RANGE = 0.0

    ZOOM_RANGE = 0.10

    HORIZONTAL_FLIP = True

    VERTICAL_FLIP = False

    # =====================================================
    # CALLBACKS
    # =====================================================

    MONITOR = "val_accuracy"

    MODE = "max"

    SAVE_BEST_ONLY = True

    EARLY_STOPPING_PATIENCE = 4

    REDUCE_LR_PATIENCE = 2

    MIN_LEARNING_RATE = 0.000001

    # =====================================================
    # IMAGE EXTENSIONS
    # =====================================================

    ALLOWED_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "bmp",
        "tif",
        "tiff",
        "webp"
    }

    # =====================================================
    # PREDICTION
    # =====================================================

    THRESHOLD = 0.50

    # =====================================================
    # ELA
    # =====================================================

    JPEG_QUALITY = 90

    ELA_SCALE = 15

    # =====================================================
    # GRAD-CAM
    # =====================================================

    LAST_CONV_LAYER = "conv5_block3_out"

    COLORMAP = "JET"

    # =====================================================
    # DIRECTORIES
    # =====================================================

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    OUTPUT_FOLDER = os.path.join(
        BASE_DIR,
        "outputs"
    )

    TEMP_FOLDER = os.path.join(
        BASE_DIR,
        "temp"
    )

    # =====================================================
    # CREATE DIRECTORIES
    # =====================================================

    @staticmethod
    def create_directories():

        directories = [
            Config.MODEL_DIR,
            Config.HISTORY_DIR,
            Config.UPLOAD_FOLDER,
            Config.OUTPUT_FOLDER,
            Config.TEMP_FOLDER
        ]

        for directory in directories:

            os.makedirs(
                directory,
                exist_ok=True
            )


Config.create_directories()