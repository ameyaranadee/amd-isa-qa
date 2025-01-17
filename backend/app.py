from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    results = {"suggestions": ["Example Result 1", "Example Result 2"]}
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)