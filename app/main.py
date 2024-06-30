from fastapi import FastAPI
import uvicorn


app = FastAPI()


@app.get("/")
async def main_page():
    return {"Welcome to": "main_page"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
