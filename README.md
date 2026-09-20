# JWKS Server

A basic Python Flask server that demonstrates JSON Web Key Set (JWKS) and JWT authentication. It generates RSA key pairs, assigns each key a unique key ID (`kid`), serves active public keys, and returns signed JWTs.

## Endpoints

* **`GET /.well-known/jwks.json`** — Returns unexpired public keys in JWKS format.
* **`POST /auth`** — Returns a JWT signed with the active key.
* **`POST /auth?expired=true`** — Returns a JWT signed with an expired key for testing.

## Requirements

* Python 3.10 or newer

## Installation & Setup

Navigate to the repository directory:

```bash
cd jwks-server
python -m venv venv

```

Activate the virtual environment:

* **Windows:**
```cmd
venv\Scripts\activate

```


* **macOS / Linux:**
```bash
source venv/bin/activate

```



Install dependencies:

```bash
pip install -r requirements.txt

```

Start the server:

```bash
python server.py

```

The server runs on port 8080 at `http://localhost:8080`.

## Testing the Endpoints

Get active public keys:

```bash
curl http://localhost:8080/.well-known/jwks.json

```

Request a valid JWT:

```bash
curl -X POST http://localhost:8080/auth

```

Request a JWT signed with an expired key:

```bash
curl -X POST "http://localhost:8080/auth?expired=true"

```

## Running Tests

From the `jwks-server` directory, run pytest:

```bash
pytest -v

```

Run tests with code coverage report:

```bash
pytest --cov=server --cov-report=term-missing

```

