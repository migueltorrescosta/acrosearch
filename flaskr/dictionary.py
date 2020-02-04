from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('dictionary', __name__)


@bp.route('/')
def index():
    db = get_db()
    acronyms = db.execute(
        'SELECT p.id, acronym, description, created, author_id, username'
        ' FROM acronym p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('dictionary/index.html', acronyms=acronyms)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        acronym = request.form['acronym']
        description = request.form['description']
        error = None

        if not acronym:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO acronym (acronym, description, author_id)'
                ' VALUES (?, ?, ?)',
                (acronym, description, g.user['id'])
            )
            db.commit()
            return redirect(url_for('dictionary.index'))

    return render_template('dictionary/create.html')


def get_acronym(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, acronym, description, created, author_id, username'
        ' FROM acronym p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    acronym = get_acronym(id)

    if request.method == 'POST':
        acronym = request.form['acronym']
        description = request.form['description']
        error = None

        if not acronym:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE acronym SET acronym = ?, description = ?'
                ' WHERE id = ?',
                (acronym, description, id)
            )
            db.commit()
            return redirect(url_for('dictionary.index'))

    return render_template('dictionary/update.html', acronym=acronym)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_acronym(id)
    db = get_db()
    db.execute('DELETE FROM acronym WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('dictionary.index'))
