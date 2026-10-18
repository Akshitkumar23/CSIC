import sys
sys.path.insert(0, r"D:\Projects\CSIC")
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

accounts = [
    {"name": "Rashi", "email": "rashi@csic.edu", "role": "student", "protected_route": "/api/v1/attendance/me"},
    {"name": "Vanshika", "email": "vanshika@csic.edu", "role": "student", "protected_route": "/api/v1/attendance/me"},
    {"name": "Silki", "email": "silki@csic.edu", "role": "student", "protected_route": "/api/v1/attendance/me"},
    {"name": "Akshit", "email": "akshit@csic.edu", "role": "student", "protected_route": "/api/v1/attendance/me"},
    {"name": "Akshit", "email": "rajesh.kumar@csic.edu", "role": "faculty", "protected_route": "/api/v1/admin/faculty-assignments"},
    {"name": "Prof. Anita Deshmukh", "email": "anita.deshmukh@csic.edu", "role": "faculty", "protected_route": "/api/v1/admin/faculty-assignments"},
    {"name": "Akshit", "email": "admin@csic.edu", "role": "admin", "protected_route": "/api/v1/admin/stats"},
]

print("=" * 80)
print("CSIC 7 DEMO ACCOUNTS END-TO-END AUTHENTICATION & ACCESS VERIFICATION")
print("=" * 80)

all_passed = True
for idx, acc in enumerate(accounts, 1):
    email = acc["email"]
    expected_name = acc["name"]
    expected_role = acc["role"]
    route = acc["protected_route"]

    # 1. Real Login API call
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "1234"})
    if res.status_code != 200:
        print(f"[{idx}/7] FAIL: Login for {email} failed with status {res.status_code}: {res.text}")
        all_passed = False
        continue

    data = res.json()
    token = data.get("access_token")
    if not token or len(token) < 20:
        print(f"[{idx}/7] FAIL: Token missing or invalid for {email}")
        all_passed = False
        continue

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Real /api/v1/auth/me profile call
    me_res = client.get("/api/v1/auth/me", headers=headers)
    if me_res.status_code != 200:
        print(f"[{idx}/7] FAIL: /auth/me failed for {email} with status {me_res.status_code}")
        all_passed = False
        continue

    profile = me_res.json()
    name_ok = (profile.get("full_name") == expected_name)
    role_ok = (profile.get("role") == expected_role)

    # 3. Role-based Protected Route Access
    prot_res = client.get(route, headers=headers)
    prot_ok = (prot_res.status_code == 200)

    # 4. Cross-role negative access verification
    if expected_role == "student":
        # Student cannot access admin stats
        neg_res = client.get("/api/v1/admin/stats", headers=headers)
        neg_ok = (neg_res.status_code == 403)
    elif expected_role == "faculty":
        # Faculty cannot access student personal attendance
        neg_res = client.get("/api/v1/attendance/me", headers=headers)
        neg_ok = (neg_res.status_code == 403)
    else:
        # Admin can access admin stats
        neg_ok = True

    status_str = "PASS" if (name_ok and role_ok and prot_ok and neg_ok) else "FAIL"
    if status_str == "FAIL":
        all_passed = False

    print(f"[{idx}/7] {status_str}: {expected_name:<20} | {email:<25} | Role: {expected_role:<7} | Auth: 200 | Protected: {prot_res.status_code} | RBAC: {'PASS' if neg_ok else 'FAIL'}")

print("=" * 80)
print(f"Final Verification Result: {'ALL 7 PASS' if all_passed else 'SOME FAILED'}")
print("=" * 80)
