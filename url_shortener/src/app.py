from flask import Flask, redirect, abort
from sqlalchemy.orm import scoped_session, sessionmaker
from database import engine, URL


app = Flask(__name__)
Session = scoped_session(sessionmaker(bind=engine))

@app.route('/<short_code>')
def redirect_to_url(short_code):
    session = Session()
    try:
        url = session.query(URL).filter_by(short_code=short_code).first()
        
        if not url:
            return "Error 404: Short URL not found", 404
        
        if url.clicks is None:
            url.clicks = 1
        else:
            url.clicks += 1
            
        session.commit()
        
        original_url = url.original_url
        
        return redirect(original_url, code=302)
        
    except Exception as e:
        session.rollback()
        app.logger.error(f"Error redirecting for short_code '{short_code}': {str(e)}")
        abort(500, description="Internal server error")
    finally:
        Session.remove()

@app.errorhandler(404)
def not_found_error(error):
    return f"Error 404: {error.description}", 404

@app.errorhandler(500)
def internal_error(error):
    return f"Error 500: {error.description}", 500

if __name__ == '__main__':
    app.run(debug=True)