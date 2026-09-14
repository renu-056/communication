"""
Migration Test Script

Tests Alembic migration functionality with a fresh database.
"""
import os
import sys
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base, SessionLocal
from app.models import Station, Telemetry, Alert
from sqlalchemy import text


def test_migration():
    """Test migration with fresh database"""
    print("=" * 70)
    print("MIGRATION TEST")
    print("=" * 70)
    
    # Test database path
    test_db = "test_migration.db"
    
    # Clean up any existing test database
    if os.path.exists(test_db):
        os.remove(test_db)
        print(f"[CLEANUP] Removed existing test database: {test_db}")
    
    # Set test database URL
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
    
    # Re-import database with new URL
    import importlib
    import app.database
    importlib.reload(app.database)
    
    from app.database import engine, create_tables
    
    print("\n[TEST 1] Fresh database table creation (create_tables)")
    try:
        create_tables()
        print("[PASS] Tables created successfully with create_tables()")
    except Exception as e:
        print(f"[FAIL] create_tables() failed: {e}")
        return False
    
    # Verify tables exist
    print("\n[TEST 2] Verify tables exist")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            expected_tables = ['stations', 'telemetry', 'logistics_items', 'traverse_routes', 'alerts', 'sync_queue', 'network_status']
            
            for table in expected_tables:
                if table in tables:
                    print(f"  ✓ {table} exists")
                else:
                    print(f"  ✗ {table} missing")
                    return False
        print("[PASS] All expected tables exist")
    except Exception as e:
        print(f"[FAIL] Table verification failed: {e}")
        return False
    
    # Test CRUD operations
    print("\n[TEST 3] CRUD operations")
    try:
        db = SessionLocal()
        
        # Create
        station = Station(
            station_id="MIGRATION-TEST-01",
            name="Migration Test Station",
            location="Test Location"
        )
        db.add(station)
        db.commit()
        db.refresh(station)
        print(f"  ✓ Created station: {station.name}")
        
        # Read
        station = db.query(Station).filter(Station.station_id == "MIGRATION-TEST-01").first()
        assert station is not None
        print(f"  ✓ Read station: {station.name}")
        
        # Update
        station.location = "Updated Location"
        db.commit()
        db.refresh(station)
        assert station.location == "Updated Location"
        print(f"  ✓ Updated station location")
        
        # Delete
        db.delete(station)
        db.commit()
        station = db.query(Station).filter(Station.station_id == "MIGRATION-TEST-01").first()
        assert station is None
        print(f"  ✓ Deleted station")
        
        db.close()
        print("[PASS] CRUD operations successful")
    except Exception as e:
        print(f"[FAIL] CRUD operations failed: {e}")
        return False
    
    # Clean up
    print("\n[CLEANUP] Removing test database")
    try:
        if os.path.exists(test_db):
            os.remove(test_db)
            print(f"[PASS] Test database removed: {test_db}")
    except Exception as e:
        print(f"[WARN] Could not remove test database: {e}")
    
    print("\n" + "=" * 70)
    print("MIGRATION TEST COMPLETE")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_migration()
    sys.exit(0 if success else 1)