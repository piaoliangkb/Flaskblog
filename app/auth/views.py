from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,login_required,logout_user,current_user
from . import auth
from ..models import User
from .forms import LoginForm,ChangePasswordForm,RegistrationForm
from .. import db

@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        #filter_by=where
        #filter也可用
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html',form=form)

@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,
                  username=form.username.data,
                  password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can login now')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You hava been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated user are allowed!'

@auth.route('/changepassword',methods=['GET','POST'])
@login_required
def change_password():
    form=ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password=form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('You password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template('auth/changepassword.html',form=form)