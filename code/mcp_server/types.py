import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from visualization.chart_types import ChartType, InsightType, chart_registry

logger = logging.getLogger(__name__)


@dataclass
class VisualizationRequest:
    """Represents an active visualization request"""

    id: str
    chart_type: ChartType
    table_name: str
    original_request: str
    column_mappings: Dict[str, str]
    insights_requested: List[InsightType]
    status: str  # "pending_config", "ready", "completed", "error"
    error_message: Optional[str] = None
