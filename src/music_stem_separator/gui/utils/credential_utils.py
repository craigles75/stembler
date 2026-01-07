"""Utilities for managing Spotify credentials."""

import os
from typing import Tuple, Optional


def check_spotify_credentials() -> Tuple[bool, Optional[str]]:
    """
    Check if Spotify credentials are configured.

    Returns:
        Tuple of (credentials_valid, error_message)
    """
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

    if not client_id:
        return False, "SPOTIFY_CLIENT_ID environment variable not set"

    if not client_secret:
        return False, "SPOTIFY_CLIENT_SECRET environment variable not set"

    # Basic validation - check they're not empty
    if not client_id.strip():
        return False, "SPOTIFY_CLIENT_ID is empty"

    if not client_secret.strip():
        return False, "SPOTIFY_CLIENT_SECRET is empty"

    return True, None


def get_credential_setup_instructions() -> str:
    """
    Get instructions for setting up Spotify credentials.

    Returns:
        Multi-line string with setup instructions
    """
    return """To use Spotify URLs, you need to set up Spotify API credentials:

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app details and click "Create"
5. Copy your Client ID and Client Secret

Then set these environment variables:

**On macOS/Linux:**
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"

**On Windows (Command Prompt):**
set SPOTIFY_CLIENT_ID=your_client_id_here
set SPOTIFY_CLIENT_SECRET=your_client_secret_here

**On Windows (PowerShell):**
$env:SPOTIFY_CLIENT_ID="your_client_id_here"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret_here"

After setting the variables, restart the application."""


def has_any_credentials() -> bool:
    """
    Quick check if any credentials are set (even if invalid).

    Returns:
        True if at least one credential variable exists
    """
    return bool(
        os.environ.get("SPOTIFY_CLIENT_ID") or os.environ.get("SPOTIFY_CLIENT_SECRET")
    )
