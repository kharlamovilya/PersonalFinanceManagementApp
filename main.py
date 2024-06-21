import sys
from modules.app import App

# Run the script.
if __name__ == '__main__':
    """Create and set up instances with console-set arguments."""
    args = sys.argv
    DEBUG = False
    if len(args) == 2:
        if args[1] in ["--DEBUG", "-d"]:
            DEBUG = True

    app = App(DEBUG)
    app.run()
