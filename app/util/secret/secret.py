#!/usr/bin/env python3
"""
Google Cloud Secret Manager client implementation forsimple interface for retrieving secrets
"""
import os
from typing import Optional

from google.cloud import secretmanager
from google.cloud.secretmanager_v1.services.secret_manager_service import (
    SecretManagerServiceClient,
)
from google.cloud.secretmanager_v1.types import AccessSecretVersionRequest


class SecretManagerClient:
    """
    SecretManagerClient wraps the Google Secret Manager client.
    This class provides a simple interface for retrieving secrets
    from Google Cloud Secret Manager.
    """

    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        """
        Initialize SecretManagerClient with project ID.

        Args:
            project_id: GCP project ID where secrets are stored
            credentials_path: Optional path to GCP credentials JSON file.
                            If None, uses default authentication (e.g., Workload Identity)

        Raises:
            Exception: If client initialization fails
        """
        try:
            self.project_id = project_id

            # Create the Secret Manager client
            if credentials_path:
                # If credentials path is provided, use it for authentication
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

            self.client: SecretManagerServiceClient = (
                secretmanager.SecretManagerServiceClient()
            )
        except Exception as e:
            raise Exception(f"Failed to create secret manager client: {e}")

    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Retrieve a secret from Google Cloud Secret Manager.

        Args:
            secret_id: The ID of the secret to retrieve
            version: The version of the secret to retrieve (default: "latest")

        Returns:
            The secret data as a string

        Raises:
            Exception: If secret retrieval fails
        """
        try:
            # Build the resource name for the secret version
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"

            # Create the request
            request = AccessSecretVersionRequest(name=name)

            # Access the secret version
            response = self.client.access_secret_version(request=request)

            # Return the secret data as string
            return response.payload.data.decode("utf-8")

        except Exception as e:
            raise Exception(f"Failed to access secret {secret_id}: {e}")
