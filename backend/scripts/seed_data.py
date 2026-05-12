import random
import pandas as pd


def generate_workers(n=50):
    workers = []

    for i in range(n):
        workers.append({
            "worker_id": i,
            "rating": round(random.uniform(2.5, 5.0), 2),
            "completion_rate": round(random.uniform(0.4, 1.0), 2),
            "disputes": random.randint(0, 5),
            "availability": round(random.uniform(0.3, 1.0), 2),
        })

    return workers


def generate_jobs(n=20):
    jobs = []

    for i in range(n):
        jobs.append({
            "job_id": i,
            "urgency": random.randint(1, 5),
        })

    return jobs


def generate_dataset(workers, jobs, rows=500):
    data = []

    for _ in range(rows):
        w = random.choice(workers)
        j = random.choice(jobs)

        distance = round(random.uniform(0.5, 20), 2)
        skill_overlap = round(random.uniform(0.2, 1.0), 2)

        trust_score = (
            0.4 * w["completion_rate"] +
            0.3 * (w["rating"] / 5) +
            0.2 * (1 - min(w["disputes"] / 5, 1)) +
            0.1 * w["availability"]
        )

        # fake label logic (VERY IMPORTANT)
        score = (
            0.3 * (1 - distance / 20) +
            0.3 * skill_overlap +
            0.4 * trust_score
        )

        label = 1 if score > 0.6 else 0

        data.append({
            "worker_id": w["worker_id"],
            "job_id": j["job_id"],
            "distance_km": distance,
            "skill_overlap": skill_overlap,
            "trust_score": trust_score,
            "rating": w["rating"],
            "completion_rate": w["completion_rate"],
            "disputes": w["disputes"],
            "availability": w["availability"],
            "label": label
        })

    return pd.DataFrame(data)


if __name__ == "__main__":
    workers = generate_workers()
    jobs = generate_jobs()

    df = generate_dataset(workers, jobs)

    df.to_csv("dataset.csv", index=False)

    print("Dataset generated:", len(df))