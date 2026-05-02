import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # telegram_id -> list of web.WebSocketResponse
        self.active_connections: dict[int, list] = {}

    def connect(self, user_id: int, ws):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(ws)
        logger.info(f"User {user_id} connected to WebSocket. Total connections for user: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: int, ws):
        if user_id in self.active_connections:
            if ws in self.active_connections[user_id]:
                self.active_connections[user_id].remove(ws)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket.")

    async def broadcast(self, user_id: int, event: str, data: dict = None):
        """
        Send an event to all connected websockets for a specific user.
        """
        if data is None:
            data = {}
            
        if user_id in self.active_connections:
            message = json.dumps({"event": event, "data": data}, default=str)
            websockets = self.active_connections[user_id].copy()
            for ws in websockets:
                try:
                    await ws.send_str(message)
                except Exception as e:
                    logger.error(f"Error sending websocket message to {user_id}: {e}")
                    self.disconnect(user_id, ws)

    async def broadcast_all(self, event: str, data: dict = None):
        """
        Send an event to ALL connected websockets (used for graceful shutdown).
        """
        if data is None:
            data = {}
        message = json.dumps({"event": event, "data": data}, default=str)
        
        for user_id in list(self.active_connections.keys()):
            websockets = self.active_connections[user_id].copy()
            for ws in websockets:
                try:
                    await ws.send_str(message)
                except Exception as e:
                    self.disconnect(user_id, ws)


ws_manager = ConnectionManager()
