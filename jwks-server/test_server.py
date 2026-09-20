import pytest
import jwt
from server import app, KEY_STORE, VALID_KID, EXPIRED_KID

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_jwks_endpoint_returns_only_valid_keys(client):
    """Test that JWKS endpoint excludes expired keys."""
    response = client.get('/.well-known/jwks.json')
    assert response.status_code == 200
    
    data = response.get_json()
    assert "keys" in data
    
    # Check that returned kids only contain active keys
    kids = [key['kid'] for key in data['keys']]
    assert VALID_KID in kids
    assert EXPIRED_KID not in kids

def test_auth_valid_token(client):
    """Test /auth POST endpoint returning a valid unexpired JWT."""
    response = client.post('/auth')
    assert response.status_code == 200
    
    data = response.get_json()
    assert "jwt" in data
    
    token = data["jwt"]
    unverified_header = jwt.get_unverified_header(token)
    assert unverified_header["kid"] == VALID_KID

def test_auth_expired_token(client):
    """Test /auth POST endpoint with ?expired=true parameter."""
    response = client.post('/auth?expired=true')
    assert response.status_code == 200
    
    data = response.get_json()
    assert "jwt" in data
    
    token = data["jwt"]
    unverified_header = jwt.get_unverified_header(token)
    assert unverified_header["kid"] == EXPIRED_KID