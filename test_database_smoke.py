"""
Database Smoke Test

Verifies basic database operations: CREATE, READ, UPDATE, DELETE
Tests the current database configuration (SQLite by default)
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, test_database_connection, get_database_info, create_tables
from app.models import Station, Telemetry, Alert


def test_database_smoke():
    """Test basic CRUD operations on database"""
    print("=" * 70)
    print("DATABASE SMOKE TEST")
    print("=" * 70)
    
    # Test 1: Database Connection
    print("\n[TEST 1] Database Connection")
    success, message = test_database_connection()
    print(f"Connection Status: {success}")
    print(f"Message: {message}")
    assert success, "Database connection failed"
    print("[PASS] Database connection successful")
    
    # Test 2: Database Info
    print("\n[TEST 2] Database Configuration")
    info = get_database_info()
    print(f"Database Type: {info['database_type']}")
    print(f"Database URL: {info['database_url']}")
    print(f"DTN Database Path: {info['dtn_database_path']}")
    print("[PASS] Database configuration retrieved")
    
    # Test 3: Create Station
    print("\n[TEST 3] CREATE - Station")
    db = SessionLocal()
    try:
        station = Station(
            station_id="SMOKE-TEST-01",
            name="Smoke Test Station",
            location="Test Location",
            is_active=True
        )
        db.add(station)
        db.commit()
        db.refresh(station)
        print(f"Created Station ID: {station.id}")
        print(f"Station ID: {station.station_id}")
        print("[PASS] Station created successfully")
    except Exception as e:
        db.rollback()
        print(f"[FAIL] Station creation failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 4: Read Station
    print("\n[TEST 4] READ - Station")
    db = SessionLocal()
    try:
        station = db.query(Station).filter(Station.station_id == "SMOKE-TEST-01").first()
        assert station is not None, "Station not found"
        print(f"Read Station: {station.name}")
        print(f"Location: {station.location}")
        print("[PASS] Station read successfully")
    except Exception as e:
        print(f"[FAIL] Station read failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 5: Update Station
    print("\n[TEST 5] UPDATE - Station")
    db = SessionLocal()
    try:
        station = db.query(Station).filter(Station.station_id == "SMOKE-TEST-01").first()
        station.location = "Updated Test Location"
        db.commit()
        db.refresh(station)
        print(f"Updated Location: {station.location}")
        assert station.location == "Updated Test Location", "Update failed"
        print("[PASS] Station updated successfully")
    except Exception as e:
        db.rollback()
        print(f"[FAIL] Station update failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 6: Create Telemetry (Foreign Key)
    print("\n[TEST 6] CREATE - Telemetry with Foreign Key")
    db = SessionLocal()
    try:
        telemetry = Telemetry(
            station_id="SMOKE-TEST-01",
            battery_level=95.5,
            generator_status="OPTIMAL",
            outside_temp_celsius=-20.5,
            inside_temp_celsius=18.0
        )
        db.add(telemetry)
        db.commit()
        db.refresh(telemetry)
        print(f"Created Telemetry ID: {telemetry.id}")
        print(f"Battery Level: {telemetry.battery_level}%")
        print("[PASS] Telemetry created successfully")
    except Exception as e:
        db.rollback()
        print(f"[FAIL] Telemetry creation failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 7: Create Alert (JSON field)
    print("\n[TEST 7] CREATE - Alert with JSON metadata")
    db = SessionLocal()
    try:
        alert = Alert(
            station_id="SMOKE-TEST-01",
            alert_type="SMOKE_TEST_ALERT",
            severity="INFO",
            message="Smoke test alert",
            source="SMOKE_TEST",
            alert_metadata={
                "test_key": "test_value",
                "test_number": 42,
                "test_nested": {"nested_key": "nested_value"}
            }
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        print(f"Created Alert ID: {alert.id}")
        print(f"Alert Type: {alert.alert_type}")
        print(f"Metadata: {alert.alert_metadata}")
        print("[PASS] Alert created successfully")
    except Exception as e:
        db.rollback()
        print(f"[FAIL] Alert creation failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 8: Read Related Data
    print("\n[TEST 8] READ - Related Data")
    db = SessionLocal()
    try:
        station = db.query(Station).filter(Station.station_id == "SMOKE-TEST-01").first()
        telemetry_count = len(station.telemetry_records)
        print(f"Station: {station.name}")
        print(f"Telemetry Records: {telemetry_count}")
        print("[PASS] Related data read successfully")
    except Exception as e:
        print(f"[FAIL] Related data read failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 9: Delete Records (Cleanup)
    print("\n[TEST 9] DELETE - Cleanup")
    db = SessionLocal()
    try:
        # Delete telemetry
        db.query(Telemetry).filter(Telemetry.station_id == "SMOKE-TEST-01").delete()
        # Delete alerts
        db.query(Alert).filter(Alert.station_id == "SMOKE-TEST-01").delete()
        # Delete station
        db.query(Station).filter(Station.station_id == "SMOKE-TEST-01").delete()
        db.commit()
        print("[PASS] Test records deleted successfully")
    except Exception as e:
        db.rollback()
        print(f"[FAIL] Cleanup failed: {e}")
        return False
    finally:
        db.close()
    
    # Test 10: Verify Deletion
    print("\n[TEST 10] VERIFY - Deletion")
    db = SessionLocal()
    try:
        station = db.query(Station).filter(Station.station_id == "SMOKE-TEST-01").first()
        assert station is None, "Station was not deleted"
        print("[PASS] Records verified as deleted")
    except Exception as e:
        print(f"[FAIL] Verification failed: {e}")
        return False
    finally:
        db.close()
    
    print("\n" + "=" * 70)
    print("ALL DATABASE SMOKE TESTS PASSED")
    print("=" * 70)
    return True


if __name__ == "__main__":
    # Ensure tables exist
    create_tables()
    
    # Run smoke test
    success = test_database_smoke()
    
    if success:
        print("\n[PASS] Database smoke test completed successfully")
        sys.exit(0)
    else:
        print("\n[FAIL] Database smoke test failed")
        sys.exit(1)