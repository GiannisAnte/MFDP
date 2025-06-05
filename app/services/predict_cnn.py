import torch
from PIL import Image
from torchvision import transforms
import torch.nn.functional as F
from sqlmodel import Session
import logging
from ml.core.cnn_model import get_model
from models.prediction import Prediction


logger = logging.getLogger(__name__)


transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

def predict_cnn(image: Image.Image) -> dict:
    input_tensor = transform(image).unsqueeze(0)#.to(_device)

    with torch.no_grad():
        model = get_model()
        output = model(input_tensor)
        probs = F.softmax(output, dim=1)
        confidence, pred_class = torch.max(probs, 1)
        class_names = ['nowildfire', 'wildfire']
        predicted_label = class_names[pred_class.item()]
        confidence_pct = confidence.item() * 100

    return {"predicted_label": predicted_label, "confidence_pct": f"{confidence_pct:.2f}%"}


def run_cnn_prediction(image: Image.Image, event_id: str, session: Session) -> Prediction:
    result = predict_cnn(image)

    rec = session.query(Prediction).filter_by(fire_event_id=event_id).first()
    if not rec:
        raise ValueError(f"Prediction not found for event_id={event_id}")
    
    logger.info("Before update: %s", rec.to_dict())

    rec.status = 'SUCCESS'
    rec.variant = 'CNN'
    rec.score =  result.get('confidence_pct', 'None').replace('%', '').strip()
    rec.result = result.get('predicted_label')

    return rec