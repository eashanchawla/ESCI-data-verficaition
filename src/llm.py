'''
Purpose: interaction layer with LLMs
'''

from litellm import completion
from src.schemas.response_schema import MyResponse
from src.prompts import EVALUATION_PROMPT

class ModelEvaluator:
    def __init__(self, model_name: str='ollama/gemma3:4b', system_prompt: str=EVALUATION_PROMPT, temperature: float=0.1, response_schema=MyResponse):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.response_schema = response_schema
    
    def evaluate_pair(self, query: str, title: str, desc: str, brand: str, bullets: str) -> dict:
        user_prompt = f'''Query:{query}\nProduct Information:\n\tTitle: {title}\n\tDescription:{desc}\n\tBrand: {brand}\n\tBullets: {bullets}'''
        response = completion(
            model=self.model_name,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            api_base='http://localhost:11434',
            response_format=self.response_schema
        )
        solution = self.response_schema.model_validate_json(response['choices'][0]['message'].content)
        return solution

    # def second_pass(self, )