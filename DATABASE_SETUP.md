# Database Setup and Deployment Guide

## Overview

The Antarctica Research Station Backend supports dual database architecture:

- **Local Development**: SQLite (default)
- **Production/Supabase**: PostgreSQL

The same application code works with both database types through SQLAlchemy abstraction.

## Architecture

### Dual Database System

The application uses two separate databases:

1. **Main Application Database** (`DATABASE_URL`)
   - Stores stations, telemetry, logistics, routes, alerts, network status
   - Can be SQLite (local) or PostgreSQL/Supabase (production)
   - Accessed via SQLAlchemy ORM

2. **DTN Queue Database** (`DTN_DATABASE_PATH`)
   - Always uses local SQLite file
   - Designed for store-and-forward operation during network outages
   - Critical for Antarctica offline scenarios
   - Must work even when main database is unavailable

### Why DTN Remains Local

The DTN (Delay-Tolerant Networking) queue intentionally uses local SQLite because:

- **Offline Operation**: Antarctica stations experience frequent network outages
- **Local Persistence**: Messages must be stored locally when network is unavailable
- **No Dependency**: DTN queue must function independently of central database connectivity
- **Performance**: Local SQLite provides fast, reliable local storage
- **Simplicity**: No network dependency for queue operations

## Local Development (SQLite)

### Quick Start

1. **No configuration required** - SQLite is the default
2. **Application startup**: Tables are created automatically
3. **Database file**: `antarctica_test.db` (created automatically)

### Running with SQLite

```bash
# Using default configuration (no .env file needed)
python -m uvicorn app.main:app --reload
```

### Database Location

- **File**: `antarctica_test.db` (in project root)
- **DTN Queue**: `dtn_queue.db` (in project root)

## Production (PostgreSQL/Supabase)

### Prerequisites

- PostgreSQL database or Supabase project
- Database connection string
- `psycopg2-binary` driver (already in requirements.txt)

### Configuration

1. **Copy environment template**:
```bash
cp .env.example .env
```

2. **Edit `.env` file**:
```bash
# For PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/antarctica_db

# For Supabase
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

3. **Run application**:
```bash
python -m uvicorn app.main:app --reload
```

### Connection Pooling

The PostgreSQL configuration includes optimized connection pooling:

- **Pool Size**: 5 connections maintained
- **Max Overflow**: 10 additional connections when needed
- **Pool Timeout**: 30 seconds wait time
- **Pool Recycle**: 1 hour (prevents stale connections)
- **Pre-Ping**: Verifies connections before use

### Supabase Specific Configuration

Supabase uses PostgreSQL, so the standard PostgreSQL configuration applies:

```bash
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

**Important Supabase Notes**:
- Use Supabase's connection pooling for production
- Enable SSL for secure connections
- Configure Supabase row-level security if needed
- Use Supabase dashboard to monitor database performance

## Database Schema

### Tables

The application automatically creates these tables on startup:

- **stations**: Research station information
- **telemetry**: Environmental and operational telemetry
- **logistics_items**: Supply and inventory management
- **traverse_routes**: Travel route information
- **alerts**: System alerts and notifications
- **sync_queue**: Message synchronization queue (SQLAlchemy model)
- **network_status**: Network monitoring data

### Model Compatibility

All SQLAlchemy models use PostgreSQL-compatible types:

- **Primary Keys**: String UUIDs (compatible with both databases)
- **Timestamps**: DateTime fields (compatible)
- **JSON Fields**: JSON columns (PostgreSQL JSONB, SQLite JSON)
- **Foreign Keys**: Standard SQLAlchemy relationships
- **Indexes**: Standard database indexes
- **Unique Constraints**: Standard unique constraints

## Security

### Credential Management

**Never commit credentials to version control**

1. **Use `.env` file** for local development
2. **Use environment variables** for production
3. **Never include `.env` in git**
4. **Use different passwords** for each environment
5. **Rotate credentials regularly**

### Supabase Security

- **Never hardcode Supabase credentials**
- **Use Supabase environment variables**
- **Enable Row Level Security (RLS)** in Supabase
- **Use Supabase authentication** for API access
- **Monitor Supabase logs** for suspicious activity

## Database Verification

### Check Database Status

Use the `/database-info` endpoint to verify database configuration:

```bash
curl http://localhost:8000/database-info
```

**Response Example**:
```json
{
  "connection_status": "connected",
  "connection_message": "Database connection successful",
  "configuration": {
    "database_type": "SQLite",
    "database_url": "sqlite:///./antarctica_test.db",
    "dtn_database_path": "dtn_queue.db"
  }
}
```

### Health Check

The `/health` endpoint includes database connectivity:

```bash
curl http://localhost:8000/health
```

## Deployment Checklist

### Before Deployment

- [ ] Create PostgreSQL/Supabase database
- [ ] Configure `DATABASE_URL` environment variable
- [ ] Test database connection
- [ ] Verify DTN queue path is writable
- [ ] Review security settings
- [ ] Set up database backups
- [ ] Configure connection pooling for production

### Environment Variables Required

- `DATABASE_URL`: PostgreSQL/Supabase connection string
- `DTN_DATABASE_PATH`: Path to local DTN queue file (optional, defaults to `dtn_queue.db`)

### Migration Strategy

**Current State**: No migration system (Alembic in requirements but not configured)

**Strategy**: 
- Development: Automatic table creation (`create_tables()`)
- Production: Consider implementing Alembic migrations for schema versioning
- For now: Automatic creation is sufficient for initial deployment

## Troubleshooting

### SQLite Issues

**Problem**: Database file locked
**Solution**: Ensure only one application instance is running

**Problem**: Permission denied
**Solution**: Check file permissions on database file

### PostgreSQL Issues

**Problem**: Connection refused
**Solution**: Verify PostgreSQL is running and accessible

**Problem**: Authentication failed
**Solution**: Check username/password in DATABASE_URL

**Problem**: Connection pool exhausted
**Solution**: Increase pool_size in database.py configuration

### Supabase Issues

**Problem**: Connection timeout
**Solution**: Check network connectivity to Supabase

**Problem**: SSL certificate error
**Solution**: Add `?sslmode=require` to DATABASE_URL

**Problem**: Performance issues
**Solution**: Monitor Supabase dashboard and optimize queries

## API Endpoints

### Database Information

- **GET `/database-info`**: Get current database configuration and status
- **GET `/health`**: Health check including database connectivity

## Best Practices

### Development

- Use SQLite for local development
- Keep `.env` file out of version control
- Test with both SQLite and PostgreSQL before deployment
- Use database transactions for data consistency

### Production

- Use PostgreSQL/Supabase for production
- Enable connection pooling
- Monitor database performance
- Set up automated backups
- Use read replicas for scaling if needed
- Implement proper error handling for database failures

### Antarctica Deployment

- Ensure DTN queue has sufficient disk space
- Monitor DTN queue size during network outages
- Test offline scenarios regularly
- Plan for extended network outages (days/weeks)
- Ensure local database persistence is reliable

## Support

For database-related issues:

1. Check `/database-info` endpoint status
2. Review application logs
3. Verify environment variables
4. Test database connection independently
5. Check Supabase dashboard (if using Supabase)