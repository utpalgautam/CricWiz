from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from websearch import websearch
from webapi import CricketAPI
from config import logger  # Only use the shared logger

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

searcher = websearch()
cricapi = CricketAPI()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('message', '')
    logger.info(f"Received question: {question}")
    if not question:
        logger.warning("No question provided in request.")
        return jsonify({'reply': 'Please enter a question.'})
    try:
        api_result = cricapi.analyze_and_route(question)
        if api_result is not None and not api_result.get('error'):
            logger.info("Answered using CricketAPI.")
            # Format API result for better display
            import json
            formatted_result = json.dumps(api_result, indent=2) if isinstance(api_result, dict) else str(api_result)
            return jsonify({'reply': formatted_result})
        answer = searcher.get_answer(question)
        logger.info("Answered using websearch.")
        # Format answer with line breaks for HTML display
        formatted_answer = answer.replace('\n', '<br>') if answer else "No answer found."
        return jsonify({'reply': formatted_answer})
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'reply': 'Sorry, an error occurred while processing your request.'})

@app.route('/')
def root():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
