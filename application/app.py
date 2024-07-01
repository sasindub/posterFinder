from flask import Flask, request, render_template, jsonify
from flask_pymongo import PyMongo
import pytesseract
from PIL import Image
import io
import os
from dotenv import load_dotenv
import uuid
import re
import speech_recognition as sr

load_dotenv() #load environment variables from .env file

app = Flask(__name__)
 
 #configure flask app
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

#Initialize PyMongo
mongo = PyMongo(app)

#folder to save upload images
UPLOAD_FOLDER = 'static/uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def uploadPage():
    return render_template('upload.html')

@app.route('/search')
def searchPage():
    return render_template('search.html')

@app.route('/test')
def test():
    return render_template('testjs.html')

@app.route('/fileUpload', methods=["POST"])
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            return jsonify({"error: " "No file uploaded"}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error: " "No file selected"}), 400
    
    try:
        #get an id
        unique_id = str(uuid.uuid4())

        #extract filename dan save to uploadfolder
        filename = f"{unique_id+file.filename}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        #read the image for OCR
        image = Image.open(save_path)
        text = pytesseract.image_to_string(image)

        #clean text
        cleaned_text = re.sub(r'\s+', ' ', text).strip()

        if cleaned_text == "":
            return "0"

        #insert data into db
        file_data = {"id": unique_id, "filename": filename, "text": cleaned_text}
        mongo.db.files.insert_one(file_data)

        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "text": cleaned_text
        }), 200
    except Exception as e:
        return jsonify({"error: ": str(e)}), 500
    
@app.route('/searchResult', methods=['GET'])
def search():
    query = request.args.get('query', '')

    if query:
        # Tokenize the query into words
        keywords = re.findall(r'\w+', query.lower())

        # Construct the regex pattern to match whole words
        regex_pattern = r'\b(?:' + '|'.join(re.escape(word) for word in keywords) + r')\b'
    
        matches = mongo.db.files.find({"text": {"$regex": regex_pattern, "$options": "i"}})
        result = [
            {
                "id": str(match["_id"]),
                "text": match["text"],
                "filename": match.get("filename", "N/A")
            }
            for match in matches
        ]
        print(result)
        return jsonify(result)
    else:
        return jsonify({"error": "No query provided"}), 400

    
@app.route('/searchVoice', methods=['POST'])
def searchVoice():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            try:  
                r.adjust_for_ambient_noise(source)
                return jsonify("Say something!")
                
            except sr.UnknownValueError:
              return jsonify("Recognition could not understand the audio")
            except sr.RequestError as e:
                return jsonify(f"Could not request results from Google Speech Recognition service; {e}")
            except sr.WaitTimeoutError:
                return jsonify({"error": "Voice input timed out"}), 408
            except Exception as e:
                return jsonify(f"Unexpected error: {e}")

    except Exception as mic_error:
        return jsonify(f"Microphone error: {mic_error}")
    


# @app.route('/searchVoice', methods=['POST'])
# def searchVoiceRecord():
#     r = sr.Recognizer()

#     try:
#         if 'voiceInput' not in request.files:
#             return jsonify({"error": "No voice input found"}), 400

#         # Recognize speech from the provided audio file
#         audio_file = request.files['voiceInput']
#         audio_content = audio_file.read()

#         query = r.recognize_google(audio_content)

#         if query:
#             # Tokenize the query into words
#             keywords = re.findall(r'\w+', query.lower())

#             # Construct the regex pattern to match whole words
#             regex_pattern = r'\b(?:' + '|'.join(re.escape(word) for word in keywords) + r')\b'

#             # Query MongoDB for matching documents
#             matches = mongo.db.files.find({"text": {"$regex": regex_pattern, "$options": "i"}})
#             result = [
#                 {
#                     "id": str(match["_id"]),
#                     "text": match["text"],
#                     "filename": match.get("filename", "N/A")
#                 }
#                 for match in matches
#             ]
#             return jsonify(result)
#         else:
#             return jsonify({"error": "No query provided"}), 400

#     except sr.UnknownValueError:
#         return jsonify({"error": "Recognition could not understand the audio"}), 400
#     except sr.RequestError as e:
#         return jsonify({"error": f"Could not request results from Google Speech Recognition service: {e}"}), 500
#     except Exception as e:
#         return jsonify({"error": f"Unexpected error: {e}"}), 500
    

if __name__ == '__main__':
    app.run(debug=True)