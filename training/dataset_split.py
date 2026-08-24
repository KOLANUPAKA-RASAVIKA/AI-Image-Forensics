import os
import shutil
import random

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.join(os.path.dirname(__file__), "dataset")

CLASSES = [
    "AI_GENERATED",
    "AUTHENTIC",
    "MANIPULATED"
]

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".jfif", ".tif", ".tiff"  )

random.seed(42)


# =========================================================
# GET IMAGES
# =========================================================

def get_images(folder):

    images = []

    for root, _, files in os.walk(folder):

        for file in files:

            file_path = os.path.join(root, file)

            if os.path.isfile(file_path):
                images.append(file_path)

    return images


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 60)
    print("AI IMAGE FORENSICS")
    print("CLEAN DATASET SPLITTER")
    print("=" * 60)

    # Temporary location for collected images
    source_dir = os.path.join(BASE_DIR, "_all_images")

    if os.path.exists(source_dir):
        shutil.rmtree(source_dir)

    os.makedirs(source_dir)

    # -----------------------------------------------------
    # Collect images from existing train/validation/test
    # -----------------------------------------------------

    for class_name in CLASSES:

        class_source = os.path.join(
            source_dir,
            class_name
        )

        os.makedirs(class_source)

        seen = set()

        print(f"\nCollecting {class_name}...")

        for split in ["train", "validation", "test"]:

            folder = os.path.join(
                BASE_DIR,
                split,
                class_name
            )

            images = get_images(folder)

            for image in images:

                # Avoid duplicate files with same filename
                filename = os.path.basename(image)

                if filename.lower() in seen:
                    continue

                seen.add(filename)

                destination = os.path.join(
                    class_source,
                    filename
                )

                # If filename collision occurs, create unique name
                if os.path.exists(destination):

                    base, ext = os.path.splitext(filename)

                    counter = 1

                    while os.path.exists(destination):

                        destination = os.path.join(
                            class_source,
                            f"{base}_{counter}{ext}"
                        )

                        counter += 1

                shutil.copy2(
                    image,
                    destination
                )

        count = len(get_images(class_source))

        print(
            f"{class_name}: {count} unique images"
        )

    # -----------------------------------------------------
    # Recreate clean splits
    # -----------------------------------------------------

    print("\nCreating clean dataset splits...")

    for split in ["train", "validation", "test"]:

        for class_name in CLASSES:

            folder = os.path.join(
                BASE_DIR,
                split,
                class_name
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            # Remove existing images
            for root, _, files in os.walk(folder):

                for file in files:

                    if file.lower().endswith(
                        IMAGE_EXTENSIONS
                    ):

                        try:
                            os.remove(
                                os.path.join(root, file)
                            )
                        except:
                            pass

    # -----------------------------------------------------
    # Split images
    # -----------------------------------------------------

    for class_name in CLASSES:

        source = os.path.join(
            source_dir,
            class_name
        )

        images = get_images(source)

        random.shuffle(images)

        total = len(images)

        train_count = int(
            total * TRAIN_RATIO
        )

        val_count = int(
            total * VAL_RATIO
        )

        train_images = images[:train_count]

        val_images = images[
            train_count:
            train_count + val_count
        ]

        test_images = images[
            train_count + val_count:
        ]

        splits = {
            "train": train_images,
            "validation": val_images,
            "test": test_images
        }

        print(
            f"\n{class_name}"
        )

        for split, split_images in splits.items():

            destination = os.path.join(
                BASE_DIR,
                split,
                class_name
            )

            for image in split_images:

                shutil.copy2(
                    image,
                    os.path.join(
                        destination,
                        os.path.basename(image)
                    )
                )

            print(
                f"{split}: {len(split_images)}"
            )

    # -----------------------------------------------------
    # Cleanup
    # -----------------------------------------------------

    shutil.rmtree(source_dir)

    print("\n" + "=" * 60)
    print("DATASET SPLIT COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()