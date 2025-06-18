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

## Prerequisites

- Python 3.11 or higher
- Chrome browser (for Selenium)
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
```

## Usage

Run the script with a Bandcamp URL:
```bash
python track_creator.py "https://bandcamp.com/track/your-track-url"
```

The script will:
1. Scrape track information from Bandcamp
2. Download the track artwork
3. Generate a markdown file with frontmatter
4. Save files to the configured output paths

## Project Structure

```
cardcreator/
├── .venv/                  # Virtual environment
├── images/                 # Local image storage
├── .env                    # Environment configuration
├── .env_template          # Template for environment variables
├── requirements.in        # Direct dependencies
├── requirements.txt       # Locked dependencies
├── track_creator.py       # Main script
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