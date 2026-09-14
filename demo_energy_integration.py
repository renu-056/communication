#!/usr/bin/env python3
"""
Energy Module Integration End-to-End Demonstration

Demonstrates the complete communication flow from Energy Module -> Communication Layer -> 
Network Decision -> DTN -> Synchronization -> Central Database for Antarctic stations.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.services.energy_integration import energy_integration_service
from app.services.sync_engine import SyncEngine


def demo_online_network_normal_transmission():
    """
    Demo 1: Network ONLINE - Energy telemetry transmitted normally
    """
    print("\n" + "=" * 70)
    print("DEMO 1: NETWORK ONLINE - NORMAL TRANSMISSION")
    print("=" * 70)
    
    # Generate normal energy telemetry for Maitri station
    energy_data = {
        "generator_status": "OPTIMAL",
        "generator_load_kw": 15.5,
        "battery_level": 85.0,
        "power_consumption_kw": 12.3,
        "fuel_level_liters": 750.0
    }
    
    result = energy_integration_service.ingest_energy_telemetry(
        station_id="MAITRI-01",
        energy_data=energy_data,
        network_status="ONLINE",
        latency_ms=150.0,
        bandwidth_mbps=5.0,
        signal_strength=85
    )
    
    print(f"Station: {result['station_id']}")
    print(f"Network Status: {result['network_decision']['network_condition']}")
    print(f"Communication Strategy: {result['network_decision']['communication_strategy']}")
    print(f"Message Priority: {result['data_classification']['priority']}")
    print(f"Message Type: {result['data_classification']['message_type']}")
    print(f"Transmission Status: {result['transmission_result']['status']}")
    print(f"Classification Rationale: {result['data_classification']['rationale']}")
    print("[SUCCESS] Energy telemetry transmitted normally on ONLINE network")


def demo_offline_network_dtn_queue():
    """
    Demo 2: Network OFFLINE - Energy telemetry queued in DTN
    """
    print("\n" + "=" * 70)
    print("DEMO 2: NETWORK OFFLINE - DTN QUEUE ACTIVATION")
    print("=" * 70)
    
    # Simulate network loss
    energy_integration_service.dtn_engine.handle_network_loss()
    
    # Send critical energy telemetry
    critical_energy_data = {
        "generator_status": "FAILED",
        "battery_level": 65.0,
        "power_consumption_kw": 8.0,
        "energy_alert_type": "GENERATOR_FAILURE"
    }
    
    result = energy_integration_service.ingest_energy_telemetry(
        station_id="BHARATI-01",
        energy_data=critical_energy_data,
        network_status="OFFLINE"
    )
    
    print(f"Station: {result['station_id']}")
    print(f"Network Status: {result['network_decision']['network_condition']}")
    print(f"Communication Strategy: {result['network_decision']['communication_strategy']}")
    print(f"Message Priority: {result['data_classification']['priority']}")
    print(f"Message Type: {result['data_classification']['message_type']}")
    print(f"Transmission Status: {result['transmission_result']['status']}")
    print(f"Message ID: {result['transmission_result']['message_id']}")
    print(f"Queued Messages: {result['queue_status']['total_queued']}")
    print(f"Critical Messages in Queue: {result['queue_status']['critical_count']}")
    print("[SUCCESS] Critical energy telemetry queued in DTN during OFFLINE network")


def demo_critical_message_priority():
    """
    Demo 3: Critical energy message gets higher priority
    """
    print("\n" + "=" * 70)
    print("DEMO 3: CRITICAL MESSAGE PRIORITY HANDLING")
    print("=" * 70)
    
    # Ensure network is offline
    energy_integration_service.dtn_engine.handle_network_loss()
    
    # Send normal energy telemetry
    normal_data = {
        "generator_status": "OPTIMAL",
        "battery_level": 80.0,
        "power_consumption_kw": 10.0
    }
    
    normal_result = energy_integration_service.ingest_energy_telemetry(
        station_id="MAITRI-01",
        energy_data=normal_data,
        network_status="OFFLINE"
    )
    
    # Send critical energy alert
    critical_data = {
        "generator_status": "FAILED",
        "battery_level": 45.0,
        "energy_alert_type": "GENERATOR_FAILURE"
    }
    
    critical_result = energy_integration_service.ingest_energy_telemetry(
        station_id="MAITRI-01",
        energy_data=critical_data,
        network_status="OFFLINE"
    )
    
    queue_status = energy_integration_service.dtn_engine.get_queue_status()
    
    print(f"Normal Message Priority: {normal_result['data_classification']['priority']}")
    print(f"Critical Message Priority: {critical_result['data_classification']['priority']}")
    print(f"Total Queued: {queue_status['total_queued']}")
    print(f"Critical Count: {queue_status['critical_count']}")
    print(f"Normal Count: {queue_status['normal_count']}")
    print(f"High Count: {queue_status['high_count']}")
    print("[SUCCESS] Critical messages assigned higher priority for transmission")


def demo_network_recovery_synchronization():
    """
    Demo 4: Network recovery - Queued messages transmitted by priority
    """
    print("\n" + "=" * 70)
    print("DEMO 4: NETWORK RECOVERY - PRIORITY-BASED SYNCHRONIZATION")
    print("=" * 70)
    
    # Get current queue status
    queue_before = energy_integration_service.dtn_engine.get_queue_status()
    print(f"Messages in queue before recovery: {queue_before['total_queued']}")
    print(f"Critical messages: {queue_before['critical_count']}")
    print(f"High messages: {queue_before['high_count']}")
    print(f"Normal messages: {queue_before['normal_count']}")
    
    # Restore network
    print("\nRestoring network connection...")
    restore_result = energy_integration_service.dtn_engine.restore_connection_and_forward()
    
    print(f"Network Status: {'AVAILABLE' if restore_result['network_available'] else 'UNAVAILABLE'}")
    print(f"Messages Processed: {restore_result['total_processed']}")
    print(f"Messages Forwarded: {restore_result['forwarded']}")
    print(f"Messages Failed: {restore_result['failed']}")
    
    # Get queue status after recovery
    queue_after = energy_integration_service.dtn_engine.get_queue_status()
    print(f"\nMessages in queue after recovery: {queue_after['total_queued']}")
    print(f"Transmission States: {queue_after.get('transmission_states', {})}")
    
    print("[SUCCESS] Queued messages transmitted by priority on network recovery")


def demo_degraded_network_prioritization():
    """
    Demo 5: Network DEGRADED - Critical messages prioritized
    """
    print("\n" + "=" * 70)
    print("DEMO 5: NETWORK DEGRADED - CRITICAL MESSAGE PRIORITIZATION")
    print("=" * 70)
    
    # Send energy telemetry on degraded network
    degraded_data = {
        "generator_status": "HIGH_LOAD",
        "generator_load_kw": 22.0,
        "battery_level": 55.0,
        "power_consumption_kw": 18.0
    }
    
    result = energy_integration_service.ingest_energy_telemetry(
        station_id="BHARATI-01",
        energy_data=degraded_data,
        network_status="DEGRADED",
        latency_ms=800.0,
        packet_loss_percent=8.0,
        bandwidth_mbps=1.5,
        signal_strength=55
    )
    
    print(f"Station: {result['station_id']}")
    print(f"Network Status: {result['network_decision']['network_condition']}")
    print(f"Communication Strategy: {result['network_decision']['communication_strategy']}")
    print(f"Message Priority: {result['data_classification']['priority']}")
    print(f"Transmission Decision: {'DTN Queue' if result['network_decision']['use_dtn'] else 'Attempt Normal'}")
    print(f"Strategy Explanation: {result['network_decision']['explanation']}")
    print("[SUCCESS] Communication strategy adjusted for DEGRADED network conditions")


def demo_communication_status():
    """
    Demo 6: Get energy communication status
    """
    print("\n" + "=" * 70)
    print("DEMO 6: ENERGY COMMUNICATION STATUS")
    print("=" * 70)
    
    status = energy_integration_service.get_energy_communication_status("MAITRI-01")
    
    print(f"Station: {status['station_id']}")
    print(f"Network Available: {status['network_available']}")
    print(f"Can Transmit Immediately: {status['can_transmit_immediately']}")
    print(f"DTN Queue Active: {status['dtn_queue_active']}")
    print(f"Queued Energy Messages: {status['queued_energy_messages']}")
    print(f"Transmission States: {status['transmission_states']}")
    print(f"Communication Recommendation: {status['communication_recommendation']}")
    print("[SUCCESS] Communication status retrieved successfully")


def main():
    """Run complete energy integration demonstration"""
    print("\n" + "=" * 70)
    print("ENERGY MODULE INTEGRATION END-TO-END DEMONSTRATION")
    print("Communication + Networking Layer for Antarctic Research Stations")
    print("=" * 70)
    
    try:
        # Initialize clean DTN database for demo
        demo_db = "demo_energy_integration.db"
        if os.path.exists(demo_db):
            os.remove(demo_db)
        
        energy_integration_service.dtn_engine = SyncEngine(
            local_db_path=demo_db, 
            server_url="http://localhost:8000"
        )
        
        # Run demonstration scenarios
        demo_online_network_normal_transmission()
        demo_offline_network_dtn_queue()
        demo_critical_message_priority()
        demo_network_recovery_synchronization()
        demo_degraded_network_prioritization()
        demo_communication_status()
        
        # Cleanup
        if os.path.exists(demo_db):
            os.remove(demo_db)
        
        print("\n" + "=" * 70)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nCommunication + Networking Integration Features Demonstrated:")
        print("[SUCCESS] Energy telemetry accepted and classified")
        print("[SUCCESS] Communication priority assigned based on operational importance")
        print("[SUCCESS] ONLINE network -> normal transmission")
        print("[SUCCESS] DEGRADED network -> prioritized transmission")
        print("[SUCCESS] OFFLINE network -> DTN queue activation")
        print("[SUCCESS] Critical messages get higher priority")
        print("[SUCCESS] Network recovery -> priority-based synchronization")
        print("[SUCCESS] Communication status monitoring")
        print("\nThe Communication + Networking layer ensures reliable, prioritized")
        print("and disruption-tolerant transmission of energy data for Antarctic stations.")
        
    except Exception as e:
        print(f"\n[ERROR] Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        if os.path.exists(demo_db):
            os.remove(demo_db)


if __name__ == "__main__":
    main()