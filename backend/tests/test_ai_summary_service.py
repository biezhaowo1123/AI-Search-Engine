# AI Summary Service tests - basic import verification
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.services.ai_summary_service import AISummaryService
    from backend.app.config import config
except ModuleNotFoundError:
    from app.services.ai_summary_service import AISummaryService
    from app.config import config

def test_ai_summary_service_import():
    assert AISummaryService is not None

def test_ai_summary_service_can_be_instantiated():
    service = AISummaryService()
    assert service is not None
    assert hasattr(service, 'generate_summary')
