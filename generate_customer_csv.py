import csv
import random
from datetime import datetime, timedelta

# 고객 데이터 생성
customers = []
for i in range(1000):
    customer_id = i + 1
    name = f"Customer_{customer_id:04d}"
    email = f"customer{customer_id}@example.com"
    phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    registration_date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
    
    customers.append({
        'customer_id': customer_id,
        'name': name,
        'email': email,
        'phone': phone,
        'registration_date': registration_date
    })

# CSV 파일 저장
csv_file = '/home/informix/CISAM/customers.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['customer_id', 'name', 'email', 'phone', 'registration_date'])
    writer.writeheader()
    writer.writerows(customers)

print(f"✅ {csv_file} 생성 완료 (1000 레코드)")
