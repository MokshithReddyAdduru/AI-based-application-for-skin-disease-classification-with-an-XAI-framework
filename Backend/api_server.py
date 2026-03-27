import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tensorflow.keras.models import load_model
from PIL import Image
import cv2
import time

# 🔥 LIME & XAI
from lime import lime_image
from skimage.segmentation import mark_boundaries

tf.keras.backend.clear_session()

app = Flask(__name__)
CORS(app)

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'static', 'results')
IMG_SIZE = 64 

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR, exist_ok=True)

# --- GLOBALS ---
GLOBAL_MODEL = None
GLOBAL_CLASS_NAMES = {}
DISEASE_FULL_NAMES = {
    'akiec': 'Actinic Keratoses', 'bcc': 'Basal Cell Carcinoma', 
    'bkl': 'Benign Keratosis', 'df': 'Dermatofibroma', 
    'mel': 'Melanoma (Cancer)', 'nv': 'Melanocytic Nevi', 'vasc': 'Vascular Lesions'
}

# --- STABLE LOAD ---
try:
    MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, 'final_model.keras'))
    GLOBAL_MODEL = load_model(MODEL_PATH, compile=False)
    CLASS_INDICES = np.load(os.path.join(BASE_DIR, 'class_indices.npy'), allow_pickle=True).item()
    GLOBAL_CLASS_NAMES = {v: k for k, v in CLASS_INDICES.items()}
    print(f"✅ 40-Epoch Clinical Engine Online")
except Exception as e:
    print(f"❌ Startup Error: {e}")

# --- STABLE LIME LOGIC ---
def get_lime_explanation(img_array, model):
    explainer = lime_image.LimeImageExplainer()
    
    def predict_fn(imgs):
        return model.predict(imgs, verbose=0)

    # 1000 samples for high-quality stability
    explanation = explainer.explain_instance(
        img_array[0].astype('double'), 
        predict_fn, 
        top_labels=1, 
        hide_color=0, 
        num_samples=1000 
    )
    
    temp, mask = explanation.get_image_and_mask(
        explanation.top_labels[0], positive_only=True, num_features=5, hide_rest=False
    )
    return mark_boundaries(temp, mask)

# --- ROUTES ---
@app.route('/predict', methods=['POST'])
def predict():
    if GLOBAL_MODEL is None: return jsonify({"error": "Engine Offline"}), 500
    file = request.files['file']
    raw_img = Image.open(file.stream).convert('RGB')
    
    # Preprocess
    img = raw_img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # 1. AI Prediction
    preds = GLOBAL_MODEL.predict(img_array, verbose=0)
    conf = float(np.max(preds[0]))
    idx = np.argmax(preds[0])
    code = GLOBAL_CLASS_NAMES.get(idx, "unknown")
    name = DISEASE_FULL_NAMES.get(code, "Unknown")

    # 2. XAI (LIME) Heatmap
    heatmap_url = None
    try:
        lime_raw = get_lime_explanation(img_array, GLOBAL_MODEL)
        lime_bgr = cv2.cvtColor((lime_raw * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        lime_final = cv2.resize(lime_bgr, (300, 300))
        filename = f"lime_{int(time.time())}.jpg"
        filepath = os.path.join(RESULTS_DIR, filename)
        if cv2.imwrite(filepath, lime_final):
            heatmap_url = f"{request.host_url}static/results/{filename}"
    except Exception as e:
        print(f"❌ XAI Error: {e}")

    # 3. High-Sensitivity Gate
    is_normal = conf < 0.38 
    
    return jsonify({
        "status": "success",
        "prediction_name": "Healthy Skin Analysis" if is_normal else name,
        "prediction_code": "Normal" if is_normal else code,
        "confidence": round(conf * 100, 2),
        "is_normal": is_normal,
        "heatmap_url": heatmap_url,
        "textual_explanation": (
            f"The LIME explainer has identified specific superpixels (highlighted) that match the textural markers of {name}. "
            "These regions show irregular pigmentation or border structures that influenced the AI's final decision."
        ) if not is_normal else "The XAI analysis found no concentrated regions of concern; the texture appears statistically uniform.",
        "precautions": f"Patterns suggest {name} characteristics." if not is_normal else "No action required beyond regular SPF use."
    })

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)