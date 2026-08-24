"""
=========================================================
AI Image Forensics
Dataset Loader
=========================================================

Loads a 3-class image dataset:

0 -> AI_GENERATED
1 -> AUTHENTIC
2 -> MANIPULATED

Expected structure:

training/
└── dataset/
    ├── train/
    │   ├── AI_GENERATED/
    │   ├── AUTHENTIC/
    │   └── MANIPULATED/
    │
    ├── validation/
    │   ├── AI_GENERATED/
    │   ├── AUTHENTIC/
    │   └── MANIPULATED/
    │
    └── test/
        ├── AI_GENERATED/
        ├── AUTHENTIC/
        └── MANIPULATED/
=========================================================
"""

from pathlib import Path
import json
import logging

from tensorflow.keras.preprocessing.image import ImageDataGenerator

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
# DATASET LOADER
# =========================================================

class DatasetLoader:

    def __init__(self):

        # -------------------------------------------------
        # Dataset paths
        # -------------------------------------------------

        self.dataset_dir = Path(
            Config.DATASET_DIR
        )

        self.train_dir = (
            self.dataset_dir / "train"
        )

        self.validation_dir = (
            self.dataset_dir / "validation"
        )

        self.test_dir = (
            self.dataset_dir / "test"
        )

        # -------------------------------------------------
        # Image configuration
        # -------------------------------------------------

        self.image_size = (
            Config.IMAGE_HEIGHT,
            Config.IMAGE_WIDTH
        )

        self.batch_size = Config.BATCH_SIZE

        self.seed = Config.RANDOM_SEED

        # -------------------------------------------------
        # Supported image extensions
        # -------------------------------------------------

        self.image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tif",
            ".tiff",
            ".webp"
        }

        # -------------------------------------------------
        # Training augmentation
        # -------------------------------------------------

        self.train_datagen = ImageDataGenerator(

            rescale=1.0 / 255.0,

            rotation_range=Config.ROTATION_RANGE,

            width_shift_range=Config.WIDTH_SHIFT,

            height_shift_range=Config.HEIGHT_SHIFT,

            shear_range=Config.SHEAR_RANGE,

            zoom_range=Config.ZOOM_RANGE,

            horizontal_flip=Config.HORIZONTAL_FLIP,

            vertical_flip=Config.VERTICAL_FLIP
        )

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        self.validation_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0
        )

        # -------------------------------------------------
        # Test
        # -------------------------------------------------

        self.test_datagen = ImageDataGenerator(
            rescale=1.0 / 255.0
        )

        logger.info(
            f"Dataset directory: {self.dataset_dir}"
        )

        logger.info(
            f"Classes: {Config.CLASS_NAMES}"
        )


    # =====================================================
    # COUNT IMAGES
    # =====================================================

    def count_images(self, directory):

        if not directory.exists():
            return 0

        return sum(

            1

            for file in directory.rglob("*")

            if file.is_file()

            and file.suffix.lower()
            in self.image_extensions
        )


    # =====================================================
    # VALIDATE DATASET
    # =====================================================

    def validate_dataset(self):

        logger.info("=" * 60)

        logger.info(
            "VALIDATING DATASET"
        )

        logger.info("=" * 60)

        # -------------------------------------------------
        # Dataset directory
        # -------------------------------------------------

        if not self.dataset_dir.exists():

            raise FileNotFoundError(
                f"Dataset directory not found:\n"
                f"{self.dataset_dir}"
            )

        # -------------------------------------------------
        # Split directories
        # -------------------------------------------------

        split_dirs = {

            "train": self.train_dir,

            "validation": self.validation_dir,

            "test": self.test_dir

        }

        # -------------------------------------------------
        # Check every split
        # -------------------------------------------------

        for split_name, split_dir in split_dirs.items():

            logger.info(
                f"\nChecking {split_name}:"
            )

            # -------------------------------------------------
            # Check split exists
            # -------------------------------------------------

            if not split_dir.exists():

                raise FileNotFoundError(
                    f"Missing split directory:\n"
                    f"{split_dir}"
                )

            # -------------------------------------------------
            # Check all classes
            # -------------------------------------------------

            for class_name in Config.CLASS_NAMES:

                class_dir = (
                    split_dir / class_name
                )

                # -------------------------------------------------
                # Check class directory
                # -------------------------------------------------

                if not class_dir.exists():

                    raise FileNotFoundError(
                        f"Missing class directory:\n"
                        f"{class_dir}"
                    )

                # -------------------------------------------------
                # Count images
                # -------------------------------------------------

                image_count = self.count_images(
                    class_dir
                )

                logger.info(
                    f"{split_name}/{class_name}: "
                    f"{image_count} images"
                )

                # -------------------------------------------------
                # Warning if empty
                # -------------------------------------------------

                if image_count == 0:

                    logger.warning(
                        f"WARNING: {class_dir} "
                        f"contains 0 images"
                    )

        logger.info(
            "\nDataset validation completed."
        )


    # =====================================================
    # LOAD TRAIN DATA
    # =====================================================

    def load_train_data(self):

        logger.info(
            "\nLoading training dataset..."
        )

        generator = (
            self.train_datagen.flow_from_directory(

                directory=str(
                    self.train_dir
                ),

                target_size=self.image_size,

                batch_size=self.batch_size,

                class_mode=Config.CLASS_MODE,

                classes=Config.CLASS_NAMES,

                shuffle=True,

                seed=self.seed
            )
        )

        logger.info(
            f"Training images: "
            f"{generator.samples}"
        )

        logger.info(
            f"Training classes: "
            f"{generator.class_indices}"
        )

        self._validate_class_indices(
            generator.class_indices
        )

        return generator


    # =====================================================
    # LOAD VALIDATION DATA
    # =====================================================

    def load_validation_data(self):

        logger.info(
            "\nLoading validation dataset..."
        )

        generator = (
            self.validation_datagen.flow_from_directory(

                directory=str(
                    self.validation_dir
                ),

                target_size=self.image_size,

                batch_size=self.batch_size,

                class_mode=Config.CLASS_MODE,

                classes=Config.CLASS_NAMES,

                shuffle=False
            )
        )

        logger.info(
            f"Validation images: "
            f"{generator.samples}"
        )

        logger.info(
            f"Validation classes: "
            f"{generator.class_indices}"
        )

        self._validate_class_indices(
            generator.class_indices
        )

        return generator


    # =====================================================
    # LOAD TEST DATA
    # =====================================================

    def load_test_data(self):

        logger.info(
            "\nLoading test dataset..."
        )

        generator = (
            self.test_datagen.flow_from_directory(

                directory=str(
                    self.test_dir
                ),

                target_size=self.image_size,

                batch_size=self.batch_size,

                class_mode=Config.CLASS_MODE,

                classes=Config.CLASS_NAMES,

                shuffle=False
            )
        )

        logger.info(
            f"Test images: "
            f"{generator.samples}"
        )

        logger.info(
            f"Test classes: "
            f"{generator.class_indices}"
        )

        self._validate_class_indices(
            generator.class_indices
        )

        return generator


    # =====================================================
    # LOAD COMPLETE DATASET
    # =====================================================

    def load_dataset(self):

        logger.info("=" * 60)

        logger.info(
            "LOADING DATASET"
        )

        logger.info("=" * 60)

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        self.validate_dataset()

        # -------------------------------------------------
        # Load train
        # -------------------------------------------------

        train_generator = (
            self.load_train_data()
        )

        # -------------------------------------------------
        # Load validation
        # -------------------------------------------------

        validation_generator = (
            self.load_validation_data()
        )

        # -------------------------------------------------
        # Load test
        # -------------------------------------------------

        test_generator = (
            self.load_test_data()
        )

        # -------------------------------------------------
        # Final information
        # -------------------------------------------------

        logger.info("=" * 60)

        logger.info(
            "DATASET LOADED SUCCESSFULLY"
        )

        logger.info("=" * 60)

        logger.info(
            f"Classes: "
            f"{train_generator.class_indices}"
        )

        logger.info(
            f"Train: "
            f"{train_generator.samples}"
        )

        logger.info(
            f"Validation: "
            f"{validation_generator.samples}"
        )

        logger.info(
            f"Test: "
            f"{test_generator.samples}"
        )

        return (
            train_generator,
            validation_generator,
            test_generator
        )


    # =====================================================
    # VALIDATE CLASS INDICES
    # =====================================================

    def _validate_class_indices(
        self,
        class_indices
    ):

        expected = {

            "AI_GENERATED": 0,

            "AUTHENTIC": 1,

            "MANIPULATED": 2

        }

        if class_indices != expected:

            raise ValueError(

                "\nClass mapping mismatch!\n"

                f"Expected: {expected}\n"

                f"Found:    {class_indices}"
            )

        logger.info(
            "Class mapping verified:"
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


    # =====================================================
    # CLASS NAMES
    # =====================================================

    def get_class_names(self):

        return Config.CLASS_NAMES


    # =====================================================
    # CLASS INDICES
    # =====================================================

    def get_class_indices(self):

        return {

            "AI_GENERATED": 0,

            "AUTHENTIC": 1,

            "MANIPULATED": 2

        }


    # =====================================================
    # SAVE DATASET INFORMATION
    # =====================================================

    def save_dataset_info(self):

        info = {

            "classes": Config.CLASS_NAMES,

            "class_indices": {

                "AI_GENERATED": 0,

                "AUTHENTIC": 1,

                "MANIPULATED": 2

            },

            "image_size": [

                Config.IMAGE_HEIGHT,

                Config.IMAGE_WIDTH,

                Config.CHANNELS

            ],

            "batch_size": Config.BATCH_SIZE,

            "dataset_path": str(
                self.dataset_dir
            )

        }

        output_file = (
            self.dataset_dir /
            "dataset_info.json"
        )

        with open(

            output_file,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                info,

                file,

                indent=4

            )

        logger.info(
            f"Dataset information saved to:\n"
            f"{output_file}"
        )


# =========================================================
# PUBLIC FUNCTION
# =========================================================

def get_dataset():

    loader = DatasetLoader()

    train_generator, validation_generator, test_generator = (

        loader.load_dataset()

    )

    loader.save_dataset_info()

    return {

        "train": train_generator,

        "validation": validation_generator,

        "test": test_generator

    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "AI IMAGE FORENSICS"
    )

    print(
        "DATASET LOADER TEST"
    )

    print("=" * 60)

    try:

        dataset = get_dataset()

        train_generator = (
            dataset["train"]
        )

        validation_generator = (
            dataset["validation"]
        )

        test_generator = (
            dataset["test"]
        )

        print("\nSUCCESS!")

        print(
            "Class mapping:",
            train_generator.class_indices
        )

        print(
            "Training images:",
            train_generator.samples
        )

        print(
            "Validation images:",
            validation_generator.samples
        )

        print(
            "Test images:",
            test_generator.samples
        )

    except Exception as error:

        print("\nERROR:")

        print(error)

        raise