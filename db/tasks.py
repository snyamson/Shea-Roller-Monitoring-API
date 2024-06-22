import sqlalchemy
import numpy as np
import pandas as pd
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from utils.logger import logger
from .utils import calculate_growth_rate, return_hubs_list, get_time_saved_allocation
from .dependencies import get_db
from .models import Hub, Submission
from .shared import analytics_data

def parse_username(username):
    try:
        hub_id, hub_name = username.split(", ")
        return int(hub_id), hub_name.strip().capitalize()
    except ValueError:
        logger.error(f"Error parsing username: {username}")
        return None, None

# Get today's date
today_date = date.today()

def process_data(data):
    try:
        new_hubs = []
        new_submissions = []

        with get_db() as db:
            # Cache existing hubs to avoid redundant queries
            existing_hub_ids = {hub.id for hub in db.query(Hub.id).all()}
            existing_submission_ids = {sub.submission_id for sub in db.query(Submission.submission_id).all()}

            # Iterate through the results
            for result in data['results']:
                logger.info(f"Processing result: {result}")

                hub_id, hub_name = parse_username(result['username'])
                if hub_id is None or hub_name is None:
                    logger.error(f"Skipping result due to invalid username: {result['username']}")
                    continue

                # Add new hub if it does not exist
                if hub_id not in existing_hub_ids:
                    new_hubs.append(Hub(id=hub_id, name=hub_name))
                    existing_hub_ids.add(hub_id)
                    logger.info(f"Adding new hub: {hub_name} (ID: {hub_id})")

                # Check if submission already exists
                submission_id = result.get("_id")
                if not submission_id:
                    logger.error(f"Skipping result due to missing submission ID: {result}")
                    continue

                if submission_id not in existing_submission_ids:
                    new_submissions.append(Submission(
                        hub_id=hub_id,
                        submission_id=submission_id,
                        today=datetime.strptime(result.get("today", ""), "%Y-%m-%d") if result.get("today", "") else None,
                        first_name=result.get("survey_start/respondent/First_Name", ""),
                        last_name=result.get("survey_start/respondent/Last_Name", ""),
                        age=result.get("survey_start/respondent/Age", ""),
                        age_range=result.get("survey_start/respondent/Age_Range", ""),
                        gender=result.get("survey_start/respondent/Gender", ""),
                        contact=result.get("survey_start/respondent/Contact", ""),
                        date_of_rental=datetime.strptime(result.get("survey_start/rental_information/Date_of_Rental", ""), "%Y-%m-%d") if result.get("survey_start/rental_information/Date_of_Rental", "") else None,
                        did_roller_help=result.get("survey_start/rental_information/Did_Roller_Help", ""),
                        bowls_usually_picked=result.get("survey_start/rental_information/Bowls_Usually_Picked", None),
                        bowls_picked_with_roller=result.get("survey_start/rental_information/Bowls_Picked_with_Roller", None),
                        additional_shea_collected_due_to_roller=result.get("survey_start/rental_information/Additional_Shea_Collected_due_to_Roller", None),
                        less_difficulty_using_roller=result.get("survey_start/rental_information/Less_Difficulty_using_Roller", ""),
                        time_saved=result.get("survey_start/rental_information/Time_Saved", None),
                        time_saved_used_for=result.get("survey_start/rental_information/Time_Saved_Used_For", ""),
                        time_saved_used_for_other=result.get("survey_start/rental_information/Time_Saved_Used_For_Other", ""),
                        hours_taken_to_use=result.get("survey_start/rental_information/Hours_Taken_to_Use", None),
                        why_long_hours_of_use=result.get("survey_start/rental_information/Why_Long_Hours_of_Use", ""),
                        uuid=result.get("_uuid", ""),
                        status=result.get("_status", ""),
                        submission_time=datetime.strptime(result.get("_submission_time", ""), "%Y-%m-%dT%H:%M:%S") if result.get("_submission_time", "") else None,
                    ))
                    existing_submission_ids.add(submission_id)
                    logger.info(f"Adding new submission ID: {submission_id} for hub ID: {hub_id}")

            # Add new hubs and submissions in bulk
            if new_hubs:
                db.bulk_save_objects(new_hubs)
            if new_submissions:
                db.bulk_save_objects(new_submissions)
            db.commit()

            # Add metrics to the analytics data dictionary
            # Query to get the count of males and females
            male_count = db.query(func.count(Submission.id)).filter(Submission.gender == 'male').scalar()
            female_count = db.query(func.count(Submission.id)).filter(Submission.gender == 'female').scalar()
            total_count = male_count + female_count

            # INDICATORS
            # Query to get all submissions
            submissions = db.query(Submission.time_saved, Submission.hours_taken_to_use, Submission.additional_shea_collected_due_to_roller).all()
            
            # Convert the query results to a pandas DataFrame
            df = pd.DataFrame(submissions, columns=['time_saved', 'hours_taken_to_use', 'additional_shea_collected_due_to_roller'])

            # Calculate average time saved and average hours taken to use
            average_time_saved = np.round(df['time_saved'].dropna().mean(), 2) if not df['time_saved'].dropna().empty else None
            average_hours_taken_to_use = np.round(df['hours_taken_to_use'].dropna().mean(), 2) if not df['hours_taken_to_use'].dropna().empty else None
            average_additional_shea_collected_due_to_roller = np.round(df['additional_shea_collected_due_to_roller'].dropna().mean(), 2) if not df['additional_shea_collected_due_to_roller'].dropna().empty else None

            # Calculate percentages
            percentage_male = np.round((male_count / total_count) * 100, 0) if total_count else 0
            percentage_female = np.round((female_count / total_count) * 100, 0) if total_count else 0

            # ANALYTICS DATA
            analytics_data['total_submissions'] = data['count']
            analytics_data['today_submissions'] = db.query(func.count(Submission.id)).filter(Submission.today == today_date).scalar()
            analytics_data['total_hubs'] = db.query(func.count(func.distinct(Hub.id))).scalar()
            analytics_data['growth_rate'] = calculate_growth_rate(db=db)
            analytics_data['respondents'] = {
                "male": male_count,
                "percentage_male": percentage_male,
                "female": female_count,
                "percentage_female": percentage_female
            }
            analytics_data['indicators'] = {
                "average_time_saved": average_time_saved,
                "time_saved_allocation": get_time_saved_allocation(db=db),
                "average_hours_taken_to_use": average_hours_taken_to_use,
                "average_additional_shea_collected_due_to_roller": average_additional_shea_collected_due_to_roller
            }
            analytics_data['hubs_submissions'] = return_hubs_list(db=db)

            
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Error processing data: {e}")

