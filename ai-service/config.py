"""
=========================================================
AI IMAGE FORENSICS
Central Configuration
=========================================================
"""

import os


# =========================================================
# BASE DIRECTORIES
# =========================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    CURRENT_DIR
)


# =========================================================
# FOLDERS
# =========================================================

UPLOAD_FOLDER = os.path.join(
    CURRENT_DIR,
    "uploads"
)

OUTPUT_FOLDER = os.path.join(
    CURRENT_DIR,
    "outputs"
)

TEMP_FOLDER = os.path.join(
    CURRENT_DIR,
    "temp"
)

MODEL_FOLDER = os.path.join(
    CURRENT_DIR,
    "model"
)


# =========================================================
# MODEL
# =========================================================

MODEL_PATH = os.path.join(
    MODEL_FOLDER,
    "resnet_model.h5"
)

NUM_CLASSES = 3

CLASS_NAMES = [
    "AI_GENERATED",
    "AUTHENTIC",
    "MANIPULATED"
]


# =========================================================
# IMAGE SETTINGS
# =========================================================

IMAGE_WIDTH = 128

IMAGE_HEIGHT = 128

IMAGE_SIZE = (
    IMAGE_WIDTH,
    IMAGE_HEIGHT
)


# =========================================================
# ELA SETTINGS
# =========================================================

JPEG_QUALITY = 90

ELA_SCALE = 10


# =========================================================
# UPLOAD SETTINGS
# =========================================================

MAX_CONTENT_LENGTH = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "tiff",
    "bmp"
}


# =========================================================
# SERVER SETTINGS
# =========================================================

HOST = "127.0.0.1"

PORT = 5001

DEBUG = True


# =========================================================
# RESULT SETTINGS
# =========================================================

RESULT_AUTHENTIC = "AUTHENTIC"

RESULT_MANIPULATED = "MANIPULATED"

RESULT_AI_GENERATED = "AI_GENERATED"


# =========================================================
# INVESTIGATION DATABASE
# =========================================================

INVESTIGATIONS_FILE = os.path.join(
    CURRENT_DIR,
    "investigations.json"
)


# =========================================================
# CREATE REQUIRED FOLDERS
# =========================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

os.makedirs(
    TEMP_FOLDER,
    exist_ok=True
)

os.makedirs(
    MODEL_FOLDER,
    exist_ok=True
)


# =========================================================
# CONFIG CLASS
# =========================================================

class Config:

    # -----------------------------------------------------
    # Base
    # -----------------------------------------------------

    CURRENT_DIR = CURRENT_DIR

    PROJECT_DIR = PROJECT_DIR

    # -----------------------------------------------------
    # Folders
    # -----------------------------------------------------

    UPLOAD_FOLDER = UPLOAD_FOLDER

    OUTPUT_FOLDER = OUTPUT_FOLDER

    TEMP_FOLDER = TEMP_FOLDER

    MODEL_FOLDER = MODEL_FOLDER

    # -----------------------------------------------------
    # Model
    # -----------------------------------------------------

    MODEL_PATH = MODEL_PATH

    NUM_CLASSES = NUM_CLASSES

    CLASS_NAMES = CLASS_NAMES

    # -----------------------------------------------------
    # Image
    # -----------------------------------------------------

    IMAGE_WIDTH = IMAGE_WIDTH

    IMAGE_HEIGHT = IMAGE_HEIGHT

    IMAGE_SIZE = IMAGE_SIZE

    # -----------------------------------------------------
    # ELA
    # -----------------------------------------------------

    JPEG_QUALITY = JPEG_QUALITY

    ELA_SCALE = ELA_SCALE

    # -----------------------------------------------------
    # Upload
    # -----------------------------------------------------

    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH

    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS

    # -----------------------------------------------------
    # Server
    # -----------------------------------------------------

    HOST = HOST

    PORT = PORT

    DEBUG = DEBUG

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    RESULT_AUTHENTIC = RESULT_AUTHENTIC

    RESULT_MANIPULATED = RESULT_MANIPULATED

    RESULT_AI_GENERATED = RESULT_AI_GENERATED

    # -----------------------------------------------------
    # Database
    # -----------------------------------------------------

    INVESTIGATIONS_FILE = INVESTIGATIONS_FILE