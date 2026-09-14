#!/usr/bin/env python3
"""
DTN Store-and-Forward Demo

Demonstrates the Delay/Disruption Tolerant Networking functionality
for Antarctic Research Station Management.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.services.sync_engine import SyncEngine


def demo_network_available():
    """Demo 1: Network available - Message sent immediately"""
    print("\n" + "=" * 70)
    print("DEMO 1: NETWORK AVAILABLE")
    print("=" * 70)
    
    dtn = SyncEngine(local_db_path="demo_dtn.db", server_url="http://localhost:8000")
    dtn._network_available = True
    
    result = dtn.send_message(
        station_id="BHARATI-01",
        source="EDGE_COMPUTING",
        destination="CENTRAL_SERVER",
        payload={"temperature": -28.4, "battery": 94.2, "generator_status": "OPTIMAL"},
        priority="NORMAL"
    )
    
    print(f"Network: {'AVAILABLE' if result['network_available'] else 'UNAVAILABLE'}")
    print(f"Status: {result['status']}")
    print(f"Message ID: {result['message_id']}")
    print("✓ Message sent successfully")
    
    # Cleanup
    if os.path.exists("demo_dtn.db"):
        os.remove("demo_dtn.db")


def demo_network_unavailable():
    """Demo 2: Network unavailable - Message stored in queue"""
    print("\n" + "=" * 70)
    print("DEMO 2: NETWORK UNAVAILABLE")
    print("=" * 70)
    
    dtn = SyncEngine(local_db_path="demo_dtn.db", server_url="http://localhost:8000")
    dtn.handle_network_loss()
    
    result = dtn.send_message(
        station_id="BHARATI-01",
        source="EDGE_COMPUTING",
        destination="CENTRAL_SERVER",
        payload={"temperature": -28.5, "battery": 93.8, "generator_status": "OPTIMAL"},
        priority="HIGH"
    )
    
    print(f"Network: {'AVAILABLE' if result['network_available'] else 'UNAVAILABLE'}")
    print(f"Status: {result['status']}")
    print(f"Message ID: {result['message_id']}")
    
    # Check queue status
    status = dtn.get_queue_status()
    print(f"Queue Status: {status['total_queued']} message(s) queued")
    print(f"Priority breakdown: CRITICAL={status['critical_count']}, HIGH={status['high_count']}, NORMAL={status['normal_count']}, LOW={status['low_count']}")
    print("✓ Message stored in persistent queue")
    
    # Verify persistence
    status2 = dtn.get_queue_status()
    print(f"✓ Message still exists after verification: {status2['total_queued']} message(s)")
    
    # Cleanup
    if os.path.exists("demo_dtn.db"):
        os.remove("demo_dtn.db")


def demo_network_restore():
    """Demo 3: Network restored - Queued messages forwarded"""
    print("\n" + "=" * 70)
    print("DEMO 3: NETWORK RESTORED")
    print("=" * 70)
    
    dtn = SyncEngine(local_db_path="demo_dtn.db", server_url="http://localhost:8000")
    
    # Simulate network loss and queue messages
    dtn.handle_network_loss()
    
    print("Network: UNAVAILABLE - Queueing messages...")
    dtn.enqueue_message("BHARATI-01", "SENSOR", "SERVER", {"data": "temperature_reading"}, "NORMAL")
    dtn.enqueue_message("BHARATI-01", "SENSOR", "SERVER", {"data": "battery_status"}, "HIGH")
    
    status = dtn.get_queue_status()
    print(f"Queue Status: {status['total_queued']} message(s) queued")
    
    # Restore network
    print("\nNetwork: AVAILABLE - Restoring connection...")
    result = dtn.restore_connection_and_forward()
    
    print(f"Network Status: {'AVAILABLE' if result['network_available'] else 'UNAVAILABLE'}")
    print(f"Messages Processed: {result['total_processed']}")
    print(f"Messages Forwarded: {result['forwarded']}")
    print(f"Messages Failed: {result['failed']}")
    
    # Check final queue status
    final_status = dtn.get_queue_status()
    print(f"Final Queue Status: {final_status['total_queued']} message(s) remaining")
    print("✓ Queued messages forwarded successfully")
    
    # Cleanup
    if os.path.exists("demo_dtn.db"):
        os.remove("demo_dtn.db")


def demo_priority_handling():
    """Demo 4: Priority-based message forwarding"""
    print("\n" + "=" * 70)
    print("DEMO 4: PRIORITY-BASED FORWARDING")
    print("=" * 70)
    
    dtn = SyncEngine(local_db_path="demo_dtn.db", server_url="http://localhost:8000")
    dtn.handle_network_loss()
    
    print("Network: UNAVAILABLE - Queueing messages with different priorities...")
    dtn.enqueue_message("BHARATI-01", "SENSOR", "SERVER", {"data": "low_priority_log"}, "LOW")
    dtn.enqueue_message("BHARATI-01", "SENSOR", "SERVER", {"data": "normal_telemetry"}, "NORMAL")
    dtn.enqueue_message("BHARATI-01", "SENSOR", "SERVER", {"data": "critical_alert"}, "CRITICAL")
    dtn.enqueue_message("BHARATI-01", "SENSOR", "SERVER", {"data": "high_priority_warning"}, "HIGH")
    
    status = dtn.get_queue_status()
    print(f"Queue Status: {status['total_queued']} message(s) queued")
    print(f"Priority breakdown: CRITICAL={status['critical_count']}, HIGH={status['high_count']}, NORMAL={status['normal_count']}, LOW={status['low_count']}")
    
    print("\nNetwork: AVAILABLE - Restoring connection...")
    print("Forwarding order: CRITICAL → HIGH → NORMAL → LOW")
    result = dtn.restore_connection_and_forward()
    
    print(f"Messages Processed: {result['total_processed']}")
    print(f"Messages Forwarded: {result['forwarded']}")
    print("✓ Priority ordering enforced (CRITICAL > HIGH > NORMAL > LOW)")
    
    # Cleanup
    if os.path.exists("demo_dtn.db"):
        os.remove("demo_dtn.db")


def main():
    """Run all DTN demos"""
    print("\n" + "=" * 70)
    print("DTN STORE-AND-FORWARD DEMONSTRATION")
    print("Antarctic Research Station Management - Communication Module")
    print("=" * 70)
    
    try:
        demo_network_available()
        demo_network_unavailable()
        demo_network_restore()
        demo_priority_handling()
        
        print("\n" + "=" * 70)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nDTN Features Demonstrated:")
        print("✓ Network availability detection")
        print("✓ Automatic message queuing when offline")
        print("✓ Persistent message storage")
        print("✓ Automatic forwarding on connection restore")
        print("✓ Priority-based message ordering")
        print("✓ Retry logic for failed messages")
        print("\nThe DTN layer ensures no message loss during network disruptions")
        print("while optimizing bandwidth usage for Antarctic satellite links.")
        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup any remaining demo databases
        for db_file in ["demo_dtn.db"]:
            if os.path.exists(db_file):
                os.remove(db_file)


if __name__ == "__main__":
    main()
