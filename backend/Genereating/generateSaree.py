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

class GenerateComplete:
    def __init__(self) -> None:
        self.__PROJECT_ID__ = 'sareefusion'
        self.__LOCATION__ = 'global'
        # genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        # self.client = genai # The module itself (genai) often acts as the client
        self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        #self.client = genai.Client(vertexai=True,api_key="AQ.Ab8RN6IAA1lIMEZ3etPZxiR4RKAj_niNMgK9rhlqdzNDbTvkpA" )
        self.text_input = ('This image is a saree template. Based on this template,Keep the border as in image and match the colors if needed, generate a realistic 4K image of the saree draped on a mannequin , Keep the templete border , body and pallu as given in twmplete. The image should be clean, neat, professionally photographed, and visually appealing. NOTE : User prompt ')
        self.text_vector_input = ("Convert the image into flat vector graphic style preserve the pattern and perserv the details")
    def predict(self,image=None , custom_prompt=""):
        if image is None:
            response = self.client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
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
if __name__ =="__main__":
    genereator = GenerateComplete()
    img = Image.open('C:/sareefusion/sareeFusion/backend/Genereating/border_rotated ch11.png')
    result_img = genereator.predict_vector(img)
    result_img.save('C:/sareefusion/sareeFusion/backend/Genereating/generated_vector.png')  # Save the generated image
    