from PIL import Image
import cv2
import numpy as np
from Genereating.generateSaree import GenerateComplete

class GenerateSaree:

        def tempelete(self, border , pallu ,  body):
            print(border.size, pallu.size, body.size)
        # === 2. Define saree dimensions ===
            saree_width = 3000
            saree_height =(2 * border.height) + body.height

            border_height = border.height
            body_height = saree_height - (2 * border_height)

            # === 3. Resize body and pallu to fit ===
            body_aspect_ratio = body.width / body.height
            new_body_width = int(body_height * body_aspect_ratio)
            body = body.resize((new_body_width, body_height), Image.Resampling.LANCZOS)

            pallu_aspect_ratio = pallu.width / pallu.height
            new_pallu_width = int(body_height * pallu_aspect_ratio)
            pallu = pallu.resize((new_pallu_width, body_height), Image.Resampling.LANCZOS)

            # === 4. Convert PIL to OpenCV (for CLAHE) ===
            def pil_to_cv2(img_pil):
                return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

            def cv2_to_pil(img_cv):
                return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

            body_cv = pil_to_cv2(body)
            pallu_cv = pil_to_cv2(pallu)
            border_cv = pil_to_cv2(border)

            # === 5. CLAHE Enhancer ===
            def apply_clahe_to_region(region_bgr, clipLimit):
                lab = cv2.cvtColor(region_bgr, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(8, 8))
                l_clahe = clahe.apply(l)
                lab_clahe = cv2.merge((l_clahe, a, b))
                return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

            # === 6. Apply CLAHE ===
            enhanced_body_cv = apply_clahe_to_region(body_cv, clipLimit=2.0)
            enhanced_pallu_cv = apply_clahe_to_region(pallu_cv, clipLimit=1.2)
            enhanced_border_cv = apply_clahe_to_region(border_cv, clipLimit=1.0)

            # === 7. Convert back to PIL ===
            body = cv2_to_pil(enhanced_body_cv)
            pallu = cv2_to_pil(enhanced_pallu_cv)
            border = cv2_to_pil(enhanced_border_cv)

            # === 8. Create blank canvas ===
            saree = Image.new('RGB', (saree_width, saree_height), 'white')

            # === 9. Paste borders ===
            for x in range(0, saree_width, border.width):
                saree.paste(border, (x, 0))  # Top border
                saree.paste(border, (x, saree_height - border_height))  # Bottom border

            # === 10. Blending helper: Seam blur ===
            def apply_seam_blur(image, x, y, width, height, blur_strength=9):
                img_np = np.array(image)
                region = img_np[y:y+height, x:x+width]
                blurred = cv2.GaussianBlur(region, (blur_strength, blur_strength), sigmaX=3)
                img_np[y:y+height, x:x+width] = blurred
                return Image.fromarray(img_np)

            # === 11. Paste body tiles with overlap blending ===
            body_area_width = saree_width - new_pallu_width
            overlap_width = 100
            x = 0
            while x < body_area_width:
                if x == 0:
                    saree.paste(body, (x, border_height))
                    last_body_patch = body
                else:
                    # Extract overlaps
                    left_overlap = last_body_patch.crop((last_body_patch.width - overlap_width, 0, last_body_patch.width, body.height))
                    right_overlap = body.crop((0, 0, overlap_width, body.height))

                    # Blend overlaps
                    left_np = np.array(left_overlap).astype(np.float32)
                    right_np = np.array(right_overlap).astype(np.float32)
                    alpha = np.linspace(1, 0, overlap_width).reshape(1, -1, 1)
                    alpha = np.repeat(alpha, body.height, axis=0)
                    blended_np = (alpha * left_np + (1 - alpha) * right_np).astype(np.uint8)
                    blended_patch = Image.fromarray(blended_np)

                    blend_x = x - overlap_width
                    saree.paste(blended_patch, (blend_x, border_height))
                    saree.paste(body.crop((overlap_width, 0, body.width, body.height)), (x, border_height))

                    # Apply seam blur
                    saree = apply_seam_blur(saree, blend_x, border_height, 10, body.height)

                    last_body_patch = body

                x += body.width - overlap_width

            # === 12. Blend body with pallu ===
            body_overlap = body.crop((body.width - overlap_width, 0, body.width, body.height))
            pallu_overlap = pallu.crop((0, 0, overlap_width, pallu.height))

            body_np = np.array(body_overlap).astype(np.float32)
            pallu_np = np.array(pallu_overlap).astype(np.float32)
            alpha = np.linspace(1, 0, overlap_width).reshape(1, -1, 1)
            alpha = np.repeat(alpha, body.height, axis=0)
            blended_np = (alpha * body_np + (1 - alpha) * pallu_np).astype(np.uint8)
            blended = Image.fromarray(blended_np)

            # Construct full pallu with blend
            remaining_pallu = pallu.crop((overlap_width, 0, pallu.width, pallu.height))
            new_pallu = Image.new('RGB', (blended.width + remaining_pallu.width, pallu.height))
            new_pallu.paste(blended, (0, 0))
            new_pallu.paste(remaining_pallu, (blended.width, 0))

            # === 13. Paste pallu and blur junction ===
            pallu_x = body_area_width
            saree.paste(new_pallu, (pallu_x, border_height))
            saree = apply_seam_blur(saree, pallu_x - 5, border_height, 10, body.height)

            # === 14. Optional: Smooth top/bottom border joins ===
            saree = apply_seam_blur(saree, 0, 0, saree_width, 10)  # Top
            saree = apply_seam_blur(saree, 0, saree_height - border_height, saree_width, 10)  # Bottom

            # === 15. Save final output ===
            return saree
                # === Convert PIL to OpenCV and back ===
        def pil_to_cv2(self, img_pil):
            return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        def cv2_to_pil(self, img_cv):
            return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

        # === CLAHE enhancer for border ===
        def apply_clahe_to_border(self,  border_pil, clip_limit=1.0):
            """
            Enhance the border image using CLAHE (Contrast Limited Adaptive Histogram Equalization)
            """
            border_cv = self.pil_to_cv2(border_pil)
            
            lab = cv2.cvtColor(border_cv, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
            l_clahe = clahe.apply(l)
            lab_clahe = cv2.merge((l_clahe, a, b))
            
            enhanced_border_cv = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
            enhanced_border_pil = self.cv2_to_pil(enhanced_border_cv)
            
            return enhanced_border_pil
        def get_border_processed(self , filepath = None , file = None):
            if filepath :
                file = Image.open(filepath)
            border = file 
            if border.mode == "RGBA":
                border = border.convert("RGB") 
            self.apply_clahe_to_border(border)
            return border

            
if __name__ =="__main__":
    genereate = GenerateSaree()
    border  = Image.open("C:/sareefusion/sareeFusion/backend/Genereating/testborder.jpg")
    # pallu  =  Image.open("C:/sareefusion/sareeFusion/backend/Genereating/pallu.png")
    # body  =  Image.open("C:/sareefusion/sareeFusion/backend/Genereating/body.png")
    # print(border.size, pallu.size, body.size)
    # templete = genereate.tempelete(border, pallu, body)
    # saree = templete.save("C:/sareefusion/sareeFusion/backend/Genereating/saree.png")
    sareeGeneration = GenerateComplete()
    if border.mode == "RGBA":
        border = border.convert("RGB")
    
    enhanced_border = genereate.apply_clahe_to_border(border, clip_limit=1.0)
    enhanced_border.show("output")
    image = sareeGeneration.predict_vector(enhanced_border)
    image.show()
    image.save("C:/sareefusion/sareeFusion/backend/Genereating/saree_saree.png")
    
    
