import os
from PIL import Image, ImageChops, ImageEnhance


# ============================================================
# AI IMAGE FORENSICS
# ERROR LEVEL ANALYSIS (ELA)
# ============================================================

# Input image
IMAGE_PATH = os.path.join(
    "dataset",
    "test",
    "AI_GENERATED",
    "car_11.png"
)

# Output folder
OUTPUT_DIR = "ela_results"

# ELA settings
JPEG_QUALITY = 90
SCALE = 10


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# CHECK IMAGE
# ============================================================

if not os.path.exists(IMAGE_PATH):
    print("ERROR: Image not found!")
    print(IMAGE_PATH)
    exit()

print("=" * 60)
print("AI IMAGE FORENSICS")
print("ERROR LEVEL ANALYSIS (ELA)")
print("=" * 60)

print("\nInput image:")
print(IMAGE_PATH)


# ============================================================
# OPEN IMAGE
# ============================================================

try:
    original = Image.open(IMAGE_PATH).convert("RGB")
except Exception as e:
    print("\nERROR: Could not open image.")
    print(e)
    exit()


print("Image loaded successfully.")

# ============================================================
# TEMPORARY JPEG
# ============================================================

temp_path = os.path.join(
    OUTPUT_DIR,
    "temp_ela.jpg"
)

original.save(
    temp_path,
    "JPEG",
    quality=JPEG_QUALITY
)


# ============================================================
# REOPEN COMPRESSED IMAGE
# ============================================================

compressed = Image.open(temp_path).convert("RGB")


# ============================================================
# CALCULATE DIFFERENCE
# ============================================================

difference = ImageChops.difference(
    original,
    compressed
)


# ============================================================
# FIND MAX DIFFERENCE
# ============================================================

extrema = difference.getextrema()

max_difference = max(
    channel_max
    for channel_min, channel_max in extrema
)


print("\nMaximum pixel difference:", max_difference)


# ============================================================
# ENHANCE DIFFERENCE
# ============================================================

if max_difference == 0:
    print("No visible compression difference detected.")
    scale = 1
else:
    scale = 255 / max_difference

ela_image = ImageEnhance.Brightness(
    difference
).enhance(scale)


# ============================================================
# SAVE ELA IMAGE
# ============================================================

output_path = os.path.join(
    OUTPUT_DIR,
    "car_11_ela.png"
)

ela_image.save(output_path)


# ============================================================
# REMOVE TEMP FILE
# ============================================================

try:
    os.remove(temp_path)
except OSError:
    pass


# ============================================================
# RESULT
# ============================================================

print("\n" + "=" * 60)
print("ELA COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nELA image saved to:")
print(os.path.abspath(output_path))

print("\nYou can now open:")
print(output_path)