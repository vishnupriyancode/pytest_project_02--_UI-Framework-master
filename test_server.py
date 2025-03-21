from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health-check', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API server is running'})

@app.route('/process-edit', methods=['POST'])
def process_edit():
    data = request.json
    file_path = data.get('file_path', '')
    edit_id = data.get('edit_id', 'Edit 1')
    
    return jsonify({
        'status': 'success',
        'message': 'Edit is working properly',
        'file_path': file_path,
        'edit_id': edit_id,
        'processed': True
    })

if __name__ == '__main__':
    print('Server starting on http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
