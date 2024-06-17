from fastapi import APIRouter
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Create router
router = APIRouter()

# KoboCollect Submission
KOBO_SERVER_DATA_URL = os.getenv('KOBO_SERVER_DATA_URL')
KOBO_SERVER_TOKEN = 'Token '+ os.getenv('KOBO_SERVER_TOKEN')

# Get route
@router.get('/raw_data')
async def get_raw_data():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(KOBO_SERVER_DATA_URL, headers={"Authorization": KOBO_SERVER_TOKEN})
            response.raise_for_status()
            return response.json()
        
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting {e.request.url!r}."}
    except httpx.HTTPStatusError as e:
        return {"error": f"Error response {e.response.status_code} while requesting {e.request.url!r}."}