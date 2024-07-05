from functools import wraps

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required

from app import db
from app.admin import bp
from app.models import User, Post, Thread, Report


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated and current_user.admin:
            return f(*args, **kwargs)
        else:
            flash('You need to be an admin to view this page.')
            return redirect(url_for('main.index'))

    return wrap


@bp.route('/dashboard')
@bp.route('/')
@admin_required
@login_required
def dashboard():
    return render_template("admin/admin.html", title='Dashboard')


@bp.route('/users')
@admin_required
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    users_query = sa.select(User).order_by(User.id.asc())
    page = db.paginate(users_query, page=page, per_page=current_app.config['USERS_PER_PAGE'], error_out=True)

    return render_template("admin/users.html", title='Users', page=page)


@bp.route('/statistics')
@admin_required
@login_required
def statistics():
    users_count = db.session.query(User).count()
    posts_count = db.session.query(Post).count()
    threads_count = db.session.query(Thread).count()

    return render_template("admin/statistics.html", title='Statistics',
                           users_count=users_count,
                           posts_count=posts_count,
                           threads_count=threads_count)


@bp.route('/reports')
@admin_required
@login_required
def reports():
    page = request.args.get('page', 1, type=int)

    query = sa.select(Report)
    page = db.paginate(query, page=page, per_page=current_app.config['REPORTS_PER_PAGE'], error_out=True)

    return render_template("admin/reports.html", title='Reports', page=page)
