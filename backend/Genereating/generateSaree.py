from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import numpy as np
import PIL.Image
import os
from dotenv import load_dotenv
load_dotenv()

class GenerateComplete:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        self.text_input = ('This image is a saree template. Based on this template,Keep the border as in image and match the colors if needed, generate a realistic 4K image of the saree draped on a mannequin , Keep the templete border , body and pallu as given in twmplete. The image should be clean, neat, professionally photographed, and visually appealing.')
#text_input = ("This image is a saree template , convert this into high carity flat vector image and make sure that all the pattern adn details are visible")
    def predict(self,image):
        response = self.client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=[self.text_input, image],
        config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
        ))    
        image = Image.open(BytesIO(response.candidates[0].content.parts[1].inline_data.data))
        return image
        
if __name__ =="__main__":
    genereator = GenerateComplete()
    img = Image.open('backend/Genereating/final_saree.png')
    result_img = genereator.predict(img)
    result_img.save('backend/Genereating/generated.png')  # Save the generated image
    