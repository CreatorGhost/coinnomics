from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()




promt = "Generate an image of a beautiful American-style news anchor with an Indian twist. She should be dressed in a contemporary fusion outfit that blends a modern Western business attire with elegant Indian design accents. Think of a tailored blazer with intricate Indian embroidery or a sleek dress with a sari-inspired drape. Her hair and makeup should be polished and professional, with a hint of vibrant Indian color. The backdrop is a high-tech newsroom with advanced broadcasting equipment. The anchor should exude charisma, intelligence, and a global appeal, reflecting a blend of cultures in a futuristic setting."


def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    return response.data[0].url

image_url = generate_image(promt)
print(image_url)
