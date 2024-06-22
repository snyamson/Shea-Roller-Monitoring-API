from fastapi import APIRouter
import httpx
import os
from dotenv import load_dotenv
from db.tasks import process_data
from db.shared import analytics_data

load_dotenv()

# Create router
router = APIRouter()

# KoboCollect Submission
KOBO_SERVER_DATA_URL = os.getenv('KOBO_SERVER_DATA_URL')
KOBO_SERVER_TOKEN = 'Token '+ os.getenv('KOBO_SERVER_TOKEN')

# Get route
@router.get('/analytics')
async def get_analytics():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(KOBO_SERVER_DATA_URL, headers={"Authorization": KOBO_SERVER_TOKEN})
            response.raise_for_status()
            process_data(response.json())
            
            return analytics_data
        
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}
    except httpx.HTTPStatusError as e:
        return {"error": f"Error response {e.response.status_code} while requesting {e.request.url!r}."}
