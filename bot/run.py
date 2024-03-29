import logging
import uvicorn

from concurrent.futures import ThreadPoolExecutor

from general.settings import settings
from general import FISHER_BOT, FisherBotServer, app


def main() -> int:
    try:
        FisherBotServer(app).init_bot_data(FISHER_BOT)
        ThreadPoolExecutor().submit(
            uvicorn.run,
            app="run:app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT
        )
        FISHER_BOT.run()
    except Exception as exception:
        logging.critical(exception, exc_info=True)
    finally:
        FISHER_BOT.is_running = False
        FISHER_BOT.save_current_location()

    return 0


if __name__ == '__main__':
    exit(main())
