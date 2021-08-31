from pychess.ui.termui import TermUI
from pychess.variants import ClassicVariant, Variant
import pychess.ui
import argparse


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Launch pychess")
    p.add_argument("--ui", type=str, default="terminal", help="Choose which UI to use. Possible values are 'terminal' (default) and 'gui'.", required=False)

    args = p.parse_args()
    if args.ui.lower() == "terminal":
        pychess.ui.set_default_ui(TermUI())
    elif args.ui.lower() == "gui":
        raise NotImplementedError

    ui = pychess.ui.get_default_ui()

    variant_class = ui.choice("Please choose a variant to play :", {"Standard": ClassicVariant})

    variant: Variant = variant_class()

    variant.setup()
    variant.start()

    ui.print("Exiting program")
