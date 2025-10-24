"""
Alert management routes - now with authentication
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from loguru import logger
from datetime import datetime

from api.models.alert import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    TriggeredAlertResponse,
    AlertAcknowledge,
    AlertResolve
)
from api.models.database import AlertRule, TriggeredAlert, User
from api.utils.database import get_db_session
from api.utils.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    rule: AlertRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Create a new alert rule (requires authentication)
    """
    try:
        db_rule = AlertRule(
            name=rule.name,
            description=rule.description,
            query=rule.query,
            condition=rule.condition,
            threshold=rule.threshold,
            time_window=rule.time_window,
            services=rule.services,
            levels=rule.levels,
            notification_channel=rule.notification_channel,
            notification_config=rule.notification_config,
            is_active=rule.is_active,
            owner_id=current_user.id
        )
        
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        
        logger.info(f"User {current_user.username} created alert rule: {db_rule.name}")
        
        return db_rule
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create alert rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert rule: {str(e)}")


@router.get("/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    active_only: bool = False,
    db: Session = Depends(get_db_session)
):
    """
    List all alert rules (public endpoint)
    """
    try:
        query = db.query(AlertRule)
        
        if active_only:
            query = query.filter(AlertRule.is_active == True)
        
        rules = query.order_by(AlertRule.created_at.desc()).all()
        
        return rules
        
    except Exception as e:
        logger.error(f"Failed to list alert rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list alert rules: {str(e)}")


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db_session)
):
    """Get a specific alert rule by ID"""
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    return rule


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    rule_update: AlertRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Update an alert rule (requires authentication, owner or admin only)
    """
    try:
        db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not db_rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        # Check permissions
        if db_rule.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to update this rule"
            )
        
        # Update fields
        update_data = rule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rule, field, value)
        
        db_rule.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_rule)
        
        logger.info(f"User {current_user.username} updated alert rule: {db_rule.name}")
        
        return db_rule
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update alert rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update alert rule: {str(e)}")


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_alert_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Delete an alert rule (requires authentication, owner or admin only)
    """
    try:
        db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not db_rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        # Check permissions
        if db_rule.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this rule"
            )
        
        db.delete(db_rule)
        db.commit()
        
        logger.info(f"User {current_user.username} deleted alert rule: {db_rule.name}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete alert rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete alert rule: {str(e)}")


@router.get("/triggered", response_model=List[TriggeredAlertResponse])
async def list_triggered_alerts(
    status: str = None,
    rule_id: int = None,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """List triggered alerts (public endpoint)"""
    try:
        query = db.query(TriggeredAlert)
        
        if status:
            query = query.filter(TriggeredAlert.status == status)
        
        if rule_id:
            query = query.filter(TriggeredAlert.rule_id == rule_id)
        
        alerts = query.order_by(TriggeredAlert.triggered_at.desc()).limit(limit).all()
        
        result = []
        for alert in alerts:
            alert_dict = {
                "id": alert.id,
                "rule_id": alert.rule_id,
                "rule_name": alert.rule.name if alert.rule else None,
                "triggered_at": alert.triggered_at,
                "value": alert.value,
                "threshold": alert.threshold,
                "log_count": alert.log_count,
                "sample_logs": alert.sample_logs,
                "status": alert.status,
                "acknowledged_at": alert.acknowledged_at,
                "acknowledged_by": alert.acknowledged_by,
                "resolved_at": alert.resolved_at,
                "notes": alert.notes
            }
            result.append(TriggeredAlertResponse(**alert_dict))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list triggered alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list triggered alerts: {str(e)}")


@router.post("/triggered/{alert_id}/acknowledge", response_model=TriggeredAlertResponse)
async def acknowledge_alert(
    alert_id: int,
    ack: AlertAcknowledge,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Acknowledge a triggered alert (requires authentication)"""
    try:
        alert = db.query(TriggeredAlert).filter(TriggeredAlert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Triggered alert not found")
        
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = current_user.id
        if ack.notes:
            alert.notes = ack.notes
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"User {current_user.username} acknowledged alert ID: {alert_id}")
        
        alert_dict = {
            "id": alert.id,
            "rule_id": alert.rule_id,
            "rule_name": alert.rule.name if alert.rule else None,
            "triggered_at": alert.triggered_at,
            "value": alert.value,
            "threshold": alert.threshold,
            "log_count": alert.log_count,
            "sample_logs": alert.sample_logs,
            "status": alert.status,
            "acknowledged_at": alert.acknowledged_at,
            "acknowledged_by": alert.acknowledged_by,
            "resolved_at": alert.resolved_at,
            "notes": alert.notes
        }
        
        return TriggeredAlertResponse(**alert_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/triggered/{alert_id}/resolve", response_model=TriggeredAlertResponse)
async def resolve_alert(
    alert_id: int,
    resolve: AlertResolve,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Resolve a triggered alert (requires authentication)"""
    try:
        alert = db.query(TriggeredAlert).filter(TriggeredAlert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Triggered alert not found")
        
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        if resolve.notes:
            alert.notes = resolve.notes
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"User {current_user.username} resolved alert ID: {alert_id}")
        
        alert_dict = {
            "id": alert.id,
            "rule_id": alert.rule_id,
            "rule_name": alert.rule.name if alert.rule else None,
            "triggered_at": alert.triggered_at,
            "value": alert.value,
            "threshold": alert.threshold,
            "log_count": alert.log_count,
            "sample_logs": alert.sample_logs,
            "status": alert.status,
            "acknowledged_at": alert.acknowledged_at,
            "acknowledged_by": alert.acknowledged_by,
            "resolved_at": alert.resolved_at,
            "notes": alert.notes
        }
        
        return TriggeredAlertResponse(**alert_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")
