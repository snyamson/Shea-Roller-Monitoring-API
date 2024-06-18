from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic_core import from_json
from pydantic import ValidationError
from datetime import datetime
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from utils.logger import logger
from db.tasks import process_data
from db.shared import analytics_data
import os
from dotenv import load_dotenv

load_dotenv()

# KoboCollect Submission
KOBO_SERVER_DATA_URL = os.getenv('KOBO_SERVER_DATA_URL')
KOBO_SERVER_TOKEN = 'Token '+ os.getenv('KOBO_SERVER_TOKEN')


# App Intialization and Version
app = FastAPI(
    title="Kobo Collect Custom Data Processing Microservice Server",
    description="The Kobo Collect Custom Data Processing Microservice Server is designed to handle custom data processing tasks for Kobo Collect submissions and efficiently processes and manages data in the database.",
    version="1.0.0"
)

scheduler = BackgroundScheduler()
scheduler.start()

templates = Jinja2Templates(directory="templates")

total_submissions = None


def fetch_and_save_submissions():
    global total_submissions  # Declare that we're modifying the global variable
    current_date = datetime.now().date().isoformat()

    try:
        response = httpx.get(KOBO_SERVER_DATA_URL, headers={"Authorization": KOBO_SERVER_TOKEN})
        response.raise_for_status()
        submissions = response.json()

        total_submissions=submissions['count']

        process_data(submissions)


    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
        
@app.get('/')
def hello_world():
    return "Hello,World"

# App server setup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
