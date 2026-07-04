import logging
from db import ensure_indexes
from ui import App

def main():
    # Configure logging for better visibility
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # Ensure database indexes
    try:
        ensure_indexes()
        logging.info("Database indexes ensured successfully.")
    except Exception as e:
        logging.warning(f"Index creation skipped or failed: {e}")

    # Launch the UI application
    try:
        app = App()
        logging.info("Starting Build Flow Manager UI...")
        app.mainloop()
    except Exception as e:
        logging.error(f"Application crashed: {e}", exc_info=True)

if __name__ == "__main__":
    main()

