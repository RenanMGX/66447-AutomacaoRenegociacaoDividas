from openai import OpenAI
from typing import Literal


class ChatGptIa:
    def __init__(self, *, 
                 token:str,
                 temperature:float = 0.5, 
                 model:Literal['gpt-3.5-turbo', 'gpt-3.5-turbo-0125', 'gpt-4o'] = 'gpt-3.5-turbo',
                 instructions:str = "voce é um assistente virual prestavito e educado!",
                 ) -> None:
        
        self.temperature = temperature
        self.model = model
        self.instructions = instructions
        
        
        self.client = OpenAI(
            api_key=token,
        )
        
    
    def perguntar(self, pergunta:str):
        response = self.client.responses.create(
            temperature=self.temperature,
            model=self.model,
            instructions=self.instructions,
            input=pergunta,
        )
        return response.output_text
    
if __name__ == "__main__":
    with open("token_gpt.txt", "r") as _file:
        api_token = _file.read().strip()
    
    ia = ChatGptIa(token=api_token)
    
    print(ia.perguntar("Qual é o seu nome?"))