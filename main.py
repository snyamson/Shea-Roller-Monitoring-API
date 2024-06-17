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


        # # Initialize a dictionary to store the count of submissions by date
        # submission_counts_by_date = {}

        # # Loop through the results
        # for result in submissions['results']:
        #     # Get the 'today' value
        #     today_date = result['today']
        #     print(parse_username(result['username']))
            
        #     # Increment the count for this date in the dictionary
        #     if today_date in submission_counts_by_date:
        #         submission_counts_by_date[today_date] += 1
        #     else:
        #         submission_counts_by_date[today_date] = 1

        # # Print the counts
        # for date, count in submission_counts_by_date.items():
        #     print(f"Date: {date}, Count: {count}")

    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
# Post Route to the webhook 
# @app.post("/webhook")
# async def webhook_listener(request: Request, background_tasks: BackgroundTasks):
#     body = await request.body()
#     signature = request.headers.get('X-Kobo-Signature')
    
#     if not signature or not verify_signature(request, body, signature):
#         logger.warning("Invalid signature")
#         raise HTTPException(status_code=403, detail="Forbidden")
    
#     # Log the raw request body for debugging
#     logger.info(f"Data received: {body.decode()}")
    
#     try:
#         # Parse the JSON payload using pydantic_core.from_json
#         parsed_data = from_json(body, allow_partial=True)
#         # Manually create an instance of KoboData
#         data = KoboData(
#             submission_id=parsed_data.get('_id'),
#             formhub_uuid=parsed_data.get('formhub/uuid'),
#             data=parsed_data
#         )
#     except ValidationError as e:
#         logger.error(f"Error parsing or validating payload: {e}")
#         raise HTTPException(status_code=400, detail="Invalid payload structure")
    
#     # Log the data
#     logger.info(f"Submission Id: {data.submission_id}")
    
#     # Process the data in the background
#     background_tasks.add_task(process_data, data)
    
#     return {"status": "ok"}

# fetch_and_save_submissions()
# Schedule the job to run every 10 seconds
# trigger = IntervalTrigger(seconds=10)
# scheduler.add_job(fetch_and_save_submissions, trigger)

# Route to serve HTML template at /
# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request, "analytics_data":analytics_data})
@app.get('/')
def hello_world():
    return "Hello,World"

# App server setup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
