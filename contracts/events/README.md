# Event schemas
One JSON Schema per event listed in docs/EVENT_CATALOG.md, versioned `name.vN.json`. Common envelope: event_id, correlation_id, tenant, account, market_ts?, emitted_ts, schema_version, producer, payload_hash. Registered in the schema registry [Source: 03]. Changes require Integration Architect + consuming-context owner review.
