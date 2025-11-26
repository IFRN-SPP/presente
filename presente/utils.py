from django.core.signing import Signer, TimestampSigner, BadSignature, SignatureExpired


def encode_activity_id(activity_id):
    """
    Encode activity ID to a hash for public URLs.
    """
    signer = Signer(salt="activity-public")
    return signer.sign(str(activity_id))


def decode_activity_id(encoded_id):
    """
    Decode hashed activity ID back to integer.
    Returns None if invalid.
    """
    try:
        signer = Signer(salt="activity-public")
        activity_id = signer.unsign(encoded_id)
        return int(activity_id)
    except (BadSignature, ValueError):
        return None


def generate_checkin_token(activity_id, timeout_seconds):
    """
    Generate a time-based token for check-in that expires after timeout_seconds.
    """
    signer = TimestampSigner(salt="activity-checkin")
    return signer.sign(str(activity_id))


def verify_checkin_token(token, timeout_seconds):
    """
    Verify and decode a check-in token.
    Returns activity_id if valid and not expired, None otherwise.
    """
    try:
        signer = TimestampSigner(salt="activity-checkin")
        activity_id = signer.unsign(token, max_age=timeout_seconds)
        return int(activity_id)
    except (BadSignature, SignatureExpired):
        return None
