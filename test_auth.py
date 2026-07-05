import requests

API_URL = "http://localhost:8000/api"

# 1. Test unauthenticated request
print("1. Unauthenticated Request:")
res = requests.get(f"{API_URL}/invoices")
print(f"Status: {res.status_code}") # Should be 401

# 2. Test Login
print("\n2. Login Request:")
login_res = requests.post(f"{API_URL}/token", data={"username": "admin", "password": "password"})
print(f"Status: {login_res.status_code}") # Should be 200
token = login_res.json().get("access_token")
print(f"Token acquired: {bool(token)}")

# 3. Test Authenticated request
if token:
    print("\n3. Authenticated Request:")
    res = requests.get(f"{API_URL}/invoices", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {res.status_code}") # Should be 200
    print(f"Invoices returned: {len(res.json())}")
