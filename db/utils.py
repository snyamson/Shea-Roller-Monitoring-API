import pandas as pd
import numpy as np
from collections import Counter
import os
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

# Hub Submission List
def return_hubs_list(db: Session):
    hubs_sheet = pd.read_csv(os.path.join(os.path.dirname(__file__), 'static_data', 'hub_id_name_sheet.csv'))
    hubs = db.query(Hub.id, Hub.name).all()
    database_hubs = pd.DataFrame(hubs, columns=['id', 'name'])
    # Identify hubs that have submitted data (matching IDs)
    submitted = hubs_sheet[hubs_sheet['id'].isin(database_hubs['id'])]

    # Identify hubs that have not submitted data (non-matching IDs)
    not_submitted = hubs_sheet[~hubs_sheet['id'].isin(database_hubs['id'])]

    # Convert to list of dicts
    submitted_list = submitted.to_dict(orient='records')
    not_submitted_list = not_submitted.to_dict(orient='records')

    # Create the final dictionary
    hubs_submission = {
        'hubs_submitted': submitted_list,
        'hubs_not_submitted': not_submitted_list
    }

    return hubs_submission

# Time saved allocation
def get_time_saved_allocation(db: Session):

    # Convert the query results to a pandas DataFrame
    df = pd.DataFrame(db.query(Submission.time_saved_used_for, Submission.time_saved_used_for_other).all(), columns=['time_saved_used_for', 'time_saved_used_for_other'])

    print(df['time_saved_used_for_other'])

    # Split the 'time_saved_used_for' column into individual categories
    categories = df['time_saved_used_for'].replace('', np.nan).dropna().str.split().explode()

    # Count occurrences of each category
    category_counts = Counter(categories)

    # Handle 'time_saved_used_for_other' column
    other_counts = df['time_saved_used_for_other'].replace('', np.nan).dropna()

    # If 'time_saved_used_for_other' contains valid text, count it under the category 'Other'
    if not other_counts.empty:
        category_counts['Other'] = len(other_counts)

    # Convert the counts to the required format
    time_saved_allocation = {
        'series': list(category_counts.values()),
        'category': list(category_counts.keys())
    }

    # Mapping of old category names to new ones
    rename_mapping = {
        'Cooked_prepared_to_cook': 'Cooked',
        'Farming_preparing_to_farm': 'Farming',
        'Cared_for_children_or_other_family_members': 'Cared for children',
        'Earned_money_from_another_job': 'Earned money from another job'
    }

    # Apply the mapping to the categories
    time_saved_allocation['category'] = [
        rename_mapping.get(cat, cat) for cat in time_saved_allocation['category']
    ]

    return time_saved_allocation

