# 🚀 Internship Project

## Container setup

- **main** – Main application container
- **postgres-container** – PostgreSQL database
        
        Manage with command
        docker exec -it postgres-container psql -U postgres -d internship
    
- **redis-container** – Redis database

        Manage with command
        docker exec -it redis-container redis-cli

## ▶️ Run the Project

```bash
docker-compose up
```

## Database Migrations
### Initialize Alembic
```bash
alembic init elembic
```
### Configure Alembic
1. Edit alembic.ini
```bash
sqlalchemy.url = db_url
```
2. Edit env.py
```bash
from app.db.models import Base
target_metadata = Base.metadata
```
### Creating and Applying Migrations
1. Autogenerate migration
```bash 
alembic revision --autogenerate -m "comment"
```
2. Apply Migrations
```bash
alembic upgrade head
```
or
```bash
alembic upgrade <revision_id>
```
        

    