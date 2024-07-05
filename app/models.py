import os.path
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime(),
                                                                default=lambda: datetime.now(timezone.utc))
    joined: so.Mapped[datetime] = so.mapped_column(sa.DateTime(), default=lambda: datetime.now(timezone.utc))
    admin: so.Mapped[bool] = so.mapped_column(sa.Boolean(), default=False)
    posts: so.WriteOnlyMapped['Post'] = so.relationship('Post',
                                                        back_populates='author',
                                                        passive_deletes=True)
    threads: so.WriteOnlyMapped['Thread'] = so.relationship('Thread',
                                                            back_populates='user',
                                                            passive_deletes=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        filepath = os.path.join(f'app/static/img/avatars/{self.id}.png')
        if os.path.isfile(filepath):
            return url_for('static', filename=f'img/avatars/{self.id}.png')
        return url_for('static', filename='img/avatars/default_avatar.png')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Thread(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(100))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id, ondelete='CASCADE'), index=True)
    user: so.Mapped[User] = so.relationship('User', back_populates='threads')
    posts: so.WriteOnlyMapped['Post'] = so.relationship('Post',
                                                        back_populates='thread',
                                                        passive_deletes=True)

    def posts_count(self):
        query = sa.select(sa.func.count()).select_from(self.posts.select().subquery())
        return db.session.scalar(query)

    def last_post(self):
        query = self.posts.select().order_by(Post.timestamp.desc())
        return db.session.scalar(query)

    def __repr__(self):
        return '<Thread {}>'.format(self.title)


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(1_000))
    body_raw: so.Mapped[str] = so.mapped_column(sa.String(1_000))
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime(), index=True,
                                                      default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id, ondelete='CASCADE'), index=True)
    thread_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Thread.id, ondelete='CASCADE'), index=True)
    author: so.Mapped[User] = so.relationship('User', back_populates='posts')
    thread: so.Mapped[Thread] = so.relationship('Thread', back_populates='posts')
    reports: so.WriteOnlyMapped['Report'] = so.relationship('Report',
                                                            back_populates='post',
                                                            passive_deletes=True)

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Report(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    reason: so.Mapped[str] = so.mapped_column(sa.String(1_000))
    post_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Post.id, ondelete='CASCADE'), index=True)
    post: so.Mapped[Post] = so.relationship('Post', back_populates='reports')

    def __repr__(self):
        return '<Report {}>'.format(self.reason)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
