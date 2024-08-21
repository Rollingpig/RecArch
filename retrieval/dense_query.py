from utils.app_types import CaseDatabase, EnrichedQuery, RetrievalResult, RawTextItem
from typing import List
import numpy as np
from utils.llm import LLMHandler

def dense_query(database: CaseDatabase, 
                query: EnrichedQuery,
                text_only: bool = False,
                **kwargs
                ) -> List[RetrievalResult]:
    """
    Query the database, return unsorted retrieval results
    """
    retrieval_results = []
    llm_handler = LLMHandler()

    category_focus_list = query.asset_filter
    query_embs = llm_handler.get_text_embeddings(query.content)
    np_query_embs = np.array(query_embs)  # shape: (emb_dim, )

    for _, case_item in database.cases.items():
        mask = case_item.get_emb_mask(category_focus_list, text_only) # shape: (entry_count, )
        masked_embs = case_item.embeddings[mask]  # shape: (entry_count, emb_dim)
        dot_product = np.dot(masked_embs, np_query_embs.T)  # shape: (entry_count,)

        # concatenate the similarities
        max_dot_product = np.max(dot_product)
        max_item_idx = np.argmax(dot_product)
        max_item, max_entry = case_item.look_up_content(max_item_idx)
        if isinstance(max_item, RawTextItem) or ("txt" in str(max_item.asset_path)):
            # use any image item for visualization
            for item in case_item.content:
                if "txt" not in str(item.asset_path):
                    max_item = item
                    break
        retrieval_results.append(
            RetrievalResult(case_item.case_id, case_item.name, max_dot_product, 
                            case_item.web_link,
                            max_entry, max_item))
                
    return retrieval_results
    










