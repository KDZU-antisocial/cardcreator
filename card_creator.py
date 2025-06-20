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
from instagram_poster import create_instagram_post

# Try to import mastodon_poster, but don't fail if it's not available
try:
    from mastodon_poster import create_mastodon_post
    MASTODON_AVAILABLE = True
except ImportError:
    MASTODON_AVAILABLE = False
    print("Note: Mastodon posting not available (mastodon.py not installed)")

# Try to import bluesky_poster, but don't fail if it's not available
try:
    from bluesky_poster import create_bluesky_post
    BLUESKY_AVAILABLE = True
except ImportError:
    BLUESKY_AVAILABLE = False
    print("Note: Bluesky posting not available (atproto not installed)")

def get_pacific_time():
    pacific = pytz.timezone('US/Pacific')
    return datetime.now(pacific).strftime('%Y-%m-%d')

def download_image(url, filename):
    """Download image from URL and save to specified path."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            base_path = os.path.expanduser(os.getenv('IMAGE_OUTPUT_PATH'))
            full_path = os.path.join(base_path, os.path.basename(filename))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as f:
                f.write(response.content)
            print(f"Image saved to: {full_path}")
            return full_path
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

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

def validate_paths():
    """Validate that required paths exist and are writable."""
    markdown_path = os.path.expanduser(os.getenv('MARKDOWN_OUTPUT_PATH', ''))
    image_path = os.path.expanduser(os.getenv('IMAGE_OUTPUT_PATH', ''))
    
    if not markdown_path or not image_path:
        print("Error: MARKDOWN_OUTPUT_PATH and IMAGE_OUTPUT_PATH must be set in .env file")
        return False
    
    # Check if paths exist
    if not os.path.exists(markdown_path):
        print(f"Error: Markdown output path does not exist: {markdown_path}")
        return False
        
    if not os.path.exists(image_path):
        print(f"Error: Image output path does not exist: {image_path}")
        return False
    
    # Check if paths are writable
    try:
        # Test markdown path
        test_file = os.path.join(markdown_path, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        # Test image path
        test_file = os.path.join(image_path, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except Exception as e:
        print(f"Error: Paths are not writable: {e}")
        return False
    
    return True

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
        chromedriver_path = os.path.expanduser("~/.wdm/drivers/chromedriver/mac64/137.0.7151.119/chromedriver-mac-arm64/chromedriver")
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
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
        image_filename = f"{sanitized_title}.jpg"
        
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
heroImage: "https://static.kdzu.org/images/tracks/{image_filename}"
pubDate: {pub_date}
bandcamp: "{url}"
youtube: ""
spotify: ""
---

Write your track review here. Keep it concise but descriptive. Focus on the sound, mood, and impact of the track.
"""
        
        # Write to file
        output_filename = f"{sanitized_title}.md"
        base_path = os.path.expanduser(os.getenv('MARKDOWN_OUTPUT_PATH'))
        filepath = os.path.join(base_path, output_filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"Markdown file created: {filepath}")
        return filepath, title, artist
        
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
    # Load environment variables and validate paths
    load_dotenv()
    if not validate_paths():
        return
        
    url = input("Enter the Bandcamp track URL: ")
    
    # Create the track file and get title/artist
    output_file, title, artist = create_track_file(url)
    if not output_file or not title or not artist:
        print("\nScript stopped due to missing required information.")
        return
        
    print(f"Image file created: {output_file}")
    
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
    
    # Replace the empty YouTube and Spotify links in the frontmatter
    if youtube_link:
        content = content.replace('youtube: ""', f'youtube: "{youtube_link}"')
    if spotify_link:
        content = content.replace('spotify: ""', f'spotify: "{spotify_link}"')
    
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
    
    # Ask if user wants to post to Instagram
    post_to_instagram = input("\nWould you like to post this track to Instagram? (y/n): ").lower().strip() == 'y'
    
    if post_to_instagram:
        # Get the image path from the markdown content
        image_filename = os.path.basename(output_file).replace('.md', '.jpg')
        image_path = os.path.join(os.path.expanduser(os.getenv('IMAGE_OUTPUT_PATH')), image_filename)
        
        if os.path.exists(image_path):
            success = create_instagram_post(
                image_path=image_path,
                title=title,
                artist=artist,
                review=review,
                bandcamp_url=url,
                spotify_url=spotify_link,
                youtube_url=youtube_link
            )
            if success:
                print("Successfully posted to Instagram!")
            else:
                print("Failed to post to Instagram. Check the error message above.")
        else:
            print(f"Error: Image file not found at {image_path}")
    
    # Ask if user wants to post to Mastodon
    if MASTODON_AVAILABLE:
        post_to_mastodon = input("\nWould you like to post this track to Mastodon? (y/n): ").lower().strip() == 'y'
        
        if post_to_mastodon:
            # Get the image path from the markdown content
            image_filename = os.path.basename(output_file).replace('.md', '.jpg')
            image_path = os.path.join(os.path.expanduser(os.getenv('IMAGE_OUTPUT_PATH')), image_filename)
            
            if os.path.exists(image_path):
                success = create_mastodon_post(
                    image_path=image_path,
                    title=title,
                    artist=artist,
                    review=review,
                    bandcamp_url=url,
                    spotify_url=spotify_link,
                    youtube_url=youtube_link
                )
                if success:
                    print("Successfully posted to Mastodon!")
                else:
                    print("Failed to post to Mastodon. Check the error message above.")
            else:
                print(f"Error: Image file not found at {image_path}")
    else:
        print("\nMastodon posting not available. Install mastodon.py to enable this feature.")
    
    # Ask if user wants to post to Bluesky
    if BLUESKY_AVAILABLE:
        post_to_bluesky = input("\nWould you like to post this track to Bluesky? (y/n): ").lower().strip() == 'y'
        
        if post_to_bluesky:
            # Get the image path from the markdown content
            image_filename = os.path.basename(output_file).replace('.md', '.jpg')
            image_path = os.path.join(os.path.expanduser(os.getenv('IMAGE_OUTPUT_PATH')), image_filename)
            
            if os.path.exists(image_path):
                success = create_bluesky_post(
                    image_path=image_path,
                    title=title,
                    artist=artist,
                    review=review,
                    bandcamp_url=url,
                    spotify_url=spotify_link,
                    youtube_url=youtube_link
                )
                if success:
                    print("Successfully posted to Bluesky!")
                else:
                    print("Failed to post to Bluesky. Check the error message above.")
            else:
                print(f"Error: Image file not found at {image_path}")
    else:
        print("\nBluesky posting not available. Install atproto to enable this feature.")

if __name__ == "__main__":
    main() 