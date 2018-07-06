import time
from operator import itemgetter

from sanic import Blueprint
from sanic.response import redirect, html

from src.config import ENGINE_PRIORITY
from src.fetcher.novels_tools import get_novels_info
from src.utils.tools import template

search_bp = Blueprint('search_blueprint')

@search_bp.route("/search", methods=['GET'])
async def search(request):
    start = time.time()
    name = str(request.args.get('wd', '')).strip()
    novels_keyword = name.split(' ')[0]
    if not name:
        return redirect('/')

    # 通过搜索引擎获取检索结果
    parse_result = None
    if name.startswith('!baidu'):
        novels_keyword = name.split('baidu')[1].strip()
        novels_name = 'intitle:{name} 小说 阅读'.format(name=novels_keyword)
        parse_result = await get_novels_info(class_name='baidu', novels_name=novels_name)
        print(parse_result)
    else:
        for each_engine in ENGINE_PRIORITY:
            # for bing
            if each_engine == "bing":
                novels_name = "{name} 小说 阅读 最新章节".format(name=name)
                parse_result = await get_novels_info(class_name='bing', novels_name=novels_name)
                if parse_result:
                    break
            # for 360 so
            if each_engine == "360":
                novels_name = "{name} 小说 最新章节".format(name=name)
                parse_result = await get_novels_info(class_name='so', novels_name=novels_name)
                if parse_result:
                    break
            # for baidu
            if each_engine == "baidu":
                novels_name = 'intitle:{name} 小说 阅读'.format(name=name)
                parse_result = await get_novels_info(class_name='baidu', novels_name=novels_name)
                if parse_result:
                    break
            # for duckduckgo
            if each_engine == "duck_go":
                novels_name = '{name} 小说 阅读 最新章节'.format(name=name)
                parse_result = await get_novels_info(class_name='duck_go', novels_name=novels_name)
                if parse_result:
                    break
    if parse_result:
        result_sorted = sorted(
            parse_result,
            reverse=True,
            key=itemgetter('is_recommend', 'is_parse', 'timestamp'))
        user = request['session'].get('user', None)
        if user:
            return template(
                '/novels/result.html',
                is_login=1,
                user=user,
                name=novels_keyword,
                time='%.2f' % (time.time() - start),
                result=result_sorted,
                count=len(parse_result))
        else:
            return template(
                '/novels/result.html',
                is_login=0,
                name=novels_keyword,
                time='%.2f' % (time.time() - start),
                result=result_sorted,
                count=len(parse_result))
    else:
        return html("No Result！请将小说名反馈给本站，谢谢！")