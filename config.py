import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    POSTS_PER_PAGE = 10
    THREADS_PER_PAGE = 10
    USERS_PER_PAGE = 10
    REPORTS_PER_PAGE = 10
    MAX_CONTENT_LENGTH = 1024 * 1024
