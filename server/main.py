from aiohttp import web

from web.app import create_app


def main():
    app = create_app()
    # app = web.Application()
    web.run_app(app)


if __name__ == '__main__':
    main()
