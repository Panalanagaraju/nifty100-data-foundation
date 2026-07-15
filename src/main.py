import sys

def load():
    print("Loading data...")

def validate():
    print("Running validation...")

def clean():
    print("Cleaning data...")

def report():
    print("Generating report...")

def dashboard():
    print("Launching dashboard...")

def api():
    print("Starting API...")

def ratios():
    print("Calculating financial ratios...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <command>")
        sys.exit()

    command = sys.argv[1]

    commands = {
        "load": load,
        "validate": validate,
        "clean": clean,
        "report": report,
        "dashboard": dashboard,
        "api": api,
        "ratios": ratios
    }

    if command in commands:
        commands[command]()
    else:
        print("Unknown command")