from litellm import completion
import os
from dotenv import load_dotenv
from database.control import DatabaseControl

load_dotenv()

def hard_filter(criteria):
    """
    Filters real estate listings from database based on specified criteria.
    Args:
        criteria (dict): A dictionary containing filter parameters, which may include:
            - 'transaction_type' (str): Type of transaction (e.g., 'Prodaja', 'Najam').
            - 'property_types' list(str): List of types of properties (e.g., ['Kuća', 'Stan']).
            - 'county' list(str): List of counties or regions to filter by.
            - 'min_price' (float or int): Minimum price.
            - 'max_price' (float or int): Maximum price.
            - 'min_area' (float or int): Minimum area in square meters.
            - 'max_area' (float or int): Maximum area in square meters.
            - 'min_id' (int): Minimum ID to filter new listings.
    Returns:
        list: A list of property dictionaries that match the given criteria.
    """
    db = DatabaseControl()

    realestate_id_list = db.filter_properties(transaction_type=criteria['transaction_type'], 
                                              property_types=criteria['property_type'], 
                                              counties=criteria['county'], 
                                              min_price=criteria['min_price'], 
                                              max_price=criteria['max_price'], 
                                              min_area=criteria['min_area'], 
                                              max_area=criteria['max_area'],
                                              min_id=criteria['min_id'])
    
    properties_dict = db.get_properties_by_ids(realestate_id_list)

    if properties_dict is None:
        return []

    list_of_property_dicts = [properties_dict[str(id)] for id in realestate_id_list]

    return list_of_property_dicts

def soft_filter(json_data, personal_criteria):
    """
    Filters real estate listings based on user-defined personal criteria using an AI language model.
    Args:
        json_data (str): A string representation of the JSON data containing real estate listings that passed the initial hard filter.
        personal_criteria (str): A string describing the user's personal preferences for filtering listings.
    Returns:
        str: A string representation of a list of integers, where each integer is the ID of a real estate listing that matches the user's preferences.
    Note:
        The function uses an AI model to evaluate the listings and returns only the IDs of those that match the criteria.
    """
    system_prompt = """You are a helpful assistant that filters real estate listings based on user preferences. 
    You use the provided personal criteria to evaluate each listing in the JSON data. Only return a list of integers which represent real estate ID numbers that match the user's preferences.
    If no listings match, return only word "NO", otherwise return a list of integers like this: "12345, 67890"
    Do not return any text other than the list of integers or empty list.
    Examples of your output: "12345,67890", "", "54321" """
    prompt = f"""These are the listing that got through the initial hard filter:
    {json_data}
    
    This is the user's personal criteria:
    {personal_criteria}

    Return only a comma separated list of integers which represent real estate ID numbers that match the user's preferences."""
    
    response = completion(
        model="groq/openai/gpt-oss-120b", 
        messages=[
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": prompt}
       ],
       
    )
    
    return response.choices[0].message['content']

def presentation(property_list, user_information):
    """
    Generates an attractive HTML email presenting a list of real estate properties for a client.
    This function takes a list of property dictionaries and user information, then uses an LLM to generate a professional, responsive HTML email. The email includes a header, welcome message, property cards with key details, and a footer, all styled for email compatibility.
    Args:
        property_list (list): A list of dictionaries, each representing a property with fields such as property type, location, price, area, features, and description.
        user_information (dict): Information about the user receiving the email
    Returns:
        str: A complete HTML email as a string, ready to be sent via AWS SES.
    """

    system_prompt = """You are a Croatian real estate email generator. You will receive a list of pre-filtered JSON property objects that represent the best suitable properties for a client from today.

Your task is to create an attractive HTML email that presents these properties as a "Daily Property Insights" email.

Input format: Array of JSON objects with property data including fields like Property type, Transaction type, County, Municipality, Place, ID, Price, Currency, Area, Number of rooms, View, Near transport, Near beach, Floor, Elevator, English description, etc.

Create an HTML email with:

1. Professional email header with "Daily Property Insights - [Current Date]"
2. Brief welcome message (2-3 sentences)
3. Property cards for each property showing:
   - Property type and location
   - Price and currency
   - Area in m²
   - Number of rooms and bathrooms
   - Key features (view, transport, beach proximity, elevator, etc.)
   - Brief description from English description field
   - Calculate and show price per m²
4. Professional footer

HTML Requirements:
- Use inline CSS styles only
- Table-based layout for email compatibility
- Max-width 600px
- Professional blue/gray color scheme
- Web-safe fonts (Arial, Helvetica, sans-serif)
- Responsive design
- Clean, modern look

Format the response as complete HTML email ready for sending via AWS SES.

Handle null values gracefully and convert "+" symbols to "Yes" for better readability."""
    prompt = f"""These are the listings you need to present in the email:
    {[json for json in property_list]}

    This is the user information:
    {user_information}"""
    
    response = completion(
        model="groq/openai/gpt-oss-120b", 
        messages=[
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": prompt}
       ],
       
    )
    
    return response.choices[0].message['content']