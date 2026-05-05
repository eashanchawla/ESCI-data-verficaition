'''
Purpose: helper functions to evaluate pairs and some statistics
'''

from time import time
from pathlib import Path
from tqdm import tqdm
from src.llm import ModelEvaluator
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import pandas as pd

def predict(subset: pd.DataFrame, model_evaluator: ModelEvaluator) -> pd.DataFrame:
    '''
    Loop through dataframe passing through current iteration of ModelEvaluator prompt
    
    Args:
        subset: current dataframe to iterate through and pass through LLM
        model_evaluator: initialized model with a system prompt and settings

    Returns:
        Dataframe that has the outputs from the LLM runs
    '''
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
    return pd.DataFrame(results_list)

def run_experiment(df: pd.DataFrame, evaluator: ModelEvaluator, run_name: str | Path) -> pd.DataFrame:
    '''
    Wrapper around predict, could help with logging if I get time for it
    
    Args:
        run_name: saves run_name.csv in the /data/processed file
        df: dataframe to pass through the LLM
        evaluator: current model setup with initialized system prompt and other settings
    
    Returns:
        df with results from the LLM
    '''
    save_path = Path(f'../data/processed/{run_name}.csv') #TODO: maybe extract this out to the config so I don't have to maintain brittle paths
    results = predict(df, evaluator)
    results.to_csv(save_path, index=False)
    # logging.info()
    return results

def score_against_human(merged_df: pd.DataFrame) -> None:
    '''
    Generate a report of metrics on how the model performs against human labels. Assumes that merged df contains human labels'''
    #TODO: I want to make this better and also return query level performance? 
    clean_data = merged_df.dropna(subset=['Conflict_Found_GT', 'conflict_found'])
    print(classification_report(clean_data['Conflict_Found_GT'].astype(bool), clean_data['conflict_found'].astype(bool), target_names=["No Conflict", "Conflict"]))
    cm = confusion_matrix(clean_data['Conflict_Found_GT'].astype(bool), clean_data['conflict_found'].astype(bool))
    ConfusionMatrixDisplay(cm, display_labels=["No Conflict", "Conflict"]).plot()
    plt.show()

DISPLAY_COLS = ["query", "title", "human_label", "Conflict_Found_GT", 
                "conflict_found", "reasoning", "reformulated_query"]

# Written by AI completely
def show(df, n=None):
    """Tight, presentation-friendly view."""
    view = df[DISPLAY_COLS] if n is None else df[DISPLAY_COLS].head(n)
    return view.style.set_properties(**{
        'text-align': 'left',
        'white-space': 'pre-wrap',
        'max-width': '400px',
    })
