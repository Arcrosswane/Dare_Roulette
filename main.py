from flask import Flask, render_template, redirect, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_UsEkXiG68OIx@ep-square-wildflower-ahpyz2xf-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
app.config['SECRET_KEY'] = 'arcrosswane1212'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"   
    id = db.Column(db.Integer(), primary_key=True)
    userName = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    videos = db.relationship("Video", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "userName": self.userName,
            "email": self.email
        }

class Dare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    videos = db.relationship("Video", backref="dare", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "difficulty": self.difficulty
        }

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    dare_id = db.Column(db.Integer, db.ForeignKey("dare.id"), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activities = db.relationship("UserVideoActivity", backref="video", lazy=True)
    
    def to_dict(self):
        # Check if current user has liked this video
        liked = False
        if session.get('id'):
            activity = UserVideoActivity.query.filter_by(
                video_id=self.id,
                user_id=session.get('id')
            ).first()
            if activity:
                liked = activity.like
        
        return {
            "id": self.id,
            "user_id": self.user_id,
            "dare_id": self.dare_id,
            "video_url": self.video_url,
            "likes": self.likes,
            "views": self.views,
            "score": self.score,
            "created_at": self.created_at,
            "liked": liked
        }

class UserVideoActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    watch_time = db.Column(db.Integer)
    like = db.Column(db.Boolean, default=False)
    watched = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_videos(limit=5, offset=0):
    """Get videos with pagination support"""
    seen_ids = session.get('seen_videos', [])
    
    # Get top-score videos not yet seen
    videos = (
        Video.query\
        .filter(~Video.id.in_(seen_ids) if seen_ids else True)\
        .order_by(Video.score.desc(), Video.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()
    )
    
    # If we've exhausted all videos, reset and start over
    if not videos and seen_ids:
        session['seen_videos'] = []
        videos = (
            Video.query\
            .order_by(func.random())\
            .offset(0)\
            .limit(limit)\
            .all()
        )
    
    # Mark as seen
    for v in videos:
        if v.id not in seen_ids:
            seen_ids.append(v.id)
    
    session['seen_videos'] = seen_ids
    session.modified = True
    
    return videos

def format_num(num):
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

def calculate_score(video):
    hours = (datetime.utcnow() - video.created_at).total_seconds() / 3600
    freshness = max(0, 48 - hours)
    score = (
        video.likes * 3 +
        video.views * 0.5 +
        freshness
    )
    return round(score, 2)

@app.route("/")
def index():
    if session.get('id', None) != None:
        return redirect('/dashboard')
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        bio = request.form.get('Bio')
        
        if username and email and password:
            user = User(userName=username, email=email, bio=bio, 
                       password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=16))
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    
    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = None
        email = request.form.get("email")
        password = request.form.get("password").strip()
        
        if not ('@' in email and '.' in email):
            username = email
        
        if email and password:
            if username != None:
                user = User.query.filter_by(userName=username).first()
                if user and check_password_hash(user.password, password):
                    session['id'] = user.id
                    return redirect('/dashboard')
            else:
                user = User.query.filter_by(email=email).first()
                if user and check_password_hash(user.password, password):
                    session['id'] = user.id
                    return redirect('/dashboard')
            return redirect('/login')
    
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    id = session.get('id', None)
    if id != None:
        user = User.query.filter_by(id=id).first()
        users = []
        dares_l = []
        
        for per in User.query.all():
            videos = Video.query.filter_by(user_id=per.id).all()
            likes = 0
            views = 0
            dares = 0
            user_entry = {
                'user_id': per.id,
                'user_data': []
            }
            
            for vid in videos:
                likes += vid.likes
                views += vid.views
                if vid.dare_id:
                    dares += 1
                    user_entry['user_data'].append({
                        'dare': Dare.query.get(vid.dare_id).to_dict(),
                        'vid': vid.to_dict()
                    })
            
            dares_l.append(user_entry)

            dares_from_DB = []
            for dare in Dare.query.all():
                dares_from_DB.append(dare.text)
            
            users.append({
                'id': per.id,
                'username': per.userName,
                'bio': per.bio if per.bio else 'N/A',
                'likes': format_num(likes),
                'views': format_num(views),
                'dares': format_num(dares),
                'dares_l': dares_l,
                'avatar': per.userName[0],
                'short_bio': per.bio[:15] if per.bio else 'N/A'
            })
        
        user_data = next((u for u in users if u["username"] == user.userName), None)
        session.setdefault('seen_videos', [])
        return render_template("dashboard.html", user=user_data, users=users, dares_from_DB=dares_from_DB)
    
    return redirect('/login')

# API Endpoints

@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    if request.method == 'POST':
        temp = request.json
        url = temp.get('url')
        dare_text = temp.get('dare_text')
        
        video = Video(
            user_id=session.get('id'),
            dare_id=Dare.query.filter_by(text=dare_text).first().id,
            video_url=url
        )
        db.session.add(video)
        db.session.commit()
        return {'status': 'OK'}

@app.route('/api/get-videos', methods=['POST'])
def give_videos():
    """Get videos with pagination support"""
    if request.method == 'POST':
        offset = request.json.get('offset', 0)
        limit = request.json.get('limit', 5)
        
        videos = get_videos(limit=limit, offset=offset)
        
        feed = []
        for ved in videos:
            feed.append({
                'video': ved.to_dict(),
                'user': User.query.filter_by(id=ved.user_id).first().to_dict(),
                'dare': Dare.query.filter_by(id=ved.dare_id).first().to_dict()
            })
        
        return jsonify(feed)

@app.route('/api/like', methods=['POST'])
def like_post():
    user_id = session.get('id')
    if not user_id:
        return {'error': 'Not logged in'}, 401
    
    vid_id = request.json.get('post_id')
    video = Video.query.get(vid_id)
    
    if not video:
        return {'error': 'Video not found'}, 404
    
    if video.user_id == user_id:
        return {'error': 'Owner cannot like'}, 403
    
    # Check if user already has activity for this video
    activity = UserVideoActivity.query.filter_by(
        video_id=vid_id,
        user_id=user_id
    ).first()
    
    if not activity:
        activity = UserVideoActivity(video_id=vid_id, user_id=user_id)
        db.session.add(activity)
    
    # Toggle like
    if activity.like:
        activity.like = False
        video.likes = max(0, video.likes - 1)
        liked = False
    else:
        activity.like = True
        video.likes += 1
        liked = True
    
    video.score = calculate_score(video)
    db.session.commit()
    
    return {
        'liked': liked,
        'likes': video.likes
    }

@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect('/login')

@app.route('/api/video-watched', methods=['POST'])
def increase_views():
    if request.method == 'POST':
        temp = request.json
        vid_id = temp.get('video_id').replace('video-', '')
        
        try:
            vid = Video.query.filter_by(id=int(vid_id)).first()
            if vid:
                vid.views += 1
                vid.score = calculate_score(vid)
                db.session.commit()
        except:
            pass
        
        return {'status': 'OK'}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)

