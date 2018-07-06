import os
import sys

import aiocache
from sanic import Sanic

#把python-read目录加入到path路径.
from sanic.response import html, redirect
from sanic_session import RedisSessionInterface

from src.config import LOGGER, CONFIG
from src.database.redis import RedisSession
from src.views import index_bp, search_bp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Sanic(__name__)
app.static('/static/', CONFIG.BASE_DIR + '/static/')

app.blueprint(index_bp)
app.blueprint(search_bp)




@app.listener('before_server_start')
def init_cache(app, loop):
    LOGGER.info("Starting aiocache")
    app.config.from_object(CONFIG)
    REDIS_DICT = CONFIG.REDIS_DICT
    aiocache.settings.set_defaults(
        class_="aiocache.RedisCache",
        endpoint=REDIS_DICT.get('REDIS_ENDPOINT', 'localhost'),
        port=REDIS_DICT.get('REDIS_PORT', 6379),
        db=REDIS_DICT.get('CACHE_DB', 0),
        password=REDIS_DICT.get('REDIS_PASSWORD', None),
        loop=loop,
    )
    LOGGER.info("Starting redis pool")
    redis_session = RedisSession()
    # redis instance for app
    app.get_redis_pool = redis_session.get_redis_pool
    # pass the getter method for the connection pool into the session
    app.session_interface = RedisSessionInterface(
        app.get_redis_pool, cookie_name="owl_sid", expiry=30 * 24 * 60 * 60)


@app.middleware('request')
async def add_session_to_request(request):
    host = request.headers.get('host',None)
    user_agent = request.headers.get('user-agent',None)
    if user_agent:
        user_ip = request.headers.get('X-Forwarded-For')
        if user_ip in CONFIG.FORBIDDEN:
            return html("<h3>网站正在维护...</h3>")
        if CONFIG.VAL_HOST == 'true':
            if not host or host not in CONFIG.HOST:
                return redirect('http://www.rsfight.com')
        if CONFIG.WEBSITE['IS_RUNNING']:
            await app.session_interface.open(request)
        else:
            return html("<h3>网站正在维护...</h3>")
    else:
        return html("<h3>网站正在维护...</h3>")


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    # await app.session_interface.save(request, response)
    if request.path == '/operate/login' and request['session'].get('user', None):
        await app.session_interface.save(request, response)
        import datetime
        response.cookies['lhz_sid']['expires'] = datetime.datetime.now(
        ) + datetime.timedelta(days=30)
    elif request.path == '/register':
        try:
            response.cookies['reg_index'] = str(request['session']['index'][0])
        except KeyError as e:
            LOGGER.error(e)


if __name__ == "__main__":
    app.run(host="127.0.0.1", workers=1, port=8001, debug=CONFIG.DEBUG)