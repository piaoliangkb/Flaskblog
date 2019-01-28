from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import PERMISSION

# 将permission类加入模板上下文
@main.app_context_processor
def inject_permissions():
    return dict(Permission=PERMISSION)
