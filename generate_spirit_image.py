import csv
import requests
import time
import json
import os
from urllib.parse import urlparse
from pathlib import Path
from dotenv import load_dotenv

# At the top of the file
load_dotenv()

# Update API configuration
IDEOGRAM_API_KEY = os.getenv('IDEOGRAM_API_KEY')
IDEOGRAM_API_URL = 'https://api.ideogram.ai/generate'

headers = {
    'Api-Key': IDEOGRAM_API_KEY,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def generate_and_download_spirit_animal_image(gender):
    input_file = f'october/spooky_spirit_prompt_{gender}_data.csv'
    output_directory = f'october/spirit_animal_images_{gender}/orig'
    output_csv = f'october/generated_spirit_animal_image_{gender}.csv'
    
    os.makedirs(output_directory, exist_ok=True)

    # First, create the output CSV with headers if it doesn't exist
    if not os.path.exists(output_csv):
        with open(output_csv, 'w', newline='') as outfile:
            reader = csv.DictReader(open(input_file, 'r'))
            fieldnames = reader.fieldnames + ['spirit_animal_image_url']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

    # Now, open the input file for reading and output file for appending
    with open(input_file, 'r') as infile, open(output_csv, 'a', newline='') as outfile:
        reader = csv.DictReader(infile)
        # Get total rows first
        rows = list(reader)
        total_rows = len(rows)
        
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames + ['spirit_animal_image_url'])

        for counter, row in enumerate(rows, 1):
            try:
                prompt = row['spirit_animal_image_prompt']
                print(f"\n[{counter}/{total_rows}] Processing:")
                print(f"Profile ID: {row['profile_id']}")
                print(f"Prompt: {prompt[:100]}...")  # Show first 100 chars
                
                # Update payload structure to include image_request wrapper
                payload = {
                    "image_request": {
                        "model": "V_2",
                        "magic_prompt_option": "AUTO",
                        "aspect_ratio": "ASPECT_1_1",
                        "prompt": prompt,
                        "style_type": "GENERAL",
                        "negative_prompt": "words, human faces, negativity of tone, watercolors"
                    }
                }

                # Make the API request
                response = requests.post(IDEOGRAM_API_URL, json=payload, headers=headers)
                        
                if response.status_code != 200:
                    print(f"Error Status Code: {response.status_code}")
                    print(f"Error Response: {response.text}")
                    print(f"Request Headers: {headers}")
                    print(f"Request Payload: {json.dumps(payload, indent=2)}")
                    
                if response.status_code == 200:
                    data = response.json()
                    print(f"API Response: {json.dumps(data, indent=2)}")  # Debug line
                    
                    image_url = data['data'][0]['url']
                    
                    # Parse the animal_interpretation JSON
                    animal_interpretation = json.loads(row['animal_interpretation'])
                    animal = animal_interpretation['spiritAnimalRecommendation']['animal']
                    
                    print(f"Downloading image from: {image_url}")  # Debug line
                    
                    # Download the image
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        # Generate filename
                        animal_underscore = animal.replace(' ', '_')
                        file_extension = '.png'  # Ideogram always returns PNGs
                        new_filename = f"{row['profile_id']}_{row['first_name']}_{animal_underscore}{file_extension}"
                        file_path = os.path.join(output_directory, new_filename)
                        
                        # Save image
                        with open(file_path, 'wb') as img_file:
                            img_file.write(image_response.content)
                        print(f"Saved image to: {file_path}")  # Debug line
                        
                        # Update CSV
                        row['spirit_animal_image_url'] = new_filename
                        writer.writerow(row)
                        outfile.flush()  # Force write to disk
                        print(f"Updated CSV with new row")  # Debug line
                    else:
                        print(f"Failed to download image. Status: {image_response.status_code}")
                        
                else:
                    print(f"[{counter}/{total_rows}] Error downloading image for prompt: {row['spirit_animal_image_prompt']}")
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                print(f"Full error: {e.__class__.__name__}: {str(e)}")
                continue

    print(f"Generated and downloaded spirit animal images for {gender}. Output saved to {output_directory}")
    print(f"Updated CSV saved as {output_csv}")

# Generate and download images for both genders
generate_and_download_spirit_animal_image('M')
# generate_and_download_spirit_animal_image('F')
