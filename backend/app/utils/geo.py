from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def fetch_jobs_within_radius(
    db: AsyncSession,
    lat: float,
    lng: float,
    radius_km: float,
    skill: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """
    PostGIS ST_DWithin radius query.
    Returns jobs sorted by distance ascending.
    """
    radius_m = radius_km * 1000

    skill_clause = "AND skill_required = :skill" if skill else ""

    query = text(f"""
        SELECT
            j.id,
            j.title,
            j.skill_required,
            j.pay_per_worker,
            j.workers_needed,
            j.workers_hired,
            j.location_name,
            j.status,
            j.expires_at,
            ST_X(j.location::geometry)  AS longitude,
            ST_Y(j.location::geometry)  AS latitude,
            ST_Distance(
                j.location,
                ST_Point(:lng, :lat)::geography
            ) / 1000.0                 AS distance_km,
            ep.id                       AS employer_id,
            u.full_name                 AS employer_name,
            ep.trust_score              AS employer_trust_score
        FROM jobs j
        JOIN employer_profiles ep ON ep.id = j.employer_id
        JOIN users u ON u.id = ep.user_id
        WHERE ST_DWithin(
            j.location,
            ST_Point(:lng, :lat)::geography,
            :radius_m
        )
        AND j.status = 'open'
        AND (j.expires_at IS NULL OR j.expires_at > now())
        {skill_clause}
        ORDER BY j.location <-> ST_Point(:lng, :lat)::geography
        LIMIT :limit
    """)

    params = {"lat": lat, "lng": lng, "radius_m": radius_m, "limit": limit}
    if skill:
        params["skill"] = skill

    result = await db.execute(query, params)
    return [dict(row._mapping) for row in result.fetchall()]


async def insert_job_with_location(
    db: AsyncSession,
    employer_id: str,
    title: str,
    description: str,
    skill_required: str,
    pay_per_worker: int,
    workers_needed: int,
    location_name: str,
    lat: float,
    lng: float,
    duration_days: int = 1,
    tools_provided: bool = False,
) -> str:
    """Insert a job with a PostGIS geography point."""
    result = await db.execute(
        text("""
            INSERT INTO jobs (
                employer_id, title, description, skill_required,
                pay_per_worker, workers_needed, location_name,
                location, duration_days, tools_provided
            ) VALUES (
                :employer_id, :title, :description, :skill_required,
                :pay, :needed, :location_name,
                ST_Point(:lng, :lat)::geography,
                :days, :tools
            )
            RETURNING id
        """),
        {
            "employer_id": employer_id, "title": title,
            "description": description, "skill_required": skill_required,
            "pay": pay_per_worker, "needed": workers_needed,
            "location_name": location_name,
            "lat": lat, "lng": lng,
            "days": duration_days, "tools": tools_provided,
        },
    )
    await db.commit()
    return str(result.scalar())