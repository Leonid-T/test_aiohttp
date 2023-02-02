from aiohttp import web

from srv.settings.app import create_app


def main():
    app = create_app()
    web.run_app(app)


if __name__ == '__main__':
    main()
