from flask import Flask, request, render_template

from retrieval.query import query_handler
from visualization.results_to_html import results_to_html_dict

app = Flask(__name__)

# Path to the database folder
database_folder_path = "static/indexing"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-python', methods=['POST'])
def run_python():
    # Get the input data from the AJAX request
    input_data = request.form['inputData']

    # Here you can call your Python function with input_data as the argument
    results = query_handler(input_data, database_folder_path)
    results_dict = results_to_html_dict(results)
    return results_dict

if __name__ == "__main__":
    # use browser to go to http://127.0.0.1:5000
    app.run(debug=False)

    


