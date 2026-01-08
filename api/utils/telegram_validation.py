"""Telegram Mini App initData validation."""
import hmac
import hashlib
import logging
from typing import Optional, Dict
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def validate_telegram_init_data(init_data: str, bot_token: str) -> Dict[str, str]:
    """
    Validate Telegram Mini App initData signature.
    
    Args:
        init_data: Raw initData string from Telegram.WebApp.initData
        bot_token: Telegram bot token for signature validation
        
    Returns:
        Dictionary with parsed and validated data (user, auth_date, etc.)
        
    Raises:
        ValueError: If signature is invalid or data is too old
    """
    if not init_data:
        raise ValueError("initData is empty")
    
    if not bot_token:
        raise ValueError("bot_token is required for validation")
    
    # Parse initData (it's URL-encoded query string)
    # Format: "user=%7B%22id%22%3A123%7D&auth_date=1234567890&hash=abc123..."
    params = {}
    for pair in init_data.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[key] = value
    
    # Extract hash
    if 'hash' not in params:
        raise ValueError("hash parameter missing in initData")
    
    received_hash = params.pop('hash')
    
    # Sort parameters and create data_check_string
    # Format: "auth_date=1234567890\nquery_id=abc\nuser=..."
    sorted_params = sorted(params.items())
    data_check_string = '\n'.join([f"{key}={value}" for key, value in sorted_params])
    
    # Create secret key: HMAC-SHA256('WebAppData', bot_token)
    secret_key = hmac.new(
        'WebAppData'.encode('utf-8'),
        bot_token.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Calculate signature: HMAC-SHA256(secret_key, data_check_string)
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Compare hashes
    if calculated_hash != received_hash:
        logger.warning(f"Invalid signature: calculated={calculated_hash}, received={received_hash}")
        raise ValueError("Invalid signature - data may be tampered")
    
    # Check auth_date (should be within last 5 minutes)
    if 'auth_date' in params:
        try:
            auth_date = int(params['auth_date'])
            current_time = int(datetime.now(timezone.utc).timestamp())
            time_diff = current_time - auth_date
            
            if time_diff > 300:  # 5 minutes = 300 seconds
                logger.warning(f"Auth data too old: {time_diff} seconds")
                raise ValueError(f"Auth data is too old ({time_diff} seconds) - possible replay attack")
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid auth_date: {e}")
            raise ValueError(f"Invalid auth_date: {e}")
    else:
        logger.warning("auth_date missing in initData")
        raise ValueError("auth_date parameter missing")
    
    # Parse user data if present
    user_data = None
    if 'user' in params:
        import json
        from urllib.parse import unquote
        try:
            user_json = unquote(params['user'])
            user_data = json.loads(user_json)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse user data: {e}")
            # Don't raise error, user might not be present
    
    logger.info(f"Successfully validated initData for user_id={user_data.get('id') if user_data else 'unknown'}")
    
    return {
        'user': user_data,
        'auth_date': int(params['auth_date']),
        'query_id': params.get('query_id'),
        'all_params': params
    }


def extract_user_id_from_init_data(init_data: str, bot_token: str) -> Optional[int]:
    """
    Extract and validate user_id from initData.
    
    Args:
        init_data: Raw initData string from Telegram.WebApp.initData
        bot_token: Telegram bot token for signature validation
        
    Returns:
        User ID if validation successful, None otherwise
    """
    try:
        validated_data = validate_telegram_init_data(init_data, bot_token)
        user = validated_data.get('user')
        if user and 'id' in user:
            return int(user['id'])
        return None
    except Exception as e:
        logger.error(f"Failed to extract user_id from initData: {e}")
        return None

