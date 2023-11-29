"""Set up dict of env values from .env file."""
import os

from dotenv import load_dotenv


def config():
    """Load the secret email configuration from .env file."""
    load_dotenv()
    return {
        key: os.getenv(key)
        for key in ("EMAIL_USERNAME", "EMAIL_PASSWORD", "EMAIL_HOST")
    }
