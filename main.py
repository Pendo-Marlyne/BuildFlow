# main.py
from db import ensure_indexes
from ui import App

def main():
    # Ensure essential indexes exist (idempotent)
    try:
        ensure_indexes()
    except Exception:
        # Index creation should not block the UI in development;
        # in production you may want to log or raise.
        pass

    # Launch the Tkinter application
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
