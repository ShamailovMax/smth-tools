from flask import Flask, redirect, abort, request, jsonify
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError

from database import engine, URL

import random
import string
import re


app = Flask(__name__)
Session = scoped_session(sessionmaker(bind=engine))

def generate_short_code(length=6):
    """Generates short code for URL"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def is_valid_url(url):
    """Checks URL if invalid"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Creates short URL with the generaed code"""
    session = Session()
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        original_url = data.get('url')
        if not original_url:
            return jsonify({"error": "URL is required"}), 400
        
        if not is_valid_url(original_url):
            return jsonify({"error": "Invalid URL format"}), 400
        
        existing = session.query(URL).filter_by(original_url=original_url).first()
        if existing:
            return jsonify({
                "short_url": f"http://localhost:5000/{existing.short_code}",
                "original_url": original_url,
                "existing": True
            })
        
        attempts = 0
        max_attempts = 10
        short_code = None
        
        while attempts < max_attempts:
            short_code = generate_short_code()
            if not session.query(URL).filter_by(short_code=short_code).first():
                break
            attempts += 1
        
        if attempts >= max_attempts:
            return jsonify({"error": "Failed to generate unique short code"}), 500
        
        new_url = URL(original_url=original_url, short_code=short_code)
        session.add(new_url)
        session.commit()
        
        return jsonify({
            "short_url": f"http://localhost:5000/{short_code}",
            "original_url": original_url,
            "existing": False
        }), 201
        
    except IntegrityError:
        # processing short_code duplication case
        session.rollback()
        app.logger.error("IntegrityError: short_code collision detected")
        return jsonify({"error": "Failed to create short URL, please try again"}), 500
        
    except Exception as e:
        session.rollback()
        app.logger.error(f"Error creating short URL: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
        
    finally:
        Session.remove()

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
        return "Error 500: Internal server error", 500
        
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