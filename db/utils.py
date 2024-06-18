from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Hub, Submission


# Calculate growth rate and add it to analytics_data
def calculate_growth_rate(db: Session):
    # Get today's date and yesterday's date
    today_date = date.today()
    yesterday_date = today_date - timedelta(days=1)
    
    # Query total submissions for today
    total_submissions_today = db.query(func.count(Submission.id)).filter(Submission.today == today_date).scalar()
    
    # Query total submissions for yesterday
    total_submissions_yesterday = db.query(func.count(Submission.id)).filter(Submission.today == yesterday_date).scalar()
    
    # Handle the case where there are no submissions yesterday to avoid division by zero
    if total_submissions_yesterday == 0:
        growth_rate = 0  # Or handle it as per your business logic
    else:
        # Calculate the growth rate
        growth_rate = ((total_submissions_today - total_submissions_yesterday) / total_submissions_yesterday) * 100

    return growth_rate

