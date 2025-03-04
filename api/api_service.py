from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from datetime import timedelta
from werkzeug.utils import secure_filename
import os
import uuid
import shutil
import jwt
import datetime
from chatbot import Chatbot
from langchain.memory import ConversationBufferMemory
from config import *

chatbot = Chatbot()

app = Flask(__name__)
app.secret_key = JWT_SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60*3)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_EXPIRATION_DELTA"] = JWT_EXPIRATION_DELTA
CORS(app, origins="http://localhost:3000", supports_credentials=True)

shutil.rmtree(UPLOAD_FOLDER)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def GenerateJWTtoken(session_id):
    payload = {
        'session_id': session_id,
        'exp': datetime.datetime.now(datetime.UTC) + JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def VerifyJWTtoken(token):
    if not token:
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['session_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route("/start_session", methods=["POST"])
def start_session():
    session["session_id"] = str(uuid.uuid4())
    if USE_LANGCHAIN:
        session["memory"] = ConversationBufferMemory()
    token = GenerateJWTtoken(session["session_id"])
    session.modified = True
    response = make_response(jsonify({"message": "Session Started"}))
    response.set_cookie('jwt_token', token, httponly=True, secure=True)
    return response, 200

@app.route("/check_session", methods=["GET"])
def check_session():
    token = request.cookies.get('jwt_token')

    if not VerifyJWTtoken(token):
        return jsonify({"message": "Invalid token"}), 200

    return jsonify({"message": "Token is valid"}), 200

@app.route("/upload", methods=["POST"])
def upload():
    token = request.cookies.get('jwt_token')

    if not VerifyJWTtoken(token):
        return jsonify({"error": "Invalid token"}), 401
    
    content = request.data.decode('utf-8')

    if not content:
        return jsonify({"error": "Content is empty"}), 400
    
    # Take only the first 512 characters of the string because the model is limited to only that much #
    content = content[:512]

#    if "file" not in request.files:
#        return jsonify({"error": "No file part in the request"}), 400

#    file = request.files["file"]
#    if file.filename == "":
#        return jsonify({"error": "No selected file"}), 400
#
#    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
#        return jsonify({"error": "Bad File Extension"}), 400

    try:
        filename = secure_filename(session["session_id"])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, "w") as file:
            file.write(content)
        session["filename"] = filename
        if USE_LANGCHAIN:
            doc_with_metadata = [{"text": content, "metadata": {"user_id": session["session_id"]}}]
            chatbot.vector_store.add_documents(doc_with_metadata)
            chatbot.vector_store.persist()
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ask_question", methods=["POST"])
def ask_question():
    token = request.cookies.get("jwt_token")
    
    if not VerifyJWTtoken(token):
        return jsonify({"error": "Invalid token"}), 401
    
    try:
        question = request.data.decode('utf-8')

        if isinstance(question, str):
            with open(os.path.join(UPLOAD_FOLDER, session.get("filename", ''))) as file:
                try:
                    return jsonify({"message": chatbot.GenerateAnswer(session, question, file.read())}), 200
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "Invalid data format"}), 400

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Unexpected error occurred"}), 500

@app.route("/get_questions", methods=["GET"])
def get_questions():
    token = request.cookies.get("jwt_token")
    
    if not VerifyJWTtoken(token):
        return jsonify({"error": "Invalid token"}), 401
    
    try:
        with open(os.path.join(UPLOAD_FOLDER, session.get("filename", ''))) as file:
            try:
                return jsonify({"message": chatbot.GenerateQuestions(session, file.read())}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Unexpected error occurred"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)