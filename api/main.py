from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
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

@app.get('/')
def read_root(background_tasks: BackgroundTasks):
    # Run fetch_and_save_submissions in the background to fetch data asynchronously
    background_tasks.add_task(fetch_and_save_submissions)
    
    # Return the fetched submission_data as JSON response
    return JSONResponse(content=submission_data)


# App server setup
if os.getenv("ENVIRONMENT") == "development":
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app)