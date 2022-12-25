from aiohttp import web

from app.app import create_app


def main():
    app = create_app()
    web.run_app(app, host='localhost')


if __name__ == '__main__':
    main()
