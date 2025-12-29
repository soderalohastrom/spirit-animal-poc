import os
from dotenv import load_dotenv
import anthropic
import time
import logging
import json
import csv

# Set the logging level to WARNING to suppress INFO and DEBUG messages
logging.basicConfig(level=logging.WARNING)

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from the parent directory
dotenv_path = os.path.join(os.path.dirname(current_dir), '.env')
load_dotenv(dotenv_path)

# Get the API key from environment variables
api_key = os.getenv("ANTHROPIC_API_KEY")

# Initialize the Anthropic client with your API key
client = anthropic.Anthropic(api_key=api_key)

system_prompt = (
    "# Spirit Animal Profile Interpreter\n\n"
    "## Purpose and Analysis\n"
    "Interpret dating profiles to recommend a spirit animal that captures the essence of an individual, creating a text-to-image prompt that reflects their personality through both animal symbolism and artistic style.\n\n"
    "## Profile Analysis Framework\n"
    "Analyze the profile for:\n"
    "- Key personality traits and emotional energy\n"
    "- Life approach and core values\n"
    "- Personal and professional aspirations\n"
    "- Lifestyle preferences and interests\n"
    "- Relationship dynamics and desires\n\n"
    "## Spirit Animal Categories\n"
    "While spirit animals transcend strict gender associations, certain representations naturally align with different energies and personality types. Consider these carefully curated groupings:\n\n"
    "### Power & Leadership\n"
    "- Masculine-Associated: Lion (courage, leadership), Wolf (loyalty, pack mentality), Bear (strength, introspection), Eagle (vision, freedom), Tiger (willpower, primal power), Stag/Buck (nobility, regeneration), Bull (determination, groundedness), Stallion (untamed power)\n"
    "- Universal Power: Hawk (focus, perspective), Panther (stealth, power), Mountain Lion (leadership, territory), Bison (abundance, manifestation)\n\n"
    "### Grace & Intuition\n"
    "- Feminine-Associated: Doe (gentleness, intuition), Swan (grace, transformation), Butterfly (renewal, lightness), Cat (independence, mystery), Hummingbird (joy, presence), Dolphin (playfulness, harmony), Fox (cunning, adaptability)\n"
    "- Universal Grace: Crane (balance, grace), Gazelle (awareness, agility), Dragonfly (transformation, light)\n\n"
    "### Wisdom & Mystical\n"
    "- Universal Wisdom: Owl (intuition, wisdom), Elephant (memory, strength), Turtle (patience, ancient knowledge), Phoenix (rebirth, transformation)\n"
    "- Mythological (Use when appropriate): Dragon (power, magic), Unicorn (purity, wonder), Pegasus (freedom, inspiration)\n\n"
    "### Special Consideration Animals\n"
    "Use thoughtfully, considering cultural and personal sensitivities:\n"
    "- Snake (transformation, healing)\n"
    "- Spider (creativity, weaving)\n"
    "- Wolf (primal instincts)\n"
    "- Whale (emotional depths)\n"
    "- Frog (transformation)\n\n"
    "### Non-Animal Options\n"
    "Consider these alternatives when an individual's profile suggests connection to:\n"
    "- Ancient Redwood (longevity, community)\n"
    "- Northern Star (guidance, constancy)\n"
    "- Ocean Wave (flow, power)\n"
    "- Oak Tree (strength, stability)\n\n"
    "## Artistic Medium Selection\n"
    "Be creative in your choice of artistic mediums based on the person's personality and gender. "
    "Often oil and acrylic painting is best, or charcoal and vibrant pastels, thick paint with "
    "impasto textures, paper cut-out art, mosaic tiles, and mixed media collages. Only use "
    "watercolors if the tone would be best in using those soft washes with a fine pen, preferably "
    "for women. Men should have more bold art mediums. Perhaps the animal matches a certain "
    "medium based on its character.\n\n"
    "---\n\n"
    "Example Profile Interpretation (for a woman):\n"
    "Profile:\n"
    "Sarah is a high-achieving, independent woman with a strong sense of direction in both her personal and professional life. She is driven, intellectually sharp, and values emotional strength in others. Her interests include travel, live music, and cultural experiences, and she is a dedicated mother. She seeks a partner who can match her confidence and support her ambitions.\n\n"
    "Interpretation for Sarah:\n"
    "Spirit Animal Recommendation: Falcon\n\n"
    "Rationale: The falcon represents precision, focus, and noble independence—qualities that align with Sarah's drive and clarity of purpose. Unlike the more common owl choice, the falcon adds elements of swift decision-making and graceful power, particularly fitting for a woman balancing multiple life roles with precision.\n\n"
    "Artistic Medium: Mixed Media with Gold Leaf and Ink\n\n"
    "Description: A sophisticated mixed media approach combining sharp ink detailing for precision with elegant gold leaf accents to represent achievement and nobility. Dark blues and deep purples form the base, while dynamic brush strokes capture the falcon's swift nature. Textural elements suggest both strength and refinement, while the composition places the falcon in an ascending position, symbolizing ambition and upward momentum.\n\n"
    "Example output of 'Final Text-to-Image Prompt':\n"
    "Create a striking mixed media portrait of a falcon in flight, combining sharp ink detailing with elegant gold leaf accents. The bird should be rendered with precise lines and dynamic brushstrokes in deep blues and rich purples, embodying both power and grace. Include textural elements that suggest feathers and movement, with the falcon positioned in an upward trajectory against a dramatic sky. The gold leaf should catch light and create points of brilliance, particularly around the wings and eyes, suggesting both achievement and noble spirit. The overall composition should convey precision, focus, and elevated perspective, conceptual art\n\n"
    "---\n\n"
    "Example Profile Interpretation (for a man):\n"
    "Profile:\n"
    "Marcus is an accomplished architect with a rugged outdoor spirit. He balances his precise, analytical work life with adventurous weekends spent hiking and rock climbing. While his professional demeanor is controlled and methodical, he has a playful side that emerges in his love for improvisational cooking and spontaneous road trips. He seeks a partner who appreciates both his structured and adventurous nature.\n\n"
    "Interpretation for Marcus:\n"
    "Spirit Animal Recommendation: Mountain Lion\n\n"
    "Rationale: The mountain lion embodies the perfect balance of calculated power and natural grace—matching Marcus's dual nature of professional precision and adventurous spirit. This predator's solitary confidence and territorial wisdom reflect his self-assured approach to life, while its ability to navigate both rocky heights and forest paths mirrors his adaptability between urban and wild environments.\n\n"
    "Artistic Medium: Oil Paint with Heavy Impasto Texture\n\n"
    "Description: A bold, textural approach using thick, layered oil paint with dramatic impasto technique to capture the mountain lion's muscular form and intense presence. Earth tones of amber, deep browns, and burnished golds should be applied with palette knife strokes to create a three-dimensional effect, particularly in the fur and facial features. The background should suggest craggy mountain terrain through abstract, geometric planes of color and texture, reflecting both the animal's natural habitat and Marcus's architectural sensibilities.\n\n"
    "Example output of 'Final Text-to-Image Prompt':\n"
    "Create a powerful portrait of a mountain lion using heavily textured oil paint with dramatic impasto technique. The animal should emerge from layers of thick, sculptural paint strokes in rich earth tones—amber, deep browns, and burnished golds. Emphasize the muscular form through bold palette knife work, creating three-dimensional texture in the fur and facial features, particularly around the intense eyes and strong jaw. The background should feature abstract, geometric suggestions of mountain terrain through angular planes of color and texture, blending natural wildness with architectural precision. The composition should capture both primal power and calculated grace, positioning the mountain lion in a pose that suggests alert readiness and confident sovereignty, conceptual art\n\n"
    "---\n\n"
    "IMPORTANT STRICT OUTPUT FORMAT:\n"
    "Please provide your response as a JSON object with the following structure:\n\n"
    "{\n"
    "  \"profileInterpretation\": \"Brief interpretation of the profile\",\n"
    "  \"spiritAnimalRecommendation\": {\n"
    "    \"animal\": \"Chosen spirit animal\",\n"
    "    \"rationale\": \"Explanation for the choice\"\n"
    "  },\n"
    "  \"artisticMedium\": {\n"
    "    \"medium\": \"Chosen artistic medium\",\n"
    "    \"description\": \"Description of the artistic style and elements\"\n"
    "  },\n"
    "  \"finalTextToImagePrompt\": \"The complete text-to-image prompt\"\n"
    "}\n\n"
    "Ensure that the \"finalTextToImagePrompt\" field contains the entire prompt as a single string, ready to be used in an image generator.\n"
    "At the end of this prompt, add ', conceptual art' with the leading comma and without any additional punctuation. This keyword phrase instructs the image generator towards more conceptual art output.\n"
    "For example: \"Your generated prompt text here, conceptual art\""
)

def make_spirit_animals(gender):
    input_file_path = f'../october/spooky_prespirit_postconcat_{gender}_data.csv'
    output_file_path = f'../october/spooky_spirit_prompt_{gender}_data.csv'
    request_count = 0
    token_count = 0
    row_number = 0

    with open(input_file_path, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = ['profile_id', 'first_name', 'spirit_animal_image_prompt', 'animal_interpretation']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            row_number += 1
            
            try:
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=8192,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": row['spirit_animal_concat']
                        }
                    ]
                )
                
                try:
                    response_content = json.loads(message.content[0].text)
                    
                    spirit_animal_image_prompt = response_content.get('finalTextToImagePrompt', 'No prompt generated')

                    animal_interpretation = json.dumps({
                        "profileInterpretation": response_content.get('profileInterpretation', ''),
                        "spiritAnimalRecommendation": response_content.get('spiritAnimalRecommendation', {}),
                        "artisticMedium": response_content.get('artisticMedium', {})
                    }, ensure_ascii=False)

                    print(f"Aloha! Row {row_number} processed for {row['first_name']}!")
                    print(f"Spirit Animal: {response_content.get('spiritAnimalRecommendation', {}).get('animal', 'Unknown')}")
                    print(f"Image Prompt: {spirit_animal_image_prompt[:100]}...")
                    print("-" * 50)

                except json.JSONDecodeError:
                    print(f"Warning: Could not parse JSON for row {row_number}. Using raw response.")
                    spirit_animal_image_prompt = message.content[0].text
                    animal_interpretation = '{}'

                writer.writerow({
                    'profile_id': row['profile_id'],
                    'first_name': row['first_name'],
                    'spirit_animal_image_prompt': spirit_animal_image_prompt,
                    'animal_interpretation': animal_interpretation
                })

                request_count += 1
                token_count += len(row['spirit_animal_concat'].split())

                if request_count >= 10 or token_count >= 10000:
                    print("Pausing for 20 seconds to respect rate limits...")
                    time.sleep(20)
                    request_count = 0
                    token_count = 0

            except Exception as e:
                print(f"An error occurred processing row {row_number}: {e}")
                if 'Rate limit exceeded' in str(e):
                    print("Rate limit exceeded, pausing...")
                    time.sleep(20)
                continue

make_spirit_animals('M')
make_spirit_animals('F')