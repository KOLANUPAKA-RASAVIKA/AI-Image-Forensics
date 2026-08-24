"""
=========================================================
AI IMAGE FORENSICS
Integrated Flask REST API
=========================================================

Features:
- Image upload
- ResNet50 prediction
- ELA analysis
- Grad-CAM visualization
- Risk assessment
- Investigation history
- Dashboard statistics
- Evidence storage
- Batch prediction
- Static file serving
=========================================================
"""

import os
import json
import uuid
import time
import logging

from datetime import datetime, timezone
from threading import Lock

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from predict import predict_image
from ela import ELAProcessor
from gradcam import GradCAMGenerator


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    }
)


app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = Config.OUTPUT_FOLDER
app.config["JSON_SORT_KEYS"] = False


# =========================================================
# DIRECTORIES
# =========================================================

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
os.makedirs(Config.TEMP_FOLDER, exist_ok=True)

# IMPORTANT:
# ELA files are stored inside outputs/ela
ELA_FOLDER = os.path.join(
    Config.OUTPUT_FOLDER,
    "ela"
)

os.makedirs(ELA_FOLDER, exist_ok=True)


# =========================================================
# INVESTIGATION DATABASE
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FOLDER = os.path.join(
    BASE_DIR,
    "data"
)

INVESTIGATIONS_FILE = os.path.join(
    DATA_FOLDER,
    "investigations.json"
)

os.makedirs(DATA_FOLDER, exist_ok=True)

storage_lock = Lock()


# =========================================================
# RESULT CATEGORIES
# =========================================================

RESULT_AUTHENTIC = "AUTHENTIC"
RESULT_MANIPULATED = "MANIPULATED"
RESULT_AI_GENERATED = "AI_GENERATED"
RESULT_REVIEW = "REQUIRES_REVIEW"

VALID_RESULTS = {
    RESULT_AUTHENTIC,
    RESULT_MANIPULATED,
    RESULT_AI_GENERATED,
    RESULT_REVIEW
}


# =========================================================
# INITIALIZE FORENSIC MODULES
# =========================================================

logger.info("Initializing ELA Processor...")

ela_processor = ELAProcessor()

logger.info("ELA Processor ready.")


logger.info("Initializing Grad-CAM Generator...")

gradcam_generator = GradCAMGenerator()

logger.info("Grad-CAM Generator ready.")


# =========================================================
# STORAGE HELPERS
# =========================================================

def ensure_storage():
    """
    Create investigation database if it does not exist.
    """

    if not os.path.exists(INVESTIGATIONS_FILE):

        with open(
            INVESTIGATIONS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                indent=2
            )


def read_investigations():
    """
    Read investigation records.
    """

    ensure_storage()

    try:

        with open(
            INVESTIGATIONS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (
        OSError,
        json.JSONDecodeError
    ):

        logger.exception(
            "Could not read investigation database."
        )

        return []


def write_investigations(records):
    """
    Safely write investigation records.
    """

    temp_file = INVESTIGATIONS_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )

    os.replace(
        temp_file,
        INVESTIGATIONS_FILE
    )


def add_investigation(record):
    """
    Add a new investigation.
    """

    with storage_lock:

        records = read_investigations()

        records.insert(
            0,
            record
        )

        write_investigations(
            records
        )


def get_investigation(case_id):
    """
    Find investigation by case ID.
    """

    records = read_investigations()

    for record in records:

        if record.get("case_id") == case_id:
            return record

    return None


def delete_investigation(case_id):
    """
    Delete investigation and associated files.
    """

    with storage_lock:

        records = read_investigations()

        target = next(
            (
                record
                for record in records
                if record.get("case_id") == case_id
            ),
            None
        )

        if target is None:
            return None

        records = [
            record
            for record in records
            if record.get("case_id") != case_id
        ]

        write_investigations(records)

    # -----------------------------------------------------
    # Delete associated files
    # -----------------------------------------------------

    files_to_delete = [

        (
            Config.UPLOAD_FOLDER,
            target.get("stored_image")
        ),

        (
            ELA_FOLDER,
            target.get("ela_file")
        ),

        (
            Config.OUTPUT_FOLDER,
            target.get("gradcam_file")
        )
    ]

    for folder, filename in files_to_delete:

        if not filename:
            continue

        filename = os.path.basename(filename)

        path = os.path.join(
            folder,
            filename
        )

        try:

            if os.path.exists(path):
                os.remove(path)

        except OSError:

            logger.exception(
                "Could not delete %s",
                path
            )

    return target


ensure_storage()


# =========================================================
# RESPONSE HELPERS
# =========================================================

def success_response(data, status=200):

    return jsonify(
        {
            "success": True,
            "data": data
        }
    ), status


def error_response(message, status=400):

    return jsonify(
        {
            "success": False,
            "error": message
        }
    ), status


# =========================================================
# FILE HELPERS
# =========================================================

def allowed_file(filename):
    """
    Check whether uploaded file extension is allowed.
    """

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = (
        filename
        .rsplit(".", 1)[1]
        .lower()
    )

    return (
        extension in Config.ALLOWED_EXTENSIONS
    )


def generate_filename(filename):
    """
    Generate unique secure filename.
    """

    extension = (
        filename
        .rsplit(".", 1)[1]
        .lower()
    )

    return (
        f"{uuid.uuid4().hex}.{extension}"
    )


def save_uploaded_image(file):
    """
    Save uploaded evidence image.
    """

    original_filename = secure_filename(
        file.filename
    )

    stored_filename = generate_filename(
        original_filename
    )

    image_path = os.path.join(
        Config.UPLOAD_FOLDER,
        stored_filename
    )

    file.save(image_path)

    logger.info(
        "Evidence saved: %s",
        image_path
    )

    return (
        image_path,
        stored_filename
    )


def elapsed_time(start):

    return round(
        time.time() - start,
        3
    )


def public_url(route, filename):

    if not filename:
        return None

    return (
        f"{route}/"
        f"{os.path.basename(filename)}"
    )


# =========================================================
# RESULT NORMALIZATION
# =========================================================

def normalize_result(result):

    if result is None:
        return RESULT_REVIEW

    value = str(
        result
    ).strip().upper()

    aliases = {

        "AUTHENTIC": RESULT_AUTHENTIC,
        "REAL": RESULT_AUTHENTIC,

        "MANIPULATED": RESULT_MANIPULATED,
        "FAKE": RESULT_MANIPULATED,
        "EDITED": RESULT_MANIPULATED,

        "AI_GENERATED": RESULT_AI_GENERATED,
        "AI-GENERATED": RESULT_AI_GENERATED,
        "AI": RESULT_AI_GENERATED,

        "REQUIRES_REVIEW": RESULT_REVIEW,
        "REVIEW": RESULT_REVIEW,
        "UNKNOWN": RESULT_REVIEW
    }

    return aliases.get(
        value,
        RESULT_REVIEW
    )


# =========================================================
# RISK LEVEL
# =========================================================

def calculate_risk(result, confidence):

    result = normalize_result(result)

    try:

        confidence = float(confidence)

    except (
        TypeError,
        ValueError
    ):

        confidence = 0.0

    if result == RESULT_AI_GENERATED:

        if confidence >= 0.85:
            return "HIGH"

        if confidence >= 0.70:
            return "MEDIUM"

        return "REVIEW"

    if result == RESULT_MANIPULATED:

        if confidence >= 0.85:
            return "HIGH"

        if confidence >= 0.70:
            return "MEDIUM"

        return "REVIEW"

    if result == RESULT_AUTHENTIC:

        if confidence >= 0.85:
            return "LOW"

        return "REVIEW"

    return "REVIEW"


# =========================================================
# EXTRACT MODEL VALUES
# =========================================================

def extract_prediction_values(analysis):

    if not isinstance(
        analysis,
        dict
    ):

        return (
            RESULT_REVIEW,
            0.0,
            {},
            None
        )

    predicted_class = normalize_result(
        analysis.get(
            "predicted_class"
        )
    )

    confidence = analysis.get(
        "confidence",
        0.0
    )

    class_index = analysis.get(
        "class_index"
    )

    probabilities = analysis.get(
        "probabilities",
        {}
    )

    try:

        confidence = float(
            confidence
        )

    except (
        TypeError,
        ValueError
    ):

        confidence = 0.0

    return (
        predicted_class,
        confidence,
        probabilities,
        class_index
    )


# =========================================================
# HOME
# =========================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return success_response({

        "project":
            "AI Image Forensics",

        "version":
            "4.0.0",

        "status":
            "Running",

        "framework":
            "Flask",

        "model":
            "ResNet50",

        "result_categories": [

            {
                "code":
                    RESULT_AUTHENTIC,

                "label":
                    "Authentic / Camera Captured"
            },

            {
                "code":
                    RESULT_MANIPULATED,

                "label":
                    "Manipulated / Edited"
            },

            {
                "code":
                    RESULT_AI_GENERATED,

                "label":
                    "AI Generated"
            },

            {
                "code":
                    RESULT_REVIEW,

                "label":
                    "Requires Review"
            }
        ],

        "features": [

            "ResNet50 classification",
            "Error Level Analysis",
            "Grad-CAM",
            "Risk assessment",
            "Investigation history",
            "Evidence storage",
            "Dashboard statistics",
            "Batch prediction"
        ],

        "endpoints": {

            "health":
                "/health",

            "predict":
                "/predict",

            "batch":
                "/predict/batch",

            "stats":
                "/api/stats",

            "investigations":
                "/api/investigations",

            "investigation_detail":
                "/api/investigations/<case_id>",

            "uploads":
                "/uploads/<filename>",

            "outputs":
                "/outputs/<filename>",

            "ela":
                "/outputs/ela/<filename>"
        }

    })


# =========================================================
# HEALTH
# =========================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    model_loaded = False

    try:

        model_loaded = os.path.exists(
            Config.MODEL_PATH
        )

    except Exception:

        pass

    return success_response({

        "status":
            "healthy",

        "server":
            "running",

        "model_loaded":
            model_loaded,

        "model_path":
            Config.MODEL_PATH,

        "database":
            INVESTIGATIONS_FILE,

        "upload_folder":
            Config.UPLOAD_FOLDER,

        "output_folder":
            Config.OUTPUT_FOLDER,

        "ela_folder":
            ELA_FOLDER

    })


# =========================================================
# API INFO
# =========================================================

@app.route(
    "/api/info",
    methods=["GET"]
)
def api_info():

    return success_response({

        "name":
            "AI Image Forensics API",

        "description":
            "AI-powered digital image forensic analysis",

        "version":
            "4.0.0",

        "model":
            "ResNet50",

        "classes":
            Config.CLASS_NAMES,

        "result_categories": [

            RESULT_AUTHENTIC,
            RESULT_MANIPULATED,
            RESULT_AI_GENERATED,
            RESULT_REVIEW
        ],

        "supported_formats":
            list(
                Config.ALLOWED_EXTENSIONS
            ),

        "max_upload_size":
            Config.MAX_CONTENT_LENGTH

    })


# =========================================================
# VALIDATE UPLOAD
# =========================================================

def validate_upload():

    if "image" not in request.files:

        return (
            False,
            error_response(
                "Image file is required.",
                400
            )
        )

    file = request.files["image"]

    if not file.filename:

        return (
            False,
            error_response(
                "No file selected.",
                400
            )
        )

    if not allowed_file(
        file.filename
    ):

        return (
            False,
            error_response(
                "Unsupported file format.",
                400
            )
        )

    return (
        True,
        file
    )


# =========================================================
# MAIN PREDICTION
# =========================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    start = time.time()

    image_path = None
    stored_filename = None
    ela_file = None
    gradcam_file = None

    try:

        # =================================================
        # VALIDATE UPLOAD
        # =================================================

        valid, result = validate_upload()

        if not valid:
            return result

        uploaded_file = result

        original_filename = secure_filename(
            uploaded_file.filename
        )

        # =================================================
        # SAVE IMAGE
        # =================================================

        (
            image_path,
            stored_filename
        ) = save_uploaded_image(
            uploaded_file
        )

        logger.info(
            "Starting forensic analysis: %s",
            original_filename
        )

        # =================================================
        # STEP 1 - RESNET PREDICTION
        # =================================================

        logger.info(
            "Running ResNet50 prediction..."
        )

        prediction = predict_image(
            image_path
        )

        if not isinstance(
            prediction,
            dict
        ):

            raise ValueError(
                "Invalid prediction response."
            )

        logger.info(
            "Prediction completed: %s",
            prediction.get(
                "predicted_class"
            )
        )

        (
            predicted_class,
            confidence,
            probabilities,
            class_index
        ) = extract_prediction_values(
            prediction
        )

        # =================================================
        # STEP 2 - RISK
        # =================================================

        risk = calculate_risk(
            predicted_class,
            confidence
        )

        logger.info(
            "Risk level: %s",
            risk
        )

        # =================================================
        # STEP 3 - ELA
        # =================================================

        logger.info(
            "Generating ELA..."
        )

        ela_filename = (
            "ela_"
            + uuid.uuid4().hex
            + ".png"
        )

        # ELAProcessor may internally save to outputs/ela
        ela_result = ela_processor.save_ela(
            image_path,
            ela_filename
        )

        if isinstance(
            ela_result,
            dict
        ):

            ela_path = ela_result.get(
                "path"
            )

        else:

            ela_path = ela_result

        if not ela_path:
            raise ValueError(
                "ELA generation returned no file path."
            )

        ela_file = os.path.basename(
            ela_path
        )

        # =================================================
        # IMPORTANT ELA LOCATION FIX
        # =================================================

        # If ELAProcessor saved it somewhere else,
        # make sure it exists in outputs/ela.

        expected_ela_path = os.path.join(
            ELA_FOLDER,
            ela_file
        )

        if not os.path.exists(
            expected_ela_path
        ):

            if os.path.exists(
                ela_path
            ):

                os.makedirs(
                    ELA_FOLDER,
                    exist_ok=True
                )

                os.replace(
                    ela_path,
                    expected_ela_path
                )

            else:

                raise FileNotFoundError(
                    f"ELA file was not found: {ela_path}"
                )

        logger.info(
            "ELA generated: %s",
            expected_ela_path
        )

        # =================================================
        # STEP 4 - ELA STATISTICS
        # =================================================

        try:

            ela_statistics = (
                ela_processor.statistics(
                    image_path
                )
            )

        except Exception:

            logger.exception(
                "ELA statistics generation failed."
            )

            ela_statistics = {}

        # =================================================
        # STEP 5 - GRAD-CAM
        # =================================================

        logger.info(
            "Generating Grad-CAM..."
        )

        gradcam_filename = (
            "gradcam_"
            + uuid.uuid4().hex
            + ".jpg"
        )

        gradcam_path = (
            gradcam_generator.save_gradcam(
                image_path
            )
        )

        if not gradcam_path:
            raise ValueError(
                "Grad-CAM generation returned no file path."
            )

        generated_gradcam = os.path.basename(
            gradcam_path
        )

        unique_gradcam_path = os.path.join(
            Config.OUTPUT_FOLDER,
            gradcam_filename
        )

        if os.path.exists(
            gradcam_path
        ):

            # If already has desired filename,
            # do not replace itself.
            if os.path.abspath(
                gradcam_path
            ) != os.path.abspath(
                unique_gradcam_path
            ):

                os.replace(
                    gradcam_path,
                    unique_gradcam_path
                )

            else:

                unique_gradcam_path = gradcam_path

        else:

            raise FileNotFoundError(
                f"Grad-CAM file was not found: {gradcam_path}"
            )

        gradcam_file = os.path.basename(
            unique_gradcam_path
        )

        logger.info(
            "Grad-CAM generated: %s",
            gradcam_file
        )

        # =================================================
        # CASE INFORMATION
        # =================================================

        case_id = (
            "IF-"
            + datetime.now(
                timezone.utc
            ).strftime(
                "%Y%m%d"
            )
            + "-"
            + uuid.uuid4().hex[:8].upper()
        )

        created_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        processing_time = elapsed_time(start)

        # =================================================
        # URLs
        # =================================================

        image_url = public_url(
            "/uploads",
            stored_filename
        )

        # IMPORTANT:
        # ELA is inside outputs/ela
        ela_url = public_url(
            "/outputs/ela",
            ela_file
        )

        gradcam_url = public_url(
            "/outputs",
            gradcam_file
        )

        # =================================================
        # INVESTIGATION RECORD
        # =================================================

        record = {

            "case_id":
                case_id,

            "created_at":
                created_at,

            "status":
                "COMPLETED",

            "original_filename":
                original_filename,

            "stored_image":
                stored_filename,

            "result":
                predicted_class,

            "result_label":
                predicted_class,

            "confidence":
                confidence,

            "confidence_percentage":
                round(
                    confidence * 100,
                    2
                ),

            "class_index":
                class_index,

            "probabilities":
                probabilities,

            "risk_level":
                risk,

            "processing_time":
                processing_time,

            "image_url":
                image_url,

            "ela_file":
                ela_file,

            "ela_url":
                ela_url,

            "ela_statistics":
                ela_statistics,

            "gradcam_file":
                gradcam_file,

            "gradcam_url":
                gradcam_url,

            "analysis":
                prediction
        }

        # =================================================
        # SAVE INVESTIGATION
        # =================================================

        add_investigation(
            record
        )

        logger.info(
            "Investigation saved: %s",
            case_id
        )

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return jsonify({

            "success":
                True,

            "case_id":
                case_id,

            "created_at":
                created_at,

            "status":
                "COMPLETED",

            "filename":
                original_filename,

            "result":
                predicted_class,

            "result_label":
                predicted_class,

            "confidence":
                confidence,

            "confidence_percentage":
                round(
                    confidence * 100,
                    2
                ),

            "class_index":
                class_index,

            "probabilities":
                probabilities,

            "risk_level":
                risk,

            "processing_time":
                processing_time,

            "image_url":
                image_url,

            # FIXED
            "ela_url":
                ela_url,

            "ela_statistics":
                ela_statistics,

            "gradcam_url":
                gradcam_url,

            "prediction":
                prediction

        }), 200

    except Exception as exc:

        logger.exception(
            "Forensic prediction failed."
        )

        return error_response(
            str(exc),
            500
        )


# =========================================================
# BATCH PREDICTION
# =========================================================

@app.route(
    "/predict/batch",
    methods=["POST"]
)
def batch_predict():

    if "images" not in request.files:

        return error_response(
            "No images uploaded.",
            400
        )

    files = request.files.getlist(
        "images"
    )

    results = []

    for file in files:

        try:

            if not file.filename:
                continue

            if not allowed_file(
                file.filename
            ):
                continue

            (
                image_path,
                stored_filename
            ) = save_uploaded_image(
                file
            )

            prediction = predict_image(
                image_path
            )

            (
                predicted_class,
                confidence,
                probabilities,
                class_index
            ) = extract_prediction_values(
                prediction
            )

            result_record = {

                "filename":
                    secure_filename(
                        file.filename
                    ),

                "stored_filename":
                    stored_filename,

                "result":
                    predicted_class,

                "confidence":
                    confidence,

                "confidence_percentage":
                    round(
                        confidence * 100,
                        2
                    ),

                "class_index":
                    class_index,

                "probabilities":
                    probabilities,

                "risk_level":
                    calculate_risk(
                        predicted_class,
                        confidence
                    ),

                "analysis":
                    prediction
            }

            results.append(
                result_record
            )

        except Exception as exc:

            logger.exception(
                "Batch item failed."
            )

            results.append({

                "filename":
                    secure_filename(
                        file.filename
                    ),

                "error":
                    str(exc)
            })

    return success_response({

        "total":
            len(results),

        "results":
            results

    })


# =========================================================
# INVESTIGATION HISTORY
# =========================================================

@app.route(
    "/api/investigations",
    methods=["GET"]
)
def investigations():

    records = read_investigations()

    search = request.args.get(
        "search",
        ""
    ).strip().lower()

    result_filter = request.args.get(
        "result",
        ""
    ).strip().upper()

    risk_filter = request.args.get(
        "risk",
        ""
    ).strip().upper()

    if search:

        records = [

            record

            for record in records

            if (
                search in str(
                    record.get(
                        "case_id",
                        ""
                    )
                ).lower()

                or

                search in str(
                    record.get(
                        "original_filename",
                        ""
                    )
                ).lower()
            )
        ]

    if result_filter:

        records = [

            record

            for record in records

            if normalize_result(
                record.get(
                    "result"
                )
            ) == result_filter
        ]

    if risk_filter:

        records = [

            record

            for record in records

            if str(
                record.get(
                    "risk_level",
                    ""
                )
            ).upper() == risk_filter
        ]

    return success_response({

        "total":
            len(records),

        "investigations":
            records

    })


# =========================================================
# INVESTIGATION DETAIL
# =========================================================

@app.route(
    "/api/investigations/<case_id>",
    methods=["GET"]
)
def investigation_detail(case_id):

    record = get_investigation(
        case_id
    )

    if record is None:

        return error_response(
            "Investigation not found.",
            404
        )

    return success_response(
        record
    )


# =========================================================
# DELETE INVESTIGATION
# =========================================================

@app.route(
    "/api/investigations/<case_id>",
    methods=["DELETE"]
)
def delete_investigation_api(case_id):

    record = delete_investigation(
        case_id
    )

    if record is None:

        return error_response(
            "Investigation not found.",
            404
        )

    return success_response({

        "message":
            "Investigation deleted successfully.",

        "case_id":
            case_id

    })


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@app.route(
    "/api/stats",
    methods=["GET"]
)
def stats():

    records = read_investigations()

    total = len(records)

    authentic_count = 0
    manipulated_count = 0
    ai_generated_count = 0
    review_count = 0

    confidence_values = []

    for record in records:

        result = normalize_result(
            record.get(
                "result"
            )
        )

        if result == RESULT_AUTHENTIC:

            authentic_count += 1

        elif result == RESULT_MANIPULATED:

            manipulated_count += 1

        elif result == RESULT_AI_GENERATED:

            ai_generated_count += 1

        else:

            review_count += 1

        try:

            confidence_values.append(
                float(
                    record.get(
                        "confidence",
                        0
                    )
                )
            )

        except (
            TypeError,
            ValueError
        ):

            pass

    average_confidence = (

        round(
            sum(confidence_values)
            / len(confidence_values),
            2
        )

        if confidence_values

        else 0
    )

    return success_response({

        "total_cases":
            total,

        "authentic_images":
            authentic_count,

        "manipulated_images":
            manipulated_count,

        "ai_generated_images":
            ai_generated_count,

        "requires_review":
            review_count,

        "average_confidence":
            average_confidence,

        "risk": {

            "high":
                sum(
                    str(
                        r.get(
                            "risk_level",
                            ""
                        )
                    ).upper() == "HIGH"

                    for r in records
                ),

            "medium":
                sum(
                    str(
                        r.get(
                            "risk_level",
                            ""
                        )
                    ).upper() == "MEDIUM"

                    for r in records
                ),

            "low":
                sum(
                    str(
                        r.get(
                            "risk_level",
                            ""
                        )
                    ).upper() == "LOW"

                    for r in records
                ),

            "review":
                sum(
                    str(
                        r.get(
                            "risk_level",
                            ""
                        )
                    ).upper() == "REVIEW"

                    for r in records
                )
        }

    })


# =========================================================
# SERVE UPLOADED IMAGES
# =========================================================

@app.route(
    "/uploads/<path:filename>",
    methods=["GET"]
)
def uploaded_file(filename):

    try:

        return send_from_directory(
            Config.UPLOAD_FOLDER,
            filename
        )

    except Exception:

        logger.exception(
            "Uploaded file not found."
        )

        return error_response(
            "File not found.",
            404
        )


# =========================================================
# SERVE NORMAL OUTPUT FILES
# =========================================================

@app.route(
    "/outputs/<path:filename>",
    methods=["GET"]
)
def output_file(filename):

    try:

        return send_from_directory(
            Config.OUTPUT_FOLDER,
            filename
        )

    except Exception:

        logger.exception(
            "Output file not found."
        )

        return error_response(
            "Output file not found.",
            404
        )


# =========================================================
# SERVE ELA FILES
# =========================================================

@app.route(
    "/outputs/ela/<path:filename>",
    methods=["GET"]
)
def ela_output_file(filename):

    try:

        return send_from_directory(
            ELA_FOLDER,
            filename
        )

    except Exception:

        logger.exception(
            "ELA output file not found."
        )

        return error_response(
            "ELA output file not found.",
            404
        )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(400)
def bad_request(error):

    return error_response(
        "Bad Request.",
        400
    )


@app.errorhandler(404)
def not_found(error):

    return error_response(
        "Resource not found.",
        404
    )


@app.errorhandler(405)
def method_not_allowed(error):

    return error_response(
        "Method Not Allowed.",
        405
    )


@app.errorhandler(413)
def request_entity_too_large(error):

    return error_response(
        "Uploaded file exceeds maximum size.",
        413
    )


@app.errorhandler(500)
def internal_server_error(error):

    logger.error(
        "Internal Server Error: %s",
        error
    )

    return error_response(
        "Internal Server Error.",
        500
    )


# =========================================================
# SECURITY HEADERS
# =========================================================

@app.after_request
def security_headers(response):

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "Referrer-Policy"
    ] = "strict-origin-when-cross-origin"

    response.headers[
        "Cache-Control"
    ] = "no-store"

    return response


# =========================================================
# STARTUP
# =========================================================

def startup():

    logger.info("=" * 60)

    logger.info(
        "AI IMAGE FORENSICS API"
    )

    logger.info("=" * 60)

    logger.info(
        "Upload Folder : %s",
        Config.UPLOAD_FOLDER
    )

    logger.info(
        "Output Folder : %s",
        Config.OUTPUT_FOLDER
    )

    logger.info(
        "ELA Folder    : %s",
        ELA_FOLDER
    )

    logger.info(
        "Database      : %s",
        INVESTIGATIONS_FILE
    )

    logger.info(
        "Model         : %s",
        Config.MODEL_PATH
    )

    logger.info(
        "Classes       : %s",
        Config.CLASS_NAMES
    )

    logger.info(
        "Server        : http://localhost:5001"
    )

    logger.info("=" * 60)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    startup()

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )