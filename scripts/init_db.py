from backend.app.db.database import Base, engine

# Import models so SQLAlchemy registers their tables.
from backend.app.models import AuditLog, ExceptionRecord  # noqa: F401


def main() -> None:
    Base.metadata.create_all(
        bind=engine
    )

    print(
        "FineOBS database initialized successfully."
    )


if __name__ == "__main__":
    main()