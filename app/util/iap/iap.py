#!/usr/bin/env python3
"""Helpers for verifying Google IAP JWT assertions."""

import logging

import jwt
from jwt import InvalidTokenError, PyJWKClient
from starlette.requests import Request


class IAPVerificationError(Exception):
    """Custom exception for IAP verification errors."""

    pass


logger = logging.getLogger(__name__)


def verify_iap_jwt_from_request(
    request: Request, *, audience: str, issuer: str = "https://cloud.google.com/iap"
) -> str:
    """
    Verify an IAP-signed JWT from a Starlette request and return the email claim.

    Args:
        request: The Starlette request object containing the IAP JWT assertion header.
        audience: The expected audience (aud) claim.
        issuer: The expected issuer (iss) claim. Default is "https://cloud.google.com/iap".

    Returns:
        The email claim from the JWT if verification is successful.

    Raises:
        IAPVerificationError: When IAP assertion is missing, invalid, or verification fails.
    """
    assertion = request.headers.get("X-Goog-IAP-JWT-Assertion")

    if not assertion:
        raise IAPVerificationError(
            "X-Goog-IAP-JWT-Assertion header is required. Please enable IAP."
        )

    try:
        jwk_client = PyJWKClient("https://www.gstatic.com/iap/verify/public_key-jwk")
        signing_key = jwk_client.get_signing_key_from_jwt(assertion)

        claim = jwt.decode(
            assertion,
            signing_key.key,
            algorithms=["ES256"],
            audience=audience,
            issuer=issuer,
        )

        email = claim.get("email")
        if not email:
            raise IAPVerificationError("Email claim is missing in IAP assertion")

        return email
    except InvalidTokenError as exc:
        logger.exception("Invalid IAP JWT")
        raise IAPVerificationError("Failed to verify IAP JWT") from exc
    except Exception as exc:
        logger.exception("Unexpected error during IAP verification")
        raise IAPVerificationError("Unexpected error during IAP verification") from exc
