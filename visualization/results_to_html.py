from utils.app_types import RetrievalResult
from typing import List

def results_to_html_dict(results: List[RetrievalResult]) -> list[dict]:
    """
    Convert the results to a list of dictionaries for HTML rendering
    """
    results_list = []
    for result in results:
        path = str(result.max_item_by_concentrate[0].asset_path)
        path = "static/" + path.split("static")[-1].replace("\\", "/")
        # keep 1 decimal places for the similarity score
        score = "{:.1f}%".format(result.score * 100)
        results_list.append({
            'name': result.name,
            'similarity': score,
            'image_path': path,
            'web_url': result.url,
            'entry': result.max_entry_by_concentrate[0],
        })
    return results_list