import os
from flask import Flask, render_template
from config import config_by_name
from db import db

# Blueprint imports
from profile import profile_bp
from career import career_bp
from education import education_bp
from opportunities import opportunities_bp
from eligibility import eligibility_bp
from skill_gap import skill_gap_bp
from planner import planner_bp
from notifications import notifications_bp
from agents import agents_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'dev')
    
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['dev']))

    # Initialize shared database
    db.init_app(app)

    # Register modular blueprints
    app.register_blueprint(profile_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(education_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(eligibility_bp)
    app.register_blueprint(skill_gap_bp)
    app.register_blueprint(planner_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(agents_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    # Direct User-Facing Route for Student Profile UI (Member 2)
    from profile.routes import profile_ui
    app.add_url_rule('/profile', 'profile_root', profile_ui, methods=['GET'])
    app.add_url_rule('/profile/<int:profile_id>', 'profile_view', profile_ui, methods=['GET'])

    # Direct User-Facing Route for Career Guidance Dashboard (Member 2)
    from career.routes import career_guidance_dashboard
    app.add_url_rule('/career/guidance', 'career_guidance_root', career_guidance_dashboard, methods=['GET'])
    app.add_url_rule('/career/guidance/<int:profile_id>', 'career_guidance_view', career_guidance_dashboard, methods=['GET'])

    # Direct User-Facing Route for Education Pathways Dashboard (Member 2)
    from education.routes import education_pathways_dashboard
    app.add_url_rule('/education/pathways', 'education_pathways_root', education_pathways_dashboard, methods=['GET'])
    app.add_url_rule('/education/pathways/<int:profile_id>', 'education_pathways_view', education_pathways_dashboard, methods=['GET'])

    # Create database schema within app context
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
