# scada_telemetry_timeseries

## Entities
- assets
- sensors
- readings
- shift_calendar

## Distinctiveness
Captures high-frequency sensor readings from industrial assets.

## Indexes
- `sensors(asset_id)`
- `readings(sensor_id, reading_time)`

## Expected Row Counts
- sensors: 200
- readings: 500k

## Efficiency Notes
Composite index supports range scans by sensor and time.
