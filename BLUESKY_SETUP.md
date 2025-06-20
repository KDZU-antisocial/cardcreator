# Bluesky Setup Guide

This guide will help you set up Bluesky posting functionality for the Card Creator tool.

## Prerequisites

1. A Bluesky account (sign up at https://bsky.app)
2. Python environment with the required dependencies installed

## Step 1: Get Your Bluesky Credentials

1. **Log into your Bluesky account** at https://bsky.app

2. **Find your handle**:
   - Your handle is your username (e.g., `username.bsky.social`)
   - You can find this in your profile or account settings

3. **Use your account password**:
   - Bluesky uses your regular account password
   - No app setup or access tokens required (unlike Mastodon)

## Step 2: Configure Environment Variables

1. **Open your `.env` file** in the Card Creator directory

2. **Add your Bluesky credentials**:
   ```env
   BLUESKY_HANDLE=your_handle.bsky.social
   BLUESKY_PASSWORD=your_password_here
   ```

   Replace:
   - `your_handle.bsky.social` with your actual Bluesky handle
   - `your_password_here` with your Bluesky account password

## Step 3: Install the Bluesky Library

1. **Install the atproto library**:
   ```bash
   uv pip install atproto
   ```

## Step 4: Test the Setup

1. **Run the Bluesky poster script** to test:
   ```bash
   python bluesky_poster.py
   ```

   This will check if your credentials are properly configured.

## Step 5: Use with Card Creator

Now when you run the main Card Creator script:
```bash
python card_creator.py
```

After creating a track review, you'll be prompted to post to Bluesky. The script will:
1. Ask if you want to post to Bluesky
2. Prompt for custom hashtags
3. Upload the track artwork
4. Post the review with links to streaming services

## Troubleshooting

### Common Issues

1. **"Bluesky credentials not found"**
   - Make sure your `.env` file contains both `BLUESKY_HANDLE` and `BLUESKY_PASSWORD`
   - Check that there are no extra spaces or quotes around the values

2. **"Error posting to Bluesky"**
   - Verify your handle and password are correct
   - Check that your Bluesky account is active
   - Ensure you can log in normally at https://bsky.app

3. **"Image upload failed"**
   - Make sure the image file exists in your images directory
   - Check that the image format is supported (JPEG, PNG, GIF)

### Getting Help

- Check the [atproto documentation](https://atproto.com/)
- Verify your Bluesky account is working by logging in normally
- Test with a simple post first before using with Card Creator

## Security Notes

- Keep your Bluesky password secure and don't share it
- The password is used to authenticate with Bluesky's servers
- Consider using environment variables or a secure credential manager for production use
- Bluesky uses your regular account credentials, so treat them with the same security as your main account

## Bluesky Post Format

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