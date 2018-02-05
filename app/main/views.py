from flask import render_template
from . import main
from ..decorators import admin_required,permission_required
from ..models import PERMISSION
from flask_login import login_required

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'For adminstretors!'

@main.route('/moderator')
@login_required
@permission_required(PERMISSION.MODERATE)
def for_moderators_only():
    return 'For comment moderators!'

