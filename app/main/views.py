from flask import render_template, flash, redirect, url_for, request, current_app, abort
from . import main
from ..decorators import admin_required, permission_required
from ..models import PERMISSION, User, Post, AnonymousUser, AnonymousUserMixin, Comment
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm, EditPostForm
from ..models import db, Role
import os
from config import Config
from ..extends.boolsearch import BoolSearch
from ..extends.invert import InvertedFile


@main.route('/', methods=['GET', 'POST'])
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
        error_out=False)
    posts = pagination.items
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
    return render_template('user.html', user=user, posts=posts)


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
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.member_since = form.registertime.data
        db.session.add(user)
        db.session.commit()
        flash('Admin profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.registertime.data = user.member_since
    return render_template('edit_profile.html', form=form, user=user)


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
    form = EditPostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        post.timestamp = form.time.data
        db.session.add(post)
        db.session.commit()
        flash('This post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.time.data = post.timestamp
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
        flash("You have deleted this article.")
        return request.args.get('next') or redirect(url_for('.user', username=user.username))


@main.route('/post')
def post_list():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTLISTS_FOR_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('posts_list.html', posts=posts, pagination=pagination, endpoint='.post_list')


@main.route('/webmining', methods = ['POST', 'GET'])
def webmining():
    from ..extends.invert import InvertedFile
    InvertedFile.BuildDocumentIndex()
    InvertedFile.BuildWordIndex()
    #建立文章索引和单词索引
    basedir = Config.BOOLEANSEARCH_PATH
    allfilename = []
    #文章路径list
    with open(basedir + "/documentindex.txt") as file:
        for content in file.readlines():
            filepath = content.split('\t')[1].replace('\n', '')
            allfilename.append(filepath)
    content = {}
    #文章内容list
    for path in allfilename:
        with open(path) as file:
            filename = os.path.split(path)[1]
            #分割路径和文件名
            content[filename] = file.read()
    data = request.args.get('query', None)
    queryresult = {}
    isfound = True
    occurset, isfound = BoolSearch.SearchSingleKeyword(data, isfound)
    if occurset:
        queryresult = BoolSearch.GenerateResultDict(occurset)
    return render_template('webmining.html', content=content, result=queryresult, isfound=isfound)


@main.route('/boolsearch', methods = ['POST', 'GET'])
def boolsearch():
    InvertedFile.BuildDocumentIndex()
    InvertedFile.BuildWordIndex()
    #建立文章索引和单词索引
    basedir = Config.BOOLEANSEARCH_PATH
    allfilename = []
    #文章路径list
    with open(basedir + "/documentindex.txt") as file:
        for content in file.readlines():
            filepath = content.split('\t')[1].replace('\n', '')
            allfilename.append(filepath)
    content = {}
    #文章内容list
    for path in allfilename:
        with open(path) as file:
            filename = os.path.split(path)[1]
            #分割路径和文件名
            content[filename] = file.read()
    query = request.args.get('query', None)
    if query:
        words = query.split()
        for item in words:
            print(item)
    # isfound = True
    # if data is not None:
    #     with open(basedir + "\wordindex.txt") as file:
    #         for line in file.readlines():
    #             if data == line.split('\t')[0]:
    #                 occurset = set(line.split('\t')[1].split())
    #     if not occurset:
    #         isfound = False
    #     else:
    #         with open(basedir + "\documentindex.txt") as file:
    #             for line in file.readlines():
    #                 for i in occurset:
    #                     if i == line.split('\t')[0]:
    #                         resultpath = line.split('\t')[1].replace('\n', '')
    #                         with open(resultpath) as file:
    #                             filename = os.path.split(resultpath)[1]
    #                             queryresult[filename] = file.read()
    #                         occurset.remove(i)
    #                         break
    return render_template('boolsearch.html', content=content)