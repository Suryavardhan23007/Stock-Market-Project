import datetime

ref = datetime.date(1899, 12, 30)
d = datetime.date(2019, 3, 1)
print(f"Days between {ref} and {d}: {(d - ref).days}")
