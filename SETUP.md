# Setup Guide

## Spotify Credentials Setup

To use the Spotify integration feature, you need to obtain Spotify API credentials:

### 1. Create a Spotify Developer Account

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account (or create one if needed)
3. Click "Create App"

### 2. Create a New App

1. Fill in the app details:
   - **App name**: `Music Stem Separator` (or any name you prefer)
   - **App description**: `AI-powered music stem separation tool`
   - **Website**: `https://github.com/craigles75/stembler` (optional)
   - **Redirect URI**: `http://localhost:8080` (required but not used)
   - **API/SDKs**: Check "Web API"
   - **App type**: Choose "Non-commercial" or "Commercial" as appropriate

2. Click "Save"

### 3. Get Your Credentials

1. Once your app is created, you'll see the app dashboard
2. Click on your app name
3. You'll see your **Client ID** and **Client Secret**
4. Copy these values - you'll need them for the environment variables

### 4. Set Environment Variables

#### Option A: Export in Terminal (Temporary)
```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
```

#### Option B: Create a .env file (Recommended)
Create a `.env` file in your project root:
```bash
# .env file
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

Then load it before running:
```bash
source .env
stem-separator "https://open.spotify.com/track/..."
```

#### Option C: Add to Shell Profile (Permanent)
Add to your `~/.bashrc`, `~/.zshrc`, or equivalent:
```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
```

Then reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

### 5. Test the Setup

```bash
# Test with a Spotify URL
stem-separator "https://open.spotify.com/track/7snQQk1zcKl8gZ92AnueZW" -v
```

## Security Notes

- **Never commit your credentials** to version control
- Add `.env` to your `.gitignore` file (already done)
- Keep your Client Secret private
- If credentials are compromised, regenerate them in the Spotify dashboard

## Troubleshooting

### "Spotify credentials not found" Error
- Make sure environment variables are set correctly
- Check that variable names are exactly `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
- Restart your terminal after setting environment variables

### "Invalid client" Error
- Verify your credentials are correct
- Make sure there are no extra spaces or quotes in your environment variables
- Check that your Spotify app is active in the dashboard

### "Rate limit exceeded" Error
- Spotify has API rate limits
- Wait a few minutes and try again
- Consider implementing rate limiting in your usage
