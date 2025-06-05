import json
import joblib
from pathlib import Path
from typing import Tuple, Any

THRESHOLDS_FILE = Path("ml") / "thresholds.json"

def get_model_and_threshold(name: str) -> Tuple[Any, float, str]:
    with open(THRESHOLDS_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    for customer, params in cfg.items():
        if params.get("name") == name:
            model_path = Path(params["model_path"]).resolve()
            print(f"load model from: {model_path}")
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            model = joblib.load(model_path)
            return model, params["threshold"], params["description"]

    raise ValueError(f"No model found with name: {name}")
