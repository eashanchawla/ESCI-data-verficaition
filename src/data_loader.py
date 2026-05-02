'''
Purpose: handle interactions with the parquet files 
'''
import pandas as pd
from typing import Tuple, Iterable
from pathlib import Path

def load_raw_data(data_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_examples = pd.read_parquet(Path(data_dir) / 'shopping_queries_dataset_examples.parquet')
    df_products = pd.read_parquet(Path(data_dir) / 'shopping_queries_dataset_products.parquet')
    return df_examples, df_products


def random_sample():
    return NotImplementedError

def get_evaluation_dataset(df_examples: pd.DataFrame, df_products: pd.DataFrame, target_queries: Iterable[str] | None=None) -> pd.DataFrame:
    df_merged = pd.merge(
        df_examples, df_products, how='left', on=['product_locale', 'product_id']
    )
    return df_merged.copy() if not target_queries else df_merged[df_merged['query'].isin(target_queries)].copy()
