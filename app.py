from flask import Flask, request, jsonify, render_template, url_for

from query import query_handler

app = Flask(__name__)

# Path to the database folder
database_folder_path = "static/database"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-python', methods=['POST'])
def run_python():
    # Get the input data from the AJAX request
    input_data = request.form['inputData']

    # Here you can call your Python function with input_data as the argument
    # For demonstration, let's just echo back the input data with some modification
    result = query_handler(input_data, database_folder_path)
    
    # for each element in the result, change its image path
    for project_name in result:
        project_dict = result[project_name]
        if "image_path" not in project_dict:
            continue
        if project_dict["image_path"] is None:
            continue
        # replace the "\\" in the path with "/"
        project_dict["image_path"] = project_dict["image_path"].replace("\\", "/")
        # add the static folder to the path
        result[project_name]["image_path"] = project_dict["image_path"]

    # sort the dictionary by similarity into a list
    result = sorted(result.items(), key=lambda item: item[1]["similarity"], reverse=True)
    return result

if __name__ == "__main__":
    # use browser to go to http://127.0.0.1:5000
    import webbrowser
    webbrowser.open('http://127.0.0.1:5000')
    app.run(debug=True)

    


