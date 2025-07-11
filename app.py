import pickle
from flask import Flask, request, app, jsonify, url_for, render_template
import numpy as np
import pandas as pd 
import os


app = Flask(__name__)
with open('models/xgboost_model.pkl', 'rb') as f:
    model = pickle.load(f)
print("XGBoost model loaded successfully!")

REQUIRED_FEATURES = [
    'MedInc',
    'HouseAge',
    'AveRooms',
    'AveBedrms',
    'Population',
    'AveOccup',
    'Latitude',
    'Longitude'
]

@app.route('/')
def home():
    # render_template looks for 'home.html' in the 'templates' folder
    return render_template('home.html')

@app.route('/predict_api', methods=['POST'])
def predict_api():
    # Get JSON data from request as {"MedInc":.., "HouseAge":.., ..}
    data = request.json

    # Create a dictionary to hold input values
    input_data = {}

    for feature in REQUIRED_FEATURES:
        input_data[feature] = float(data[feature])

    # Convert the dictionary to a pandas DataFrame
    # Ensure the order of columns matches the REQUIRED_FEATURES
    input_df = pd.DataFrame([input_data])
    input_df = input_df[REQUIRED_FEATURES] # Enforce column order

    prediction = model.predict(input_df)[0] # [0] because predict returns an array
    output = float(round(prediction, 2)) # Round to 2 decimal places

    return jsonify(prediction=output) # Return the prediction as JSON



if __name__ == "__main__":
    app.run(debug=True)