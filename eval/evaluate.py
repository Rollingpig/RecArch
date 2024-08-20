from retrieval.query import fusion_query
from retrieval.query_preprocess import query_preprocess
import logging
from retrieval.query import load_database
import numpy as np

def read_labels(label_file_path: str):
    """
    Read the labels from the file
    """
    with open(label_file_path, "r") as file:
        lines = file.readlines()
        queries = [line.split(",")[0] for line in lines]
        labels = [line.split(",")[1:] for line in lines]
        labels = [[int(label) for label in group] for group in labels]
    return queries, labels

def read_results(result_file_path: str):
    """
    Read the results from the file
    """
    with open(result_file_path, "r") as file:
        lines = file.readlines()
        retrieve_results = [line.split(",")[1:] for line in lines]
        retrieve_results = [[int(result) for result in group] for group in retrieve_results]
    return retrieve_results


def run_system(label_file_path: str, 
               database_folder_path: str,
               result_file_path: str,
               config: dict = None,
               ):

    # read the labels
    queries, labels = read_labels(label_file_path)

    # load all pkl files from the database folder
    database = load_database(database_folder_path)

    # iterate over the queries
    retrieve_results = []
    for query, gt_ids in zip(queries, labels):
        enriched_query = query_preprocess(query)
        retrieval_results = fusion_query(database, enriched_query, **config)
        retrieved_ids = [result.case_id for result in retrieval_results]
        retrieve_results.append(retrieved_ids)

    # save the results
    with open(result_file_path, "w") as file:
        for query, results in zip(queries, retrieve_results):
            file.write(f"{query},{','.join([str(result) for result in results])}\n")

    return retrieve_results

def recall(label_file_path: str, result_path: str):
    queries, labels = read_labels(label_file_path)
    retrieve_results = read_results(result_path)

    recall = np.zeros((len(queries), 4))
    for idx, gt_ids in enumerate(labels):
        # calculate the recall at 1, 5, 10, 20
        recall_1 = len(set(gt_ids) & set(retrieve_results[idx][:1])) / len(gt_ids)
        recall_5 = len(set(gt_ids) & set(retrieve_results[idx][:5])) / len(gt_ids)
        recall_10 = len(set(gt_ids) & set(retrieve_results[idx][:10])) / len(gt_ids)
        recall_20 = len(set(gt_ids) & set(retrieve_results[idx][:20])) / len(gt_ids)
        recall[idx] = [recall_1, recall_5, recall_10, recall_20]

    return recall


def precision(label_file_path: str, result_path: str):
    queries, labels = read_labels(label_file_path)
    retrieve_results = read_results(result_path)

    precision = np.zeros((len(queries), 4))
    for idx, gt_ids in enumerate(labels):
        # calculate the precision at 1, 5, 10, 20
        precision_1 = len(set(gt_ids) & set(retrieve_results[idx][:1])) / 1
        precision_5 = len(set(gt_ids) & set(retrieve_results[idx][:5])) / 5
        precision_10 = len(set(gt_ids) & set(retrieve_results[idx][:10])) / 10
        precision_20 = len(set(gt_ids) & set(retrieve_results[idx][:20])) / 20
        precision[idx] = [precision_1, precision_5, precision_10, precision_20]

    return precision



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    label_file_path = "eval/example.csv"
    database_folder_path = "static/indexing"
    result_file_path = "eval/results.csv"
    
    result_text_only_file_path = "eval/results_text_only.csv"

    result_random_file_path = "eval/results_random.csv"
    run_system(label_file_path, database_folder_path, result_random_file_path,
               {"text_only": True, "random": True})

