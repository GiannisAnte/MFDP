import torch
import os
from ml.core.CNN_arch import CNNModel 

# _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_model = None

def get_model():
    global _model
    if _model is None:
        MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "cnn_model_weights.pth")
        MODEL_PATH = os.path.abspath(MODEL_PATH)
        _model = CNNModel()#.to(_device)
        _model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu"), weights_only=True))
        _model.eval()
    return _model


# cold start для модели
# try:
#     _ = get_model()(torch.zeros(1, 3, 32, 32, device=_device))
# except Exception as e:
#     import logging
#     logging.getLogger(__name__).warning("Model warm-up failed: %s", e)