"""
=========================================================
AI IMAGE FORENSICS
CONFUSION MATRIX
=========================================================
"""

import os
import logging
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)

from tensorflow.keras.models import load_model

from config import Config
from dataset_loader import get_dataset


# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 60)
    print("AI IMAGE FORENSICS")
    print("CONFUSION MATRIX ANALYSIS")
    print("=" * 60)

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------

    logger.info("Loading dataset...")

    dataset = get_dataset()

    test_dataset = dataset["test"]

    logger.info(
        f"Test images: {test_dataset.samples}"
    )

    # -----------------------------------------------------
    # Load trained model
    # -----------------------------------------------------

    logger.info("Loading trained model...")

    model_path = Config.MODEL_PATH

    if not os.path.exists(model_path):

        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    model = load_model(model_path)

    logger.info(
        f"Model loaded from: {model_path}"
    )

    # -----------------------------------------------------
    # Get predictions
    # -----------------------------------------------------

    logger.info("Generating predictions...")

    test_dataset.reset()

    predictions = model.predict(
        test_dataset,
        verbose=1
    )

    predicted_classes = np.argmax(
        predictions,
        axis=1
    )

    true_classes = test_dataset.classes

    # -----------------------------------------------------
    # Class names
    # -----------------------------------------------------

    class_names = list(
        Config.CLASS_NAMES
    )

    logger.info(
        f"Classes: {class_names}"
    )

    # -----------------------------------------------------
    # Confusion matrix
    # -----------------------------------------------------

    cm = confusion_matrix(
        true_classes,
        predicted_classes
    )

    print("\n")
    print("=" * 60)
    print("CONFUSION MATRIX")
    print("=" * 60)

    print(cm)

    # -----------------------------------------------------
    # Classification report
    # -----------------------------------------------------

    print("\n")
    print("=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)

    report = classification_report(
        true_classes,
        predicted_classes,
        target_names=class_names,
        digits=4,
        zero_division=0
    )

    print(report)

    # -----------------------------------------------------
    # Save confusion matrix
    # -----------------------------------------------------

    os.makedirs(
        Config.HISTORY_DIR,
        exist_ok=True
    )

    cm_path = os.path.join(
        Config.HISTORY_DIR,
        "confusion_matrix.png"
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=class_names
    )

    fig, ax = plt.subplots(
        figsize=(8, 8)
    )

    display.plot(
        ax=ax,
        cmap="Blues",
        xticks_rotation=45
    )

    plt.title(
        "AI Image Forensics - Confusion Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        cm_path,
        dpi=300
    )

    plt.close()

    logger.info(
        f"Confusion matrix saved to: {cm_path}"
    )

    print("\n")
    print("=" * 60)
    print("ANALYSIS COMPLETED")
    print("=" * 60)

    print(
        f"Confusion matrix saved at:\n{cm_path}"
    )


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":
    main()