from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import get_settings
from urllib.parse import urlparse, parse_qs, urlencode

settings = get_settings()

# Parse the database URL and remove pgbouncer parameter
# psycopg2 doesn't support pgbouncer as a connection option
db_url = settings.database_url
if "pgbouncer" in db_url:
    # Remove pgbouncer parameter from query string
    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query)
    query_params.pop('pgbouncer', None)
    new_query = urlencode(query_params, doseq=True)
    db_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if new_query:
        db_url += f"?{new_query}"

# Use the pooled connection URL for regular operations
engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from backend.app.models import user, image, audio, project
    Base.metadata.create_all(bind=engine)
