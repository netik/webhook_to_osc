# Webhook to OSC Bridge for QLab

A simple Python script that accepts HTTP webhooks and sends OSC messages over UDP to trigger QLab cues.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure QLab is running and has OSC enabled:
   - In QLab, go to Preferences → Network
   - Enable "Receive OSC Messages" 
   - Set an OSC password if desired (for security)
   - Note the port (default is 53000)

3. Run the script:
```bash
python webhook_to_osc.py
```

The server will start on `http://localhost:4888`

## Usage

### Webhook Endpoint

Send GET or POST requests to `http://localhost:4888/webhook`:

**POST requests** with JSON payload:

```json
{
  "cue_id": "1",
  "action": "start"
}
```

**GET requests** with query parameters:
```
http://localhost:4888/webhook?cue_id=1&action=start
```

**Parameters:**
- `cue_id` (optional): The cue number to trigger (default: "1")
- `action` (optional): The action to perform (default: "start")

### Example Webhook Calls

**POST requests:**
```bash
# Trigger cue 1
curl -X POST http://localhost:4888/webhook \
  -H "Content-Type: application/json" \
  -d '{"cue_id": "1", "action": "start"}'

# Trigger cue 5
curl -X POST http://localhost:4888/webhook \
  -H "Content-Type: application/json" \
  -d '{"cue_id": "5", "action": "start"}'
```

**GET requests:**
```bash
# Trigger cue 1
curl "http://localhost:4888/webhook?cue_id=1&action=start"

# Trigger cue 5
curl "http://localhost:4888/webhook?cue_id=5&action=start"

# Simple trigger (uses defaults: cue_id=1, action=start)
curl "http://localhost:4888/webhook"
```

### Other Endpoints

- `GET /` - Information about the service
- `GET /health` - Health check

## QLab OSC Commands

The script sends OSC messages over UDP in the format: `/cue/{cue_id}/{action}`

Common QLab OSC actions:
- `start` - Start the cue
- `stop` - Stop the cue
- `pause` - Pause the cue
- `resume` - Resume the cue

## Configuration

You can modify the QLab connection settings in the script:
- `QLAB_HOST`: QLab host (default: "127.0.0.1")
- `QLAB_PORT`: QLab OSC port (default: 53000)
- `QLAB_PASSWORD`: QLab OSC password (default: "password")

**Important**: Make sure the `QLAB_PASSWORD` in the script matches the password you set in QLab's OSC preferences. If you don't have a password set in QLab, you can set `QLAB_PASSWORD = ""` to disable authentication.

## Technical Details

This script uses the `python-osc` library which provides reliable UDP OSC support. The script:

- Creates a UDP client connection to QLab
- Authenticates using the `/connect` OSC message with your password
- Sends cue commands in the format `/cue/{cue_id}/{action}`
- Uses simple, reliable UDP communication
