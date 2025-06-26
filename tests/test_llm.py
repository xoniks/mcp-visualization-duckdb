# LLM integration tests - Simple fallback implementation
import pytest
from code.llm.simple_fallback import SimpleFallbackClient


@pytest.fixture
def fallback_client():
    """Create a simple fallback client for testing"""
    return SimpleFallbackClient()


@pytest.mark.asyncio
async def test_detect_chart_type(fallback_client):
    """Test chart type detection with fallback logic"""
    result = await fallback_client.detect_chart_type(
        "Show me a scatter plot of sales vs revenue", 
        ["sales", "revenue", "date"],
        "sales_data"
    )
    
    assert result["success"] is True
    assert "chart_type" in result
    assert result["chart_type"] == "scatter"  # Should detect scatter from request


@pytest.mark.asyncio
async def test_column_suggestions(fallback_client):
    """Test column mapping suggestions"""
    columns = [
        {"name": "sales", "type": "DOUBLE"},
        {"name": "date", "type": "DATE"},
        {"name": "region", "type": "VARCHAR"}
    ]
    
    result = await fallback_client.suggest_column_mappings(
        "line", columns, "sales over time"
    )
    
    assert result["success"] is True
    assert "suggestions" in result


@pytest.mark.asyncio
async def test_check_connection(fallback_client):
    """Test connection check always succeeds"""
    result = await fallback_client.check_connection()
    assert result is True


@pytest.mark.asyncio
async def test_list_models(fallback_client):
    """Test model listing returns empty list"""
    models = await fallback_client.list_models()
    assert isinstance(models, list)
    assert len(models) == 0


@pytest.mark.asyncio
async def test_generate_insights(fallback_client):
    """Test insights generation"""
    insights = await fallback_client.generate_insights_description(
        "bar", {"count": 100}, {"max": 500, "min": 10}
    )
    
    assert isinstance(insights, str)
    assert len(insights) > 0
