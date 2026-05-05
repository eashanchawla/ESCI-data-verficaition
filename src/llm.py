'''
Purpose: interaction layer with LLMs
'''

from litellm import completion
from src.schemas.response_schema import MyResponse
from src.prompts import EVALUATION_PROMPT

class ModelEvaluator:
    def __init__(self, model_name: str='ollama/gemma3:4b', system_prompt: str=EVALUATION_PROMPT, temperature: float=0.1, response_schema=MyResponse, num_retries: int=3, timeout: int=45):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.response_schema = response_schema
        self.timeout = timeout
        self.num_retries = num_retries
    
    def evaluate_pair(self, query: str, product_info: str) -> dict:
        user_prompt = f'''Query:{query}\nProduct Information:{product_info}'''
        kwargs = {
            "model":self.model_name,
            "temperature":self.temperature,
            "messages":[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format":self.response_schema, "num_retries":self.num_retries, "timeout":self.timeout
        }
        if self.model_name.startswith("ollama"):
            kwargs["api_base"]= 'http://localhost:11434' #TODO: I can use a **kwargs pattern here to avoid passing this and make this even more flexible to using any provider

        response = completion(**kwargs)
        solution = self.response_schema.model_validate_json(response['choices'][0]['message'].content)
        return solution

    # def second_pass(self, )