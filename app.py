from flask import Flask, request, render_template, session

from retrieval.query import query_handler
from retrieval.query import QuerySet
from visualization.results_to_html import results_to_html_dict

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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
    results, query_set = query_handler(input_data, database_folder_path)

    # update the global query set
    session['global_query_set'] = query_set

    results_dict = results_to_html_dict(results, query_set)
    return results_dict

@app.route('/apply-weights', methods=['POST'])
def apply_weights():
    # Get the input data from the AJAX request
    input_data = request.form['weights']

    # Update the weights in the query set
    weights = [float(w) for w in input_data.split(",")]
    query_set = session['global_query_set']
    query_set= QuerySet.from_dict(query_set)
    query_set.weights = weights

    # rerun the query
    results, query_set = query_handler(query_set, database_folder_path)
    session['global_query_set'] = query_set
    results_dict = results_to_html_dict(results, query_set)
    return results_dict

if __name__ == "__main__":
    # use browser to go to http://127.0.0.1:5000
    app.run(debug=True)

    


