from flask import render_template
from myproject import app, db
from sqlalchemy import exc

@app.errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404

@app.errorhandler(exc.IntegrityError)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500