import urllib.request
import time

routes = [
    '/',
    '/login',
    '/dashboard',
    '/chat',
    '/attendance',
    '/marks',
    '/fees',
    '/timetable',
    '/notices',
    '/profile',
    '/faculty',
    '/admin',
    '/search',
]

print("Polling Vercel deployment on https://csic-orpin.vercel.app ...")

for attempt in range(12):
    try:
        req = urllib.request.Request("https://csic-orpin.vercel.app/dashboard", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                print(f"[Attempt {attempt+1}] Vercel deployment active with SPA rewrite working!")
                break
    except urllib.error.HTTPError as e:
        print(f"[Attempt {attempt+1}] /dashboard returned HTTP {e.code}. Waiting 5s for Vercel build to finalize...")
        time.sleep(5)

print("\n" + "="*70)
print("PRODUCTION DEEP LINK & REFRESH VERIFICATION (https://csic-orpin.vercel.app)")
print("="*70)

all_ok = True
for r in routes:
    url = f"https://csic-orpin.vercel.app{r}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            has_root = '<div id="root"></div>' in content
            status_str = f"HTTP {resp.status}"
            spa_str = "SPA OK" if has_root else "NON-SPA"
            print(f"{r:15} -> {status_str} | {spa_str}")
            if resp.status != 200 or not has_root:
                all_ok = False
    except urllib.error.HTTPError as e:
        print(f"{r:15} -> HTTP ERROR {e.code}")
        all_ok = False
    except Exception as e:
        print(f"{r:15} -> ERROR: {e}")
        all_ok = False

print("="*70)
if all_ok:
    print("ALL ROUTES VERIFIED: 100% REFRESH & DEEP LINK RELIABILITY CONFIRMED")
else:
    print("SOME ROUTES FAILED")
print("="*70)
