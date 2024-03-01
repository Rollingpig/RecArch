import argparse

from pathlib import Path
import json
import pickle

from model_call import ask_gpt_text, ask_gpt_v, get_text_embeddings


prompt_birdview = """
Based on the image, fill the following JSON questionaire about architecture design:
```json
{
    "highlights": "What is the highlight of this design?",
    "shape": "What form does it use? ",
    "spatial design": "What is the highlight of its shape and form? ",
    "material design": "What is the highlight in its spatial and material design?",
    "keywords": "Summarize some keywords, split by comma",
}
```
"""
prompt_exterior = prompt_birdview
prompt_interior = prompt_birdview
prompt_floorplan = """
Based on the image, fill the following JSON questionaire about architecture design:
```json
{
    "highlights": "What is the highlight of this design?",
    "shape": "What form does it use? ",
    "spatial design": "What is the highlight of its shape and form? ",
    "keywords": "Summarize some keywords, split by comma",
}
```
"""
prompt_other = prompt_birdview

prompt_description = """
Based on the text, fill the following JSON questionaire about architecture design:
```json
{
    "highlights": "What is the highlight of this design?",
    "shape": "What form does it use? ",
    "spatial design": "What is the highlight of its shape and form? ",
    "material design": "What is the highlight in its spatial and material design?",
    "keywords": "Summarize some keywords, split by comma",
}
```
"""

def build_json_for_one_project(project_folder_path, overwrite=False):
    """
    Build the JSON for one design project and save it to a json file.
    """
    # if the json file already exists and overwrite is False
    if not overwrite and (Path(project_folder_path) / "gpt_raw_result.json").exists():
        print(f"JSON already exists for {project_folder_path}")
        return None

    result_json = {}

    # get the text file path
    text_path = Path(project_folder_path) / "description.txt"
    if text_path.exists():
        # read the text file using utf-8 encoding
        text = text_path.read_text(encoding="utf-8")

        # ask the GPT-4 API
        json_response = ask_gpt_text(prompt_description, text)

        # add the json response to the result
        result_json["description"] = json_response
    else:
        print(f"Text file not found for {project_folder_path}")

    # iterate all jpg files in the folder
    for image_path in Path(project_folder_path).glob("*.jpg"):
        # get the image name
        image_name = image_path.stem

        # get the image path
        image_path = str(image_path)

        # assign the prompt based on the image name
        if "birdview" in image_name:
            prompt = prompt_birdview
        elif "facade" or "exterior" in image_name:
            prompt = prompt_exterior
        elif "interior" in image_name:
            prompt = prompt_interior
        elif "floorplan" in image_name:
            prompt = prompt_floorplan
        else:
            prompt = prompt_other

        # ask the GPT-4 Vision API
        json_response = ask_gpt_v(image_path, prompt)

        # add the json response to the result
        result_json[image_name.split(".jpg")[0]] = json_response

    # save the result to a json file
    result_json_path = Path(project_folder_path) / "gpt_raw_result.json"
    result_json_path.write_text(json.dumps(result_json, indent=4))


def build_embeddings_for_one_project(project_folder_path):
    """
    Build the embeddings for the project description and save them to a pickle file
    dict structure:
    {
        "description": {
            "highlights": (embeddings),
            "shape": (embeddings).
            ...
        },
        "exterior": {
            "highlights": (embeddings),
            ...
        },
        ...
    }
    """
    # if the pickle file already exists, return None
    if (Path(project_folder_path) / "gpt_embeddings.pkl").exists():
        print(f"Embeddings already exists for {project_folder_path}")
        return None
    
    # read gpt_raw_result.json
    gpt_json_path = Path(project_folder_path) / "gpt_raw_result.json"
    gpt_json = json.loads(gpt_json_path.read_text())

    embedding_dict = {}

    # iterate all keys in the json
    for key in gpt_json:
        embedding_dict[key] = {}
        # iterate all subkeys in the json
        for subkey in gpt_json[key]:
            text = gpt_json[key][subkey]
            embeddings = get_text_embeddings(text)
            embedding_dict[key][subkey] = embeddings

    # get the embeddings of the raw description
    text_path = Path(project_folder_path) / "description.txt"
    text = text_path.read_text(encoding="utf-8")
    embeddings = get_text_embeddings(text)
    embedding_dict["description_full_text"] = embeddings

    # save the result using pickle
    embedding_dict_path = Path(project_folder_path) / "gpt_embeddings.pkl"
    with open(embedding_dict_path, "wb") as f:
        pickle.dump(embedding_dict, f)

def project_folder_iterate(project_folder_path):
    """
    Iterate all project folder in the database folder
    """
    for country_folder in Path(project_folder_path).iterdir():
        # if the item is a folder
        if country_folder.is_dir():
            # iterate all folders in the country folder
            for project_folder in country_folder.iterdir():
                # if the item is a folder
                if project_folder.is_dir():
                    yield project_folder


def build_embeddings_for_all_projects(database_folder_path, overwrite=False):
    for project_folder in project_folder_iterate(database_folder_path):
        print(f"Building json for {project_folder}")
        build_json_for_one_project(project_folder, overwrite=overwrite)
        print(f"Building embeddings for {project_folder}")
        build_embeddings_for_one_project(project_folder)


def build_final_db(database_folder_path):
    """
    Build the final database by stacking all the embeddings inside each project
    {
        "project1_name": {
            "folder_path": "",
            "embeddings": [list of embeddings],
            "keys": [list of keys (file name)],
            "subkeys": [list of subkeys],
        },
    }
    """

    def get_key_embedding(key_str):
        """
        Retrieve the key embedding from the key_embedding_dict
        """
        if key_str not in key_embedding_dict:
            key_embedding_dict[key_str] = get_text_embeddings(key_str)
        return key_embedding_dict[key_str]

    # create an empty dictionary
    final_db = {}

    # embedding dictionary of keys
    key_embedding_dict = {}

    # iterate all folders in the projects folder
    for project_folder in project_folder_iterate(database_folder_path):

        # get the folder name
        project_name = project_folder.name
        print(f"Building final db for {project_name}")

        final_db[project_name] = {
            "folder_path": str(project_folder),
            "embeddings": [],
            "key_embeddings": [],
            "keys": [],
            "subkeys": [],
        }

        # load the embeddings of this project
        embedding_dict_path = project_folder / "gpt_embeddings.pkl"
        with open(embedding_dict_path, "rb") as f:
            embedding_dict = pickle.load(f)

        # iterate all keys in the embedding dictionary
        for key in embedding_dict:

            if key == "description_full_text":
                final_db[project_name]["embeddings"].append(embedding_dict[key])
                final_db[project_name]["key_embeddings"].append(get_key_embedding("description"))
                final_db[project_name]["keys"].append("description")
                final_db[project_name]["subkeys"].append("full_text")
            else:
                for subkey in embedding_dict[key]:
                    # get key combination
                    key_str = key + " " + subkey
                    # remove numbers in the key string
                    key_str = ''.join([i for i in key_str if not i.isdigit()])

                    final_db[project_name]["embeddings"].append(embedding_dict[key][subkey])
                    final_db[project_name]["key_embeddings"].append(get_key_embedding(key_str))
                    final_db[project_name]["keys"].append(key)
                    final_db[project_name]["subkeys"].append(subkey)

    # save the final database using pickle
    final_db_path = Path(database_folder_path) / "final_db.pkl"

    with open(final_db_path, "wb") as f:
        pickle.dump(final_db, f)
        

def main():
    parser = argparse.ArgumentParser(description="Build the database")
    parser.add_argument("--path", type=str, help="Path to the dataset folder")
    parser.add_argument("--overwrite", default=False, help="Overwrite the existing JSON files")
    args = parser.parse_args()

    build_embeddings_for_all_projects(args.path, overwrite=args.overwrite)
    build_final_db(args.path)

if __name__ == "__main__":
    # build_embeddings_for_all_projects("database")
    # build_final_db("database")
    main()