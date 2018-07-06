from jinja2 import Environment, PackageLoader, select_autoescape
from sanic.response import html


def env():
    return Environment(
    loader=PackageLoader('views', '../templates'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env().get_template(tpl)
    return html(template.render(kwargs))