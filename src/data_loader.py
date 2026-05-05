'''
Purpose: handle interactions with the parquet files 
'''
import pandas as pd
from typing import Tuple, Iterable
from pathlib import Path

TARGET_QUERIES = [
    "aa batteries 100 pack",
    "kodak photo paper 8.5 x 11 glossy",
    "dewalt 8v max cordless screwdriver kit, gyroscopic",
]

def load_raw_data(data_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_examples = pd.read_parquet(Path(data_dir) / 'shopping_queries_dataset_examples.parquet')
    df_products = pd.read_parquet(Path(data_dir) / 'shopping_queries_dataset_products.parquet')
    return df_examples, df_products

def merge_examples_products(df_examples: pd.DataFrame, df_products: pd.DataFrame) -> pd.DataFrame:
    df_merged = pd.merge(
        df_examples, df_products, how='left', on=['product_locale', 'product_id']
    )
    return df_merged

def get_evaluation_dataset(df_examples: pd.DataFrame, df_products: pd.DataFrame, target_queries: Iterable[str] | None=None) -> pd.DataFrame:
    df_merged = pd.merge(
        df_examples, df_products, how='left', on=['product_locale', 'product_id']
    )
    return df_merged.copy() if not target_queries else df_merged[df_merged['query'].isin(target_queries)].copy()

def filter_dataset(df: pd.DataFrame, queries: Iterable[str]=TARGET_QUERIES, esci_label: str='E') -> pd.DataFrame:
    df_filtered = df[
        (df["query"].isin(queries)) & (df["esci_label"] == esci_label)
    ].copy()
    return df_filtered

