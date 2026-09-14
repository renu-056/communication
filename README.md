# Antarctic Research Station Management - Backend API

Backend API for remote management of Indian Antarctic Research Stations (Maitri and Bharati) under the National Centre for Polar and Ocean Research (NCPOR).

## Features

- **Low-Bandwidth Sync Engine**: Offline-first data buffering and compressed batch transmission for satellite-constrained environments
- **Telemetry Ingestion**: Real-time sensor data collection from Antarctic stations
- **RESTful API**: Clean, well-documented API endpoints for all system modules
- **PostgreSQL Integration**: Persistent storage with SQLAlchemy ORM
- **Auto-generated Documentation**: Interactive Swagger/OpenAPI docs at `/docs`
- **Resilient Communication**: Queue-based data synchronization with automatic retry logic

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic 2.0
- **Compression**: Gzip for low-bandwidth transmission
- **Queue**: SQLite-based local sync queue
- **Containerization**: Docker & Docker Compose

## Architecture

```
[Antarctic Station Sensors] → [Local Sync Engine] → [Satellite Link] → [FastAPI Gateway] → [PostgreSQL]
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15
- Docker (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd antarctica_backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Set up PostgreSQL database**
```bash
# Create database
createdb antarctica_db

# Or use Docker Compose for database
docker-compose up -d db
```

6. **Run the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# The API will be available at http://localhost:8000
# Database at localhost:5432
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check
- `GET /health` - Service health status
- `GET /` - API information and documentation links

### Telemetry
- `POST /api/v1/telemetry/ingest` - Ingest sensor data from stations
- `GET /api/v1/telemetry/history` - Fetch historical telemetry records
- `GET /api/v1/telemetry/latest` - Get latest telemetry for a station

### Logistics
- `POST /api/v1/logistics/` - Create logistics inventory item
- `GET /api/v1/logistics/` - List logistics items for a station
- `GET /api/v1/logistics/{item_id}` - Get specific logistics item
- `PUT /api/v1/logistics/{item_id}` - Update logistics item

### Routes (GIS)
- `POST /api/v1/routes/` - Create traverse route
- `GET /api/v1/routes/` - List routes for a station
- `GET /api/v1/routes/{route_id}` - Get specific route
- `PUT /api/v1/routes/{route_id}` - Update route

### Alerts
- `POST /api/v1/alerts/` - Create alert (from ML models)
- `GET /api/v1/alerts/` - List alerts for a station
- `GET /api/v1/alerts/{alert_id}` - Get specific alert
- `PUT /api/v1/alerts/{alert_id}/resolve` - Mark alert as resolved

## Low-Bandwidth Sync Engine

The sync engine (`app/services/sync_engine.py`) provides offline-first data buffering:

### Features
- Local SQLite queue for pending data
- Gzip compression for reduced bandwidth usage
- Automatic retry with exponential backoff
- Batch processing for efficiency
- Persistent storage across reboots

### Usage Example

```python
from app.services.sync_engine import SyncEngine

# Initialize sync engine
sync = SyncEngine(local_db_path="local_sync.db", server_url="http://localhost:8000")

# Queue telemetry data (will be compressed by default)
sync.queue_payload(
    station_id="BHARATI-01",
    payload={
        "timestamp": 1725888000,
        "battery_level": 94.2,
        "generator_status": "OPTIMAL",
        "outside_temp_celsius": -28.4
    },
    compress=True
)

# Process pending queue when connection is available
results = sync.process_queue(batch_size=10)
print(f"Synced: {results['success']}, Failed: {results['failed']}")

# Check queue status
status = sync.get_queue_status()
print(f"Pending: {status['pending']}, Synced: {status['synced']}")
```

## Compression Benchmarks

Based on typical telemetry payloads:
- **JSON**: ~500 bytes per record
- **Gzip Compressed**: ~150 bytes per record
- **Compression Ratio**: ~3.3x reduction
- **Bandwidth Savings**: ~70% for typical telemetry batches

## Database Schema

### Core Tables
- **stations**: Station metadata and configuration
- **telemetry**: Sensor measurements and system metrics
- **logistics_items**: Inventory and supply tracking
- **traverse_routes**: GIS route data for vehicle traverses
- **alerts**: ML-generated anomaly alerts
- **sync_queue**: Local buffer for offline data

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://postgres:postgres@localhost:5432/antarctica_db |

## Team Integration

### For Dashboard Team
- Base URL: `http://localhost:8000`
- CORS: Enabled for all origins (configure for production)
- WebSocket: Planned for real-time updates

### For Edge/ML Team
- Telemetry Ingest: `POST /api/v1/telemetry/ingest`
- Alert Creation: `POST /api/v1/alerts/`
- Compression: Use gzip for batch payloads

### For Logistics Team
- Inventory CRUD: `/api/v1/logistics/` endpoints
- Low stock alerts: Query with `min_threshold` filtering

### For GIS Team
- Route CRUD: `/api/v1/routes/` endpoints
- Coordinate format: GeoJSON-like structure in JSON field

### For Energy Module Team
- **Communication + Network Integration**: Energy module can send telemetry through dedicated endpoints
- Energy Telemetry: `POST /api/v1/energy/telemetry`
- Critical Energy Alerts: `POST /api/v1/energy/alert`
- Communication Status: `GET /api/v1/energy/status/{station_id}`
- Priority-based transmission based on operational importance
- DTN queue activation during network outages
- See "Communication + Network Integration" section below

## Communication + Network Integration

The Communication + Networking layer provides reliable, prioritized, and disruption-tolerant transmission of station data, including energy telemetry from the Energy Module.

### Supported Energy Telemetry

The communication layer accepts energy data with the following structure:

```json
{
  "station_id": "MAITRI-01" or "BHARATI-01",
  "energy_data": {
    "generator_status": "OPTIMAL" | "HIGH_LOAD" | "FAILED" | "CRITICAL",
    "generator_load_kw": 15.5,
    "battery_level": 85.0,
    "power_consumption_kw": 12.3,
    "fuel_level_liters": 750.0,
    "energy_alert_type": "POWER_ANOMALY" (optional)
  },
  "network_status": "ONLINE" | "DEGRADED" | "OFFLINE",
  "latency_ms": 150.0,
  "packet_loss_percent": 2.0,
  "bandwidth_mbps": 5.0,
  "signal_strength": 85
}
```

### Communication Priority Behavior

Energy data is automatically classified based on operational importance:

**CRITICAL Priority** (Immediate transmission):
- Generator failure (status: "FAILED" or "CRITICAL")
- Critical power loss events
- Battery level below 20%

**HIGH Priority** (Priority transmission):
- Generator high load or degraded status
- Energy anomalies
- Battery level below 40%

**NORMAL Priority** (Standard transmission):
- Regular energy telemetry
- Normal operational status

### Network Behavior

**ONLINE Network**:
- Energy telemetry transmitted immediately
- Normal transmission strategy used
- All data sent in real-time

**DEGRADED Network**:
- Critical/high priority messages prioritized
- Store-and-forward mode for important data
- Non-critical data may be queued
- DTN fallback for reliability

**OFFLINE Network**:
- All energy messages queued in DTN
- Persistent storage ensures no data loss
- Priority-based queuing maintained
- Automatic transmission on network recovery

### Network Recovery Behavior

When network becomes available after being offline:
1. DTN queue messages marked as READY
2. Messages transmitted by priority: CRITICAL > HIGH > NORMAL > LOW
3. Transmission states tracked: QUEUED → READY → TRANSMITTING → DELIVERED/FAILED
4. Failed messages retried with exponential backoff
5. Compression applied for bandwidth efficiency
6. Acknowledgment and state updates on successful delivery

### Energy Module Integration Contract

**Expected Energy Module Data Structure**:

```json
{
  "station_id": "MAITRI-01",
  "energy_data": {
    "generator_status": "OPTIMAL",
    "generator_load_kw": 15.5,
    "battery_level": 85.0,
    "power_consumption_kw": 12.3,
    "fuel_level_liters": 750.0
  },
  "network_status": "ONLINE",
  "latency_ms": 150.0,
  "packet_loss_percent": 2.0,
  "bandwidth_mbps": 5.0,
  "signal_strength": 85
}
```

**Critical Alert Structure**:

```json
{
  "station_id": "BHARATI-01",
  "alert_type": "GENERATOR_FAILURE",
  "alert_data": {
    "generator_status": "FAILED",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "network_status": "ONLINE"
}
```

**API Endpoint**: `POST /api/v1/energy/telemetry`

**Response Example**:

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
    "message_id": "uuid-here",
    "network_available": true,
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
    "classification_rationale": "Regular energy telemetry - normal transmission"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Demonstration

Run the energy integration demonstration:

```bash
python demo_energy_integration.py
```

This demonstrates:
- ONLINE network → normal transmission
- OFFLINE network → DTN queue activation
- Critical message priority handling
- Network recovery → priority-based synchronization
- DEGRADED network → prioritized transmission
- Communication status monitoring

## Development Workflow

1. Create feature branch from `development`
2. Implement changes following existing patterns
3. Test with Swagger UI at `/docs`
4. Run pytest suite
5. Submit PR with description

## Demo Script

To demonstrate low-bandwidth resilience:

1. Start server: `uvicorn app.main:app --reload`
2. Open Swagger UI at `http://localhost:8000/docs`
3. Send telemetry via `/api/v1/telemetry/ingest`
4. Simulate network drop (stop server or firewall)
5. Continue sending data (queues locally via sync engine)
6. Restore network
7. Watch auto-sync process queued data

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Verify database exists: `psql -U postgres -l`

### Import Errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### CORS Issues
- Check CORS middleware in `app/main.py`
- Verify frontend origin is allowed

## License

[SIH PS ID: SIH26060] - Smart India Hackathon Project

## Contact

For backend API issues or integration support, contact the Communication & Backend team lead.
