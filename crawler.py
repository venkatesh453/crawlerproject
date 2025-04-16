import requests
import random

BASE_URL = 'http://127.0.0.1:5000'

# Sample data to randomize
names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Fiona', 'George', 'Hannah', 'Ian', 'Jane']
courses = ['B.Tech', 'MCA', 'BSc', 'BBA', 'MBA', 'B.Com', 'M.Tech']

# How many fake students to register
NUM_STUDENTS = 5

# --- 1. Register multiple random students ---
for _ in range(NUM_STUDENTS):
    form_data = {
        'name': random.choice(names),
        'age': random.randint(18, 30),
        'course': random.choice(courses)
    }

    response = requests.post(f'{BASE_URL}/register', data=form_data)
    if response.ok:
        print(f"✅ Registered: {form_data['name']} ({form_data['age']}) - {form_data['course']}")
    else:
        print(f"❌ Failed to register: {form_data}")

# --- 2. Fetch all registered students ---
response = requests.get(f'{BASE_URL}/api/students')

if response.status_code == 200:
    students = response.json()
    print("\n📚 Registered Students:")
    for s in students:
        print(f" - {s['name']} ({s['age']} yrs) - {s['course']}")
else:
    print("❌ Failed to retrieve student list:", response.status_code)
