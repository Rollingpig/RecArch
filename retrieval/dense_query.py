from utils.app_types import CaseDatabase, EnrichedQuery, RetrievalResult
from typing import List
import numpy as np
from utils.llm import LLMHandler

def dense_query(database: CaseDatabase, 
                query: EnrichedQuery,
                text_only: bool = False,
                **kwargs
                ) -> List[RetrievalResult]:
    """
    Query the database
    """
    retrieval_results = []
    llm_handler = LLMHandler()

    query_settings_list = []
    for _, concentrate in enumerate(query.concentrate):
        category_focus_list, query_list = concentrate
        query_embs = llm_handler.get_text_embeddings_multi(query_list)
        query_settings_list.append((query_embs, category_focus_list, text_only))

    for _, case_item in database.cases.items():

        # unpack the query settings
        similarities = []
        for setting in query_settings_list:
            query_embs, category_focus_list, text_only = setting
            mask = case_item.get_emb_mask(category_focus_list, text_only)
            masked_embs = case_item.embeddings[mask]
            np_query_embs = np.array(query_embs)
            similarity = np.dot(masked_embs, np_query_embs.T)  # shape: (entry_count, query_count)
            similarities.append(similarity)

        # concatenate the similarities
        dot_product = np.concatenate(similarities, axis=1)
        max_dot_product = np.max(dot_product)
        max_item_idx = np.argmax(dot_product)
        max_item, max_entry = case_item.look_up_content(max_item_idx)
        retrieval_results.append(
            RetrievalResult(case_item.case_id, case_item.name, max_dot_product, 
                            case_item.web_link,
                            [max_dot_product], [max_entry], [max_item]))
                

    # rank the retrieval results using the score
    retrieval_results = sorted(retrieval_results, key=lambda x: x.score, reverse=True)
    return retrieval_results
    










