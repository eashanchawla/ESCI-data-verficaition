from litellm import completion
from src.schemas.response_schema import MyResponse
from src.prompts import EVALUATION_PROMPT
import json

class ModelEvaluator:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.system_prompt = EVALUATION_PROMPT
    
    def evaluate_pair(self, query: str, title: str, desc: str, brand: str, bullets: str) -> dict:
        user_prompt = f'''Query:{query}\nProduct Information:\n\tTitle: {title}\n\tDescription:{desc}\n\tBrand: {brand}\n\tBullets: {bullets}'''
        response = completion(
            model='ollama/gemma3:4b',
            messages=[
                {"role": "system", "content": EVALUATION_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            api_base='http://localhost:11434',
            response_format=MyResponse
        )
        solution = MyResponse.model_validate_json(response['choices'][0]['message'].content)
        return solution