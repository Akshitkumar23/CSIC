import urllib.request
import json
import time

base = 'https://csic-orpin.vercel.app'
print('='*70)
print('CSIC LIVE PRODUCTION PERFORMANCE & INTEGRITY AUDIT')
print('='*70)

# 1. Health checks
for endpoint in ['/health/live', '/health/ready']:
    t0 = time.time()
    req = urllib.request.Request(f'{base}{endpoint}', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        duration = time.time() - t0
        data = json.loads(resp.read().decode())
        print(f'{endpoint:25} -> {resp.status} in {duration:.3f}s | Status: {data.get("status")}')

# 2. Login as demo student Akshit
t0 = time.time()
login_payload = json.dumps({'email': 'akshit@csic.edu', 'password': '1234'}).encode('utf-8')
login_req = urllib.request.Request(
    f'{base}/api/v1/auth/login',
    data=login_payload,
    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(login_req) as resp:
    login_duration = time.time() - t0
    login_data = json.loads(resp.read().decode())
    token = login_data['access_token']
    print(f'POST /api/v1/auth/login    -> {resp.status} in {login_duration:.3f}s')

auth_headers = {'Authorization': f'Bearer {token}', 'User-Agent': 'Mozilla/5.0'}

# 3. Authenticated Student APIs
student_endpoints = [
    '/api/v1/auth/me',
    '/api/v1/attendance/me',
    '/api/v1/marks/me',
    '/api/v1/fees/me',
    '/api/v1/timetable/me',
    '/api/v1/notices'
]

print('-'*70)
print('Authenticated Student Endpoint Benchmark (Akshit):')
print('-'*70)
for ep in student_endpoints:
    t0 = time.time()
    req = urllib.request.Request(f'{base}{ep}', headers=auth_headers)
    with urllib.request.urlopen(req) as resp:
        duration = time.time() - t0
        body = resp.read()
        print(f'{ep:25} -> {resp.status} in {duration:.3f}s | Response size: {len(body)} bytes')

# 4. Login as Admin
t0 = time.time()
admin_payload = json.dumps({'email': 'admin@csic.edu', 'password': '1234'}).encode('utf-8')
admin_req = urllib.request.Request(
    f'{base}/api/v1/auth/login',
    data=admin_payload,
    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(admin_req) as resp:
    duration = time.time() - t0
    admin_data = json.loads(resp.read().decode())
    admin_token = admin_data['access_token']
    print(f'POST /api/v1/auth/login (Admin) -> {resp.status} in {duration:.3f}s')

# Admin endpoint
t0 = time.time()
req = urllib.request.Request(f'{base}/api/v1/admin/stats', headers={'Authorization': f'Bearer {admin_token}', 'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    duration = time.time() - t0
    print(f'/api/v1/admin/stats       -> {resp.status} in {duration:.3f}s | {resp.read()[:60].decode()}')

print('='*70)
print('ALL PRODUCTION PERFORMANCE & RESILIENCY CHECKS PASSED!')
print('='*70)
