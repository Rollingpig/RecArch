from retrieval.dense_query import dense_query
from retrieval.query_preprocess import query_preprocess
from utils.app_types import CaseDatabase, QuerySet, RetrievalResult
from pathlib import Path
import pickle
from collections import OrderedDict
import logging
from typing import List, Tuple, Union
import numpy as np


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

def fusion_query(database: CaseDatabase, 
                query_set: QuerySet,
                random: bool = False,
                **kwargs
                ) -> List[RetrievalResult]:
    if random:
        result_list = [RetrievalResult(case_id, case.name, 0, case.web_link, "None", case.content[0]) for case_id, case in database.cases.items()]
        np.random.shuffle(result_list)
        return result_list
    else:
        result_list = [dense_query(database, query, **kwargs) for query in query_set.queries]

        # extract all scores from all results
        all_scores = [np.array([item.score for item in result]) for result in result_list]
        all_scores = np.concatenate(all_scores).reshape(len(result_list), -1) # shape: (query_count, result_count)
        # calculate the weighted sum of all scores using the weights
        weights = query_set.weights  # shape: (query_count, )
        weighted_scores = np.dot(all_scores.T, weights)  # shape: (result_count, )

        # select the result with the highest weights as the base result
        query_index_with_max_weight = np.argmax(query_set.weights)
        base_result = result_list[query_index_with_max_weight]

        # apply the weighted sum to the base result
        for i, result in enumerate(base_result):
            result.score = weighted_scores[i]

        # sort the base result
        base_result.sort(key=lambda x: x.score, reverse=True)
        return base_result
        

def query_handler(query: Union[str, QuerySet], database_folder_path: str
                  ) -> Tuple[List[RetrievalResult], QuerySet]:
    """
    Handle the query, return the retrieval results and the query set
    """
    # preprocess the query
    if isinstance(query, QuerySet):
        query_set = query
    else:
        query_set = query_preprocess(query)
        logging.info(f"Query set: {query_set}")

    # load all pkl files from the database folder
    database = load_database(database_folder_path)

    # query the database
    retrieval_results = fusion_query(database, query_set)

    # return the results
    return retrieval_results, query_set


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # test the query handler
    query = "White finish"
    database_folder_path = "static/indexing"
    result = query_handler(query, database_folder_path)
    print(result[:3])