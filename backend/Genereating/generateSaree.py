import base64
import time
from google import genai 
# You might also need:
from google.genai import types

# from google.genai import types
from PIL import Image
from io import BytesIO
import numpy as np
import PIL.Image
import os
from dotenv import load_dotenv
load_dotenv()
import cv2
class GenerateComplete:
    def __init__(self) -> None:
        self.__PROJECT_ID__ = 'sareefusion'
        self.__LOCATION__ = 'global'
        # genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        # self.client = genai # The module itself (genai) often acts as the client
        self.client =  genai.Client(vertexai=True,api_key=os.environ["GOOGLE_CLOUD_API_KEY"])
        #self.client = genai.Client(vertexai=True,api_key="AQ.Ab8RN6IAA1lIMEZ3etPZxiR4RKAj_niNMgK9rhlqdzNDbTvkpA" )
        self.text_input = ('This image is a saree template. Based on this template,Keep the border as in image and match the colors if needed, generate a realistic 4K image of the saree draped on a mannequin , Keep the templete border , body and pallu as given in twmplete. The image should be clean, neat, professionally photographed, and visually appealing. NOTE : User prompt ')
        self.text_vector_input = ("Convert the image into flat vector graphic style preserve the pattern and perserv the details")
    def predict(self,image=None , custom_prompt=""):
        if image is None:
            response = self.client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[self.text_input +custom_prompt],
            config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
            ))    
            image = Image.open(BytesIO(response.candidates[0].content.parts[1].inline_data.data))
            return image
           
        response = self.client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=[self.text_input +custom_prompt, image],
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
        ))    
        image = Image.open(BytesIO(response.candidates[0].content.parts[1].inline_data.data))
        return image
    def predict_vector(self,image):
        response = self.client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=[self.text_vector_input, image],
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
        ))    
        image = Image.open(BytesIO(response.candidates[0].content.parts[1].inline_data.data))
        return image

    def create_vector_border(self,image):
        prompt = """
                Preserve the border and remove everything outside it,
                Crop the major part and  Correct the perspective, eliminate all shadows,
                gradients, and lighting effects, and convert the image into a clean, flat vector graphic style. 
                Preserve the pattern and perserv the details Aline it Horizontally and make it neat 
                NOTE : Extract only border remove other part And do not add extra part but enhance clarity
               """
        try :
            image_output = self.create_vector_image(image  , prompt=prompt)
            return image_output
        except Exception as e:
            return ("Error during Creating Image" , 500)
    def create_vector_body(self,image):
        prompt = """
                Preserve the Body and remove everything outside it,
                Crop the major part and  Correct the perspective, eliminate all shadows,
                gradients, and lighting effects, and convert the image into a clean, flat vector graphic style. 
                Preserve the pattern and perserv the details Aline it Horizontally and make it neat 
                NOTE : Extract only Body remove other part And do not add extra part but enhance clarity
            """
        try :
            image_output = self.create_vector_image(image  , prompt=prompt)
            return image_output
        except Exception as e:
            return ("Error during Creating Image" , 500)
    def create_vector_pallu(self,image):
        prompt = """
                Preserve the pallu and remove everything outside it,
                Crop the major part and  Correct the perspective, eliminate all shadows,
                gradients, and lighting effects, and convert the image into a clean, flat vector graphic style. 
                Preserve the pattern and perserv the details Aline it Horizontally and make it neat 
                NOTE : Extract only pallu remove other part  And do not add extra part but enhance clarity
                """
        try :
            image_output = self.create_vector_image(image  , prompt=prompt)
            return image_output
        except Exception as e:
            return ("Error during Creating Image" , 500)
        
        
    def create_vector_image(self, image , prompt):
        vect_image = None 
        count = 0 
        while vect_image is None and count < 3:
            try :
                msg1_text1 = types.Part.from_text(text=prompt)
                buf = BytesIO()
                image = image.convert("RGB")
                image.save(buf, format="JPEG")  # or PNG, depending on your image
                image_bytes = buf.getvalue()

                # Now create the Part from bytes
                msg1_image1 = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                )
               
                model = "gemini-2.5-flash-image"
                contents = [
                    types.Content(
                    role="user",
                    parts=[
                        msg1_text1,
                        msg1_image1
                    ]
                    ),
                ]
                generate_content_config = types.GenerateContentConfig(
                    temperature = 1,
                    top_p = 0.95,
                    max_output_tokens = 32768,
                    response_modalities = ["TEXT", "IMAGE"],
                    
                )
                data = self.client.models.generate_content(
                    model = model,
                    contents = contents,
                    config = generate_content_config,
                    )
                vect_image = Image.open(BytesIO(data.candidates[0].content.parts[0].inline_data.data))

                # Decode and load into PIL

                return vect_image
            except Exception as e:
                print(e)
                count += 1
                if count > 3:
                    return None
                time.sleep(4)


    def remove_white_bg_cv2(self, image):
        # 1. Load the image
        
        def pil_to_cv2(img_pil):
            return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        img_bgr = pil_to_cv2(image)
        
        if img_bgr is None:
            print("Error: Could not read image.")
            return

        # 2. Convert to HSV
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # 3. Define the white color range
        # H: 0-179 (all colors)
        # S: 0-25 (very low saturation, allowing for slight variations in "white")
        # V: 200-255 (high brightness/value)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([179, 25, 255])

        # 4. Create the mask (pixels in this range are TRUE/255)
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # 5. Invert the mask
        # We want to keep the non-white pattern, so the mask for the pattern
        mask_inv = cv2.bitwise_not(mask) 

        # 6. Prepare the output image with an alpha channel
        # Split the BGR image into channels
        b, g, r = cv2.split(img_bgr)
        
        # Merge the B, G, R channels with the inverted mask as the Alpha channel
        img_rgba = cv2.merge((b, g, r, mask_inv))

        # Save the final image (must be PNG to preserve transparency)
        def cv2_to_pil(img_cv):
            return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGRA2RGBA))
        image  = cv2_to_pil(img_rgba)
        def crop_only_img(image):
            bbox = image.getbbox()

            if bbox:   
                # 3. Optional: Print the new size to confirm the padding is gone
                cropped_image = image.crop(bbox)
         

                return cropped_image
        return crop_only_img(image)
if __name__ =="__main__":
    genereator = GenerateComplete()
    img = Image.open('C:/sareefusion/sareeFusion/backend/Genereating/border_neat_output.png')
    result_img = genereator.create_vector_border(img)
    result_img.show()
    result_img.save('C:/sareefusion/sareeFusion/backend/Genereating/generated_vector.png')  # Save the generated image
    