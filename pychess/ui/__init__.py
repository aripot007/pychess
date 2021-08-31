from pychess.ui.abstractui import AbstractUI


__DEFAULT_UI = None


def get_default_ui() -> AbstractUI:
    return __DEFAULT_UI


def set_default_ui(ui: AbstractUI) -> None:
    global __DEFAULT_UI
    __DEFAULT_UI = ui
