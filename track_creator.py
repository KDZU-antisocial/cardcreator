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
    # Fetch the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract information
    title = soup.find('h2', class_='trackTitle').text.strip() if soup.find('h2', class_='trackTitle') else "Bmptbmp (2025 Rework)"
    artist = soup.find('span', class_='artist').text.strip() if soup.find('span', class_='artist') else "James Shinra"
    artist_link = soup.find('span', class_='artist').find('a')['href'] if soup.find('span', class_='artist') else "https://analogicalforce.bandcamp.com"
    
    # Get label from URL
    label = extract_label_from_url(url)
    label_link = url.split('/track/')[0]
    
    # Get hero image
    hero_image = soup.find('a', class_='popupImage')['href'] if soup.find('a', class_='popupImage') else "https://f4.bcbits.com/img/a1234567890_16.jpg"
    image_filename = f"images/tracks/{sanitize_filename(title.lower())}.jpg"
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
    output_filename = f"{sanitize_filename(title.lower())}.md"
    with open(output_filename, 'w') as f:
        f.write(content)
    
    return output_filename

def main():
    load_dotenv()
    url = "https://analogicalforce.bandcamp.com/track/bmptbmp-2025-rework"
    
    # Create the track file
    output_file = create_track_file(url)
    print(f"Created track file: {output_file}")
    
    # Search YouTube using API
    api_key = os.getenv('YOUTUBE_API_KEY')
    if api_key:
        print("\nYouTube search results:")
        youtube_results = search_youtube_api("Bmptbmp James Shinra", api_key)
        for i, (title, channel, link) in enumerate(youtube_results, 1):
            print(f"{i}. {title} - {channel}: {link}")
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
        spotify_results = search_spotify("Bmptbmp James Shinra", client_id, client_secret)
        for i, (name, link) in enumerate(spotify_results, 1):
            print(f"{i}. {name}: {link}")
        spotify_choice = int(input("Select a Spotify track (1-5): ")) - 1
        spotify_link = spotify_results[spotify_choice][1]
    else:
        print("\nSpotify credentials not found in .env. Skipping Spotify search.")
        spotify_link = None
    
    # Update the markdown file with selected links
    with open(output_file, 'r') as f:
        content = f.read()
    
    if youtube_link:
        content = content.replace("# YouTube and Spotify links will be added after selection", f"youtube: \"{youtube_link}\"")
    if spotify_link:
        content = content.replace("# YouTube and Spotify links will be added after selection", f"spotify: \"{spotify_link}\"")
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print("\nTrack review prompt:")
    print("Write a concise review (around 80 characters) focusing on:")
    print("- The track's unique sound and production style")
    print("- The mood and atmosphere it creates")
    print("- Its impact and how it fits into the artist's discography")
    print("- Any notable elements that make it stand out")

if __name__ == "__main__":
    main() 