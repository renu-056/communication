# Energy Module Integration Guide

This document provides the integration interface for the Energy/Infrastructure Module to send data to the Communication Backend.

## Overview

The Communication Backend provides a clean, stable interface for the Energy Module to send energy telemetry and alerts. The backend handles:

- **Message Classification**: Automatic priority assignment based on energy conditions
- **Network Decision**: Intelligent routing based on current network conditions
- **DTN Integration**: Store-and-forward for offline scenarios
- **Alert Generation**: Automatic database alerts for critical energy conditions

## API Endpoints

### 1. Energy Telemetry Ingestion

**Endpoint**: `POST /api/v1/energy/telemetry`

**Purpose**: Send routine energy telemetry data

**Request Format**:
```json
{
  "station_id": "MAITRI-01",
  "energy_data": {
    "generator_status": "OPTIMAL",
    "generator_load_kw": 15.5,
    "battery_level": 85.0,
    "power_consumption_kw": 12.3,
    "fuel_level_liters": 750.0,
    "energy_alert_type": null
  },
  "network_status": "ONLINE",
  "latency_ms": 150.0,
  "packet_loss_percent": 2.0,
  "bandwidth_mbps": 5.0,
  "signal_strength": 85,
  "source": "ENERGY_MODULE"
}
```

**Required Fields**:
- `station_id`: Station identifier (e.g., "MAITRI-01", "BHARATI-01")
- `energy_data`: Energy telemetry data object

**Optional Fields**:
- `network_status`: Current network status ("ONLINE", "DEGRADED", "OFFLINE") - default: "ONLINE"
- `latency_ms`: Network latency in milliseconds
- `packet_loss_percent`: Packet loss percentage (0-100)
- `bandwidth_mbps`: Bandwidth in Mbps
- `signal_strength`: Signal strength (0-100)
- `source`: Data source identifier - default: "ENERGY_MODULE"

**Energy Data Fields**:
- `generator_status`: Generator operational status
  - Accepted values: "OPTIMAL", "HIGH_LOAD", "DEGRADED", "FAILED", "CRITICAL"
- `generator_load_kw`: Generator load in kilowatts (optional)
- `battery_level`: Battery percentage 0-100 (optional)
- `power_consumption_kw`: Power consumption in kilowatts (optional)
- `fuel_level_liters`: Fuel level in liters (optional)
- `energy_alert_type`: Specific alert type if applicable (optional)

**Response**:
```json
{
  "station_id": "MAITRI-01",
  "data_classification": {
    "message_type": "ENERGY_TELEMETRY",
    "priority": "NORMAL",
    "rationale": "Regular energy telemetry - normal transmission"
  },
  "network_decision": {
    "network_condition": "ONLINE",
    "communication_strategy": "NORMAL_TRANSMISSION",
    "use_dtn": false,
    "explanation": "Network is healthy - using normal transmission for optimal performance."
  },
  "transmission_result": {
    "status": "sent",
    "message_id": "uuid",
    "strategy": "NORMAL_TRANSMISSION"
  },
  "queue_status": {
    "total_queued": 0,
    "critical_count": 0,
    "high_count": 0
  },
  "energy_integration": {
    "energy_data_received": true,
    "communication_priority": "NORMAL",
    "message_type": "ENERGY_TELEMETRY",
    "classification_rationale": "Regular energy telemetry - normal transmission",
    "alert_generated": false
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**HTTP Status Codes**:
- `202 Accepted`: Message accepted for processing
- `400 Bad Request`: Invalid payload
- `500 Internal Server Error`: Processing error

### 2. Critical Energy Alert

**Endpoint**: `POST /api/v1/energy/alert`

**Purpose**: Send critical energy alerts with highest priority

**Request Format**:
```json
{
  "station_id": "MAITRI-01",
  "alert_type": "GENERATOR_FAILURE",
  "alert_data": {
    "generator_status": "FAILED",
    "timestamp": "2024-01-15T10:30:00Z",
    "additional_context": "Generator main unit failure"
  },
  "network_status": "ONLINE"
}
```

**Required Fields**:
- `station_id`: Station identifier
- `alert_type`: Alert type (see Accepted Alert Types below)
- `alert_data`: Alert-specific data object

**Optional Fields**:
- `network_status`: Current network status - default: "ONLINE"

**Accepted Alert Types**:
- `GENERATOR_FAILURE`: Generator has failed
- `CRITICAL_POWER_LOSS`: Critical power loss event
- `BATTERY_CRITICAL`: Battery critically low

**Response**: Same format as telemetry ingestion

### 3. Energy Communication Status

**Endpoint**: `GET /api/v1/energy/status/{station_id}`

**Purpose**: Get current communication status for energy data transmission

**Response**:
```json
{
  "station_id": "MAITRI-01",
  "network_available": true,
  "can_transmit_immediately": true,
  "dtn_queue_active": false,
  "queued_energy_messages": 0,
  "transmission_states": {},
  "communication_recommendation": "Network available. Energy telemetry will be transmitted immediately."
}
```

## Priority Behavior

The communication backend automatically classifies energy messages based on operational importance:

### CRITICAL Priority
**Conditions**:
- Generator status: "FAILED" or "CRITICAL"
- Energy alert type: "CRITICAL_POWER_LOSS" or "EMERGENCY_POWER"
- Battery level: < 20%

**Behavior**:
- Immediate transmission attempt
- Highest DTN queue priority if offline
- Automatic database alert generation

### HIGH Priority
**Conditions**:
- Generator status: "HIGH_LOAD" or "DEGRADED"
- Energy alert type: "POWER_ANOMALY" or "GENERATOR_ANOMALY"
- Battery level: < 40%

**Behavior**:
- Prioritized transmission
- High DTN queue priority if offline
- Automatic database alert generation

### NORMAL Priority
**Conditions**:
- Routine energy telemetry
- Generator status: "OPTIMAL"
- Battery level: ≥ 40%

**Behavior**:
- Standard transmission
- Normal DTN queue priority if offline
- No automatic alert generation

## Network Behavior

### ONLINE Network
- **All priorities**: Immediate transmission
- **Strategy**: NORMAL_TRANSMISSION
- **Response time**: Fastest

### DEGRADED Network
- **CRITICAL**: PRIORITIZED_DTN - immediate attempt with DTN fallback
- **HIGH**: STORE_AND_FORWARD - reliable transmission
- **NORMAL/LOW**: DTN_QUEUE - queued for later transmission

### OFFLINE Network
- **All priorities**: DTN_QUEUE
- **Strategy**: STORE_AND_FORWARD
- **Behavior**: Messages queued in DTN for transmission when network restores
- **Priority ordering**: CRITICAL > HIGH > NORMAL > LOW

## Alert Generation

The backend automatically generates database alerts for critical and high-priority energy conditions:

### Alert Types Generated
- `GENERATOR_FAILURE`: When generator status is FAILED/CRITICAL
- `CRITICAL_POWER_LOSS`: When critical power loss detected
- `BATTERY_CRITICAL`: When battery < 20%
- `ENERGY_ANOMALY`: When generator HIGH_LOAD/DEGRADED or energy anomalies

### Alert Properties
- **Source**: "ENERGY_MODULE"
- **Severity**: CRITICAL for critical conditions, HIGH for anomalies
- **Cooldown**: 30 minutes between similar alerts (prevents duplicates)
- **Metadata**: Includes generator status, battery level, communication priority

## Example Requests

### Normal Energy Telemetry
```bash
curl -X POST http://localhost:8000/api/v1/energy/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": "MAITRI-01",
    "energy_data": {
      "generator_status": "OPTIMAL",
      "generator_load_kw": 15.5,
      "battery_level": 85.0,
      "power_consumption_kw": 12.3,
      "fuel_level_liters": 750.0
    },
    "network_status": "ONLINE"
  }'
```

### Critical Generator Failure
```bash
curl -X POST http://localhost:8000/api/v1/energy/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": "MAITRI-01",
    "energy_data": {
      "generator_status": "FAILED",
      "battery_level": 50.0
    },
    "network_status": "ONLINE"
  }'
```

### Critical Alert (Alternative Method)
```bash
curl -X POST http://localhost:8000/api/v1/energy/alert \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": "MAITRI-01",
    "alert_type": "GENERATOR_FAILURE",
    "alert_data": {
      "generator_status": "FAILED",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "network_status": "ONLINE"
  }'
```

### Check Communication Status
```bash
curl http://localhost:8000/api/v1/energy/status/MAITRI-01
```

## Integration Best Practices

1. **Always include network status**: Provide current network conditions for optimal routing
2. **Use appropriate alert types**: Match energy conditions to correct priority levels
3. **Handle offline scenarios**: Expect 202 responses with queued status when offline
4. **Monitor transmission results**: Check `transmission_result.status` in responses
5. **Use alert endpoint for emergencies**: `/alert` endpoint ensures highest priority handling

## Error Handling

### Common Errors

**400 Bad Request**:
- Invalid station_id format
- Missing required fields
- Invalid energy data values

**500 Internal Server Error**:
- Database connection issues
- DTN queue errors
- Network decision service errors

### Retry Logic
- The backend handles retry logic automatically through the DTN system
- No client-side retry needed for 202 responses
- For 4xx/5xx errors, implement exponential backoff

## Data Flow

```
Energy Module
    ↓
Energy API Endpoint
    ↓
Validation & Classification
    ↓
Network Decision Service
    ↓
Direct Transmission OR DTN Queue
    ↓
Database Persistence
    ↓
Alert Generation (if critical/high)
```

## Support

For integration issues or questions:
1. Check the API documentation at `/docs`
2. Review the communication status endpoint
3. Check network conditions and DTN queue status
4. Verify payload format against this guide