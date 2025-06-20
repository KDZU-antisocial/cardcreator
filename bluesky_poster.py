import os
import re
from atproto import Client
from dotenv import load_dotenv
from atproto import models

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
    Prompt user to enter hashtags for the Bluesky post.
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
    
    return hashtags  # Return as list instead of joined string

def create_bluesky_post(image_path, title, artist, review, bandcamp_url, spotify_url=None, youtube_url=None):
    """
    Create a Bluesky post for a track review.
    
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
        # Get Bluesky credentials
        bluesky_handle = os.getenv('BLUESKY_HANDLE')
        bluesky_password = os.getenv('BLUESKY_PASSWORD')
        
        if not bluesky_handle or not bluesky_password:
            print("Error: Bluesky credentials not found in .env file")
            print("Please add BLUESKY_HANDLE and BLUESKY_PASSWORD to your .env file")
            return False
        
        # Initialize Bluesky client
        client = Client()
        client.login(bluesky_handle, bluesky_password)
        
        # Get hashtags from user
        hashtags = get_hashtags()
        
        # Clean and validate URLs
        def clean_url(url):
            if not url:
                return None
            # Remove any whitespace and ensure proper formatting
            url = url.strip()
            # Ensure URL starts with https://
            if not url.startswith('https://'):
                if url.startswith('http://'):
                    url = url.replace('http://', 'https://', 1)
                else:
                    url = 'https://' + url
            # Remove any trailing punctuation that might interfere
            url = url.rstrip('.,;:!?')
            return url
        
        bandcamp_url = clean_url(bandcamp_url)
        spotify_url = clean_url(spotify_url)
        youtube_url = clean_url(youtube_url)
        
        # Create post text
        post_text = f"""{title} by {artist}

{review}"""
        
        # Add hashtags with proper spacing
        if hashtags:
            hashtag_text = ' '.join(hashtags)
            post_text += f"\n\n{hashtag_text}"
        
        # Add URLs with proper spacing
        post_text += f"\n\nBC: {bandcamp_url}"
        if spotify_url:
            post_text += f"\nSpot: {spotify_url}"
        if youtube_url:
            post_text += f"\nYT: {youtube_url}"
        
        # Add tracks web page link
        more_tracks_url = os.getenv('MORE_TRACKS_URL', 'https://kdzu.org/tracks-we-love')
        post_text += f"\nKDZU: {more_tracks_url}"
        
        # Check character limit (Bluesky has 300 character limit)
        if len(post_text) > 300:
            print(f"Post is {len(post_text)} characters, truncating to fit Bluesky's 300 character limit...")
            
            # Create a shorter version with essential info only
            short_post = f"""{title} by {artist}"""
            
            # Add hashtags if there's room
            if hashtags and len(short_post) + len(' '.join(hashtags)) + len(bandcamp_url) + len(more_tracks_url) + 50 < 300:
                hashtag_text = ' '.join(hashtags)
                short_post += f"\n\n{hashtag_text}"
            
            # Add URLs at the end
            short_post += f"\n\nBC: {bandcamp_url}"
            if spotify_url and len(short_post) + len(f"\nSpot: {spotify_url}") + 10 < 300:
                short_post += f"\nSpot: {spotify_url}"
            if youtube_url and len(short_post) + len(f"\nYT: {youtube_url}") + 10 < 300:
                short_post += f"\nYT: {youtube_url}"
            
            # Add tracks page link
            short_post += f"\nKDZU: {more_tracks_url}"
            
            post_text = short_post
            
            print(f"Truncated post is {len(post_text)} characters")
        
        # Create the post (with image)
        print("Posting to Bluesky...")
        
        # Upload image first
        print("Uploading image to Bluesky...")
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Upload the image
        upload = client.upload_blob(image_data)
        
        # Try to use facets for better URL and hashtag handling
        try:
            # Add URL facets
            urls = [bandcamp_url]
            if spotify_url:
                urls.append(spotify_url)
            if youtube_url:
                urls.append(youtube_url)
            if more_tracks_url:
                urls.append(more_tracks_url)
            
            facets = []
            for url in urls:
                if url and url in post_text:
                    start_index = post_text.find(url)
                    if start_index != -1:
                        facets.append(models.AppBskyRichtextFacet.Main(
                            features=[models.AppBskyRichtextFacet.Link(uri=url)],
                            index=models.AppBskyRichtextFacet.ByteSlice(
                                byteStart=start_index,
                                byteEnd=start_index + len(url)
                            )
                        ))
            
            # Add hashtag facets
            for hashtag in hashtags:
                if hashtag in post_text:
                    start_index = post_text.find(hashtag)
                    if start_index != -1:
                        facets.append(models.AppBskyRichtextFacet.Main(
                            features=[models.AppBskyRichtextFacet.Tag(tag=hashtag.lstrip('#'))],
                            index=models.AppBskyRichtextFacet.ByteSlice(
                                byteStart=start_index,
                                byteEnd=start_index + len(hashtag)
                            )
                        ))
            
            # Create the post with image and facets
            client.send_post(
                text=post_text,
                facets=facets,
                embed=models.AppBskyEmbedImages.Main(
                    images=[models.AppBskyEmbedImages.Image(
                        image=upload.blob,
                        alt=f"Album artwork for {title} by {artist}"
                    )]
                )
            )
        except ImportError:
            # Fallback to simple post with image if facets not available
            client.send_post(
                text=post_text,
                embed=models.AppBskyEmbedImages.Main(
                    images=[models.AppBskyEmbedImages.Image(
                        image=upload.blob,
                        alt=f"Album artwork for {title} by {artist}"
                    )]
                )
            )
        
        return True
        
    except Exception as e:
        print(f"Error posting to Bluesky: {str(e)}")
        return False

def create_bluesky_post_from_markdown(markdown_file_path):
    """
    Create a Bluesky post from a markdown file.
    
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
    
    # Create Bluesky post
    return create_bluesky_post(
        image_path=track_data['image_path'],
        title=track_data['title'],
        artist=track_data['artist'],
        review=track_data['review'],
        bandcamp_url=track_data['bandcamp_url'],
        spotify_url=track_data['spotify_url'],
        youtube_url=track_data['youtube_url']
    )

def setup_bluesky_app():
    """
    Helper function to set up Bluesky posting.
    """
    print("Setting up Bluesky posting...")
    print("You'll need your Bluesky handle and password.")
    print("Follow these steps:")
    print("1. Go to https://bsky.app and log into your account")
    print("2. Your handle is your username (e.g., username.bsky.social)")
    print("3. Use your account password")
    print("4. Add them to your .env file:")
    print("   BLUESKY_HANDLE=your_handle.bsky.social")
    print("   BLUESKY_PASSWORD=your_password")
    print("\nNote: Bluesky uses your regular account credentials, no app setup required!")
    
    return True

if __name__ == "__main__":
    print("Bluesky Poster for CardCreator")
    print("=" * 40)
    
    # Check if setup is needed
    load_dotenv()
    if not os.getenv('BLUESKY_PASSWORD'):
        print("Bluesky credentials not found. Running setup...")
        setup_bluesky_app()
    else:
        print("Bluesky credentials found. Ready to post!")
        
        # Ask for markdown file path
        markdown_file = input("\nEnter path to markdown file: ").strip()
        
        if os.path.exists(markdown_file):
            success = create_bluesky_post_from_markdown(markdown_file)
            if success:
                print("Successfully posted to Bluesky!")
            else:
                print("Failed to post to Bluesky. Check the error message above.")
        else:
            print(f"Error: Markdown file not found at {markdown_file}") 