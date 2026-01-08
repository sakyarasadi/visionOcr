from flask import Flask, request, jsonify
from google.cloud import vision
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import re
import os
import json

app = Flask(__name__)

# Get credentials from environment variable or file
# For production (GCP): Use GOOGLE_APPLICATION_CREDENTIALS_JSON env var
# For local development: Use the JSON file
credentials = None
if os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
    # Load credentials from environment variable (for GCP deployment)
    credentials_dict = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
elif os.path.exists("sublime-lens-479204-m6-03eb13e666f6.json"):
    # Load from file for local development
    credentials = service_account.Credentials.from_service_account_file(
        "sublime-lens-479204-m6-03eb13e666f6.json"
    )
else:
    # Use default GCP credentials (Workload Identity)
    credentials = None

if credentials:
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
    translate_client = translate.Client(credentials=credentials)
else:
    # Use default credentials when running on GCP with Workload Identity
    vision_client = vision.ImageAnnotatorClient()
    translate_client = translate.Client()


def contains_sinhala(text):
    return bool(re.search(r'[\u0D80-\u0DFF]', text))


@app.route("/ocr", methods=["POST"])
def ocr_image():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        image_bytes = file.read()

        image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=image)

        if response.error.message:
            return jsonify({"error": response.error.message}), 500

        texts = response.text_annotations
        extracted_text = texts[0].description.strip() if texts else ""

        translated = False
        english_text = extracted_text

        if contains_sinhala(extracted_text):
            result = translate_client.translate(
                extracted_text,
                source_language="si",
                target_language="en"
            )
            english_text = result["translatedText"]
            translated = True

        return jsonify({
            "success": True,
            "original_text": extracted_text,
            "english_text": english_text,
            "translated_by_cloud_translate": translated
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    # Use PORT environment variable for GCP Cloud Run compatibility
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
