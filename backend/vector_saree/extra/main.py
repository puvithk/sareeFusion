import cv2
import numpy as np


# Use the flag -1 or cv2.IMREAD_UNCHANGED to read all channels, including alpha
img_with_alpha = cv2.imread("C:/sareefusion/sareeFusion/backend/vector_saree/extra/b79288c91e96440084908c08b0c6c992.png", cv2.IMREAD_UNCHANGED)

# Now, the shape should correctly include 4 channels (BGRA)
print(np.shape(img_with_alpha)) 
# Expected Output: (Height, Width, 4)
# Assuming 'images' is the PIL RGBA image object
from PIL import Image
images = Image.open("C:/sareefusion/sareeFusion/backend/vector_saree/extra/b79288c91e96440084908c08b0c6c992.png")
# 1. Create a new, solid background image (e.g., white)

bbox = images.getbbox()

if bbox:   
    # 3. Optional: Print the new size to confirm the padding is gone
    cropped_image = images.crop(bbox)
    print(f"Original size: {images.size}")
    print(f"Cropped size (no transparency): {cropped_image.size}")


    cropped_image.save("output.png")