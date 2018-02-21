from flask import render_template, flash, redirect, url_for, request, current_app, abort
from . import main
from ..decorators import admin_required,permission_required
from ..models import PERMISSION, User, Post, AnonymousUser, AnonymousUserMixin, Comment
from flask_login import login_required,current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,CommentForm
from ..models import db,Role

@main.route('/', methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(PERMISSION.WRITE) and form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user._get_current_object())
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

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // current_app.config['FLASKY_COMMENTS_PER_PAGE']+1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(PERMISSION.ADMIN):
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('This post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/delete_posts/<int:id>')
@login_required
def delete_post(id):
    if current_user.can(PERMISSION.ADMIN):
        authorid = Post.query.filter_by(id=id).first().author_id
        user = User.query.filter_by(id=authorid).first()
        post = Post.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
        return request.args.get('next') or redirect(url_for('.user', username=user.username))

# @main.route('post/<int:id>/delete')
# @login_required
# def delete_post(id):
#     form = PostForm
#     post = Post.query.get_or_404(id)
#     if current_user.can(PERMISSION.ADMIN):
#         db.session.delete(post)
#         db.session.commit()
#         flash('This post has been deleted.')
