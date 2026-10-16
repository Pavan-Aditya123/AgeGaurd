"""
End-to-end HTTP API test.
Tests: create session → upload face → check result → access check
Run: python backend/scripts/test_api.py
"""
import sys, os, json, base64, urllib.request, urllib.parse

BASE = "http://localhost:5000"
UPLOADS = os.path.join(os.path.dirname(__file__), "..", "uploads")

def post(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data,
          headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def get(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

# Pick a real upload image
uploads = sorted([f for f in os.listdir(UPLOADS)
                  if f.endswith(".jpg") and "_face" not in f and "gitkeep" not in f])

print("=" * 60)
print("AGEGUARD API TEST")
print("=" * 60)

for fname in uploads[:3]:
    path = os.path.join(UPLOADS, fname)
    print(f"\n--- Testing with: {fname} ---")

    # 1. Create session (movie 3 = Dhurandhar, 18+)
    sess = post(f"{BASE}/api/verification/session", {"movieId": 3})
    session_id = sess["sessionId"]
    print(f"Session created: {session_id[:16]}...")

    # 2. Upload face
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    result = post(f"{BASE}/api/upload-face", {
        "sessionId": session_id,
        "image": b64,
    })
    print(f"Decision:  {result.get('decision')}")
    print(f"Reason:    {result.get('reason')}")
    if result.get("predictedAge") is not None:
        print(f"Age:       {result.get('predictedAge')}")
    print(f"Verified:  {result.get('verified')}")

    # 3. Poll session status
    status = get(f"{BASE}/api/verification/session/{session_id}")
    print(f"Session status: {status.get('verificationStatus')}")

    # 4. Check access (should match verified flag)
    access = get(f"{BASE}/api/verification/access?movieId=3&sessionId={session_id}")
    print(f"Access allowed: {access.get('allowed')}")

print("\n" + "=" * 60)
print("API TEST COMPLETE")
print("=" * 60)
