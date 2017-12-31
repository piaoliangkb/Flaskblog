from flask import render_template,session,redirect,url_for
from .. import db
from . import main
from ..models import User
from .forms import NameForm
from datetime import datetime


@main.route('/')
def index():
    return render_template('index.html')
# @main.route('/',methods=['GET','POST'])
# def index():
#     name = None
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None:
#             user=User(username=form.name.data)
#             db.session.add(user)
#             db.session.commit()
#             session['known']=False
#         else:
#             session['known']=True
#         session['name']=form.name.data
#         return redirect(url_for('main.index'))
#     return render_template('index.html', form=form,
#                            name=session.get('name'),
#                            known=session.get('known',False),
#                            current_time=datetime.utcnow())
