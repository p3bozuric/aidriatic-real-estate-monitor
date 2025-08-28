import asyncio
import re
import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
from crawl4ai import *

def clean_and_extract_real_estate_info(markdown_content: str, id: str) -> Dict[str, Any]:
    """
    Extract real estate information from Croatian real estate website markdown content.
    
    Args:
        markdown_content (str): Raw markdown content from the real estate website
        id (str): Unique identifier for the listing
        
    Returns:
        Dict[str, Any]: Extracted real estate information in JSON format
    """
    
    def clean_text(text: str) -> str:
        """Clean and normalize text by removing extra whitespace and newlines."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def extract_number(text: str) -> Optional[int]:
        """Extract numeric value from text, handling various formats."""
        if not text or text in ['-', '']:
            return None
        # Remove currency symbols, commas, and extract numbers
        numbers = re.findall(r'[\d,]+', str(text).replace(',', ''))
        return int(numbers[0]) if numbers else None
    
    def extract_price_and_currency(price_text: str) -> tuple:
        """Extract price number and currency from price text."""
        if not price_text:
            return None, None
        
        # Remove HTML tags and clean text
        clean_price = re.sub(r'<[^>]+>', '', price_text)
        clean_price = clean_price.replace(',', '').strip()
        
        # Extract currency symbol
        currency_match = re.search(r'[€$£]', clean_price)
        currency = currency_match.group() if currency_match else None
        
        # Extract price number
        price_match = re.search(r'([\d.]+)', clean_price)
        price = int(float(price_match.group())) if price_match else None
        
        return price, currency
    
    def find_description(content: str, id: str) -> str:
        """Extract descriptions for croatian, english and german."""

        content = content.split(f"[Ruski](http://www.realestatecroatia.com/rus/detail.asp?id={id})\n")[1]

        croatian_desc = content.split("\nInterni broj: **")[0]
        english_desc = content.split(f"REC ID: **{id}**\n")[1].split("\nIntrnal number:")[0]
        german_desc = content.split(f"REC ID: **{id}**\n")[2].split("\nInterne Nummer:")[0]

        return croatian_desc, english_desc, german_desc
        
    # Initialize result dictionary
    result = {
        "Vrsta nekretnine": "",
        "Vrsta prometa": "",
        "Županija": "",
        "Općina": "",
        "Mjesto": "",
        "ID": id,
        "Cijena": None,
        "Currency": None,
        "Površina": None,
        "Broj soba": None,
        "Broj parkirnih mjesta": None,
        "Pogled": "",
        "Okućnica": "",
        "Broj kupaona": None,
        "Garaža": None,
        "Blizina transporta": "",
        "Blizina plaže": "",
        "Kat": None,
        "Lift": "",
        "Croatian description": "",
        "English description": "",
        "German description": ""
    }
    
    # Extract and parse title
    first_line = markdown_content.splitlines()[0]
    if first_line:
        # Split title by " - " to get components
        title_parts = [part.strip() for part in first_line.split(' - ')]
        
        if len(title_parts) >= 3:
            # First part is property type
            result["Vrsta nekretnine"] = title_parts[0]
            # Second part is transaction type
            result["Vrsta prometa"] = title_parts[1]
            # Remaining parts form the location (ŽUPANIJA - OPĆINA - MJESTO)
            location_parts = title_parts[2:]
            
            if len(location_parts) >= 3:
                result["Županija"] = location_parts[0]
                result["Općina"] = location_parts[1]
                result["Mjesto"] = location_parts[2]
            elif len(location_parts) == 2:
                # Handle case with only 2 location parts
                result["Županija"] = location_parts[0]
                result["Općina"] = location_parts[1]
                result["Mjesto"] = location_parts[1]  # Use same as općina
            elif len(location_parts) == 1:
                # Handle case with only 1 location part
                result["Mjesto"] = location_parts[0]
    
    
    # Extract price and currency
    price_match = re.search(r'###\s*([\d,]+\.?\d*)\s*€', markdown_content)
    if price_match:
        price_text = price_match.group(0)
        price, currency = extract_price_and_currency(price_text)
        result["Cijena"] = price
        result["Currency"] = currency
    
    # Extract property details from the table
    property_details = {
        r'Površina:\s*\|\s*\*\*(\d+)\s*m2?\*\*': "Površina",
        r'Broj soba:\s*\|\s*\*\*(\d+)\*\*': "Broj soba",
        r'Broj parkirnih mjesta:\s*\|\s*\*\*(\d+)\*\*': "Broj parkirnih mjesta",
        r'Pogled:\s*\|\s*\*\*([^*\n]+)\*\*': "Pogled",
        r'Okućnica:\s*\|\s*\*\*([^*\n]+)\*\*': "Okućnica",
        r'Broj kupaona:\s*\|\s*\*\*(\d+)\*\*': "Broj kupaona",
        r'Garaža:\s*\|\s*\*\*(\d+)\*\*': "Garaža",
        r'Blizina transporta:\s*\|\s*\*\*([^*\n]+)\*\*': "Blizina transporta",
        r'Blizina plaže:\s*\|\s*\*\*([^*\n]+)\*\*': "Blizina plaže",
        r'Kat:\s*\|\s*\*\*(\d+)\*\*': "Kat",
        r'Lift:\s*\|\s*\*\*([^*\n]+)\*\*': "Lift"
    }
    
    for pattern, key in property_details.items():
        match = re.search(pattern, markdown_content)
        if match:
            value = match.group(1).strip()
            if key in ["Površina", "Broj soba", "Broj parkirnih mjesta", "Broj kupaona", "Garaža", "Kat"]:
                result[key] = extract_number(value)
            else:
                result[key] = clean_text(value)
    
    # Extract Croatian description
    croatian_desc, english_desc, german_desc = find_description(markdown_content, id=id)
    
    result["Croatian description"] = clean_text(croatian_desc)

    result["German description"] = clean_text(german_desc)

    result["English description"] = clean_text(english_desc)
    
    return result

def save_to_json(data: Dict[str, Any], filename: str = "real_estate_data.json") -> None:
    """
    Save the extracted data to a JSON file.
    
    Args:
        data (Dict[str, Any]): Extracted real estate data
        filename (str): Output filename for JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def run_crawl_job(url):
    """
    Crawl a real estate website and return the markdown content.
    
    Args:
        url (str): URL to crawl
        
    Returns:
        str: Markdown content from the crawled page
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown
    
def save_crawl_job_markdown(markdown, id=None, folder="crawl_export"):
    """
    Save crawled markdown content to a file.
    
    Args:
        markdown (str): Markdown content to save
        folder (str): Folder to save the file in
        
    Returns:
        str: Path to the saved file
    """

    # Prepare export folder and filename
    os.makedirs(folder, exist_ok=True)

    if id:
        filename = f"crawl_export_{id}.md"
    else:
        timestamp = datetime.now().strftime("%d%m%Y%H")
        filename = f"crawl_export_{timestamp}.md"

    filepath = os.path.join(folder, filename)

    # Save the markdown to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Saved crawl job markdown to {filepath}")
    return filepath

def clean_file(content: str) -> str:
    """
    Clean the crawled markdown content by removing unwanted sections.

    Args:
        content (str): Raw markdown content to clean

    Returns:
        str: Cleaned content
    """
    # Remove content before the main property listing
    marker = "#### "
    if marker in content:
        cleaned_content = "".join(content.split(marker)[1:])
    else:
        cleaned_content = content

    # Remove content after the contact section
    if "[Uspostavi kontakt]" in cleaned_content:
        cleaned_content = cleaned_content.split("[Uspostavi kontakt]")[0]

    return cleaned_content

def process_real_estate_listing(url: str, id: str, output_folder: str = "real_estate_export") -> Dict[str, Any]:
    """
    Complete pipeline: crawl, clean, and extract real estate data.
    
    Args:
        url (str): URL of the real estate listing
        id (str): Unique identifier for the listing
        output_folder (str): Folder to save output files
        
    Returns:
        Dict[str, Any]: Extracted real estate information
    """
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Step 1: Crawl the website
    print(f"Crawling {url}...")
    markdown = asyncio.run(run_crawl_job(url))

    # Step 2: Clean the file
    print("Cleaning markdown...")
    cleaned_content = clean_file(markdown)
    
    # Step 3: Save raw markdown
    markdown_filepath = save_crawl_job_markdown(cleaned_content, id, output_folder)
    
    # Step 4: Extract real estate information
    print("Extracting real estate information...")
    extracted_data = clean_and_extract_real_estate_info(cleaned_content, id)
    
    json_filename = f"real_estate_data_{extracted_data["ID"]}.json"
    json_filepath = os.path.join(output_folder, json_filename)
    
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved extracted data to {json_filepath}")
    
    return extracted_data

# Example usage:
if __name__ == "__main__":
    # Example URL - replace with actual real estate listing URL
    url = "http://www.realestatecroatia.com/hrv/detail.asp?id=1209086"
    
    try:
        # Process the real estate listing
        data = process_real_estate_listing(url)
        
        # Print the extracted data
        print("\nExtracted Real Estate Information:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Error processing real estate listing: {e}")
    
    # Alternative: If you already have markdown content
    # with open('your_existing_file.md', 'r', encoding='utf-8') as f:
    #     markdown_content = f.read()
    # 
    # extracted_data = clean_and_extract_real_estate_info(markdown_content)
    # save_to_json(extracted_data, "real_estate_output.json")