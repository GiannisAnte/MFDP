from typing import Dict


def validate_data(data):
    data = data.dict()
    invalid_data: Dict[str: float] = {}
    # print(data)
    required_keys = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        invalid_data["missing_keys"] = missing_keys
    
    for key, value in data.items():
        if key in ("Age", "DiabetesPedigreeFunction"): 
            if value <= 0:
                invalid_data[key] = value
        else:
            if value < 0:
                invalid_data[key] = value
    
    return invalid_data

