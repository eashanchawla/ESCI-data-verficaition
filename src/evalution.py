'''
Purpose: helper functions to evaluate pairs and some statistics
'''

import time
from pathlib import Path
from tqdm import tqdm
from src.llm import ModelEvaluator
from src.data_loader import build_product_context
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import pandas as pd
import json

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
            start = time.time()
            q = str(row.get('query', ''))
            title = str(row.get('product_title', ''))
            desc = str(row.get('product_description', ''))
            brand = str(row.get('product_brand', ''))
            bullets = str(row.get('product_bullet_point', ''))
            solution = model_evaluator.evaluate_pair(q, build_product_context(row))
            elapsed_time = time.time() - start
            record = {
                'example_id': row['example_id'],
                'original_label': row['esci_label'],
                'query': q, 'title': title, 'brand': brand, 'bullet': bullets, 
                'latency_sec': round(elapsed_time, 2),
                'error': None
            }
            record.update(solution.model_dump())
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
                'latency_sec': None,
                'error': str(e)
            }
            null_schema = {field: None for field in model_evaluator.response_schema.model_fields}
            record.update(null_schema)
            results_list.append(record)
    return pd.DataFrame(results_list)

def needs_second_pass(row: pd.Series) -> bool:
    '''Check if this row needs a second pass or not'''
    alignment = row.get('feature_alignment')
    if not alignment:
        return False
    items = json.loads(alignment) if isinstance(alignment, str) else alignment
    return any(a.get('status') == 'contradiction' for a in items)

def run_two_pass(df: pd.DataFrame, evaluator1: ModelEvaluator, evaluator2: ModelEvaluator, run_name: str | Path) -> pd.DataFrame:
    save_path = Path(f'../data/processed/{run_name}.csv') #TODO: maybe extract this out to the config so I don't have to maintain brittle paths

    pass1_results = predict(df, evaluator1)
    contradiction = pass1_results.apply(needs_second_pass, axis=1)
    pass1_results['reasoning'] = None
    pass1_results['conflict_found'] = None
    pass1_results['reformulated_query'] = None

    pass1_results.loc[~contradiction, 'conflict_found'] = False
    pass1_results.loc[~contradiction, 'reasoning'] = 'No contradictions found'

    pass2_candidates = pass1_results[contradiction]
    if len(pass2_candidates) > 0:
        for idx, row in tqdm(pass2_candidates.iterrows(), total=len(pass2_candidates), desc='Pass 2'):
            alignment = row['feature_alignment']
            items = json.loads(alignment) if isinstance(alignment, str) else alignment
            
            try:
                judgment = evaluator2.evaluate_alignment(row['query'], items)
                pass1_results.at[idx, 'conflict_found'] = judgment.conflict_found
                pass1_results.at[idx, 'reasoning'] = judgment.reasoning
                pass1_results.at[idx, 'reformulated_query'] = judgment.reformulated_query
            except Exception as e:
                pass1_results.at[idx, 'conflict_found'] = None
                pass1_results.at[idx, 'reasoning'] = f'ERROR: {str(e)}'
    #TODO: Save file with run name like in run_experiment
    pass1_results.to_csv(save_path, index=False)
    return pass1_results

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

DISPLAY_COLS = ["example_id", "query", "title", "human_label", "Conflict_Found_GT", 
                "conflict_found", "reasoning", "reformulated_query", "error"]

# Written by AI completely
def show(df, display_cols=DISPLAY_COLS, n=None):
    """Tight, presentation-friendly view."""
    view = df[display_cols] if n is None else df[display_cols].head(n)
    return view.style.set_properties(**{
        'text-align': 'left',
        'white-space': 'pre-wrap',
        'max-width': '400px',
    })
