# LivingWay 3D — সহজ Setup Guide (বাংলা)

## ZIP-এ কী আছে?
- `public` — মূল ওয়েবসাইট + `/admin/` login/dashboard UI
- `python-backend` — FastAPI backend ও SQLite database starter
- `ORIGINAL-FRONTEND-BACKUP.zip` — আগের frontend backup

**সতর্কতা:** এই ZIP live Cloudflare deployment নয়। Backend Python FastAPI; `wrangler deploy` দিয়ে Cloudflare Worker হিসেবে এটি deploy হবে না। Python চালাতে পারে এমন hosting দরকার। Cloudflare-এ live domain/routing পরিবর্তনের আগে staging-এ পরীক্ষা ও backup আবশ্যক।

Dashboard-এর কিছু অংশ record/metadata সংরক্ষণ করে; payment gateway, private file upload/download, PDF invoice, customer portal, email password reset, customer-কে বাস্তব message delivery এবং legally binding e-signature সম্পূর্ণ production integration নয়।

## Windows-এ Local test
1. Python 3.11 বা নতুন version install করুন।
2. ZIP Extract করুন।
3. `LivingWay-3D-Admin-Package\python-backend` folder খুলুন।
4. Folder-এর address bar-এ `cmd` লিখে Enter চাপুন।
5. একে একে command দিন:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

6. একই CMD window-তে নিজের দুই Admin-এর email/password ও secret set করুন:

```bat
set ADMIN1_EMAIL=admin1@example.com
set ADMIN1_PASSWORD=নিজের_শক্তিশালী_পাসওয়ার্ড
set ADMIN2_EMAIL=admin2@example.com
set ADMIN2_PASSWORD=দ্বিতীয়_শক্তিশালী_পাসওয়ার্ড
set SESSION_SECRET=কমপক্ষে_৩২_অক্ষরের_আলাদা_random_secret
set COOKIE_SECURE=false
```

উপরের sample email/password বদলে নিজের credential দিন। Password কারও সঙ্গে share করবেন না।

7. Backend চালু করুন:

```bat
uvicorn main:app --host 127.0.0.1 --port 8000
```

8. Browser-এ খুলুন:
- Website: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`
- API health: `http://127.0.0.1:8000/api/health`

CMD window চালু রাখুন। বন্ধ করতে `Ctrl+C` চাপুন।

## Live করার আগে
- প্রথমে আলাদা staging-এ deploy/test করুন।
- HTTPS production-এ `COOKIE_SECURE=true` দিন এবং persistent database storage configure করুন।
- দুই Admin-এর unique credential ও আলাদা strong `SESSION_SECRET` দিন।
- Login/logout, wrong password, unauthenticated API, request submit, record edit এবং restart-এর পর data থাকে কি না পরীক্ষা করুন।
- বর্তমান live website-এর backup না নিয়ে DNS/route/production Worker পরিবর্তন করবেন না।
- `design3.livingwayd2.workers.dev`-এ এই Python backend সরাসরি `wrangler deploy` দিয়ে চালানো যাবে না।

## Login-এ JSON error এলে
`Failed to execute 'json' on 'Response': Unexpected end of JSON input` হলে `/api/health` খুলে দেখুন backend চালু আছে কি না। API route না চললে frontend empty/non-JSON response পেতে পারে।
