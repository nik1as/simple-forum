from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ThreadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    body = PageDownField('Post', validators=[Length(min=1, max=1000)])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    body = PageDownField('Post', validators=[Length(min=1, max=1000)])
    submit = SubmitField('Submit')


class DeletePostForm(FlaskForm):
    submit = SubmitField('Delete')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')


class ReportForm(FlaskForm):
    reason = StringField('Reason', validators=[Length(min=1, max=1000)])
    submit = SubmitField('Submit')
