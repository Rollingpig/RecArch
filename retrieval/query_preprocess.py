from utils.app_types import EnrichedQuery
from utils.llm import call_gpt_v
from pathlib import Path
import logging
from retrying import retry


def enrich_query(raw_query: str) -> EnrichedQuery:
    """
    Enrich the query
    """
    return EnrichedQuery(raw_query, 
                         [(['text', 'facade', 'interior', 'floorplan', 
                            'section', 'detail', 'birdview', 'other'], 
                            [raw_query])])

@retry(wait_fixed=5000, stop_max_attempt_number=3)
def query_preprocess(query: str) -> EnrichedQuery:
    """
    Handle the query
    """
    # check if the query is a file path to an image
    if Path(query).exists():
        logging.info("Query recognized as an image file path")

        # get the text description of the image
        query_str = call_gpt_v(query, "Describe in detail about this architecture design, specifying the form, function, material and context.")
        
        # if the response is an empty dictionary, raise an error
        if not query_str:
            raise ValueError("We cannot find the file")
    else:
        logging.info("Query recognized as a text")
        query_str = query

    # enrich the query
    enriched_query = enrich_query(query_str)

    return enriched_query