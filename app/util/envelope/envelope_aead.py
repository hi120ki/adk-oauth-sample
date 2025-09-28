#!/usr/bin/env python3
"""
Tink Envelope AEAD implementation for encrypting and decrypting data using GCP KMS
"""

import base64
from typing import Optional

import tink
from tink import aead
from tink.integration import gcpkms


class EnvelopeAEAD:
    """
    EnvelopeAEAD wraps Tink's AEAD interface for envelope encryption using GCP KMS.
    This class provides a simple interface for encrypting and decrypting data
    using envelope encryption with a Key Encryption Key (KEK) stored in GCP KMS.
    """

    def __init__(self, kek_uri: str, credentials_path: Optional[str] = None):
        """
        Initialize EnvelopeAEAD with GCP KMS KEK URI.
        Args:
            kek_uri: GCP KMS URI format:
                    "gcp-kms://projects/PROJECT_ID/locations/LOCATION/keyRings/RING_ID/cryptoKeys/KEY_ID"
            credentials_path: Optional path to GCP credentials JSON file.
                            If None, uses default authentication (e.g., Workload Identity)
        Raises:
            tink.TinkError: If initialization fails
        """
        try:
            # Register AEAD key managers
            aead.register()

            # Create GCP KMS client
            self.client = gcpkms.GcpKmsClient(kek_uri, credentials_path)

            # Get remote AEAD from KMS
            self.remote_aead = self.client.get_aead(kek_uri)

            # Create envelope AEAD primitive using AES256 GCM for data encryption
            self.envelope_aead = aead.KmsEnvelopeAead(
                aead.aead_key_templates.AES256_GCM, self.remote_aead
            )

        except Exception as e:
            raise tink.TinkError(f"Failed to initialize EnvelopeAEAD: {e}")

    def _encrypt(self, plaintext: bytes, additional_data: bytes = b"") -> bytes:
        """
        Encrypt plaintext with optional additional authenticated data (AAD).
        Args:
            plaintext: Data to encrypt
            additional_data: Optional additional authenticated data
        Returns:
            Encrypted ciphertext bytes
        Raises:
            tink.TinkError: If encryption fails
        """
        try:
            return self.envelope_aead.encrypt(plaintext, additional_data)
        except Exception as e:
            raise tink.TinkError(f"Failed to encrypt: {e}")

    def _decrypt(self, ciphertext: bytes, additional_data: bytes = b"") -> bytes:
        """
        Decrypt ciphertext with optional additional authenticated data (AAD).
        Args:
            ciphertext: Data to decrypt
            additional_data: Optional additional authenticated data (must match encryption)
        Returns:
            Decrypted plaintext bytes
        Raises:
            tink.TinkError: If decryption fails
        """
        try:
            return self.envelope_aead.decrypt(ciphertext, additional_data)
        except Exception as e:
            raise tink.TinkError(f"Failed to decrypt: {e}")

    def encrypt_token(self, token: str, additional_data: str = "") -> str:
        """
        Encrypt token data and return Base64 encoded string.
        Args:
            token: String token to encrypt
            additional_data: Optional additional authenticated data string
        Returns:
            Base64 encoded encrypted token
        Raises:
            tink.TinkError: If encryption fails
        """
        try:
            ciphertext = self._encrypt(
                token.encode("utf-8"), additional_data.encode("utf-8")
            )
            return base64.b64encode(ciphertext).decode("utf-8")
        except Exception as e:
            raise tink.TinkError(f"Failed to encrypt token: {e}")

    def decrypt_token(self, base64_ciphertext: str, additional_data: str = "") -> str:
        """
        Decrypt token data from Base64 encoded string.
        Args:
            base64_ciphertext: Base64 encoded encrypted token
            additional_data: Optional additional authenticated data string (must match encryption)
        Returns:
            Decrypted token string
        Raises:
            tink.TinkError: If decryption fails
        """
        try:
            ciphertext = base64.b64decode(base64_ciphertext.encode("utf-8"))
            plaintext = self._decrypt(ciphertext, additional_data.encode("utf-8"))
            return plaintext.decode("utf-8")
        except Exception as e:
            raise tink.TinkError(f"Failed to decrypt token: {e}")
