# add_fighters.py
import os
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fighter_analysis.settings')  # Replace 'fighter_analysis' with your project name
django.setup()

from fighters.models import Fighter

# List of new fighters to add (as a list of dictionaries)
new_fighters = [
  # Add to the new_fighters list in add_fighters.py
{
  "name": "Kamaru Usman",
  "martial_art": "MMA",
  "record": "20-4-0",
  "strengths": "Elite wrestling, powerful striking, high fight IQ, relentless pressure",
  "weaknesses": "Knees prone to injury, age-related decline in speed",
  "bio": "Kamaru 'The Nigerian Nightmare' Usman is a Nigerian-American mixed martial artist and former UFC Welterweight Champion. Dominating the division with his wrestling and striking, Usman defended his title five times before losing to Leon Edwards at UFC 278. He faced Edwards again at UFC 286 but was defeated via decision. As of April 2025, Usman is contemplating a move to middleweight.",
  "defense": 90,
  "grappling": 95,
  "photo": "fighters/USMAN_KAMARU_L_10-21.png",
  "speed": 80,
  "stamina": 90,
  "striking": 85,
  "detailed_stats": {
    "height (CM)": 183,
    "reach (CM)": 193,
    "stance": "Orthodox",
    "Significant Strikes Landed Per Min": 4.66,
    "Takedown Accuracy": 47,
    "Submission Average Per 15Min": 0.2
  },
  "recent_fights": "Dec 2024: vs. Leon Edwards (Loss)\nMar 2024: vs. Khamzat Chimaev (Loss)\nAug 2023: vs. Jorge Masvidal (Win)\nMar 2023: vs. Leon Edwards (Loss)\nAug 2022: vs. Leon Edwards (Loss)",
  "video_id": "eY52Zsg-KVI",
  "is_active": True,
  "p4p_ranking": None,
  "weight_class": "WELTERWEIGHT"
}


]

# Add fighters to the database
for fighter_data in new_fighters:
    try:
        # Check if the fighter already exists to avoid duplicates
        if not Fighter.objects.filter(name=fighter_data["name"]).exists():
            Fighter.objects.create(**fighter_data)
            print(f"Added fighter: {fighter_data['name']}")
        else:
            print(f"Fighter {fighter_data['name']} already exists in the database.")
    except Exception as e:
        print(f"Error adding fighter {fighter_data['name']}: {e}")

print("Finished adding fighters.")