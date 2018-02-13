from flask import render_template, flash, redirect, url_for, request, current_app
from . import main
from ..decorators import admin_required,permission_required
from ..models import PERMISSION, User, Post, AnonymousUser, AnonymousUserMixin
from flask_login import login_required,current_user
from .forms import EditProfileForm,EditProfileAdminForm,PostForm
from ..models import db,Role

@main.route('/', methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(PERMISSION.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_AGE'],
        error_out=False
    )
    posts = pagination.items
    #posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


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

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user, posts=posts)

@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)

@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user=User.query.get_or_404(id)
    form=EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email=form.email.data
        user.username=form.username.data
        user.role=Role.query.get(form.role.data)
        user.name=form.name.data
        user.location=form.location.data
        user.about_me=form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('Admin profile has been updated.')
        return redirect(url_for('.user',username=user.username))
    form.email.data=user.username
    form.username.data=user.username
    form.role.data=user.role_id
    form.name.data=user.name
    form.location.data=user.location
    form.about_me.data=user.about_me
    return render_template('edit_profile.html',form=form,user=user)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])
