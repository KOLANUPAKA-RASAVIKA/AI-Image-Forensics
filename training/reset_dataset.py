import os
import shutil
import random
from pathlib import Path

# ============================================================
# AI IMAGE FORENSICS
# CLEAN DATASET RESET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
SOURCE_DIR = DATASET_DIR / "balanced_train"

CLASSES = [
    "AI_GENERATED",
    "AUTHENTIC",
    "MANIPULATED"
]

TRAIN_COUNT = {
    "AI_GENERATED": 350,
    "AUTHENTIC": 350,
    "MANIPULATED": 349
}

VALIDATION_COUNT = 75
TEST_COUNT = 75

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp"
}

RANDOM_SEED = 42


# ============================================================
# GET IMAGE FILES
# ============================================================

def get_image_files(folder):
    """
    Return only valid image files.
    Ignores .db and other non-image files.
    """

    if not folder.exists():
        return []

    files = []

    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(file)

    return files


# ============================================================
# CREATE DIRECTORY
# ============================================================

def create_directory(path):
    path.mkdir(parents=True, exist_ok=True)


# ============================================================
# CLEAN OLD SPLITS
# ============================================================

def clean_old_splits():

    print()
    print("Cleaning old dataset splits...")

    for split in ["train", "validation", "test"]:

        split_dir = DATASET_DIR / split

        if split_dir.exists():
            shutil.rmtree(split_dir)
            print(f"Removed: {split_dir}")

    print("Old train/validation/test folders removed.")


# ============================================================
# COPY FILES
# ============================================================

def copy_files(files, destination):

    create_directory(destination)

    for file in files:

        destination_file = destination / file.name

        shutil.copy2(file, destination_file)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("AI IMAGE FORENSICS")
    print("CLEAN DATASET RESET")
    print("=" * 60)

    print()
    print("Source:")
    print(SOURCE_DIR)

    # --------------------------------------------------------
    # Check source directory
    # --------------------------------------------------------

    if not SOURCE_DIR.exists():

        raise FileNotFoundError(
            f"Source dataset does not exist:\n{SOURCE_DIR}"
        )

    # --------------------------------------------------------
    # Clean old train/validation/test
    # --------------------------------------------------------

    clean_old_splits()

    print()
    print("Creating clean dataset splits...")
    print()

    random.seed(RANDOM_SEED)

    final_counts = {
        "train": {},
        "validation": {},
        "test": {}
    }

    # --------------------------------------------------------
    # Process each class
    # --------------------------------------------------------

    for class_name in CLASSES:

        source_class_dir = SOURCE_DIR / class_name

        files = get_image_files(source_class_dir)

        print(class_name)
        print(f"Found {len(files)} usable files")

        # ----------------------------------------------------
        # Required number of images
        # ----------------------------------------------------

        required = (
            TRAIN_COUNT[class_name]
            + VALIDATION_COUNT
            + TEST_COUNT
        )

        if len(files) < required:

            raise ValueError(
                f"\n{class_name} does not have enough images!\n"
                f"Found     : {len(files)}\n"
                f"Required  : {required}\n"
                f"Missing   : {required - len(files)}"
            )

        # ----------------------------------------------------
        # Shuffle
        # ----------------------------------------------------

        random.shuffle(files)

        # ----------------------------------------------------
        # Split
        # ----------------------------------------------------

        train_count = TRAIN_COUNT[class_name]

        train_files = files[
            :train_count
        ]

        validation_start = train_count

        validation_end = (
            validation_start + VALIDATION_COUNT
        )

        validation_files = files[
            validation_start:validation_end
        ]

        test_start = validation_end

        test_end = (
            test_start + TEST_COUNT
        )

        test_files = files[
            test_start:test_end
        ]

        # ----------------------------------------------------
        # Destination folders
        # ----------------------------------------------------

        train_dir = (
            DATASET_DIR
            / "train"
            / class_name
        )

        validation_dir = (
            DATASET_DIR
            / "validation"
            / class_name
        )

        test_dir = (
            DATASET_DIR
            / "test"
            / class_name
        )

        # ----------------------------------------------------
        # Copy files
        # ----------------------------------------------------

        copy_files(
            train_files,
            train_dir
        )

        copy_files(
            validation_files,
            validation_dir
        )

        copy_files(
            test_files,
            test_dir
        )

        # ----------------------------------------------------
        # Save counts
        # ----------------------------------------------------

        final_counts["train"][class_name] = len(
            train_files
        )

        final_counts["validation"][class_name] = len(
            validation_files
        )

        final_counts["test"][class_name] = len(
            test_files
        )

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        print(
            f"train       : {len(train_files)}"
        )

        print(
            f"validation  : {len(validation_files)}"
        )

        print(
            f"test        : {len(test_files)}"
        )

        print()

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("=" * 60)
    print("DATASET SPLIT COMPLETED")
    print("=" * 60)

    print()
    print("FINAL DATASET")

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    print()
    print("TRAIN")

    train_total = 0

    for class_name in CLASSES:

        count = final_counts["train"][class_name]

        print(
            f"{class_name:<12} : {count}"
        )

        train_total += count

    print(
        f"{'TOTAL':<12} : {train_total}"
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print()
    print("VALIDATION")

    validation_total = 0

    for class_name in CLASSES:

        count = final_counts["validation"][class_name]

        print(
            f"{class_name:<12} : {count}"
        )

        validation_total += count

    print(
        f"{'TOTAL':<12} : {validation_total}"
    )

    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    print()
    print("TEST")

    test_total = 0

    for class_name in CLASSES:

        count = final_counts["test"][class_name]

        print(
            f"{class_name:<12} : {count}"
        )

        test_total += count

    print(
        f"{'TOTAL':<12} : {test_total}"
    )

    # ========================================================
    # EXPECTED TOTAL
    # ========================================================

    print()
    print("=" * 60)
    print("EXPECTED DATASET")
    print("=" * 60)

    print()
    print("TRAIN       : 1049")
    print("VALIDATION  : 225")
    print("TEST        : 225")

    print()
    print("Source images:")
    print("AI_GENERATED : 500")
    print("AUTHENTIC    : 500")
    print("MANIPULATED  : 499")

    print()
    print("No images were duplicated.")
    print("No .db files were copied.")
    print("balanced_train was NOT modified.")

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()