#!/usr/bin/env python3
"""
Google Cloud Secret Manager client helper.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from google.cloud import secretmanager
from google.cloud.secretmanager_v1.services.secret_manager_service import (
    SecretManagerServiceClient,
)
from google.cloud.secretmanager_v1.types import AccessSecretVersionRequest

logger = logging.getLogger(__name__)


class SecretManagerError(RuntimeError):
    """Raised when Secret Manager operations fail."""


class SecretManagerClient:
    """Simple wrapper around the Google Secret Manager client."""

    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        """Initialize the Secret Manager client."""
        try:
            self.project_id = project_id
            if credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

            self.client: SecretManagerServiceClient = (
                secretmanager.SecretManagerServiceClient()
            )
        except Exception as exc:
            logger.exception("Failed to instantiate Secret Manager client")
            raise SecretManagerError("Failed to create Secret Manager client") from exc

    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """Retrieve a secret from Google Cloud Secret Manager."""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
            request = AccessSecretVersionRequest(name=name)
            response = self.client.access_secret_version(request=request)
            return response.payload.data.decode("utf-8")
        except Exception as exc:
            logger.exception(
                "Failed to access secret project=%s secret_id=%s version=%s",
                self.project_id,
                secret_id,
                version,
            )
            raise SecretManagerError(f"Failed to access secret {secret_id}") from exc
