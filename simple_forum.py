import sqlalchemy as sa
import sqlalchemy.orm as so

from app import create_app, db
from app.models import User, Post

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.filter_by(admin=True).first():
        admin = User(username='admin', email='admin@simple-forum.com', admin=True)
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}
