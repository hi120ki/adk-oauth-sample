#!/usr/bin/env python3
"""
Configuration management for environment variables
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from util.secret.secret import SecretManagerClient


class Config:
    """
    Configuration class for managing environment variables.
    This class loads environment variables using dotenv and validates
    that all required variables are present.
    """

    def __init__(self, dotenv_path: Optional[str] = None):
        """
        Initialize Config with optional dotenv file path.

        Args:
            dotenv_path: Optional path to .env file.
                        If None, loads from default locations.

        Note:
            Exits the program if required environment variables are missing
        """
        # Load environment variables from .env file
        load_dotenv(dotenv_path)

        # Validate all required environment variables
        self._validate_environment_variables()

        self.secret: SecretManagerClient = SecretManagerClient(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
        )

    def _validate_environment_variables(self) -> None:
        """
        Validate that all required environment variables are present.

        Note:
            Exits the program if any required environment variable is missing
        """
        required_vars = [
            "GCP_KMS_KEY_URI",
            "GSM_GOOGLE_CLIENT_ID",
            "GSM_GOOGLE_CLIENT_SECRET",
            "GSM_SESSION_SECRET_KEY_NAME",
            "GOOGLE_CLOUD_PROJECT",
            "GOOGLE_CLOUD_LOCATION",
            "APP_NAME",
            "REDIRECT_URI",
            "IAP_AUDIENCE",
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            sys.exit(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    @property
    def gcp_kms_key_uri(self) -> str:
        """
        Get GCP KMS Key URI for envelope encryption.

        Returns:
            GCP KMS Key URI string
        """
        return os.getenv("GCP_KMS_KEY_URI", "")

    @property
    def google_client_id(self) -> str:
        """
        Get Google OAuth2 Client ID.

        Returns:
            Google Client ID string
        """
        return self.secret.get_secret(os.getenv("GSM_GOOGLE_CLIENT_ID", ""))

    @property
    def google_client_secret(self) -> str:
        """
        Get Google OAuth2 Client Secret.

        Returns:
            Google Client Secret string
        """
        return self.secret.get_secret(os.getenv("GSM_GOOGLE_CLIENT_SECRET", ""))

    @property
    def session_secret_key(self) -> str:
        """
        Get Session Secret Key Name for session middleware.

        Returns:
            Session Secret Key Name string
        """
        return self.secret.get_secret(os.getenv("GSM_SESSION_SECRET_KEY_NAME", ""))

    @property
    def google_cloud_project(self) -> str:
        """
        Get Google Cloud Project ID.

        Returns:
            Google Cloud Project ID string
        """
        return os.getenv("GOOGLE_CLOUD_PROJECT", "")

    @property
    def google_cloud_location(self) -> str:
        """
        Get Google Cloud Location.

        Returns:
            Google Cloud Location string
        """
        return os.getenv("GOOGLE_CLOUD_LOCATION", "")

    @property
    def app_name(self) -> str:
        """
        Get Application Name.

        Returns:
            Application Name string
        """
        return os.getenv("APP_NAME", "")

    @property
    def redirect_uri(self) -> str:
        """
        Get OAuth2 Redirect URI.

        Returns:
            OAuth2 Redirect URI string
        """
        return os.getenv("REDIRECT_URI", "")

    @property
    def iap_audience(self) -> str:
        """
        Get the expected IAP audience claim value.

        Returns:
            IAP audience string
        """
        return os.getenv("IAP_AUDIENCE", "")

    @property
    def port(self) -> int:
        """
        Get application port number.

        Returns:
            Port number as integer (default: 8000)
        """
        return int(os.getenv("PORT", "8000"))
