from app.database import engine, Base


def init_db():
    print("Dropping tables defined in models (if any)...")
    Base.metadata.drop_all(bind=engine)

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
