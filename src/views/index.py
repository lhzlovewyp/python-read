
from sanic import Blueprint

from src.utils.tools import template

index_bp = Blueprint('index_blueprint')

@index_bp.route("/")
async def index(request):
    print(request)
    user = request['session'].get('user',None)
    novels_head = ['#', '小说名', '搜索次数']
    first_type_title = "搜索排行"
    first_type = []
    #search_ranking = await cache_owllook_search_ranking()
    return template('/md/index.html')


