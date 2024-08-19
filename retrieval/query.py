from retrieval.dense_query import dense_query
from retrieval.query_preprocess import query_preprocess
from utils.app_types import CaseDatabase, DesignCase, RetrievalResult
from pathlib import Path
import pickle
from collections import OrderedDict
import logging
from typing import List


def load_database(database_folder_path: str) -> CaseDatabase:
    """
    Load the database
    """
    # load all pkl files from the database folder
    database_cases = OrderedDict()
    case_idx = 0
    for pkl_file in Path(database_folder_path).glob("*.pkl"):
        try:
            with open(pkl_file, "rb") as f:
                case = pickle.load(f)
                database_cases[case_idx] = case
                case_idx += 1
        except Exception as e:
            logging.error(f"Error loading {pkl_file}: {e}")
    return CaseDatabase(database_cases)


def query_handler(query: str, database_folder_path: str) -> List[RetrievalResult]:
    """
    Handle the query
    """
    # preprocess the query
    enriched_query = query_preprocess(query)

    # load all pkl files from the database folder
    database = load_database(database_folder_path)

    # query the database
    retrieval_results = dense_query(database, enriched_query)

    # return the results
    return retrieval_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # test the query handler
    query = "White finish"
    database_folder_path = "static/database2"
    result = query_handler(query, database_folder_path)
    print(result[:3])