
# API Documentation

## 1. Chat API

### GET `/api/chat`
Returns the most recent chat messages.

**Query Parameters**
- `limit` (optional, int): Maximum number of messages to return. Default: `100`.

**Response Example**
```json
{
  "packets": [
    {
      "id": 123,
      "import_time": "2025-07-22T12:45:00",
      "from_node_id": 987654,
      "from_node": "Alice",
      "channel": "main",
      "payload": "Hello, world!"
    }
  ]
}
```

---

### GET `/api/chat/updates`
Returns chat messages imported after a given timestamp.

**Query Parameters**
- `last_time` (optional, ISO timestamp): Only messages imported after this time are returned.

**Response Example**
```json
{
  "packets": [
    {
      "id": 124,
      "import_time": "2025-07-22T12:50:00",
      "from_node_id": 987654,
      "from_node": "Alice",
      "channel": "main",
      "payload": "New message!"
    }
  ],
  "latest_import_time": "2025-07-22T12:50:00"
}
```

---

## 2. Nodes API

### GET `/api/nodes`
Returns a list of all nodes, with optional filtering by last seen.

**Query Parameters**
- `hours` (optional, int): Return nodes seen in the last N hours.
- `days` (optional, int): Return nodes seen in the last N days.
- `last_seen_after` (optional, ISO timestamp): Return nodes seen after this time.

**Response Example**
```json
{
  "nodes": [
    {
      "node_id": 1234,
      "long_name": "Alice",
      "short_name": "A",
      "channel": "main",
      "last_seen": "2025-07-22T12:40:00",
      "hardware": "T-Beam",
      "firmware": "1.2.3",
      "role": "client",
      "last_lat": 37.7749,
      "last_long": -122.4194
    }
  ]
}
```

---

## 3. Packets API

### GET `/api/packets`
Returns a list of packets with optional filters.

**Query Parameters**
- `limit` (optional, int): Maximum number of packets to return. Default: `200`.
- `since` (optional, ISO timestamp): Only packets imported after this timestamp are returned.

**Response Example**
```json
{
  "packets": [
    {
      "id": 123,
      "from_node_id": 5678,
      "to_node_id": 91011,
      "portnum": 1,
      "import_time": "2025-07-22T12:45:00",
      "payload": "Hello, Bob!"
    }
  ]
}
```

---

### Notes
- All timestamps (`import_time`, `last_seen`) are returned in ISO 8601 format.
- `portnum` is an integer representing the packet type.
- `payload` is always a UTF-8 decoded string.