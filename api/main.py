from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os
from dotenv import load_dotenv
from .endpoints import raw_data

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

# Include the router from the endpoint module
app.include_router(raw_data.router, prefix="/api")

scheduler = BackgroundScheduler()
scheduler.start()

# Global variable to store submissions
submission_data = {}

def fetch_and_save_submissions():
    global submission_data
    try:
        response = httpx.get(KOBO_SERVER_DATA_URL, headers={"Authorization": KOBO_SERVER_TOKEN})
        response.raise_for_status()
        submissions = response.json()
        # process_data(submissions)
        submission_data = submissions  # Update the global variable with the fetched data
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")

# API metadata
api_description = "The Kobo Collect Custom Data Processing Microservice Server is designed to handle custom data processing tasks for Kobo Collect submissions and efficiently processes and manages data in the database."
api_version = "1.0.0"

@app.get('/')
def read_root():
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "date": current_date_time,
        "description": api_description,
        "version": api_version
    }

# App server setup
if os.getenv("ENVIRONMENT") == "development":
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app)