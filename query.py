import argparse

from pathlib import Path
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from model_call import ask_gpt_text, ask_gpt_v_text, get_text_embeddings


def query_from_database(query, database_folder_path):
    """
    Query the database for the most similar projects to the query
    """

    # read the final database
    final_db_path = Path(database_folder_path) / "final_db.pkl"
    final_db = pickle.load(open(final_db_path, "rb"))

    # get the embeddings for the query
    query_embeddings = get_text_embeddings(query)
    print("Query embeddings got. Now calculating similarity.")

    similarity_dict = {}

    # iterate all projects in the database
    for project_name in final_db:
        folder_path = final_db[project_name]["folder_path"]

        key_embedding = np.array(final_db[project_name]["key_embeddings"])
        content_embedding = np.array(final_db[project_name]["embeddings"])

        # calculate the similarity between the query and each embedding in the project
        similarities= cosine_similarity([query_embeddings], content_embedding)
        
        # calculate the similarity between the query and each key in the project
        weights = cosine_similarity([query_embeddings], key_embedding)
        # create a mask where the key contains "description"
        mask = np.array(["description" in key for key in final_db[project_name]["keys"]])
        # set the weights of the keys that contain "description" to the average
        weights[0][mask] = 0
        avg_weights = np.mean(weights)
        weights[0][mask] = avg_weights
        # # create a mask where the key contains "keywords"
        # mask = np.array(["keywords" in key for key in final_db[project_name]["keys"]])
        # # set the weights of the keys that contain "keywords" to the 0
        # weights[0][mask] = 0

        weighted_similarities = similarities * weights
        avg_weighted_similarities = np.mean(weighted_similarities)

        # find the index where the weighted similarity is the highest
        max_index = np.argmax(weighted_similarities)

        # get the key and subkey of the most similar embedding
        key = final_db[project_name]["keys"][max_index]
        subkey = final_db[project_name]["subkeys"][max_index]

        # if the key does not contain "description"
        # then add ".jpg" to it to get the image path
        if "description" not in key:
            image_path = f"{folder_path}/{key}.jpg"
        else:
            # find any one image in the folder, jpg or png
            image_path = list(Path(folder_path).glob("*.jpg")) + list(Path(folder_path).glob("*.png"))
            if len(image_path) > 0:
                image_path = str(image_path[0])
            else:
                image_path = None

        # if there exists "meta.csv" in the folder, read the first line second column
        web_url = "google.com"
        meta_csv_path = Path(folder_path) / "meta.csv"
        if meta_csv_path.exists():
            with open(meta_csv_path, "r") as f:
                meta = f.readline().split(",")
                if len(meta) > 1:
                    web_url = meta[1]


        # add the similarity to the dictionary
        similarity_dict[project_name] = {
            "similarity": avg_weighted_similarities,
            "key": key,
            "subkey": subkey,
            "image_path": image_path,
            "folder_path": folder_path,
            "web_url": web_url
        }

    # sort the dictionary by similarity
    similarity_dict = dict(sorted(similarity_dict.items(), key=lambda item: item[1]["similarity"], reverse=True))

    return similarity_dict


def query_handler(query, database_folder_path):
    # check if the query is a file path to an image
    if Path(query).exists():
        print("Query recognized as an image file path")

        # get the text description of the image
        query_str = ask_gpt_v_text(query, "Describe in detail about this architecture design, specifying the form, function, material and context.")
        
        # if the response is an empty dictionary, raise an error
        if not query_str:
            raise ValueError("We cannot find the file")
    else:
        print("Query recognized as a text")
        query_str = query

    # query the database
    similarity_dict = query_from_database(query_str, database_folder_path)
    return similarity_dict


def main():
    # parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="The query to search for")
    parser.add_argument("--database", type=str, help="The path to the database folder")
    args = parser.parse_args()

    # query the database
    query_string = args.query
    similarity_dict = query_handler(query_string, args.database)

    # print the most similar projects
    for project_name in similarity_dict:
        print(f"{project_name}: {similarity_dict[project_name]}")

if __name__ == "__main__":
    main()
    """
    input example to run the script from the terminal:
    python query.py --query "minimalism form" --database "test_database"
    """