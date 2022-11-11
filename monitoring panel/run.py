import uvicorn

from concurrent.futures import ThreadPoolExecutor

from general.settings import settings
from general import PANEL, MonitoringPanelServer, app


def main() -> int:
    try:
        MonitoringPanelServer(app).init_panel_data(PANEL)
        ThreadPoolExecutor().submit(
            uvicorn.run,
            app="run:app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT
        )
        PANEL.run()
    except Exception as exception:
        print(exception)
    finally:
        PANEL.is_running = False

    return 0


if __name__ == '__main__':
    exit(main())
