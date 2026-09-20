import base64
import time
import uuid
from typing import Dict, Any, Tuple
from flask import Flask, jsonify, request
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

app = Flask(__name__)

# In-memory storage for key pairs
# Maps kid -> {"private_key": RSA_Obj, "public_key": RSA_Obj, "expiry": epoch_timestamp}
KEY_STORE: Dict[str, Dict[str, Any]] = {}

def int_to_base64url(val: int) -> str:
    """Helper to convert an integer to base64url-encoded string without padding."""
    val_bytes = val.to_bytes((val.bit_length() + 7) // 8, byteorder='big')
    return base64.urlsafe_b64encode(val_bytes).rstrip(b'=').decode('utf-8')

def generate_rsa_key_pair(expired: bool = False) -> Tuple[str, Any, int]:
    """Generates an RSA key pair with a unique Key ID (kid) and expiry timestamp."""
    kid = str(uuid.uuid4())
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    now = int(time.time())
    expiry = now - 3600 if expired else now + 3600  # Expired 1 hr ago OR valid for 1 hr
    
    KEY_STORE[kid] = {
        "private_key": private_key,
        "public_key": private_key.public_key(),
        "expiry": expiry
    }
    return kid, private_key, expiry

# Initialize database/keys at startup: 1 valid key and 1 expired key
VALID_KID, _, _ = generate_rsa_key_pair(expired=False)
EXPIRED_KID, _, _ = generate_rsa_key_pair(expired=True)


@app.route('/.well-known/jwks.json', methods=['GET'])
def jwks():
    """
    JWKS Endpoint: Serves unexpired public keys in JWK format.
    """
    now = int(time.time())
    valid_keys = []

    for kid, key_data in KEY_STORE.items():
        # Only include keys that have not expired
        if key_data['expiry'] > now:
            pub_numbers = key_data['public_key'].public_numbers()
            jwk = {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": kid,
                "n": int_to_base64url(pub_numbers.n),
                "e": int_to_base64url(pub_numbers.e)
            }
            valid_keys.append(jwk)

    return jsonify({"keys": valid_keys}), 200


@app.route('/auth', methods=['POST'])
def auth():
    """
    Auth Endpoint: Generates a signed JWT.
    Supports query parameter `?expired=true` to sign using an expired key.
    """
    expired_param = request.args.get('expired', '').lower() == 'true'
    now = int(time.time())

    # Select appropriate key based on query parameter
    target_kid = EXPIRED_KID if expired_param else VALID_KID
    key_info = KEY_STORE[target_kid]

    # Compute payload expiry timestamp
    token_exp = now - 3600 if expired_param else now + 3600

    payload = {
        "sub": "mock_user_123",
        "iat": now,
        "exp": token_exp
    }

    # Export private key to PEM format for PyJWT signing
    pem_private = key_info['private_key'].private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    token = jwt.encode(
        payload,
        pem_private,
        algorithm="RS256",
        headers={"kid": target_kid}
    )

    return jsonify({"jwt": token}), 200


if __name__ == '__main__':
    # Serve HTTP on port 8080 as specified by requirements
    app.run(host='0.0.0.0', port=8080)