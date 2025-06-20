# Mastodon Setup Guide

This guide will help you set up Mastodon posting functionality for the Card Creator tool.

## Prerequisites

1. A Mastodon account on any instance (e.g., mastodon.social, mastodon.art, etc.)
2. Python environment with the required dependencies installed

## Step 1: Create a Mastodon Application

1. **Log into your Mastodon instance** (e.g., https://mastodon.social)

2. **Navigate to Settings**:
   - Click on your profile picture in the top right
   - Select "Settings"

3. **Go to Development**:
   - In the left sidebar, click on "Development"
   - Click "New Application"

4. **Fill in the application details**:
   - **Application name**: `CardCreator` (or any name you prefer)
   - **Website**: Leave blank or add your website URL
   - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob`
   - **Scopes**: Check both `read` and `write`
   - **Submit** the form

5. **Copy your access token**:
   - After creating the application, you'll see an "Access token" field
   - Copy this token (it's a long string of letters and numbers)

## Step 2: Configure Environment Variables

1. **Open your `.env` file** in the Card Creator directory

2. **Add your Mastodon credentials**:
   ```env
   MASTODON_URL=https://your-instance.com
   MASTODON_ACCESS_TOKEN=your_access_token_here
   ```

   Replace:
   - `https://your-instance.com` with your Mastodon instance URL (e.g., `https://mastodon.social`)
   - `your_access_token_here` with the access token you copied in Step 1

## Step 3: Test the Setup

1. **Install the Mastodon library** (if not already installed):
   ```bash
   pip install mastodon.py
   ```

2. **Run the Mastodon poster script** to test:
   ```bash
   python mastodon_poster.py
   ```

   This will check if your credentials are properly configured.

## Step 4: Use with Card Creator

Now when you run the main Card Creator script:
```bash
python card_creator.py
```

After creating a track review, you'll be prompted to post to Mastodon. The script will:
1. Ask if you want to post to Mastodon
2. Prompt for custom hashtags
3. Upload the track artwork
4. Post the review with links to streaming services

## Troubleshooting

### Common Issues

1. **"Mastodon credentials not found"**
   - Make sure your `.env` file contains both `MASTODON_URL` and `MASTODON_ACCESS_TOKEN`
   - Check that there are no extra spaces or quotes around the values

2. **"Error posting to Mastodon"**
   - Verify your access token is correct
   - Check that your Mastodon instance URL is correct
   - Ensure your account has posting permissions

3. **"Image upload failed"**
   - Make sure the image file exists in your images directory
   - Check that the image format is supported (JPEG, PNG, GIF)

### Getting Help

- Check the [Mastodon.py documentation](https://mastodonpy.readthedocs.io/)
- Verify your Mastodon instance is working by logging in normally
- Test with a simple post first before using with Card Creator

## Security Notes

- Keep your access token secure and don't share it
- The token gives your application permission to post on your behalf
- You can revoke the token in your Mastodon settings if needed
- Consider using environment variables or a secure credential manager for production use 