from backend.app.db.database import Base, engine

# Import models so SQLAlchemy registers all tables.
from backend.app.models import AuditLog, ExceptionRecord  # noqa: F401


def main() -> None:
    print("Resetting FineOBS development database...")

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )

    print("FineOBS development database reset successfully.")


if __name__ == "__main__":
    main()