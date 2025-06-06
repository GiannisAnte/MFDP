from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database.database import init_db
from fastapi.staticfiles import StaticFiles
from utils.clear_static import clear_static_images
from ml.core.load_models import load_model_from_clearml
from ml.core.load_cnn_weights import load_cnn_weights_from_clearml
from endpoints.home.get import home_route
from endpoints.user.get import auth_router, get_user_route
from endpoints.user.post import post_user_route
from endpoints.ml.post import router_cnn, router_w, router_ml
from endpoints.ml.get import router_weather, router_h_weather

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    init_db()
    clear_static_images()
    load_model_from_clearml(project_name="Fires", task_name="Upload Stacking CB+RF-LR Model",artifact_name='stacking_cb_rf_model.pkl', destination_dir="ml/", target_filename='stacking_cb_rf_model')
    load_model_from_clearml(project_name="Fires", task_name="Upload Stacking XGB+CB-LR Model",artifact_name='stacking_xgb_cb_model.pkl', destination_dir="ml/", target_filename='stacking_xgb_cb_model')
    load_cnn_weights_from_clearml(project_name="Fires", task_name="Load CNN Weights",destination_dir="ml/")

app.include_router(home_route)
app.include_router(get_user_route, prefix='/user')
app.include_router(post_user_route, prefix='/user')
app.include_router(auth_router)
app.include_router(router_cnn)
app.include_router(router_w)
app.include_router(router_ml)
app.include_router(router_weather)
app.include_router(router_h_weather)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)