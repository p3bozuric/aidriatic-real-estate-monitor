import psycopg2
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Union
from loguru import logger

# Load environment variables
load_dotenv()

def setup_database():
    """
    Setup database with required tables if they don't exist.
    """
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'myproject_db'),
            user=os.getenv('POSTGRES_USER', 'myuser'),
            password=os.getenv('POSTGRES_PASSWORD', 'mypassword'),
            port=os.getenv('POSTGRES_EXPOSED_PORT', '5432')
        )
        
        cur = conn.cursor()
        
        # Create properties table
        create_properties_table = """
        CREATE TABLE IF NOT EXISTS properties (
            id_int SERIAL PRIMARY KEY,
            property_type VARCHAR(255) DEFAULT '',
            transaction_type VARCHAR(255) DEFAULT '',
            county VARCHAR(255) DEFAULT '',
            municipality VARCHAR(255) DEFAULT '',
            place VARCHAR(255) DEFAULT '',
            id VARCHAR(255) DEFAULT '',
            price INTEGER DEFAULT 0,
            currency VARCHAR(10) DEFAULT '',
            area INTEGER DEFAULT 0,
            number_of_rooms INTEGER DEFAULT 0,
            number_of_parking_spaces INTEGER DEFAULT 0,
            view VARCHAR(255) DEFAULT '',
            garden VARCHAR(255) DEFAULT '',
            number_of_bathrooms INTEGER DEFAULT 0,
            garage VARCHAR(255) DEFAULT '',
            near_transport VARCHAR(255) DEFAULT '',
            near_beach VARCHAR(255) DEFAULT '',
            floor INTEGER DEFAULT 0,
            elevator VARCHAR(255) DEFAULT '',
            croatian_description TEXT DEFAULT '',
            english_description TEXT DEFAULT '',
            german_description TEXT DEFAULT ''
        );
        """
        
        # Create users table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(255) PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            transaction_type VARCHAR(255) NOT NULL,
            property_types TEXT DEFAULT '',
            min_price INTEGER DEFAULT 0,
            max_price INTEGER DEFAULT 0,
            min_m2 INTEGER DEFAULT 0,
            max_m2 INTEGER DEFAULT 0,
            location_counties TEXT DEFAULT '',
            cities TEXT DEFAULT '',
            description TEXT DEFAULT ''
        );
        """
        
        cur.execute(create_properties_table)
        logger.info("Properties table exists or has been created.")

        cur.execute(create_users_table)
        logger.info("Users table exists or has been created.")
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info("Database setup completed successfully!")
        logger.info("Created tables: properties, users")
        
    except Exception as e:
        logger.info(f"Error setting up database: {e}")

if __name__ == "__main__":
    # Setup database tables
    setup_database()

    from database.control import DatabaseControl
    
    # Example usage
    db = DatabaseControl()
    
    # Test inserting a property
    sample_property = {
        "Property type": "apartment",
        "Transaction type": "sale",
        "County": "Zagreb",
        "Municipality": "Zagreb",
        "Place": "Center",
        "ID": "ZG001",
        "Price": 150000,
        "Currency": "€",
        "Area": 65,
        "Number of rooms": 2,
        "Number of parking spaces": 1,
        "View": "city",
        "Garden": "no",
        "Number of bathrooms": 1,
        "Garage": "yes",
        "Near transport": "yes",
        "Near beach": "no",
        "Floor": 3,
        "Elevator": "yes",
        "Croatian description": "Lijepa nekretnina u centru",
        "English description": "Beautiful property in the center",
        "German description": "Schöne Immobilie im Zentrum"
    }
    
    # Test inserting a user
    sample_user = {
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "transaction_type": "buy",
        "property_types": ["apartment", "house"],
        "min_price": 100000,
        "max_price": 200000,
        "min_m2": 50,
        "max_m2": 100,
        "location_counties": ["Zagreb", "Split"],
        "cities": ["Zagreb", "Split"],
        "description": "Looking for a modern apartment or house with good transport connections"
    }
    
    print("Example setup completed!")