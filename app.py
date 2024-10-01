from flask import Flask, render_template, request, jsonify
from rag_system import handle_user_query  # 导入您的RAG系统中的函数

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    context = {
        "identity": data['identity'],
        "gender": data['gender'],
        "familyBackground": data['familyBackground'],
        "priorContext": data['priorBackground'],
        "personality": data['personality']  # 添加性格特点
    }
    query = data['userInput']

    try:
        response = handle_user_query(query, context)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

if __name__ == '__main__':
    app.run(debug=True)