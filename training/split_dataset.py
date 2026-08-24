"""
=========================================================
AI IMAGE FORENSICS
3-CLASS DATASET SPLITTER
=========================================================

Creates:

dataset/
    train/
        AI_GENERATED/
        AUTHENTIC/
        MANIPULATED/

    validation/
        AI_GENERATED/
        AUTHENTIC/
        MANIPULATED/

    test/
        AI_GENERATED/
        AUTHENTIC/
        MANIPULATED/

Split:
    80% Train
    10% Validation
    10% Test
=========================================================
"""

import shutil
import random
import logging
from pathlib import Path

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
# DATASET SPLITTER
# =========================================================

class DatasetSplitter:

    def __init__(self):

        # -------------------------------------------------
        # OUTPUT DATASET
        # -------------------------------------------------

        self.dataset_root = Path(Config.DATASET_DIR)

        # -------------------------------------------------
        # IMPORTANT:
        # Change these 3 paths ONLY if your source folders
        # are located somewhere else.
        # -------------------------------------------------

        self.source_root = Path(
            r"C:\Users\rasav\Documents\AI-Image-Forensics\source_data"
        )

        self.sources = {
            "AI_GENERATED": self.source_root / "AI_GENERATED",
            "AUTHENTIC": self.source_root / "AUTHENTIC",
            "MANIPULATED": self.source_root / "MANIPULATED"
        }

        # -------------------------------------------------
        # CLASSES
        # -------------------------------------------------

        self.classes = [
            "AI_GENERATED",
            "AUTHENTIC",
            "MANIPULATED"
        ]

        # -------------------------------------------------
        # IMAGE EXTENSIONS
        # -------------------------------------------------

        self.extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tif",
            ".tiff",
            ".webp"
        }

        # -------------------------------------------------
        # SPLIT
        # -------------------------------------------------

        self.train_ratio = 0.80
        self.validation_ratio = 0.10
        self.test_ratio = 0.10

        random.seed(Config.RANDOM_SEED)

        self.create_directories()

    # =====================================================
    # CREATE DIRECTORIES
    # =====================================================

    def create_directories(self):

        for split in [
            "train",
            "validation",
            "test"
        ]:

            for class_name in self.classes:

                folder = (
                    self.dataset_root /
                    split /
                    class_name
                )

                folder.mkdir(
                    parents=True,
                    exist_ok=True
                )

    # =====================================================
    # GET IMAGES
    # =====================================================

    def get_images(self, folder):

        if not folder.exists():

            raise FileNotFoundError(
                f"\nSOURCE FOLDER NOT FOUND:\n{folder}\n"
            )

        images = []

        for file in folder.rglob("*"):

            if (
                file.is_file()
                and file.suffix.lower() in self.extensions
            ):
                images.append(file)

        return images

    # =====================================================
    # CLEAR OLD SPLIT
    # =====================================================

    def clear_old_dataset(self):

        logger.info("Clearing old dataset split...")

        for split in [
            "train",
            "validation",
            "test"
        ]:

            for class_name in self.classes:

                folder = (
                    self.dataset_root /
                    split /
                    class_name
                )

                if folder.exists():

                    for item in folder.iterdir():

                        if item.is_file():
                            item.unlink()

                        elif item.is_dir():
                            shutil.rmtree(item)

        logger.info("Old dataset split cleared.")

    # =====================================================
    # SPLIT IMAGES
    # =====================================================

    def split_images(self, images):

        random.shuffle(images)

        total = len(images)

        train_count = int(
            total * self.train_ratio
        )

        validation_count = int(
            total * self.validation_ratio
        )

        train_images = images[
            :train_count
        ]

        validation_images = images[
            train_count:
            train_count + validation_count
        ]

        test_images = images[
            train_count + validation_count:
        ]

        return (
            train_images,
            validation_images,
            test_images
        )

    # =====================================================
    # COPY IMAGES
    # =====================================================

    def copy_images(
        self,
        images,
        destination
    ):

        destination.mkdir(
            parents=True,
            exist_ok=True
        )

        copied = 0

        for image in images:

            target = destination / image.name

            # Avoid filename collision
            if target.exists():

                stem = image.stem
                suffix = image.suffix

                counter = 1

                while target.exists():

                    target = (
                        destination /
                        f"{stem}_{counter}{suffix}"
                    )

                    counter += 1

            try:

                shutil.copy2(
                    image,
                    target
                )

                copied += 1

            except Exception as e:

                logger.error(
                    f"Failed: {image}"
                )

                logger.error(str(e))

        return copied

    # =====================================================
    # PROCESS CLASS
    # =====================================================

    def process_class(
        self,
        class_name
    ):

        source = self.sources[class_name]

        logger.info("")
        logger.info("=" * 60)
        logger.info(
            f"PROCESSING: {class_name}"
        )
        logger.info("=" * 60)

        images = self.get_images(source)

        logger.info(
            f"Source images: {len(images)}"
        )

        if len(images) == 0:

            raise ValueError(
                f"{class_name} contains ZERO images:\n{source}"
            )

        (
            train_images,
            validation_images,
            test_images
        ) = self.split_images(images)

        logger.info(
            f"Train      : {len(train_images)}"
        )

        logger.info(
            f"Validation : {len(validation_images)}"
        )

        logger.info(
            f"Test       : {len(test_images)}"
        )

        # -------------------------------------------------
        # TRAIN
        # -------------------------------------------------

        train_destination = (
            self.dataset_root /
            "train" /
            class_name
        )

        self.copy_images(
            train_images,
            train_destination
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        validation_destination = (
            self.dataset_root /
            "validation" /
            class_name
        )

        self.copy_images(
            validation_images,
            validation_destination
        )

        # -------------------------------------------------
        # TEST
        # -------------------------------------------------

        test_destination = (
            self.dataset_root /
            "test" /
            class_name
        )

        self.copy_images(
            test_images,
            test_destination
        )

    # =====================================================
    # FINAL STATISTICS
    # =====================================================

    def statistics(self):

        logger.info("")
        logger.info("=" * 70)
        logger.info("FINAL DATASET STATISTICS")
        logger.info("=" * 70)

        for split in [
            "train",
            "validation",
            "test"
        ]:

            logger.info("")
            logger.info(
                f"{split.upper()}"
            )

            for class_name in self.classes:

                folder = (
                    self.dataset_root /
                    split /
                    class_name
                )

                count = sum(
                    1
                    for file in folder.rglob("*")
                    if (
                        file.is_file()
                        and
                        file.suffix.lower()
                        in self.extensions
                    )
                )

                logger.info(
                    f"{class_name:<15} : {count}"
                )

        logger.info("")
        logger.info("=" * 70)

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        logger.info(
            "STARTING 3-CLASS DATASET SPLITTER"
        )

        logger.info(
            f"Dataset output: {self.dataset_root}"
        )

        # Safety check
        logger.info("")
        logger.info(
            "SOURCE DIRECTORIES:"
        )

        for class_name, path in self.sources.items():

            logger.info(
                f"{class_name}: {path}"
            )

        # Clear previous train/validation/test
        self.clear_old_dataset()

        # Process each class
        for class_name in self.classes:

            self.process_class(
                class_name
            )

        self.statistics()

        logger.info("")
        logger.info(
            "DATASET SPLIT COMPLETED SUCCESSFULLY!"
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    splitter = DatasetSplitter()

    splitter.run()