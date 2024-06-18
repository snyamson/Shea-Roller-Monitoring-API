from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv
from .endpoints import raw_data, analytics

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
app.include_router(analytics.router, prefix="/api")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "*"],  # Allow localhost:3001 and all other origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# API metadata
api_description = "The Kobo Collect Custom Data Processing Microservice Server is designed to handle custom data processing tasks for Kobo Collect submissions and efficiently processes and manages data in the database."
api_version = "1.0.0"

# Home route
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