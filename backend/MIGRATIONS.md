# Alembic Database Migrations

## Overview

Alembic provides version control for your database schema. All schema changes are tracked in migration files under `migrations/versions/`.

## Quick Start

### Create a new migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to users"

# Or create an empty migration
alembic revision -m "Manual schema change"
```

### Apply migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade by one
alembic downgrade -1
```

### Check migration status

```bash
# Show current database version
alembic current

# Show history
alembic history --verbose
```

## Initial Migration

The initial migration (`9cbc11040b5c_initial_schema.py`) creates all tables:
- `users` - User accounts (employers and workers)
- `employer_profiles` - Employer-specific data
- `worker_profiles` - Worker-specific data
- `jobs` - Job postings
- `applications` - Worker applications to jobs
- `match_logs` - Match ranking records

## Using Migrations in CI/CD

### Pre-deployment check

```bash
# Verify migrations can be applied
alembic upgrade --sql head
```

### In your startup script

```python
import subprocess
import sys

subprocess.run(
    [sys.executable, "-m", "alembic", "upgrade", "head"],
    cwd="backend",
    check=True,
)
```

### Docker (in Dockerfile)

```dockerfile
RUN alembic upgrade head
```

## Best Practices

1. **Always auto-generate before manual edits**
   ```bash
   alembic revision --autogenerate -m "Your description"
   ```

2. **Review generated migrations**
   - Check `migrations/versions/<id>_<desc>.py`
   - Ensure `upgrade()` and `downgrade()` are correct

3. **Keep migrations small and atomic**
   - One feature per migration
   - Makes rollbacks easier

4. **Never edit applied migrations**
   - Create new migration to fix issues
   - Exception: unmigrated development databases

5. **Test migrations locally first**
   ```bash
   # Test on clean database
   rm hustle.db  # SQLite
   alembic upgrade head
   ```

## Troubleshooting

### "Can't locate revision identified by..."
The migration file was deleted. Options:
1. Restore from git
2. Manually set version: `alembic stamp <version>`

### Merge conflicts in migration files
Different branches created conflicting migrations.
1. Resolve by creating new migration combining both changes

### Rollback failed
Create downgrade-specific migration:
```python
# migrations/versions/xxx_fix_rollback.py
def upgrade():
    pass  # Forward path only needed

def downgrade():
    # Manual fix code here
```

## Configuration

Edit `alembic.ini`:
- `sqlalchemy.url` - Database connection string
- `prepend_sys_path` - Add paths to Python path
- `version_locations` - Custom migration directories

## Repository and Transaction Management Integration

Alembic migrations work seamlessly with the repository layer:

```python
# Before applying migrations
async with UnitOfWork(session) as uow:
    # Your application code
    jobs = await uow.jobs.list_all()

# After alembic upgrade head
# No code changes needed - schema is automatically synced
```

The repository layer is schema-independent and automatically adapts to database structure defined by migrations.
