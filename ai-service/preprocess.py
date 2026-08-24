"""
preprocess.py

Image preprocessing utilities used by:

- Prediction
- ELA
- GradCAM
"""

import cv2
import numpy as np
from PIL import Image

from config import Config


class ImagePreprocessor:

    @staticmethod
    def validate_extension(filename):
        """
        Check if uploaded file extension is allowed.
        """

        if "." not in filename:
            return False

        extension = filename.rsplit(
            ".",
            1
        )[1].lower()

        return extension in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def load_image(image_path):
        """
        Load image using PIL.
        """

        image = Image.open(image_path)

        image = image.convert("RGB")

        return image

    @staticmethod
    def resize_image(image):
        """
        Resize image.
        """

        return image.resize(
            Config.IMAGE_SIZE
        )

    @staticmethod
    def normalize(image):
        """
        Normalize image pixels.
        """

        image = np.array(
            image,
            dtype=np.float32
        )

        image /= 255.0

        return image

    @staticmethod
    def expand_dimension(image):
        """
        Add batch dimension.
        """

        return np.expand_dims(
            image,
            axis=0
        )

    @staticmethod
    def preprocess_for_prediction(image_path):
        """
        Full preprocessing pipeline.
        """

        image = ImagePreprocessor.load_image(
            image_path
        )

        image = ImagePreprocessor.resize_image(
            image
        )

        image = ImagePreprocessor.normalize(
            image
        )

        image = ImagePreprocessor.expand_dimension(
            image
        )

        return image

    @staticmethod
    def read_cv_image(image_path):
        """
        Read image using OpenCV.
        """

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(
                f"Cannot read image: {image_path}"
            )

        return image

    @staticmethod
    def rgb_image(image):
        """
        Convert BGR to RGB.
        """

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

    @staticmethod
    def resize_cv(image):
        """
        Resize using OpenCV.
        """

        return cv2.resize(
            image,
            Config.IMAGE_SIZE
        )

    @staticmethod
    def preprocess_for_gradcam(image_path):
        """
        Prepare image for GradCAM.
        """

        image = ImagePreprocessor.read_cv_image(
            image_path
        )

        image = ImagePreprocessor.rgb_image(
            image
        )

        image = ImagePreprocessor.resize_cv(
            image
        )

        image = image.astype(
            np.float32
        )

        image /= 255.0

        image = np.expand_dims(
            image,
            axis=0
        )

        return image

    @staticmethod
    def denormalize(image):
        """
        Convert normalized image back to uint8.
        """

        image = image * 255

        image = np.clip(
            image,
            0,
            255
        )

        return image.astype(
            np.uint8
        )

    @staticmethod
    def save_image(image, output_path):
        """
        Save RGB image.
        """

        Image.fromarray(
            image
        ).save(
            output_path
        )

    @staticmethod
    def image_information(image_path):
        """
        Return image metadata.
        """

        image = Image.open(image_path)

        return {
            "filename": image_path,
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format
        }