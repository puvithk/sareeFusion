import torch
import segmentation_models_pytorch as smp
from PIL import Image
import numpy as np
import torchvision.transforms as transforms
import torchvision.transforms as T
import cv2
import matplotlib.pyplot as plt
import numpy as np
import cv2
from ultralytics import YOLO
import os
class SegmentationModel:
    def __init__(self, model_path, n_classes=5, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.n_classes = n_classes

        # Initialize model architecture
        self.model = smp.Unet(
            encoder_name="resnet50",
            encoder_weights=None,
            in_channels=3,
            classes=n_classes,
        ).to(self.device)

        # Load trained weights
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

        # Define preprocessing
        self.transform = T.Compose([
                  T.ToTensor()
        ])

    def predict(self, image_path):
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # Make prediction
        with torch.no_grad():
            output = self.model(input_tensor)
            prediction = torch.argmax(output, dim=1).cpu().numpy()

        return prediction , image


class Processing:
    def __init__(self) -> None:
        self.model = YOLO('C:/sareefusion/sareeFusion/backend/Extracting_Element/best.pt')

    def extract_class_region(self, image_pil, mask, class_id, class_name):
        # os.makedirs("cropped_parts", exist_ok=True)
        # os.makedirs("full_parts", exist_ok=True)

        original_img_rgb = np.array(image_pil)
        original_img_bgr = cv2.cvtColor(original_img_rgb, cv2.COLOR_RGB2BGR)

        # Step 1: Handle special case: include pattern in body
        if class_id == 1:  # body
            combined_mask = ((mask == 1) | (mask == 4)).astype(np.uint8) * 255
        else:
            combined_mask = (mask == class_id).astype(np.uint8) * 255

        # Step 2: Morphological kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

        # Step 3: Add extra pixels for border/pallu
        if class_id in [2, 3]:  # border or pallu
            combined_mask = cv2.dilate(combined_mask, kernel, iterations=2)  # increase area
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            combined_mask = cv2.GaussianBlur(combined_mask, (5, 5), 0)
            combined_mask = (combined_mask > 20).astype(np.uint8) * 255  # threshold to binary
        else:
            # For others: basic smoothing
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            combined_mask = cv2.dilate(combined_mask, kernel, iterations=1)
            combined_mask = cv2.erode(combined_mask, kernel, iterations=1)

        # Step 4: Apply mask
        full_masked_img = cv2.bitwise_and(original_img_bgr, original_img_bgr, mask=combined_mask)
        #cv2.imwrite(f"full_parts/{class_name}_full.png", full_masked_img)

        # Step 5: Cropped output
        x, y, w, h = cv2.boundingRect(combined_mask)
        cropped = full_masked_img[y:y+h, x:x+w]
        

        return full_masked_img, cropped
    def extract_show(self , image , result):
        class_map = {
            0: "background",
            1: "body",
            2: "border",      # orange
            3: "pallu",       # blue
            4: "pattern"      # red dots
        }
        track_parts = {}
        # Assuming 'image' is PIL.Image and 'result[0]' is your segmentation mask

        for class_id, class_name in class_map.items():
            if class_name == "background":
                continue

            full_img, cropped_img = self.extract_class_region(image, result[0], class_id, class_name)
            track_parts[class_name] = cropped_img
            # Full View
        return track_parts
    def extract_with_yolo(self, image):
        result = self.model.predict(image)[0]
        track_parts = {}
        for i, box in enumerate(result.boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            cropped = image.crop((x1, y1, x2, y2))
            # Store in track_parts
            if class_name not in track_parts:
                track_parts[class_name] = []
            track_parts[class_name].append(cropped)
        
        return track_parts
if __name__ =="__main__":
# Usage in backend
    segmentation_model = SegmentationModel('backend/Models/segmentation_model_weights1.pth', n_classes=5)
    post_processing = Processing()
    # result , image = segmentation_model.predict('backend/Extracting Element/test1.jpg')
    # track_parts = post_processing.extract_show(image , result)
    image = Image.open('backend/Extracting_Element/test.jpg').convert("RGB")
    track_parts = post_processing.extract_with_yolo(image)
    for i , j in track_parts.items():
        for k in j:
            k.show()