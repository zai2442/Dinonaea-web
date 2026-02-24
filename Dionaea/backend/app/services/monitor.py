import asyncio
import subprocess
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.node import Node, NodeHistory
from app.api.v1.nodes import manager
import json

async def ping_node(ip_address: str) -> bool:
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping", "-c", "1", "-W", "1", ip_address,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()
        return proc.returncode == 0
    except Exception:
        return False

async def check_nodes():
    db: Session = SessionLocal()
    try:
        nodes = db.query(Node).filter(Node.is_active == True).all()
        for node in nodes:
            # If seen recently (heartbeat), skip ping check
            if node.last_seen and (datetime.utcnow() - node.last_seen).total_seconds() < 60:
                continue
            
            # Ping check
            is_alive = await ping_node(node.ip_address)
            new_status = "online" if is_alive else "offline"
            
            # Update if status changed
            if node.status != new_status:
                node.status = new_status
                if new_status == "online":
                    node.last_seen = datetime.utcnow()
                
                # Record history
                history = NodeHistory(
                    node_id=node.id,
                    status=new_status,
                    cpu_usage=node.cpu_usage,
                    details=node.cpu_usage_detail,
                    timestamp=datetime.utcnow()
                )
                db.add(history)
                db.commit()
                db.refresh(node)
                
                # Broadcast
                await manager.broadcast(json.dumps({
                    "type": "update",
                    "node_id": node.id,
                    "status": node.status,
                    "cpu_usage": node.cpu_usage,
                    "last_seen": node.last_seen.isoformat() if node.last_seen else None
                }))
            
            # Alert if offline or high CPU (simulated alert logic)
            if new_status == "offline" or node.cpu_usage > 80.0:
                # In a real system, send email/SMS here.
                # For now, just broadcast an alert event
                await manager.broadcast(json.dumps({
                    "type": "alert",
                    "node_id": node.id,
                    "message": f"Node {node.name} ({node.ip_address}) is {new_status} with CPU {node.cpu_usage}%"
                }))

    except Exception as e:
        print(f"Error monitoring nodes: {e}")
    finally:
        db.close()

async def start_monitoring():
    while True:
        await check_nodes()
        await asyncio.sleep(60)
