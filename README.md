# Card Creator

A Python tool for automatically creating track review cards from Bandcamp URLs. This tool scrapes track information, downloads images, and generates markdown files in a format suitable for the [KDZU Astro website](http://kdzu.org). The generated markdown files are used to create track review pages on the website, with proper frontmatter and image handling.

## Features

- Scrapes track information from Bandcamp URLs
- Downloads track artwork
- Generates markdown files with frontmatter
- Supports Spotify and YouTube integration
- Configurable output paths for images and markdown files
- Uses modern Python tooling (uv, pip-tools)
- Integrates with KDZU Astro website for track reviews
- Automatically posts track reviews to Instagram, Mastodon, and Bluesky with custom hashtags
- All social media posters read directly from the generated markdown files

## Prerequisites

- Python 3.11 or higher
- Chrome browser (for Selenium)
- Instagram account (for posting)
- Mastodon account (for posting)
- Bluesky account (for posting)
- API keys for:
  - Spotify (optional)
  - YouTube (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cardcreator.git
cd cardcreator
```

2. Create and activate a virtual environment using `uv`:
```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Copy the environment template and configure your settings:
```bash
cp .env_template .env
```

Edit `.env` with your configuration:
```env
SPOTIPY_CLIENT_ID=your_spotify_client_id_here
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret_here
YOUTUBE_API_KEY=your_youtube_api_key_here
MARKDOWN_OUTPUT_PATH=path/to/markdown/files
IMAGE_OUTPUT_PATH=path/to/image/files
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
MASTODON_URL=your_mastodon_instance_url_here
MASTODON_ACCESS_TOKEN=your_mastodon_access_token_here
BLUESKY_HANDLE=your_handle.bsky.social
BLUESKY_PASSWORD=your_bluesky_password_here
```

## Usage

Run the script with a Bandcamp URL:
```bash
python card_creator.py
```

The script will:
1. Prompt you for a Bandcamp track URL
2. Scrape track information from Bandcamp
3. Download the track artwork
4. Generate a markdown file with frontmatter
5. Save files to the configured output paths
6. Ask if you want to post to Instagram, Mastodon, and/or Bluesky
7. If yes, prompt for custom hashtags
8. **Read the generated markdown file to create posts with track artwork and review**

### Social Media Integration

**All three social media platforms (Instagram, Mastodon, Bluesky) read directly from the generated markdown files.** This means:

- **Consistent data**: All posts use the same track information, review, and artwork
- **Standalone posting**: You can run the poster scripts independently with any markdown file
- **Flexible workflow**: Post immediately after creation or later using the markdown file path

#### Standalone Usage

You can also post to social media independently using any markdown file:

```bash
# Post to Instagram
python instagram_poster.py

# Post to Mastodon  
python mastodon_poster.py

# Post to Bluesky
python bluesky_poster.py
```

Each script will prompt you for the path to a markdown file and create a post using that data.

### Instagram Post Format

The Instagram post will include:
- Track artwork as the main image
- Track title and artist name
- Your track review
- Custom hashtags that you provide
- Link to streaming services (in bio)

Example caption:
```
Track Title by Artist Name

Your track review here.

Listen on Bandcamp, Spotify, and YouTube
Link in bio 🔗

#your #custom #hashtags #here
```

### Mastodon Post Format

The Mastodon post will include:
- Track artwork as the main image
- Track title and artist name
- Your track review
- Direct links to Bandcamp, Spotify, and YouTube
- Custom hashtags that you provide

Example post:
```
Track Title by Artist Name

Your track review here.

Listen on Bandcamp: https://artist.bandcamp.com/track/track-name
Spotify: https://open.spotify.com/track/...
YouTube: https://www.youtube.com/watch?v=...

#your #custom #hashtags #here
```

### Bluesky Post Format

The Bluesky post will include:
- Track artwork as the main image
- Track title and artist name
- Your track review
- Direct links to Bandcamp, Spotify, and YouTube
- Custom hashtags that you provide

Example post:
```
Track Title by Artist Name

Your track review here.

Listen on Bandcamp: https://artist.bandcamp.com/track/track-name
Spotify: https://open.spotify.com/track/...
YouTube: https://www.youtube.com/watch?v=...

#your #custom #hashtags #here
```

## Project Structure

```
cardcreator/
├── .venv/                  # Virtual environment
├── .env                    # Environment configuration
├── .env_template          # Template for environment variables
├── requirements.in        # Direct dependencies
├── requirements.txt       # Locked dependencies
├── card_creator.py        # Main script
├── instagram_poster.py    # Instagram posting functionality
├── mastodon_poster.py     # Mastodon posting functionality
├── bluesky_poster.py      # Bluesky posting functionality
└── _track.md.template     # Markdown template
```

## Development

### Managing Dependencies

This project uses `pip-tools` for dependency management:

1. Add new dependencies to `requirements.in`
2. Update locked dependencies:
```bash
uv pip compile requirements.in
```
3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

### Environment Variables

Required environment variables:
- `MARKDOWN_OUTPUT_PATH`: Path where markdown files will be saved
- `IMAGE_OUTPUT_PATH`: Path where images will be saved
- `INSTAGRAM_USERNAME`: Your Instagram username
- `INSTAGRAM_PASSWORD`: Your Instagram password
- `MASTODON_URL`: Your Mastodon instance URL (e.g., https://mastodon.social)
- `MASTODON_ACCESS_TOKEN`: Your Mastodon access token
- `BLUESKY_HANDLE`: Your Bluesky handle (e.g., username.bsky.social)
- `BLUESKY_PASSWORD`: Your Bluesky password

Optional environment variables:
- `SPOTIPY_CLIENT_ID`: Spotify API client ID
- `SPOTIPY_CLIENT_SECRET`: Spotify API client secret
- `YOUTUBE_API_KEY`: YouTube API key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- BeautifulSoup4 for web scraping
- Selenium for dynamic content handling
- Spotipy for Spotify integration
- Google API Client for YouTube integration
- Instagrapi for Instagram integration
- Mastodon.py for Mastodon integration
- atproto for Bluesky integration

## Website Integration

This tool is specifically designed to work with the [KDZU Astro website](http://kdzu.org). The generated markdown files and images are structured to work seamlessly with the website's Astro-based static site generation:

- Markdown files are saved to `~/Documents/GitHub/kdzu-org/src/content/tracks`
- Images are saved to `~/Documents/GitHub/kdzu-org/public/images/tracks`
- Frontmatter is formatted to match the website's content schema
- Images are optimized and stored in the correct location for the website

The generated content will appear on the website as track review pages with:
- Track artwork
- Artist and label information
- Bandcamp link
- Spotify and YouTube embeds (when available)
- Track review content 