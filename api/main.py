from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

@app.get('/')
def hello_world():
    return "Hello,World - Main"


# App server setup
if os.getenv("ENVIRONMENT") == "development":
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app)