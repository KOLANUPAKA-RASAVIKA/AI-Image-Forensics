"""
AI IMAGE FORENSICS
Error Level Analysis (ELA)

Generates ELA images and overlays for forensic analysis.
"""

import os
import uuid
import tempfile
import logging

import cv2
import numpy as np

from PIL import Image, ImageChops, ImageEnhance

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
# ELA PROCESSOR
# =========================================================

class ELAProcessor:

    def __init__(self):

        logger.info("Initializing ELA Processor...")

        self.jpeg_quality = Config.JPEG_QUALITY
        self.scale = Config.ELA_SCALE

        # Main output directory
        self.output_folder = Config.OUTPUT_FOLDER

        # Dedicated ELA directory
        self.ela_folder = os.path.join(
            self.output_folder,
            "ela"
        )

        os.makedirs(
            self.ela_folder,
            exist_ok=True
        )

        logger.info(
            f"ELA output folder: {self.ela_folder}"
        )

        logger.info("ELA Processor Ready.")


    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate_image(self, image_path):

        if not image_path:
            raise ValueError(
                "Image path is empty."
            )

        image_path = os.path.abspath(
            image_path
        )

        if not os.path.isfile(image_path):
            raise FileNotFoundError(
                f"Image not found:\n{image_path}"
            )

        return image_path


    # =====================================================
    # OPEN IMAGE
    # =====================================================

    def _open_rgb(self, image_path):

        try:

            image = Image.open(
                image_path
            )

            image.load()

            return image.convert("RGB")

        except Exception as e:

            raise ValueError(
                f"Unable to open image:\n"
                f"{image_path}\n"
                f"Error: {e}"
            )


    # =====================================================
    # TEMPORARY FILE
    # =====================================================

    def _temporary_filename(self):

        filename = (
            str(uuid.uuid4()) +
            ".jpg"
        )

        return os.path.join(
            tempfile.gettempdir(),
            filename
        )


    # =====================================================
    # JPEG RECOMPRESSION
    # =====================================================

    def _recompress_image(
        self,
        image,
        output_path
    ):

        image.save(
            output_path,
            format="JPEG",
            quality=self.jpeg_quality
        )


    # =====================================================
    # DIFFERENCE
    # =====================================================

    def _calculate_difference(
        self,
        original,
        compressed
    ):

        return ImageChops.difference(
            original,
            compressed
        )


    # =====================================================
    # MAXIMUM DIFFERENCE
    # =====================================================

    def _max_difference(
        self,
        diff
    ):

        extrema = diff.getextrema()

        max_diff = max(
            channel[1]
            for channel in extrema
        )

        return max_diff


    # =====================================================
    # ENHANCE ELA
    # =====================================================

    def _enhance_difference(
        self,
        diff
    ):

        max_diff = self._max_difference(
            diff
        )

        if max_diff <= 0:
            max_diff = 1

        scale = (
            255.0 /
            max_diff
        )

        enhancer = ImageEnhance.Brightness(
            diff
        )

        return enhancer.enhance(
            scale
        )


    # =====================================================
    # GENERATE ELA
    # =====================================================

    def generate_ela(
        self,
        image_path,
        normalize=False
    ):

        image_path = self._validate_image(
            image_path
        )

        logger.info(
            f"Generating ELA: {image_path}"
        )

        original = self._open_rgb(
            image_path
        )

        temp_path = self._temporary_filename()

        try:

            # ---------------------------------------------
            # JPEG recompression
            # ---------------------------------------------

            self._recompress_image(
                original,
                temp_path
            )

            # ---------------------------------------------
            # Read compressed image
            # ---------------------------------------------

            compressed = self._open_rgb(
                temp_path
            )

            # ---------------------------------------------
            # Difference
            # ---------------------------------------------

            difference = self._calculate_difference(
                original,
                compressed
            )

            # ---------------------------------------------
            # Enhance
            # ---------------------------------------------

            ela_image = self._enhance_difference(
                difference
            )

            # ---------------------------------------------
            # Normalize if requested
            # ---------------------------------------------

            if normalize:

                ela_array = np.array(
                    ela_image,
                    dtype=np.float32
                )

                ela_array /= 255.0

                return ela_array

            logger.info(
                "ELA generated successfully."
            )

            return ela_image

        finally:

            # ---------------------------------------------
            # Remove temporary JPEG
            # ---------------------------------------------

            if os.path.exists(
                temp_path
            ):

                try:

                    os.remove(
                        temp_path
                    )

                except Exception:
                    pass


    # =====================================================
    # SAVE ELA IMAGE
    # =====================================================

    def save_ela(
        self,
        image_path,
        output_filename=None
    ):

        logger.info(
            "Saving ELA image..."
        )

        ela_image = self.generate_ela(
            image_path,
            normalize=False
        )

        if output_filename is None:

            output_filename = (
                "ela_" +
                str(uuid.uuid4()) +
                ".png"
            )

        output_path = os.path.join(
            self.ela_folder,
            output_filename
        )

        ela_image.save(
            output_path,
            format="PNG"
        )

        logger.info(
            f"ELA saved: {output_path}"
        )

        return {
            "filename": output_filename,
            "path": output_path
        }


    # =====================================================
    # OPENCV ELA
    # =====================================================

    def ela_cv(
        self,
        image_path
    ):

        ela = self.generate_ela(
            image_path,
            normalize=False
        )

        ela = np.array(
            ela
        )

        ela = cv2.cvtColor(
            ela,
            cv2.COLOR_RGB2BGR
        )

        return ela


    # =====================================================
    # RESIZE
    # =====================================================

    def resize(
        self,
        image,
        size=None
    ):

        if size is None:

            size = Config.IMAGE_SIZE

        return cv2.resize(
            image,
            size
        )


    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(
        self,
        image_path
    ):

        logger.info(
            "Calculating ELA statistics..."
        )

        ela = self.generate_ela(
            image_path,
            normalize=False
        )

        ela_array = np.array(
            ela,
            dtype=np.float32
        )

        stats = {

            "mean": float(
                np.mean(ela_array)
            ),

            "std": float(
                np.std(ela_array)
            ),

            "max": int(
                np.max(ela_array)
            ),

            "min": int(
                np.min(ela_array)
            ),

            "variance": float(
                np.var(ela_array)
            )
        }

        logger.info(
            f"ELA statistics: {stats}"
        )

        return stats


    # =====================================================
    # ELA HEATMAP
    # =====================================================

    def heatmap(
        self,
        image_path
    ):

        logger.info(
            "Creating ELA heatmap..."
        )

        ela = self.ela_cv(
            image_path
        )

        gray = cv2.cvtColor(
            ela,
            cv2.COLOR_BGR2GRAY
        )

        heatmap = cv2.applyColorMap(
            gray,
            cv2.COLORMAP_JET
        )

        return heatmap


    # =====================================================
    # OVERLAY
    # =====================================================

    def overlay(
        self,
        image_path,
        alpha=0.6
    ):

        logger.info(
            "Creating ELA overlay..."
        )

        image_path = self._validate_image(
            image_path
        )

        original = cv2.imread(
            image_path
        )

        if original is None:

            raise ValueError(
                f"OpenCV could not read image:\n"
                f"{image_path}"
            )

        original = cv2.resize(
            original,
            Config.IMAGE_SIZE
        )

        heatmap = self.heatmap(
            image_path
        )

        heatmap = cv2.resize(
            heatmap,
            Config.IMAGE_SIZE
        )

        overlay = cv2.addWeighted(
            original,
            alpha,
            heatmap,
            1.0 - alpha,
            0
        )

        return overlay


    # =====================================================
    # SAVE OVERLAY
    # =====================================================

    def save_overlay(
        self,
        image_path,
        filename=None
    ):

        logger.info(
            "Saving ELA overlay..."
        )

        overlay = self.overlay(
            image_path
        )

        if filename is None:

            filename = (
                "ela_overlay_" +
                str(uuid.uuid4()) +
                ".jpg"
            )

        output_path = os.path.join(
            self.ela_folder,
            filename
        )

        success = cv2.imwrite(
            output_path,
            overlay
        )

        if not success:

            raise IOError(
                f"Failed to save ELA overlay:\n"
                f"{output_path}"
            )

        logger.info(
            f"ELA overlay saved: {output_path}"
        )

        return output_path


    # =====================================================
    # COMPLETE REPORT
    # =====================================================

    def report(
        self,
        image_path
    ):

        logger.info(
            "Generating complete ELA report..."
        )

        statistics = self.statistics(
            image_path
        )

        ela_file = self.save_ela(
            image_path
        )

        overlay_file = self.save_overlay(
            image_path
        )

        return {

            "ela_image":
                ela_file["path"],

            "ela_filename":
                ela_file["filename"],

            "overlay":
                overlay_file,

            "statistics":
                statistics
        }


    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(
        self
    ):

        logger.info(
            "Cleaning ELA output files..."
        )

        if not os.path.exists(
            self.ela_folder
        ):

            return

        for filename in os.listdir(
            self.ela_folder
        ):

            if filename.lower().endswith(
                (".png", ".jpg", ".jpeg")
            ):

                file_path = os.path.join(
                    self.ela_folder,
                    filename
                )

                try:

                    os.remove(
                        file_path
                    )

                except Exception as e:

                    logger.warning(
                        f"Could not remove "
                        f"{file_path}: {e}"
                    )

        logger.info(
            "ELA cleanup completed."
        )


# =========================================================
# TEST
# =========================================================

def main():

    print("=" * 60)
    print("AI IMAGE FORENSICS - ELA TEST")
    print("=" * 60)

    image_path = input(
        "Enter image path: "
    ).strip()

    image_path = os.path.abspath(
        image_path
    )

    try:

        ela = ELAProcessor()

        result = ela.report(
            image_path
        )

        print()
        print("=" * 60)
        print("ELA COMPLETED")
        print("=" * 60)

        print(
            f"ELA Image : "
            f"{result['ela_image']}"
        )

        print(
            f"Overlay   : "
            f"{result['overlay']}"
        )

        print()

        print("ELA Statistics:")

        for key, value in (
            result["statistics"].items()
        ):

            print(
                f"  {key:<10}: {value}"
            )

        print("=" * 60)

    except Exception as e:

        logger.exception(
            "ELA generation failed."
        )

        print()
        print(
            f"ERROR: {e}"
        )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()