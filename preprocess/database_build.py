from pathlib import Path
import logging
import json
import pickle

from preprocess.case_inquiry import case_inquiry
from preprocess.case_embedding import create_embs
from utils.app_types import CaseDatabase

def project_folder_iterate(database_folder_path):
    """
    Iterate all project folder in the database folder
    """
    for country_folder in Path(database_folder_path).iterdir():
        # if the item is a folder
        if country_folder.is_dir():
            # iterate all folders in the country folder
            for project_folder in country_folder.iterdir():
                # if the item is a folder
                if project_folder.is_dir():
                    yield project_folder


def build_database(source_folder_path: str, 
                   target_folder_path: str,
                   overwrite=False
                   )-> CaseDatabase:
    # create the target folder if not exists
    target_folder_path = Path(target_folder_path)
    if not target_folder_path.exists():
        target_folder_path.mkdir(parents=True, exist_ok=True)

    idx = 0
    cases = []
    for project_folder in project_folder_iterate(source_folder_path):
        case_json_path = target_folder_path / f"case_{idx}.json"
        case_pkl_path = target_folder_path / f"case_{idx}.pkl"

        # skip if the case json exists
        if case_json_path.exists() and not overwrite:
            logging.info(f"Skipping {project_folder}")
            idx += 1
            continue

        # build the case
        logging.info(f"Building for {project_folder}")
        case = case_inquiry(idx, project_folder)
        case = create_embs(case)

        # save the case to json
        with open(case_json_path, "w") as f:
            json.dump(case.to_dict(), f, indent=2)

        # save the case to pkl
        with open(case_pkl_path, "wb") as f:
            pickle.dump(case, f, protocol=pickle.HIGHEST_PROTOCOL)

        # append the case to the list
        cases.append(case)

        # increment the index
        idx += 1

    # create the database
    return CaseDatabase(cases)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_database(r"D:\Code\RecArch\static\database", 
                   r"D:\Code\RecArch\static\indexing")