import csv
import requests
from bs4 import BeautifulSoup
import time
import re

# Headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}

# Output CSV file
CSV_FILE = 'fighters_data.csv'

def fetch_page(url):
    """Fetch the HTML content of a page with a delay to avoid rate limiting."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print(f"Successfully fetched {url}")
        time.sleep(2)  # Polite delay to respect server
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_fighter_urls():
    """Dynamically collect fighter URLs from Sherdog's UFC organization page."""
    base_url = 'https://www.sherdog.com/organizations/UFC-2'
    fighter_urls = set()  # Use set to avoid duplicates

    html = fetch_page(base_url)
    if not html:
        print("Failed to fetch the organization page. Trying the search page...")
        base_url = 'https://www.sherdog.com/stats/fightfinder?association=UFC&SearchTxt=&weight='
        html = fetch_page(base_url)
        if not html:
            return list(fighter_urls)

    soup = BeautifulSoup(html, 'html.parser')
    print("HTML fetched. Searching for fighter links...")

    # Try a more generic selector for fighter links
    fighter_links = soup.select('a[href^="/fighter/"]')
    print(f"Found {len(fighter_links)} potential fighter links.")

    for link in fighter_links:
        href = link['href']
        full_url = 'https://www.sherdog.com' + href if not href.startswith('http') else href
        if '/fighter/' in full_url:  # Ensure it's a fighter profile
            fighter_urls.add(full_url)
            print(f"Found fighter URL: {full_url}")

    # Handle pagination
    page = 1
    while True:
        page += 1
        # Try different selectors for the "Next" link
        next_page = (soup.find('a', string='Next') or 
                     soup.find('a', class_='pagination-next') or 
                     soup.find('a', string=re.compile('next', re.I)))
        if not next_page or not next_page.get('href'):
            break
        next_url = 'https://www.sherdog.com' + next_page['href']
        print(f"Fetching next page: {next_url}")
        html = fetch_page(next_url)
        if not html:
            break
        soup = BeautifulSoup(html, 'html.parser')
        fighter_links = soup.select('a[href^="/fighter/"]')
        print(f"Page {page}: Found {len(fighter_links)} potential fighter links.")
        for link in fighter_links:
            href = link['href']
            full_url = 'https://www.sherdog.com' + href if not href.startswith('http') else href
            if '/fighter/' in full_url:
                fighter_urls.add(full_url)
                print(f"Found fighter URL: {full_url}")

    return list(fighter_urls)

def extract_fighter_data(html):
    """Extract fighter data from Sherdog HTML."""
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')
    fighter_data = {}

    # Extract name
    name_tag = soup.find('span', class_='fn') or soup.find('h1', class_='fighter-name')
    fighter_data['name'] = name_tag.text.strip() if name_tag else 'Unknown'

    # Extract record (clean the format)
    record_tag = soup.find('span', class_='record') or soup.find('div', class_='record-stats')
    raw_record = record_tag.text.strip() if record_tag else '0-0-0'
    # Clean the record: e.g., "31-12-0 (Win)" -> "31-12-0"
    record_clean = re.match(r'(\d+-\d+-\d+)', raw_record)
    fighter_data['record'] = record_clean.group(1) if record_clean else '0-0-0'

    # Extract weight class
    weight_class_tag = soup.find('div', class_='weight-class') or soup.find('span', class_='weight') or soup.find('li', class_='weight')
    raw_weight_class = weight_class_tag.text.split(': ')[-1].strip() if weight_class_tag else ''
    # Map Sherdog weight class to your model's choices
    weight_class_map = {
        'Heavyweight': 'HEAVYWEIGHT',
        'Light Heavyweight': 'LIGHT_HEAVYWEIGHT',
        'Middleweight': 'MIDDLEWEIGHT',
        'Welterweight': 'WELTERWEIGHT',
        'Lightweight': 'LIGHTWEIGHT',
        'Featherweight': 'FEATHERWEIGHT',
        'Bantamweight': 'BANTAMWEIGHT',
        'Flyweight': 'FLYWEIGHT'
    }
    fighter_data['weight_class'] = weight_class_map.get(raw_weight_class, '')

    # Extract recent fights
    recent_fights = []
    fights_section = soup.find('table', class_='fight-history') or soup.find('section', id='recent_fights')
    if fights_section:
        fight_rows = fights_section.find_all('tr')[1:4]  # Skip header row, take up to 3 fights
        for row in fight_rows:
            result = row.find('td', class_='result')
            opponent = row.find('a', class_='opponent') or row.find('a', class_='sub_line')
            if result and opponent:
                recent_fights.append(f"{result.text.strip()} vs {opponent.text.strip()}")
    fighter_data['recent_fights'] = '\n'.join(recent_fights) if recent_fights else ''

    # Extract bio (summary or description)
    bio_tag = soup.find('div', class_='fighter-bio') or soup.find('p', class_='summary') or soup.find('div', class_='bio')
    fighter_data['bio'] = bio_tag.text.strip() if bio_tag else 'No bio available'

    # Extract strengths and weaknesses (if available, e.g., from bio or stats)
    # Sherdog doesn't directly provide this, so we'll infer from record and fights
    record_parts = fighter_data['record'].split('-')
    wins = int(record_parts[0])
    losses = int(record_parts[1])
    total_fights = wins + losses + int(record_parts[2])  # W-L-D

    # Estimate strengths and weaknesses
    fighter_data['strengths'] = 'Strong record' if wins > losses else 'Experienced'
    fighter_data['weaknesses'] = 'Inconsistent' if losses > wins else 'TBD'

    # Estimated stats (improved logic)
    fighter_data['striking'] = min(90, max(50, 50 + (wins * 2)))  # Higher wins = better striking
    fighter_data['grappling'] = min(90, max(50, 50 + (total_fights - losses) * 2))  # Fewer losses = better grappling
    fighter_data['stamina'] = min(90, max(50, 60 + (total_fights * 2)))  # More fights = better stamina
    fighter_data['defense'] = min(90, max(50, 60 + (wins - losses) * 2))  # Win-loss diff = better defense
    fighter_data['speed'] = min(90, max(50, 60 + (wins // 2) * 2))  # Wins = better speed

    # Determine if active (based on recent fights)
    if recent_fights:
        last_fight = recent_fights[0]
        # Look for a year in the fight (e.g., "Win vs Opponent (2023)")
        year_match = re.search(r'(\d{4})', last_fight)
        if year_match:
            last_fight_year = int(year_match.group(1))
            fighter_data['is_active'] = 'True' if last_fight_year >= 2023 else 'False'
        else:
            fighter_data['is_active'] = 'True'  # Default to active if no year found
    else:
        fighter_data['is_active'] = 'True'

    # Placeholder for other fields
    fighter_data['martial_art'] = 'MMA'
    fighter_data['photo'] = ''  # To be added manually or via image search
    fighter_data['video_id'] = ''
    fighter_data['detailed_stats'] = '{}'
    fighter_data['p4p_ranking'] = ''  # To be added manually or via external ranking

    return fighter_data

def save_to_csv(fighter_data_list):
    """Save fighter data to a CSV file."""
    fieldnames = ['name', 'martial_art', 'record', 'strengths', 'weaknesses', 'bio', 'photo', 'striking', 
                  'grappling', 'stamina', 'defense', 'speed', 'video_id', 'detailed_stats', 'recent_fights', 
                  'is_active', 'weight_class', 'p4p_ranking']
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in fighter_data_list:
            writer.writerow(data)

def main():
    # Dynamically collect fighter URLs
    fighter_urls = get_fighter_urls()
    if not fighter_urls:
        print("No fighter URLs collected. Check the base URL or network restrictions.")
        return

    fighter_data_list = []
    for url in fighter_urls:
        html = fetch_page(url)
        if html:
            fighter_data = extract_fighter_data(html)
            if fighter_data:
                fighter_data_list.append(fighter_data)
                print(f"Scraped data for {fighter_data['name']}")

    if fighter_data_list:
        save_to_csv(fighter_data_list)
        print(f"Saved data to {CSV_FILE}")
    else:
        print("No fighter data was scraped.")

if __name__ == "__main__":
    main()