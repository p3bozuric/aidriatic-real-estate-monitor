from loguru import logger
from app.database.control import DatabaseControl
from app.filtering.filter import hard_filter, soft_filter, presentation
from app.emailing.email import send_email
import json
import os

def get_min():
    # Load initial_min_id from job_data/job_runner_data.json
    job_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "job_data", "job_runner_data.json")
    with open(job_data_path, "r", encoding="utf-8") as f:
        job_data = json.load(f)

    return job_data.get("initial_min_id", None)

def main():
    db = DatabaseControl()
    users_df = db.get_users_dataframe()
    
    min_id = get_min()

    for row in users_df.iterrows():
        user = row[1]

        email = user['email']
        criteria = {
            'transaction_type': user['transaction_type'],
            'property_type': user['property_types'],
            'county': user['location_counties'],
            'min_price': user['min_price'],
            'max_price': user['max_price'],
            'min_area': user['min_m2'],
            'max_area': user['max_m2'],
            'min_id': min_id
        }
        personal_criteria = user['description']


        # Hard filter the listings 
        json_data = hard_filter(criteria)

        if not json_data:
            logger.info(f"No listings passed the hard filter for user {email}")
            continue

        # Soft filter the listings using personal criteria
        soft_filtered_listings = soft_filter(json_data, personal_criteria)

        if soft_filtered_listings == "NO" or soft_filtered_listings == "":
            logger.info(f"No listings matched for user {email}")
            continue

        # Convert the comma-separated string of IDs to a list of integers
        filtered_list = [int(id.strip()) for id in soft_filtered_listings.split(",")]

        # Get the final listings that passed both filters
        final_listings = [json_data[id] for id in filtered_list if id in json_data]

        # Generate the email content
        email_content = presentation(final_listings, user)

        send_email(email, 
                subject="Daily Property Insights",
                body=email_content)
    
if __name__ == "__main__":
    main()