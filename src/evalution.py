'''
Purpose: helper functions to evaluate pairs and some statistics
'''

from time import time
from tqdm import tqdm
import pandas as pd
from litellm import completion
from src.llm import ModelEvaluator

def predict(subset: pd.DataFrame, model_evaluator: ModelEvaluator):
    results_list = []
    for idx, row in tqdm(subset.iterrows(), total=len(subset), desc='Processing'):
        try:
            start = time()
            q = str(row.get('query', ''))
            title = str(row.get('product_title', ''))
            desc = str(row.get('product_description', ''))
            brand = str(row.get('product_brand', ''))
            bullets = str(row.get('product_bullet_point', ''))
            solution = model_evaluator.evaluate_pair(q, title, desc, brand, bullets)
            elapsed_time = time() - start
            record = {
                'example_id': row['example_id'],
                'original_label': row['esci_label'],
                'query': q, 'title': title, 'brand': brand, 'bullet': bullets, 
                'query_features': solution.query_features,
                'product_features': solution.product_features,
                'conflict_found': solution.conflict_found,
                'reasoning': solution.reasoning,
                'acceptable': solution.acceptable,
                'reformulated_query': solution.reformulated_query,
                'latency_sec': round(elapsed_time, 2),
                'error': None
            }
            results_list.append(record)
        except Exception as e:
            record = {
                'example_id': row['example_id'],
                'query_id': row['query_id'],
                'product_id': row['product_id'],
                'original_label': row['esci_label'],
                'query': q,
                'title': title,
                'brand': brand,
                'bullets': bullets,
                'query_features': None,
                'product_features': None,
                'conflict_found': None,
                'reasoning': None,
                'acceptable': None,
                'reformulated_query': None,
                'latency_sec': None,
                'error': str(e)
            }
            results_list.append(record)