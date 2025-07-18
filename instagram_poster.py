import os
import re
from instagrapi import Client
from dotenv import load_dotenv

def read_track_from_markdown(markdown_file_path):
    """
    Read track information from a markdown file.
    
    Args:
        markdown_file_path (str): Path to the markdown file
        
    Returns:
        dict: Dictionary containing track data
    """
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ValueError("Invalid markdown format: missing frontmatter")
        
        frontmatter = parts[1].strip()
        review_content = parts[2].strip()
        
        # Parse frontmatter
        track_data = {}
        for line in frontmatter.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                track_data[key] = value
        
        # Extract review (remove the placeholder text)
        review = review_content.replace(
            "Write your track review here. Keep it concise but descriptive. Focus on the sound, mood, and impact of the track.",
            ""
        ).strip()
        
        # Get image path from heroImage
        hero_image = track_data.get('heroImage', '')
        if hero_image.startswith('https://static.kdzu.org/images/tracks/'):
            # Convert to local path
            image_filename = os.path.basename(hero_image)
            image_path = os.path.join(os.path.expanduser(os.getenv('IMAGE_OUTPUT_PATH', '')), image_filename)
        else:
            image_path = None
        
        return {
            'title': track_data.get('title', ''),
            'artist': track_data.get('artist', ''),
            'review': review,
            'bandcamp_url': track_data.get('bandcamp', ''),
            'spotify_url': track_data.get('spotify', ''),
            'youtube_url': track_data.get('youtube', ''),
            'image_path': image_path
        }
        
    except Exception as e:
        print(f"Error reading markdown file: {str(e)}")
        return None

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

def create_instagram_post_from_markdown(markdown_file_path):
    """
    Create an Instagram post from a markdown file.
    
    Args:
        markdown_file_path (str): Path to the markdown file
    """
    # Load environment variables
    load_dotenv()
    
    # Read track data from markdown
    track_data = read_track_from_markdown(markdown_file_path)
    if not track_data:
        print("Error: Could not read track data from markdown file")
        return False
    
    # Check if image exists
    if not track_data['image_path'] or not os.path.exists(track_data['image_path']):
        print(f"Error: Image file not found at {track_data['image_path']}")
        return False
    
    # Create Instagram post
    return create_instagram_post(
        image_path=track_data['image_path'],
        title=track_data['title'],
        artist=track_data['artist'],
        review=track_data['review'],
        bandcamp_url=track_data['bandcamp_url'],
        spotify_url=track_data['spotify_url'],
        youtube_url=track_data['youtube_url']
    )

if __name__ == "__main__":
    print("Instagram Poster for CardCreator")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    if not os.getenv('INSTAGRAM_USERNAME') or not os.getenv('INSTAGRAM_PASSWORD'):
        print("Error: Instagram credentials not found in .env file")
        print("Please add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to your .env file")
    else:
        print("Instagram credentials found. Ready to post!")
        
        # Ask for markdown file path
        markdown_file = input("\nEnter path to markdown file: ").strip()
        
        if os.path.exists(markdown_file):
            success = create_instagram_post_from_markdown(markdown_file)
            if success:
                print("Successfully posted to Instagram!")
            else:
                print("Failed to post to Instagram. Check the error message above.")
        else:
            print(f"Error: Markdown file not found at {markdown_file}") 