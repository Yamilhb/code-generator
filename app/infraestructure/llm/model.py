from openai import OpenAI
from app.infraestructure.file_utils.utils import image_code
import os
import logging

#OPENAI_MODEL = os.getenv("OPENAI_MODEL")
logger = logging.getLogger(__name__)

class IA():
    def __init__(self, key, modelo):
        self.key=key
        self.modelo = modelo
        self.client = OpenAI(api_key=self.key)

    def chat(self,prompt,sys_promt=None,image_file=None,temperature=0):
        logger.info("Calling llm")
        model = self.modelo
        if image_file:
            b64_image = image_code(image_file)

            message = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url":f"data:image/jpeg;base64,{b64_image}"}}
                    ]
                }
            ]
        else:
            message = [
                {"role":"user", "content":prompt}
            ]
        if sys_promt:
            message.insert(
                0,
                {"role":"system","content":sys_promt}
            )
        try:
            response = self.client.chat.completions.create(
                model = model,
                messages = message,
                temperature=temperature
            )
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            response = response.choices[0].message.content
            logger.info("Exit llm")
            return response, prompt_tokens, completion_tokens
        except Exception as e:
            logger.exception(f"Error in llm: {e}")
            return f"Error in llm: {e}", 0, 0
