#!/usr/bin/env python3
"""
Credential management with encrypted refresh tokens
"""

from typing import Optional

from authlib.integrations.requests_client import OAuth2Session
from google.adk.tools import ToolContext
from util.envelope.envelope_aead import EnvelopeAEAD


class Credential:
    """
    Class for managing encrypted refresh tokens
    """

    def __init__(self, envelope_aead: EnvelopeAEAD, oauth_session=OAuth2Session):
        """
        Initialize with EnvelopeAEAD and OAuth2Session
        """
        self.envelope_aead = envelope_aead
        self.oauth_session = oauth_session

    def encrypt_token(self, token: str, user_id: str) -> str:
        """
        Encrypt token using user_id as additional authenticated data

        Args:
            token: Refresh token to encrypt
            user_id: User's email address

        Returns:
            Encrypted token (Base64 encoded)
        """
        return self.envelope_aead.encrypt_token(token, user_id)

    def get_decrypted_token_from_context(
        self, tool_context: ToolContext, state_key: str
    ) -> Optional[str]:
        """
        Get encrypted token from ToolContext and decrypt it

        Args:
            tool_context: Tool context containing encrypted token
            state_key: Key in the state dictionary where the encrypted token is stored

        Returns:
            Decrypted refresh token, or None if not authenticated
        """
        try:
            if state_key not in tool_context.state:
                return None

            encrypted_token = tool_context.state[state_key]
            user_id = tool_context._invocation_context.user_id

            return self.envelope_aead.decrypt_token(encrypted_token, user_id)
        except Exception as e:
            print(f"Failed to decrypt token: {e}")
            return None

    def _get_access_token_from_refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        Get access token from refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            Access token, or None if failed to refresh
        """
        try:
            token = self.oauth_session.refresh_token(
                refresh_token=refresh_token,
            )

            return token.get("access_token")
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None

    def get_access_token_from_context(
        self, tool_context: ToolContext, state_key: str
    ) -> Optional[str]:
        """
        Get access token using the refresh token stored in ToolContext

        Args:
            tool_context: Tool context containing encrypted token
            state_key: Key in the state dictionary where the encrypted token is stored

        Returns:
            Access token, or None if failed to retrieve
        """
        refresh_token = self.get_decrypted_token_from_context(
            tool_context=tool_context, state_key=state_key
        )
        if not refresh_token:
            return None

        return self._get_access_token_from_refresh_token(refresh_token)
