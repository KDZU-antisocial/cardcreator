import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import shutil
from urllib.parse import urlparse, quote_plus
from dotenv import load_dotenv
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time

def get_pacific_time():
    pacific = pytz.timezone('US/Pacific')
    return datetime.now(pacific).strftime('%Y-%m-%d')

def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        return True
    return False

def extract_label_from_url(url):
    parsed = urlparse(url)
    subdomain = parsed.netloc.split('.')[0]
    # Convert camelCase or snake_case to spaces
    label = re.sub(r'([a-z])([A-Z])', r'\1 \2', subdomain)
    label = label.replace('_', ' ')
    return label.title()

def search_youtube_api(query, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        part='snippet',
        q=query,
        maxResults=5,
        type='video'
    )
    response = request.execute()
    return [(item['snippet']['title'], item['snippet']['channelTitle'], f"https://www.youtube.com/watch?v={item['id']['videoId']}") for item in response['items']]

def search_spotify(query, client_id, client_secret):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))
    results = sp.search(q=query, limit=5, type='track')
    return [(track['name'], track['external_urls']['spotify']) 
            for track in results['tracks']['items']]

def sanitize_filename(name):
    # Only allow letters, numbers, underscores, and dashes
    return re.sub(r'[^a-zA-Z0-9_-]', '', name.replace(' ', '_'))

def create_track_file(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Use new headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

    try:
        # Initialize the Chrome driver with specific configuration for Mac ARM64
        service = Service()
        driver = webdriver.Chrome(options=chrome_options)
        
        # Load the page
        print(f"Loading URL: {url}")
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(3)
        
        # Get the page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find the name-section div
        name_section = soup.find('div', id='name-section')
        
        # Extract title from h2 in name-section
        title = "Unknown Title"
        artist = "Unknown Artist"
        artist_link = ""
        
        if name_section:
            # Get title from h2
            title_element = name_section.find('h2', class_='trackTitle')
            if title_element:
                # Clean up title text
                title = ' '.join(title_element.text.split())
            
            # Get artist from h3.albumTitle
            album_title = name_section.find('h3', class_='albumTitle')
            if album_title:
                # Find all spans in the album title
                spans = album_title.find_all('span')
                # The last span contains the artist link
                if spans:
                    last_span = spans[-1]
                    artist_link_element = last_span.find('a')
                    if artist_link_element:
                        # Clean up artist name and link
                        artist = ' '.join(artist_link_element.text.split())
                        artist_link = artist_link_element['href'].strip()
        
        # Debug print statements
        print("Raw HTML for name-section:", name_section)
        print(f"Scraped Title: {title}")
        print(f"Scraped Artist: {artist}")
        print(f"Scraped Artist Link: {artist_link}")
        
        # Validate required information
        if title == "Unknown Title":
            print("\nError: Could not find track title. Please check the URL and try again.")
            return None, None, None
            
        if artist == "Unknown Artist":
            print("\nError: Could not find artist name. Please check the URL and try again.")
            return None, None, None
            
        if not artist_link:
            print("\nError: Could not find artist link. Please check the URL and try again.")
            return None, None, None
        
        # Get label from URL
        label = extract_label_from_url(url)
        label_link = url.split('/track/')[0]
        
        # Sanitize file name for image and markdown
        sanitized_title = sanitize_filename(title.lower())
        image_filename = f"images/tracks/{sanitized_title}.jpg"
        
        # Get hero image with more reliable selector
        hero_image = None
        image_element = soup.find('a', class_='popupImage') or soup.find('div', class_='tralbumArt')
        if image_element:
            if image_element.name == 'a':
                hero_image = image_element['href']
            else:
                img_tag = image_element.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    hero_image = img_tag['src']
        
        if not hero_image:
            hero_image = "https://f4.bcbits.com/img/a1234567890_16.jpg"
        
        # Create images/tracks directory if it doesn't exist
        os.makedirs('images/tracks', exist_ok=True)
        
        download_image(hero_image, image_filename)
        
        # Get today's date in Pacific time
        pub_date = get_pacific_time()
        
        # Create the markdown content
        content = f"""---
title: "{title}"
artist: "{artist}"
artistLink: "{artist_link}"
label: "{label}"
labelLink: "{label_link}"
heroImage: "{image_filename}"
pubDate: {pub_date}
bandcamp: "{url}"

# YouTube and Spotify links will be added after selection
---

Write your track review here. Keep it concise but descriptive. Focus on the sound, mood, and impact of the track.
"""
        
        # Write to file
        output_filename = f"{sanitized_title}.md"
        with open(output_filename, 'w') as f:
            f.write(content)
        
        return output_filename, title, artist
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None, None, None
        
    finally:
        # Always close the driver
        try:
            driver.quit()
        except:
            pass

def main():
    load_dotenv()
    url = input("Enter the Bandcamp track URL: ")
    
    # Create the track file and get title/artist
    output_file, title, artist = create_track_file(url)
    if not output_file or not title or not artist:
        print("\nScript stopped due to missing required information.")
        return
        
    print(f"Created track file: {output_file}")
    
    # Build search query from scraped title and artist
    search_query = f"{title} {artist}"
    
    # Search YouTube using API
    api_key = os.getenv('YOUTUBE_API_KEY')
    if api_key:
        print("\nYouTube search results:")
        youtube_results = search_youtube_api(search_query, api_key)
        for i, (yt_title, channel, link) in enumerate(youtube_results, 1):
            print(f"{i}. {yt_title} - {channel}: {link}")
        youtube_choice = int(input("Select a YouTube video (1-5): ")) - 1
        youtube_link = youtube_results[youtube_choice][2]
    else:
        print("\nYouTube API key not found in .env. Skipping YouTube search.")
        youtube_link = None
    
    # Search Spotify
    client_id = os.getenv('SPOTIPY_CLIENT_ID')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    if client_id and client_secret:
        print("\nSpotify search results:")
        spotify_results = search_spotify(search_query, client_id, client_secret)
        for i, (sp_title, link) in enumerate(spotify_results, 1):
            print(f"{i}. {sp_title}: {link}")
        spotify_choice = int(input("Select a Spotify track (1-5): ")) - 1
        spotify_link = spotify_results[spotify_choice][1]
    else:
        print("\nSpotify credentials not found in .env. Skipping Spotify search.")
        spotify_link = None
    
    # Update the markdown file with selected links
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Replace the placeholder with both YouTube and Spotify links if available
    placeholder = "# YouTube and Spotify links will be added after selection"
    new_content = []
    
    if youtube_link:
        new_content.append(f"youtube: \"{youtube_link}\"")
    if spotify_link:
        new_content.append(f"spotify: \"{spotify_link}\"")
    
    if new_content:
        content = content.replace(placeholder, "\n".join(new_content))
    
    # Prompt for track review
    print("\nWrite your track review (press Enter THREE TIMES to finish):")
    print("Keep it concise but descriptive. Focus on the sound, mood, and impact of the track.")
    review_lines = []
    while True:
        line = input()
        if line == "" and review_lines and review_lines[-1] == "":
            break
        review_lines.append(line)
    
    # Join the review lines and remove the last empty line
    review = "\n".join(review_lines[:-1])
    
    # Replace the review placeholder with the actual review
    content = content.replace("Write your track review here. Keep it concise but descriptive. Focus on the sound, mood, and impact of the track.", review)
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"\nReview has been added to {output_file}")

if __name__ == "__main__":
    main() 