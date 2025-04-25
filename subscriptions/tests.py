import hmac
import hashlib
import json
import requests

# Function to generate the signature
def generate_signature(payload, secret_key):
    """
    Generate HMAC-SHA256 signature for the payload with the secret key.
    """
    # Convert the payload dictionary to a string (ensure it's in the correct format)
    payload_str = json.dumps(payload, separators=(',', ':'))  # No spaces between keys and values
    # Generate the HMAC-SHA256 signature
    signature = 'sha256=' + hmac.new(secret_key.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    return signature

# Function to verify the signature (server side)
def verify_signature(request, secret_key):
    """
    Verify the signature sent with the request.
    """
    # Extract the signature from the request header
    received_signature = request.headers.get('X-Hub-Signature-256')
    
    if not received_signature:
        return "Signature missing", 400

    # Get the payload (body of the request)
    payload = request.data  # Assuming it's a byte string

    # Recreate the signature from the payload and secret_key
    expected_signature = 'sha256=' + hmac.new(secret_key.encode(), payload, hashlib.sha256).hexdigest()

    # Compare the two signatures
    if hmac.compare_digest(received_signature, expected_signature):
        return "Signature verified", 200
    else:
        return "Invalid signature", 400

# Main function that sends a request with the signature
def send_webhook_request():
    # Payload to send
    payload = {
        "identifier": "segwiseok",
        "target_url": "https://restfulapi.net/http-status-200-ok/",
        "secret_key": "supersecretkey"
    }

    # Secret key (used to generate signature)
    secret_key = payload['secret_key']

    # Generate the HMAC signature
    signature = generate_signature(payload, secret_key)
    print(f"Generated Signature: {signature}")

    # Sample data for the request (this is just an example, it should be the same payload)
    sample_data = '{ "event": "user.signup", "user_id": 42, "email": "john@example.com" }'.encode()

    # URL where you are sending the request
    url = "http://localhost:8000/ingest/segwiseok"  # Replace with your actual URL

    # Send request with the signature in the header
    headers = {
        'X-Hub-Signature-256': signature,
    }

    response = requests.post(url, data=sample_data, headers=headers)

    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

# Run the function to send the request
send_webhook_request()

# Example of a server-side verification (for testing purposes)
# In a real server, you'd pass `request` object here, this is just an example
class MockRequest:
    def __init__(self, data, headers):
        self.data = data
        self.headers = headers

# Sample request data (mock)
mock_request = MockRequest(data='{ "event": "user.signup", "user_id": 42, "email": "john@example.com" }'.encode(), 
                           headers={'X-Hub-Signature-256': 'sha256=e07d679c7c70507f5e5364355fbaf77898f278df6c157ba116abdaad07f6ae82'})

# Verify signature server-side (mock)
verification_response, status_code = verify_signature(mock_request, "supersecretkey")
print(f"Verification Response: {verification_response} (Status code: {status_code})")
