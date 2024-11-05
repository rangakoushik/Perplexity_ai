from flask import Flask, request, jsonify
from flask_cors import CORS
from perplex import MiniPerplexity
import json

app = Flask(__name__)
CORS(app)

perplexity = MiniPerplexity()

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        # Get search results
        search_results = perplexity.search_google(query)
        
        if not search_results:
            return jsonify({'error': 'No search results found'}), 404
            
        # Get analysis
        response = perplexity.analyze_with_gpt(query, search_results)
        
        return jsonify({
            'response': response,
            'sources': search_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)