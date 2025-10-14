#!/usr/bin/env python3
"""
Simple webhook to OSC bridge for QLab
Accepts HTTP webhooks and sends OSC messages to trigger QLab cues
"""

import json
import logging
from flask import Flask, request, jsonify
from pythonosc import udp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# QLab OSC settings
QLAB_HOST = "127.0.0.1"  # localhost
QLAB_PORT = 53000  # Default QLab OSC port
QLAB_PASSWORD = "4012"  # QLab OSC password - change this to match your QLab settings

# FLASK Settings
FLASK_PORT=4888

# Create UDP client to QLab
OSC_CLIENT = udp_client.SimpleUDPClient(QLAB_HOST, QLAB_PORT)

def send_osc_message(address, *args):
    """Send OSC message to QLab"""
    try:
        OSC_CLIENT.send_message(address, args)
        logger.info(f"Sent OSC message: {address}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OSC message {address}: {str(e)}")
        return False

def authenticate_with_qlab():
    """Authenticate with QLab by sending the password"""
    if not QLAB_PASSWORD:
        logger.info("No password set, skipping authentication")
        return True
    
    try:
        # Send password to QLab for authentication
        success = send_osc_message("/connect", QLAB_PASSWORD)
        if success:
            logger.info("Authentication sent to QLab")
        return success
    except Exception as e:
        logger.error(f"Failed to authenticate with QLab: {str(e)}")
        return False

@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    """Handle incoming webhook and send OSC message to QLab"""
    try:
        # Get the webhook data from either JSON (POST) or query params (GET)
        if request.method == 'POST':
            data = request.get_json() or {}
        else:  # GET request
            data = request.args.to_dict()
        
        logger.info(f"Received {request.method} webhook: {data}")
        
        # Extract cue information from webhook
        # You can customize this based on your webhook payload structure
        cue_id = data.get('cue_id', '1')  # Default to cue 1
        action = data.get('action', 'start')  # Default to start action
        
        # Authenticate with QLab first
        if not authenticate_with_qlab():
            return jsonify({
                "status": "error",
                "message": "Failed to authenticate with QLab"
            }), 500
        
        # Send OSC message to QLab
        # QLab OSC command format: /cue/{cue_id}/{action}
        osc_address = f"/cue/{cue_id}/{action}"
        success = send_osc_message(osc_address)
        
        if not success:
            return jsonify({
                "status": "error",
                "message": "Failed to send OSC message to QLab"
            }), 500
        
        return jsonify({
            "status": "success",
            "message": f"Sent OSC command: {osc_address}",
            "cue_id": cue_id,
            "action": action
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with usage information"""
    return jsonify({
        "message": "Webhook to OSC Bridge for QLab",
        "endpoints": {
            "POST /webhook": "Send webhook data to trigger QLab cues",
            "GET /health": "Health check",
            "GET /": "This information"
        },
        "webhook_format": {
            "cue_id": "Cue number to trigger (default: 1)",
            "action": "Action to perform (default: start)"
        },
        "qlab_settings": {
            "host": QLAB_HOST,
            "port": QLAB_PORT,
            "authentication": "enabled" if QLAB_PASSWORD else "disabled"
        }
    })

if __name__ == '__main__':
    logger.info(f"Starting webhook to OSC bridge...")
    logger.info(f"QLab OSC target: {QLAB_HOST}:{QLAB_PORT}")
    logger.info(f"QLab authentication: {'enabled' if QLAB_PASSWORD else 'disabled'}")
    logger.info(f"Webhook endpoint: http://localhost:{FLASK_PORT}/webhook")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=True)
