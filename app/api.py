from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import init_db
import uvicorn
from routes.home.get import home_route
from routes.user.get import get_user_route
from routes.user.put import put_user_route
from routes.user.post import post_user_route
from routes.ml.get import get_ml_route
from routes.ml.post import post_ml_route
from routes.user.get import auth_router


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(home_route)
app.include_router(get_user_route, prefix='/user')
app.include_router(put_user_route, prefix='/user')
app.include_router(post_user_route, prefix='/user')
app.include_router(get_ml_route)
app.include_router(post_ml_route)
app.include_router(auth_router)


if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)
