# Only initialize UI if running in Anki, skip otherwise (e.g. when running tests)
try:
    from aqt import mw

    if mw and hasattr(mw, "form") and hasattr(mw.form, "menuTools"):
        from .popUpWindow import InitializeAnkiMenu

        InitializeAnkiMenu()
except (AttributeError, ImportError):
    # Not in Anki environment, skip initialization
    pass
