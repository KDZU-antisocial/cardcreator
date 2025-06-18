import os
from instagrapi import Client
from dotenv import load_dotenv

def get_hashtags():
    """
    Prompt user to enter hashtags for the Instagram post.
    Returns a string of hashtags.
    """
    print("\nEnter hashtags for your post (one per line, press Enter twice to finish):")
    print("Example: electronicmusic, techno, newrelease")
    hashtags = []
    while True:
        tag = input().strip()
        if not tag and hashtags:  # Empty line and we have at least one tag
            break
        if tag:
            # Remove # if user included it
            tag = tag.lstrip('#')
            # Add # if user didn't include it
            if not tag.startswith('#'):
                tag = '#' + tag
            hashtags.append(tag)
    
    return ' '.join(hashtags)

def create_instagram_post(image_path, title, artist, review, bandcamp_url, spotify_url=None, youtube_url=None):
    """
    Create an Instagram post for a track review.
    
    Args:
        image_path (str): Path to the track artwork
        title (str): Track title
        artist (str): Artist name
        review (str): Track review text
        bandcamp_url (str): Bandcamp URL
        spotify_url (str, optional): Spotify URL
        youtube_url (str, optional): YouTube URL
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize Instagram client
    client = Client()
    
    try:
        # Login to Instagram
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            print("Error: Instagram credentials not found in .env file")
            return False
            
        client.login(username, password)
        
        # Get hashtags from user
        hashtags = get_hashtags()
        
        # Create caption
        caption = f"""{title} by {artist}

{review}

Listen on Bandcamp, Spotify, and YouTube
Link in bio 🔗

{hashtags}"""
        
        # Upload the photo
        media = client.photo_upload(
            image_path,
            caption=caption
        )
        
        print(f"Successfully posted to Instagram! Media ID: {media.id}")
        return True
        
    except Exception as e:
        print(f"Error posting to Instagram: {str(e)}")
        return False
    finally:
        # Logout
        try:
            client.logout()
        except:
            pass 