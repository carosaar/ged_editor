from ged_editor import __version__
from ged_editor.app.constants import APP_NAME, APP_VERSION
from ged_editor.app.settings import settings


def test_project_metadata_placeholders() -> None:
    assert __version__ == APP_VERSION
    assert APP_NAME == "ged_editor"
    assert settings.log_level > 0
