# scratch_test.py

from app.db.models.user import User

print(hasattr(User, "worker_profile"))
print(hasattr(User, "applications"))
print(hasattr(User, "job_postings"))