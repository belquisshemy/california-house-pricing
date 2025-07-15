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

# Define realistic ranges for data
FEATURE_RANGES = {
    'MedInc': {'min': 0.5, 'max': 20, 'name': 'Median Income '},
    'HouseAge': {'min': 0, 'max': 55, 'name': 'House Age'},
    'AveRooms': {'min': 1.0, 'max': 15.0, 'name': 'Average Rooms'},
    'AveBedrms': {'min': 0.0, 'max': 3.0, 'name': 'Average Bedrooms'},
    'Population': {'min': 100, 'max': 40000, 'name': 'Population'},
    'AveOccup': {'min': 1.0, 'max': 10.0, 'name': 'Average Occupancy'},
    'Latitude': {'min': 32.5, 'max': 42.0, 'name': 'Latitude'},
    'Longitude': {'min': -124.5, 'max': -114.0, 'name': 'Longitude'}
}

def validate_input(data):
    """
    Validate input data against realistic ranges
    Returns (is_valid, error_messages)
    """
    errors = []
    
    # Check if all required features are present
    for feature in REQUIRED_FEATURES:
        if feature not in data or data[feature] is None:
            errors.append(f"{FEATURE_RANGES[feature]['name']} is required")
    
    # Check ranges for each feature
    for feature, value in data.items():
        if feature in FEATURE_RANGES and value is not None:
            range_info = FEATURE_RANGES[feature]
            min_val = range_info['min']
            max_val = range_info['max']
            name = range_info['name']
            
            try:
                float_value = float(value)
                if float_value < min_val or float_value > max_val:
                    errors.append(f"{name} must be between {min_val} and {max_val}")
            except (ValueError, TypeError):
                errors.append(f"{name} must be a valid number")

    # Additional logic checks
    if 'AveRooms' in data and 'AveBedrms' in data:
        try:
            ave_rooms = float(data['AveRooms'])
            ave_bedrms = float(data['AveBedrms'])
            if ave_bedrms > ave_rooms:
                errors.append("Average Bedrooms cannot be greater than Average Rooms")
        except (ValueError, TypeError):
            pass  # Will be caught by individual validation above
    
    return len(errors) == 0, errors 



@app.route('/')
def home():
    # render_template looks for 'home.html' in the 'templates' folder
    return render_template('home.html')



@app.route('/predict_api', methods=['POST'])
def predict_api():
    try:
        # Get JSON data from request as {"MedInc":.., "HouseAge":.., ..}
        data = request.json

        if not data:
            return jsonify(error="No data provided"), 400

        # Validate input data
        is_valid, error_messages = validate_input(data)

        if not is_valid:
            return jsonify(error="Invalid input: " + "; ".join(error_messages)), 400

        # Create a dictionary to hold input values
        input_data = {}

        for feature in REQUIRED_FEATURES:
            input_data[feature] = float(data[feature])

        # Convert the dictionary to a pandas DataFrame
        # Ensure the order of columns matches the REQUIRED_FEATURES
        input_df = pd.DataFrame([input_data])
        input_df = input_df[REQUIRED_FEATURES] # Enforce column order

        prediction = model.predict(input_df)[0] # [0] because predict returns an array
        output = float(round(prediction * 100000, 2))

        return jsonify(prediction=output) # Return the prediction as JSON
    
    except Exception as e:
        return jsonify(error=f"Prediction error: {str(e)}"), 500


if __name__ == "__main__":
    app.run(debug=True)