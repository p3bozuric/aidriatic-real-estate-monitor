import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Union
from loguru import logger
import bcrypt

class PasswordService:
    """
    Password service class for hashing and verifying passwords.
    """

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash a plain text password using bcrypt
        
        Args:
            plain_password: The plain text password
            
        Returns:
            str: The hashed password (includes salt)
        """

        # Generate salt
        salt = bcrypt.gensalt(rounds=12)

        # Hash password with salt
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)

        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password
        
        Args:
            plain_password: The plain text password to verify
            hashed_password: The stored hashed password
            
        Returns:
            bool: True if passwords match, False otherwise
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
        
class DatabaseControl:
    """
    Database control class for managing properties and users tables.
    """
    
    def __init__(self):
        """Initialize database connection parameters."""

        load_dotenv()

        self.password_service = PasswordService()

        self.connection_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'database': os.getenv('POSTGRES_DB', 'myproject_db'),
            'user': os.getenv('POSTGRES_USER', 'myuser'),
            'password': os.getenv('POSTGRES_PASSWORD', 'mypassword'),
            'port': os.getenv('POSTGRES_EXPOSED_PORT', '5432')
        }
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.connection_params)
    
    def insert_property(self, property_data: Dict[str, Any]) -> bool:
        """
        Insert a new property row into the properties table.
        
        Args:
            property_data: Dictionary containing property information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Map dictionary keys to database columns
            columns = [
                'id_int', 'property_type', 'transaction_type', 'county', 'municipality', 
                'place', 'id', 'price', 'currency', 'area', 'number_of_rooms',
                'number_of_parking_spaces', 'view', 'garden', 'number_of_bathrooms',
                'garage', 'near_transport', 'near_beach', 'floor', 'elevator',
                'croatian_description', 'english_description', 'german_description'
            ]
            
            # Map input keys to database columns
            key_mapping = {
                'Property type': 'property_type',
                'Transaction type': 'transaction_type',
                'County': 'county',
                'Municipality': 'municipality',
                'Place': 'place',
                'ID': 'id',
                'Price': 'price',
                'Currency': 'currency',
                'Area': 'area',
                'Number of rooms': 'number_of_rooms',
                'Number of parking spaces': 'number_of_parking_spaces',
                'View': 'view',
                'Garden': 'garden',
                'Number of bathrooms': 'number_of_bathrooms',
                'Garage': 'garage',
                'Near transport': 'near_transport',
                'Near beach': 'near_beach',
                'Floor': 'floor',
                'Elevator': 'elevator',
                'Croatian description': 'croatian_description',
                'English description': 'english_description',
                'German description': 'german_description'
            }
            
            # Prepare values
            values = []

            id_int = int(property_data['ID'])
            
            property_data['id_int'] = id_int

            for col in columns:
                original_key = next((k for k, v in key_mapping.items() if v == col), col)
                value = property_data.get(original_key, '')
                
                # Convert None to 0 for numeric fields
                if value is None and col in ['price', 'area', 'number_of_rooms', 
                                           'number_of_parking_spaces', 'number_of_bathrooms', 'floor']:
                    value = 0
                elif value is None:
                    value = ''
                    
                values.append(value)
            
            # Insert query
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            
            query = f"INSERT INTO properties ({columns_str}) VALUES ({placeholders})"
            cur.execute(query, values)
            
            conn.commit()
            cur.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.info(f"Error inserting property: {e}")
            return False
    
    def insert_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Insert a new user into the users table.
        
        Args:
            user_data: Dictionary containing user information (email, username, first_name, last_name, password)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            password_hash = self.password_service.hash_password(user_data.get('password', ''))

            user_data['password_hash'] = password_hash
            
            query = """
            INSERT INTO users (email, username, first_name, last_name, password_hash)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (
                user_data.get('email', ''),
                user_data.get('username', ''),
                user_data.get('first_name', ''),
                user_data.get('last_name', ''),
                user_data.get('password_hash', '')
            )
            
            cur.execute(query, values)
            conn.commit()
            cur.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.info(f"Error inserting user: {e}")
            return False
  
    def remove_user(self, username: str) -> bool:
        """
        Remove a user based on username.
        
        Args:
            username: User's username
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM users WHERE username = %s", (username,))
            rows_affected = cur.rowcount
            
            conn.commit()
            cur.close()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            logger.info(f"Error removing user: {e}")
            return False
    
    def update_user(self, username: str, user_data: Dict[str, Any]) -> bool:
        """
        Update an existing user based on username.
        
        Args:
            username: User's username
            user_data: Dictionary containing updated user information (first_name, last_name, old_password, new_password)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            if 'old_password' in user_data and 'new_password' in user_data:
                # Verify old password
                cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
                result = cur.fetchone()
                
                if not result:
                    return False
                
                stored_hash = result[0]
                
                if not self.password_service.verify_password(user_data['old_password'], stored_hash):
                    return False
                
                # Hash new password
                new_hashed = self.password_service.hash_password(user_data['new_password'])
                user_data['password_hash'] = new_hashed
            
            # Build update query dynamically
            set_clauses = []
            values = []
            
            field_mapping = {
                'first_name': 'first_name',
                'last_name': 'last_name',
                'password_hash': 'password_hash'
            }
            
            for key, db_field in field_mapping.items():
                if key in user_data:
                    set_clauses.append(f"{db_field} = %s")
                    values.append(user_data[key])
            
            if not set_clauses:
                return False
            
            values.append(username)
            
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE username = %s"
            cur.execute(query, values)
            
            rows_affected = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            logger.info(f"Error updating user: {e}")
            return False
    
    def insert_user_goal(self, user_goal_data: Dict[str, Any]) -> bool:
        """
        Insert a new user into the user_goals table.
        
        Args:
            user_data: Dictionary containing user information user_id, transaction_type, property_types (list), min_price, max_price, min_m2, max_m2, location_counties (list), cities (list), description)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Convert lists to comma-separated strings
            property_types = ','.join(user_goal_data.get('property_types', []))
            location_counties = ','.join(user_goal_data.get('location_counties', []))
            cities = ','.join(user_goal_data.get('cities', []))
            
            query = """
            INSERT INTO user_goals (user_id, transaction_type, 
                             property_types, min_price, max_price, min_m2, max_m2,
                             location_counties, cities, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_goal_data.get('user_id', ''),
                user_goal_data.get('transaction_type', ''),
                property_types,
                user_goal_data.get('min_price', 0),
                user_goal_data.get('max_price', 0),
                user_goal_data.get('min_m2', 0),
                user_goal_data.get('max_m2', 0),
                location_counties,
                cities,
                user_goal_data.get('description', '')
            )
            
            cur.execute(query, values)
            conn.commit()
            cur.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.info(f"Error inserting user: {e}")
            return False
        
    def remove_user_goal(self, user_goal_id: int) -> bool:
        """
        Remove a user goal based on user_goal_id.
        
        Args:
            user_goal_id: User goal's ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM user_goals WHERE id = %s", (user_goal_id,))
            rows_affected = cur.rowcount
            
            conn.commit()
            cur.close()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            logger.info(f"Error removing user goal: {e}")
            return False
        
    def update_user_goal(self, user_goal_id: int, user_goal_data: Dict[str, Any]) -> bool:
        """
        Update an existing user goal based on user_goal_id.
        
        Args:
            user_goal_id: User goal's ID
            user_goal_data: Dictionary containing updated user goal information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Build update query dynamically
            set_clauses = []
            values = []
            
            field_mapping = {
                'user_id': 'user_id',
                'transaction_type': 'transaction_type',
                'min_price': 'min_price',
                'max_price': 'max_price',
                'min_m2': 'min_m2',
                'max_m2': 'max_m2',
                'description': 'description'
            }
            
            for key, db_field in field_mapping.items():
                if key in user_goal_data:
                    set_clauses.append(f"{db_field} = %s")
                    values.append(user_goal_data[key])
            
            # Handle list fields
            if 'property_types' in user_goal_data:
                set_clauses.append("property_types = %s")
                values.append(','.join(user_goal_data['property_types']))
            
            if 'location_counties' in user_goal_data:
                set_clauses.append("location_counties = %s")
                values.append(','.join(user_goal_data['location_counties']))
            
            if 'cities' in user_goal_data:
                set_clauses.append("cities = %s")
                values.append(','.join(user_goal_data['cities']))
            
            if not set_clauses:
                return False
            
            # WHERE
            values.append(user_goal_id) 
            
            query = f"UPDATE user_goals SET {', '.join(set_clauses)} WHERE id = %s"
            cur.execute(query, values)
            
            rows_affected = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            logger.info(f"Error updating user goal: {e}")
            return False
        
    def get_highest_id_int(self) -> int:
        """
        Get the highest ID_int value from the properties table.
        
        Returns:
            int: Highest ID_int value, 0 if no records exist
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT MAX(id_int) FROM properties")
            result = cur.fetchone()
            
            cur.close()
            conn.close()
            
            return result[0] if result[0] is not None else 0
            
        except Exception as e:
            logger.info(f"Error getting highest ID: {e}")
            return 0
  
    def verify_user_email(self, username: str) -> bool:
        """
        Mark a user's email as verified based on username.
        
        Args:
            username: User's username
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("UPDATE users SET email_verified = TRUE WHERE username = %s", (username,))
            rows_affected = cur.rowcount
            
            conn.commit()
            cur.close()
            conn.close()
            
            return rows_affected > 0
            
        except Exception as e:
            logger.info(f"Error verifying user email: {e}")
            return False
        
    def get_user_goals_dataframe(self, user_id) -> pd.DataFrame:
        """
        Extract all user user goals to a pandas DataFrame.
        
        Returns:
            pd.DataFrame: DataFrame containing all user data
        """
        try:
            conn = self._get_connection()
            
            query = "SELECT * FROM user_goals WHERE user_id = %s"
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            # Convert comma-separated strings back to lists for list columns
            list_columns = ['property_types', 'location_counties', 'cities']
            for col in list_columns:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: x.split(',') if x else [])
            
            conn.close()
            return df
            
        except Exception as e:
            logger.info(f"Error getting users dataframe: {e}")
            return pd.DataFrame()
    
    def filter_properties(self, transaction_type: str = None, property_types: str = None, 
                         counties: str = None, min_price: int = None, max_price: int = None,
                         min_area: int = None, max_area: int = None, min_id: int = None) -> List[int]:
        """
        Filter properties based on criteria and return list of ID_int values.
        
        Args:
            transaction_type: Transaction type filter
            property_types: Property type filter
            counties: Counties filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_area: Minimum area filter (m2)
            max_area: Maximum area filter (m2)
            
        Returns:
            List[int]: List of ID_int values that match criteria
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Build WHERE clauses
            where_clauses = []
            values = []
            
            if transaction_type:
                where_clauses.append("transaction_type = %s")
                values.append(transaction_type)
            
            if property_types:
                property_types_placeholders = ', '.join(['%s'] * len(property_types))
                where_clauses.append(f"property_type in ({property_types_placeholders})")
                values.extend(property_types)
            
            if counties:
                placeholders = ', '.join(['%s'] * len(counties))
                where_clauses.append(f"county IN ({placeholders})")
                values.extend(counties)
            
            if min_price is not None:
                where_clauses.append("price >= %s")
                values.append(min_price)
            
            if max_price is not None:
                where_clauses.append("price <= %s")
                values.append(max_price)
            
            if min_area is not None:
                where_clauses.append("area >= %s")
                values.append(min_area)
            
            if max_area is not None:
                where_clauses.append("area <= %s")
                values.append(max_area)

            if min_id is not None:
                where_clauses.append("id_int >= %s")
                values.append(min_id)
            
            # Build and execute query
            base_query = "SELECT id_int FROM properties"
            if where_clauses:
                query = f"{base_query} WHERE {' AND '.join(where_clauses)}"
                cur.execute(query, values)
            else:
                cur.execute(base_query)
            
            results = cur.fetchall()
            id_list = [row[0] for row in results]
            
            cur.close()
            conn.close()
            
            return id_list
            
        except Exception as e:
            logger.info(f"Error filtering properties: {e}")
            return []
    
    def get_property_by_id(self, id_value: Union[str, int]) -> Dict[str, Any]:
        """
        Extract all values from properties table based on ID or ID_int.
        
        Args:
            id_value: Either string ID or integer ID_int
            
        Returns:
            Dict[str, Any]: Property data or empty dict if not found
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Determine which field to search by
            if isinstance(id_value, int):
                query = "SELECT * FROM properties WHERE id_int = %s"
            else:
                query = "SELECT * FROM properties WHERE id = %s"
            
            cur.execute(query, (id_value,))
            result = cur.fetchone()
            
            cur.close()
            conn.close()
            
            return dict(result) if result else {}
            
        except Exception as e:
            logger.info(f"Error getting property by ID: {e}")
            return {}
    
    def get_properties_by_ids(self, id_values: List[Union[str, int]]) -> Dict[str, Dict[str, Any]]:
        """ 
        Extract all values from properties table for a list of IDs or ID_ints.
        
        Args:
            id_values: List of either string IDs or integer ID_ints
            
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary with ID as key and property data as value
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            if not id_values:
                return {}
            
            # Determine which field to search by based on first element
            if isinstance(id_values[0], int):
                placeholders = ', '.join(['%s'] * len(id_values))
                query = f"SELECT * FROM properties WHERE id_int IN ({placeholders})"
                key_field = 'id_int'
            else:
                placeholders = ', '.join(['%s'] * len(id_values))
                query = f"SELECT * FROM properties WHERE id IN ({placeholders})"
                key_field = 'id'
            
            cur.execute(query, id_values)
            results = cur.fetchall()
            
            # Build result dictionary
            result_dict = {}
            for row in results:
                row_dict = dict(row)
                result_dict[str(row_dict[key_field])] = row_dict
            
            cur.close()
            conn.close()
            
            return result_dict
            
        except Exception as e:
            logger.info(f"Error getting properties by IDs: {e}")
            return {}

