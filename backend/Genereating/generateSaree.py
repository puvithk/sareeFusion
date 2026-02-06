import base64
import json
import time
from google import genai 
# You might also need:
from google.genai import types
import uuid
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
    def __init__(self ) -> None:
        self.__PROJECT_ID__ = 'sareefusion'
        self.__LOCATION__ = 'global'
        # genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        # self.client = genai # The module itself (genai) often acts as the client
        #---------------------------------------------------------------------------------------------------------
        #IF USING THE BELOW  LINE WE SHOULD USE GCLOUD AUTH CLI
        self.client =  genai.Client(vertexai=True, project=self.__PROJECT_ID__,location=self.__LOCATION__,)
        #-=-------------------------------------------------------------------------------------------------------
        #USE THIS FOR REGULAR 
        #self.client = genai.Client(vertexai=True,api_key=os.environ["GOOGLE_API_KEY"])
        self.text_input = ('This image is a saree template. Based on this template,Keep the border as in image and match the colors if needed, generate a one realistic 4K image of the saree draped on a mannequin , Keep the templete border , body and pallu as given in templete. The image should be clean, neat, professionally photographed, and visually appealing. NOTE : User prompt ')
        self.text_vector_input = ("Convert the image into flat vector graphic style preserve the pattern and perserv the details")
        self.saree_text_promnpt = ('View the given all input ingames and based on it geneate a high detailed saree image , keep all the details as given in the input images , keep the border as in image and match the colors if needed, generate a one realistic 4K image of the saree draped on a mannequin , body and pallu as given in images. The image should be clean, neat, professionally photographed, and visually appealing. NOTE : User prompt ')
    def predict(self, accept_ration,image=None, custom_prompt="" ):
        
        count = 0
        while count < 3:
            try:
                count += 1   
                if image is None:
                    model_name ="gemini-2.5-flash-image" #"gemini-3-pro-image-preview"  
                    contents = [self.text_input + custom_prompt ,  accept_ration]
                else:
                    model_name = "gemini-2.5-flash-image"  #"gemini-3-pro-image-preview" 
                    contents = [self.text_input + custom_prompt, image , accept_ration]
                # 2. Make the API Call
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE'],
                    ),
                )
                if not response.candidates:
                    print("Block reason:", response.prompt_feedback)
                    return None
                generated_image = None
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        generated_image = Image.open(BytesIO(part.inline_data.data))
                        break
                if generated_image:
                    return generated_image
                else:
                    print("Model returned text only, no image found in response.")
                    return None
            except Exception as e:
                print(f"Attempt {count} failed: {e}")
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(4 * count) 
                else:
                    time.sleep(1) 
        return None
    
    
    def predict_image_old(self,image=None, custom_prompt=""  , old_image =None ,aspect_ratio=None , image_extra=[]):
        custom_prompt = custom_prompt or ""

        self.text_input = self.text_input or ""
        count = 0
        while count < 5:
            try:
                count += 1   
                if image is None:
                    model_name = "gemini-2.5-flash-image" 
                    contents = [self.text_input + custom_prompt  ]
                elif old_image is not None and image:
                    model_name = "gemini-2.5-flash-image" 
                    contents = [self.text_input + custom_prompt + "Given the pervious genereted image + Change the varient of the saree and make it neat ", image ]
                # 2. Make the API Call
                
                else :
                    contents = [self.text_input + custom_prompt + "Given the pervious genereted image + Change the varient of the saree and make it neat ", image , old_image  ]
                
                if image_extra:
                    contents.append('This is the saree border ,pallu ,body')
                    contents.extend(image_extra)
                contents.append(aspect_ratio)
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    ),
                )
                if not response.candidates:
                    print("Block reason:", response.prompt_feedback)
                    return None
                generated_image = None
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        generated_image = Image.open(BytesIO(part.inline_data.data))
                        break
                if generated_image:
                    return generated_image
                else:
                    print("Model returned text only, no image found in response.")
                    return None
            except Exception as e:
                print(f"Attempt {count} failed: {e}")
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(5 * count) 
                else:
                    time.sleep(1) 
        return None
    
    
    
    def predict_image(self, saree_border=None, saree_body=None, saree_pallu=None, custom_prompt="" , aspect_ratio=None , max_count = 5):
        """
        Generates a saree design image using the Gemini image generation model
        based on optional reference images and a custom text prompt.

        The method constructs a multimodal prompt consisting of:
        - A base textual description (`self.text_input`)
        - An optional custom prompt
        - Optional reference images for saree border, body, and pallu
        - An optional aspect ratio instruction

        The API call is retried up to 3 times in case of transient failures
        (such as rate limiting or resource exhaustion).

        Parameters:
            saree_border (optional):
                Reference image representing the saree border design.
            saree_body (optional):
                Reference image representing the saree body or pleats design.
            saree_pallu (optional):
                Reference image representing the saree pallu design.
            custom_prompt (str, optional):
                Additional textual instructions to guide image generation.
            aspect_ratio (optional):
                Aspect ratio instruction for the generated image.

        Returns:
            tuple:
                (generated_image, uuid_filename) if image generation is successful.
                `generated_image` is a PIL Image object and `uuid_filename` is
                a unique PNG filename.
            None:
                If image generation fails or no image is returned by the model.
        """

        
        count = 0
        while count < max_count:
            try:
                count += 1
                contents = []
                full_prompt = self.saree_text_promnpt + " " + custom_prompt
                contents.append(full_prompt)
                if saree_border:
                    contents.append("Reference image for the Saree Border:")
                    contents.append(saree_border)
                
                if saree_body:
                    contents.append("Reference image for the Saree Body/Pleats:")
                    contents.append(saree_body)
                    
                if saree_pallu:
                    contents.append("Reference image for the Saree Pallu:")
                    contents.append(saree_pallu)
                if aspect_ratio:
                    contents.append(aspect_ratio)
                model_name = "gemini-2.5-flash-image"
                # model_name = "gemini-3-pro-image-preview"

                # --- 2. Make the API Call ---
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )

                if not response.candidates:
                    print("Block reason:", response.prompt_feedback)
                    return None

                generated_image = None
                # iterate through parts to find the image
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        generated_image = Image.open(BytesIO(part.inline_data.data))
                        break
                
                if generated_image:
                    uuid_id  = f'{uuid.uuid4()}.png'
                    
                    return generated_image , uuid_id
                else:
                    print("Model returned text only, no image found in response.")
                    # Optional: Print the text to see what went wrong
                    print(response.candidates[0].content.parts[0].text)
                    return None

            except Exception as e:
                print(f"Attempt {count} failed: {e}")
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(4 ** count) 
                else:
                    time.sleep(1) 
        
        return None

    def regenerate_image(self, saree_border=None, saree_body=None, saree_pallu=None, prompt="" ,currect_prompt="" , previous_saree=None, aspect_ratio=None , max_count = 5):
        """
            Regenerates or refines a saree design image by incorporating previous
            generation context, updated prompts, and optional reference images.

            This method extends the base prompt with:
            - Previous saree generation context
            - A previous prompt and a corrected/current prompt
            - Optional reference images for border, body, pallu, and the previous saree
            - An optional aspect ratio instruction

            The image generation request is retried up to `max_count` times to handle
            temporary API failures such as rate limits or resource exhaustion.

            Parameters:
                saree_border (optional):
                    Reference image representing the saree border design.
                saree_body (optional):
                    Reference image representing the saree body or pleats design.
                saree_pallu (optional):
                    Reference image representing the saree pallu design.
                prompt (str, optional):
                    Prompt describing the previous saree design.
                currect_prompt (str, optional):
                    Updated or corrected prompt for refining the design.
                previous_saree (optional):
                    Reference image of the previously generated saree.
                aspect_ratio (optional):
                    Aspect ratio instruction for the regenerated image.
                max_count (int, optional):
                    Maximum number of retry attempts for image generation.

            Returns:
                tuple:
                    (generated_image, uuid_filename) if regeneration is successful.
                    `generated_image` is a PIL Image object and `uuid_filename` is
                    a unique PNG filename.
                None:
                    If image regeneration fails or no image is returned by the model.
            """

        count = 0
        
        while count < max_count:
            try:
                count += 1
                contents = []
                full_prompt = (self.saree_text_promnpt or "") + " Previous Saree " + (prompt or "") + " Current Prompt " + (currect_prompt or "")
                contents.append(full_prompt)
                if saree_border:
                    contents.append("Reference image for the Saree Border:")
                    contents.append(saree_border)
                
                if saree_body:
                    contents.append("Reference image for the Saree Body/Pleats:")
                    contents.append(saree_body)
                    
                if saree_pallu:
                    contents.append("Reference image for the Saree Pallu:")
                    contents.append(saree_pallu)
                if previous_saree:
                    contents.append("Reference image for the Previous Saree:")
                    contents.append(previous_saree) 
                if aspect_ratio:
                    contents.append(aspect_ratio)
                model_name = "gemini-2.5-flash-image"
                # model_name = "gemini-3-pro-image-preview"

                # --- 2. Make the API Call ---
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )

                if not response.candidates:
                    print("Block reason:", response.prompt_feedback)
                    return None

                generated_image = None
                # iterate through parts to find the image
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        generated_image = Image.open(BytesIO(part.inline_data.data))
                        break
                
                if generated_image:
                    uuid_id  = f'{uuid.uuid4()}.png'
                    
                    return generated_image , uuid_id
                else:
                    print("Model returned text only, no image found in response.")
                    # Optional: Print the text to see what went wrong
                    # print(response.candidates[0].content.parts[0].text)
                    return None

            except Exception as e:
                print(f"Attempt {count} failed: {e}")
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(10 * count) 
                else:
                    time.sleep(1) 
        
        return None
   
    def mock_generation(self , *args):
        print(args)
        img = Image.new("RGB", (512, 512), (0, 0, 0))
        return img , "mock_image.png"
    def predict_vector(self,image):
        response = self.client.models.generate_content(
        model="gemini-2.5-flash-image",
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

      
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([179, 25, 255])

 
        mask = cv2.inRange(hsv, lower_white, upper_white)

       
        mask_inv = cv2.bitwise_not(mask) 

        b, g, r = cv2.split(img_bgr)
        
    
        img_rgba = cv2.merge((b, g, r, mask_inv))

   
        def cv2_to_pil(img_cv):
            return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGRA2RGBA))
        image  = cv2_to_pil(img_rgba)
        def crop_only_img(image):
            bbox = image.getbbox()

            if bbox:   
               
                cropped_image = image.crop(bbox)
         

                return cropped_image
        return crop_only_img(image)


    def get_description_title(self, image_bytes):
        # Convert image to raw bytes
       # <-- raw bytes, do NOT base64 encode
        prompt_text = "You are a fashion metadata extraction model.\n" \
            "Analyze the saree image and return ONLY valid JSON.\n\n" \
            "Extract the following fields:\n" \
            "- title: short 3–6 word saree title\n" \
            "- description: 2–3 sentence description of the saree\n" \
            "- tags:\n" \
            "    - style: e.g. Banarasi, Kanjivaram, Party wear, Traditional, Bridal\n" \
            "    - color: dominant visible colors\n" \
            "    - material: silk, cotton, synthetic, chiffon, organza etc.\n" \
            "    - cultural_origin: region/style like South Indian, North Indian, Bengali, Banarasi, etc.\n\n" \
            "VERY IMPORTANT:\n" \
            "- Do NOT guess unrealistic details.\n" \
            "- Output ONLY strict JSON, no extra text."

        contents = [ types.Part.from_bytes(
        data=image_bytes,
        mime_type='image/jpeg',
      ),prompt_text
                ]
            
        

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",   # or "gemini-1.5-flash"
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT"],
                temperature=0.2,
            ),
        )
  


        if hasattr(response, "text"):
            raw_text = response.text
        elif hasattr(response, "candidates"):
            raw_text = response.candidates[0].content[0].text
        else:
            raw_text = str(response)
 

        if raw_text.strip().startswith("```json"):
            raw_text = raw_text.split("```")[-2].strip()[4:]  # take the content inside the backticks
           
        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError:
            print("Failed to parse JSON. Returning raw text.")
            result = {"error": "Failed to parse JSON", "raw": raw_text}

      
        return result
if __name__ =="__main__":
    genereator = GenerateComplete()
    img = Image.open('C:/sareefusion/sareeFusion/backend/Genereating/6f4507a5513147ed91fa8826b28597e55b36191d14bf47a894e5c217bdd7db106f4507a5513147ed91fa8826b28597e51.png')

    result =  genereator.get_description_title(img)
    print(result.get("title"))
