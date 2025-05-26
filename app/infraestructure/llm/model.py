from openai import OpenAI

class IA():
    def __init__(self, key):
        self.key=key
        self.client = OpenAI(api_key=self.key)

    def chat(self,prompt,sys_promt=None,model="gpt-4.1-nano",temperature=0):
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
            response = response.choices[0].message.content
            return response
        except Exception as e:
            return f"Error in chat: {e}"
