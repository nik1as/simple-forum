from datetime import datetime, timezone

import markdown
import nh3
import sqlalchemy as sa
from flask import redirect, render_template, request, url_for, current_app, flash
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import PostForm, ThreadForm, ReportForm, DeletePostForm
from app.models import User, Post, Thread, Report

md = markdown.Markdown(extensions=['mdx_math'],
                       extension_configs={
                           'mdx-math': {'enable_dollar_delimiter': True}
                       })


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/explore')
@bp.route('/index')
@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)

    threads_query = sa.select(Thread)
    page = db.paginate(threads_query, page=page, per_page=current_app.config['THREADS_PER_PAGE'], error_out=True)

    return render_template('index.html', title='Home', page=page)


@bp.route('/new_thread', methods=['GET', 'POST'])
@login_required
def new_thread():
    form = ThreadForm()
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, user_id=current_user.id)
        db.session.add(thread)
        db.session.commit()

        raw = form.body.data
        text = markdown_to_html(raw)
        post = Post(body=text, body_raw=raw, user_id=current_user.id, thread_id=thread.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.thread', id=thread.id))
    return render_template('new_thread.html', title='New Thread', form=form)


@bp.route('/thread/<int:id>/', methods=['GET'])
def thread(id):
    page = request.args.get('page', 1, type=int)
    thread = db.first_or_404(sa.select(Thread).where(Thread.id == id))
    posts_query = sa.select(Post).where(Post.thread_id == id).order_by(Post.timestamp.desc())
    page = db.paginate(posts_query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=True)

    form = PostForm()

    return render_template('thread.html', title=thread.title,
                           thread=thread,
                           form=form,
                           page=page)


@bp.route('/user/<username>/', methods=['GET'])
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user.html', user=user)


@bp.route('/search', methods=['GET'])
def search():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '', type=str)

    keywords = query.split(' ')
    keyword_filters = [Thread.title.ilike(f'%{k}%') for k in keywords]
    threads_query = sa.select(Thread).where(sa.and_(*keyword_filters))
    page = db.paginate(threads_query, page=page, per_page=current_app.config['THREADS_PER_PAGE'], error_out=True)

    return render_template('search.html', title='Search', query=query, page=page)


@bp.route('/post/add/<int:thread>/', methods=['POST'])
@login_required
def new_post(thread):
    form = PostForm()

    if form.validate_on_submit():
        raw = form.body.data
        text = markdown_to_html(raw)
        post = Post(body=text, body_raw=raw, user_id=current_user.id, thread_id=thread)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('main.thread', id=thread))


@bp.route('/post/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)

    if current_user.id != post.author.id:
        flash('You are not authorized to edit that post!')
        return redirect(url_for('main.index'))

    form = PostForm()
    if form.validate_on_submit():
        text = markdown_to_html(form.body.data)
        post.body = text
        post.body_raw = form.body.data

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.thread', id=post.thread_id))
    elif request.method == 'GET':
        form.body.data = post.body_raw
    return render_template('edit_post.html', title='Edit Post', form=form)


@bp.route('/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)
    thread = post_to_delete.thread

    if current_user.id != post_to_delete.author.id and not current_user.admin:
        flash('You are not authorized to delete that post!')
        return redirect(url_for('main.index'))

    form = DeletePostForm()
    if form.validate_on_submit():
        if thread.posts_count() == 1:
            db.session.delete(post_to_delete)
            db.session.delete(thread)
            db.session.commit()
            flash('Post and thread deleted!')
            return redirect(url_for('main.index'))
        else:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post deleted!')
            return redirect(url_for('main.thread', id=thread.id))

    return render_template('delete_post.html', post=post_to_delete, form=form)


@bp.route('/post/report/<int:id>', methods=['GET', 'POST'])
def report(id):
    post = Post.query.get_or_404(id)

    if current_user.is_authenticated and current_user.id == post.author.id:
        flash('You can not report your own post!')
        return redirect(url_for('main.index'))

    form = ReportForm()
    if form.validate_on_submit():
        report = Report(reason=form.reason.data, post_id=id)
        db.session.add(report)
        db.session.commit()

        flash('Post reported!')
        return redirect(url_for('main.index'))
    return render_template('report.html', post=post, form=form)


def markdown_to_html(markdown_text):
    return nh3.clean(md.convert(markdown_text))
