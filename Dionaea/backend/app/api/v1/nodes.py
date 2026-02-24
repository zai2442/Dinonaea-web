from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import asyncio

from app.db.database import get_db
from app.models.node import Node, NodeHistory
from app.schemas.node import NodeCreate, NodeUpdate, NodeResponse, NodeStatusUpdate, NodeHistoryResponse
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

# Store active websocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.post("/", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(node: NodeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_node = db.query(Node).filter(Node.ip_address == node.ip_address).first()
    if db_node:
        raise HTTPException(status_code=400, detail="Node with this IP already exists")
    
    new_node = Node(
        name=node.name,
        ip_address=node.ip_address,
        port=node.port,
        description=node.description,
        group=node.group,
        is_active=node.is_active,
        status="offline",
        cpu_usage=0.0
    )
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node

@router.get("/", response_model=List[NodeResponse])
def read_nodes(skip: int = 0, limit: int = 100, group: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    query = db.query(Node)
    if group:
        query = query.filter(Node.group == group)
    if status:
        query = query.filter(Node.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{node_id}", response_model=NodeResponse)
def read_node(node_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.put("/{node_id}", response_model=NodeResponse)
def update_node(node_id: int, node_update: NodeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    
    update_data = node_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(node, key, value)
    
    db.commit()
    db.refresh(node)
    return node

@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(node_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    
    db.delete(node)
    db.commit()
    return None

# Status update endpoint (called by node or monitor)
@router.post("/{node_id}/status", response_model=NodeResponse)
async def update_node_status(node_id: int, status_update: NodeStatusUpdate, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Record history if status changed or cpu usage changed significantly
    if node.status != status_update.status or abs(node.cpu_usage - status_update.cpu_usage) > 5.0:
        history = NodeHistory(
            node_id=node.id,
            status=status_update.status,
            cpu_usage=status_update.cpu_usage,
            details=status_update.cpu_usage_detail
        )
        db.add(history)

    node.status = status_update.status
    node.cpu_usage = status_update.cpu_usage
    node.cpu_usage_detail = status_update.cpu_usage_detail
    node.last_seen = datetime.utcnow()
    
    db.commit()
    db.refresh(node)
    
    # Broadcast update via WebSocket
    await manager.broadcast(json.dumps({
        "type": "update",
        "node_id": node.id,
        "status": node.status,
        "cpu_usage": node.cpu_usage,
        "last_seen": node.last_seen.isoformat()
    }))
    
    return node

@router.get("/{node_id}/history", response_model=List[NodeHistoryResponse])
def read_node_history(node_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = db.query(NodeHistory).filter(NodeHistory.node_id == node_id).order_by(NodeHistory.timestamp.desc()).limit(limit).all()
    return history

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed (e.g. ping/pong)
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
