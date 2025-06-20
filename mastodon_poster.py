import os
import re
from mastodon import Mastodon
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
    Prompt user to enter hashtags for the Mastodon post.
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

def create_mastodon_post(image_path, title, artist, review, bandcamp_url, spotify_url=None, youtube_url=None):
    """
    Create a Mastodon post for a track review.
    
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
    
    try:
        # Get Mastodon credentials
        mastodon_url = os.getenv('MASTODON_URL')
        access_token = os.getenv('MASTODON_ACCESS_TOKEN')
        
        if not mastodon_url or not access_token:
            print("Error: Mastodon credentials not found in .env file")
            print("Please add MASTODON_URL and MASTODON_ACCESS_TOKEN to your .env file")
            return False
        
        # Initialize Mastodon client
        mastodon = Mastodon(
            access_token=access_token,
            api_base_url=mastodon_url
        )
        
        # Get hashtags from user
        hashtags = get_hashtags()
        
        # Create status text
        status = f"""{title} by {artist}

{review}

Listen on Bandcamp: {bandcamp_url}"""
        
        # Add optional links
        if spotify_url:
            status += f"\nSpotify: {spotify_url}"
        if youtube_url:
            status += f"\nYouTube: {youtube_url}"
        
        # Add hashtags
        if hashtags:
            status += f"\n\n{hashtags}"
        
        # Upload media first
        print("Uploading image to Mastodon...")
        media = mastodon.media_post(image_path, description=f"Album artwork for {title} by {artist}")
        
        # Post status with media
        print("Posting to Mastodon...")
        result = mastodon.status_post(
            status,
            media_ids=[media['id']],
            visibility='public'  # Options: public, unlisted, private, direct
        )
        
        print(f"Successfully posted to Mastodon! Post ID: {result['id']}")
        print(f"Post URL: {result['url']}")
        return True
        
    except Exception as e:
        print(f"Error posting to Mastodon: {str(e)}")
        return False

def create_mastodon_post_from_markdown(markdown_file_path):
    """
    Create a Mastodon post from a markdown file.
    
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
    
    # Create Mastodon post
    return create_mastodon_post(
        image_path=track_data['image_path'],
        title=track_data['title'],
        artist=track_data['artist'],
        review=track_data['review'],
        bandcamp_url=track_data['bandcamp_url'],
        spotify_url=track_data['spotify_url'],
        youtube_url=track_data['youtube_url']
    )

def setup_mastodon_app():
    """
    Helper function to set up a Mastodon app and get access token.
    This should be run once to generate the access token.
    """
    print("Setting up Mastodon app...")
    print("You'll need to create a Mastodon app to get an access token.")
    print("Follow these steps:")
    print("1. Go to your Mastodon instance (e.g., https://mastodon.social)")
    print("2. Go to Settings > Development > New Application")
    print("3. Fill in the details:")
    print("   - Application name: CardCreator")
    print("   - Website: (leave blank or add your website)")
    print("   - Redirect URI: urn:ietf:wg:oauth:2.0:oob")
    print("   - Scopes: read write")
    print("4. Submit and copy the access token")
    print("5. Add it to your .env file as MASTODON_ACCESS_TOKEN")
    print("6. Add your Mastodon instance URL as MASTODON_URL")
    
    return True

if __name__ == "__main__":
    print("Mastodon Poster for CardCreator")
    print("=" * 40)
    
    # Check if setup is needed
    load_dotenv()
    if not os.getenv('MASTODON_ACCESS_TOKEN'):
        print("Mastodon access token not found. Running setup...")
        setup_mastodon_app()
    else:
        print("Mastodon credentials found. Ready to post!")
        
        # Ask for markdown file path
        markdown_file = input("\nEnter path to markdown file: ").strip()
        
        if os.path.exists(markdown_file):
            success = create_mastodon_post_from_markdown(markdown_file)
            if success:
                print("Successfully posted to Mastodon!")
            else:
                print("Failed to post to Mastodon. Check the error message above.")
        else:
            print(f"Error: Markdown file not found at {markdown_file}") 