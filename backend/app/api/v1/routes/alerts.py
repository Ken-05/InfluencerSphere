"""
alerts.py
---------
Defines endpoints for users to create, view, and manage their monitoring alerts.
- POST /alerts: Creates a new alert rule.
- GET /alerts: Lists all active alert rules.
- DELETE /alerts/{alert_id}: Deletes a specific alert rule.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from ....services.alert_service import AlertService
from ....api import deps

router = APIRouter()


# --- Pydantic Schemas ---

class AlertRule(BaseModel):
    """Definition of a user-configurable alert."""
    alert_id: Optional[str] = Field(None, description="Unique ID of the alert (generated on creation).")
    influencer_id: str = Field(..., description="The ID of the influencer being monitored.")
    metric: Literal["engagement_rate", "follower_count", "market_score"] = Field(
        ..., description="The metric to monitor."
    )
    condition: Literal["below", "above", "drop_by"] = Field(
        ..., description="The condition type (e.g., 'below' a value, 'drop_by' a percentage)."
    )
    threshold_value: float = Field(..., description="The value used for the condition check.")
    is_active: bool = True


class AlertListResponse(BaseModel):
    """Response schema for listing all user alerts."""
    alerts: List[AlertRule]


# --- Dependencies Mock ---

def get_alerts_service() -> AlertService:
    # NOTE: Mocking the AlertService dependency
    class MockAlertService:
        mock_alerts = {}

        async def create_alert(self, user_id: str, rule_data: dict) -> str:
            new_id = f"alert-{len(self.mock_alerts) + 1}"
            rule_data['alert_id'] = new_id
            self.mock_alerts[new_id] = AlertRule(**rule_data)
            return new_id

        async def list_alerts(self, user_id: str) -> List[dict]:
            return [a.model_dump() for a in self.mock_alerts.values()]

        async def delete_alert(self, user_id: str, alert_id: str) -> bool:
            if alert_id in self.mock_alerts:
                del self.mock_alerts[alert_id]
                return True
            return False

    return MockAlertService()  # type: ignore


# --- Endpoints ---

@router.post("/alerts", response_model=AlertRule, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
        rule: AlertRule,
        svc: AlertService = Depends(get_alerts_service),  # Using the mock for now
        user_id: str = Depends(deps.get_current_user_id)
):
    """
    Creates a new monitoring alert rule for a specific influencer and metric.
    """
    try:
        alert_id = await svc.create_alert(user_id, rule.model_dump(exclude_none=True))
        rule.alert_id = alert_id
        return rule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert creation failed: {e.__class__.__name__}"
        )


@router.get("/alerts", response_model=AlertListResponse, status_code=status.HTTP_200_OK)
async def list_user_alerts(
        svc: AlertService = Depends(get_alerts_service),  # mock
        user_id: str = Depends(deps.get_current_user_id)
):
    """
    Retrieves all active and inactive alert rules configured by the current user.
    """
    alerts_data = await svc.list_alerts(user_id)
    alerts = [AlertRule(**data) for data in alerts_data]
    return AlertListResponse(alerts=alerts)


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
        alert_id: str,
        svc: AlertService = Depends(get_alerts_service),  # mock
        user_id: str = Depends(deps.get_current_user_id)
):
    """
    Deletes a specific alert rule by its unique ID.
    """
    deleted = await svc.delete_alert(user_id, alert_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule ID '{alert_id}' not found or unauthorized."
        )
    return