from django.conf import settings
import hashlib
import base64


def encode_activity_id(activity_id):
    """
    Encode activity ID to a hash for public URLs.
    Uses HMAC-based hashing to create a URL-safe hash.
    """
    # Create a hash using the activity ID and secret key
    message = f"{activity_id}:activity-public"
    hash_obj = hashlib.blake2b(
        message.encode(), key=settings.SECRET_KEY.encode()[:32], digest_size=16
    )
    # Convert to URL-safe base64
    hash_bytes = hash_obj.digest()
    # encoded = base64.urlsafe_b64encode(hash_bytes).decode().rstrip("=")
    # Store mapping: hash -> id (we'll need to store this)
    # For now, we'll use a reversible encoding with the ID embedded
    # Format: base64(id_bytes + hash_bytes)
    id_bytes = activity_id.to_bytes(8, byteorder="big")
    combined = id_bytes + hash_bytes
    result = base64.urlsafe_b64encode(combined).decode().rstrip("=")
    return result


def decode_activity_id(encoded_id):
    """
    Decode hashed activity ID back to integer.
    Returns None if invalid.
    """
    try:
        # Add padding back if needed
        padding = 4 - (len(encoded_id) % 4)
        if padding != 4:
            encoded_id += "=" * padding

        # Decode from base64
        combined = base64.urlsafe_b64decode(encoded_id)

        # Extract ID (first 8 bytes) and hash (remaining bytes)
        id_bytes = combined[:8]
        hash_bytes = combined[8:]

        activity_id = int.from_bytes(id_bytes, byteorder="big")

        # Verify the hash
        message = f"{activity_id}:activity-public"
        expected_hash = hashlib.blake2b(
            message.encode(), key=settings.SECRET_KEY.encode()[:32], digest_size=16
        ).digest()

        if hash_bytes != expected_hash:
            return None

        return activity_id
    except (ValueError, Exception):
        return None


def generate_checkin_token(activity_id, timeout_seconds):
    """
    Generate a time-based token for check-in that expires after timeout_seconds.
    Uses HMAC-based hashing with embedded timestamp.
    """
    import time

    # Get current timestamp
    timestamp = int(time.time())

    # Create message with activity ID and timestamp
    message = f"{activity_id}:{timestamp}:activity-checkin"
    hash_obj = hashlib.blake2b(
        message.encode(), key=settings.SECRET_KEY.encode()[:32], digest_size=16
    )
    hash_bytes = hash_obj.digest()

    # Format: activity_id (8 bytes) + timestamp (8 bytes) + hash (16 bytes)
    id_bytes = activity_id.to_bytes(8, byteorder="big")
    timestamp_bytes = timestamp.to_bytes(8, byteorder="big")
    combined = id_bytes + timestamp_bytes + hash_bytes

    # Encode to URL-safe base64
    result = base64.urlsafe_b64encode(combined).decode().rstrip("=")
    return result


def verify_checkin_token(token, timeout_seconds):
    """
    Verify and decode a check-in token.
    Returns activity_id if valid and not expired, None otherwise.
    """
    import time

    try:
        # Add padding back if needed
        padding = 4 - (len(token) % 4)
        if padding != 4:
            token += "=" * padding

        # Decode from base64
        combined = base64.urlsafe_b64decode(token)

        # Extract components
        id_bytes = combined[:8]
        timestamp_bytes = combined[8:16]
        hash_bytes = combined[16:]

        activity_id = int.from_bytes(id_bytes, byteorder="big")
        timestamp = int.from_bytes(timestamp_bytes, byteorder="big")

        # Check if token has expired
        current_time = int(time.time())
        if current_time - timestamp > timeout_seconds:
            return None

        # Verify the hash
        message = f"{activity_id}:{timestamp}:activity-checkin"
        expected_hash = hashlib.blake2b(
            message.encode(), key=settings.SECRET_KEY.encode()[:32], digest_size=16
        ).digest()

        if hash_bytes != expected_hash:
            return None

        return activity_id
    except (ValueError, Exception):
        return None
