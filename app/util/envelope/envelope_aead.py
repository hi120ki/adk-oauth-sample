#!/usr/bin/env python3
"""
Tink Envelope AEAD implementation for encrypting and decrypting data using GCP KMS.
"""

from __future__ import annotations

import base64
import logging
from typing import Optional

import tink
from tink import aead
from tink.integration import gcpkms

logger = logging.getLogger(__name__)


class EnvelopeAEAD:
    """Envelope AEAD helper backed by a GCP KMS-held KEK."""

    def __init__(self, kek_uri: str, credentials_path: Optional[str] = None):
        """Initialize EnvelopeAEAD with GCP KMS KEK URI."""
        try:
            aead.register()
            self.client = gcpkms.GcpKmsClient(kek_uri, credentials_path)
            self.remote_aead = self.client.get_aead(kek_uri)
            self.envelope_aead = aead.KmsEnvelopeAead(
                aead.aead_key_templates.AES256_GCM, self.remote_aead
            )
        except Exception as exc:
            logger.exception("Failed to initialize EnvelopeAEAD kek_uri=%s", kek_uri)
            raise tink.TinkError("Failed to initialize EnvelopeAEAD") from exc

    def _encrypt(self, plaintext: bytes, additional_data: bytes = b"") -> bytes:
        """Encrypt plaintext with optional additional authenticated data (AAD)."""
        try:
            return self.envelope_aead.encrypt(plaintext, additional_data)
        except Exception as exc:
            logger.exception("Envelope encryption failed")
            raise tink.TinkError("Failed to encrypt data") from exc

    def _decrypt(self, ciphertext: bytes, additional_data: bytes = b"") -> bytes:
        """Decrypt ciphertext with optional additional authenticated data (AAD)."""
        try:
            return self.envelope_aead.decrypt(ciphertext, additional_data)
        except Exception as exc:
            logger.exception("Envelope decryption failed")
            raise tink.TinkError("Failed to decrypt data") from exc

    def encrypt_token(self, token: str, additional_data: str = "") -> str:
        """Encrypt token data and return Base64 encoded string."""
        try:
            ciphertext = self._encrypt(
                token.encode("utf-8"), additional_data.encode("utf-8")
            )
            return base64.b64encode(ciphertext).decode("utf-8")
        except Exception as exc:
            logger.exception("Failed to encrypt token")
            raise tink.TinkError("Failed to encrypt token") from exc

    def decrypt_token(self, base64_ciphertext: str, additional_data: str = "") -> str:
        """Decrypt token data from Base64 encoded string."""
        try:
            ciphertext = base64.b64decode(base64_ciphertext.encode("utf-8"))
            plaintext = self._decrypt(ciphertext, additional_data.encode("utf-8"))
            return plaintext.decode("utf-8")
        except Exception as exc:
            logger.exception("Failed to decrypt token")
            raise tink.TinkError("Failed to decrypt token") from exc
