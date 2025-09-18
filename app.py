from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import random
import smtplib
import ssl
from otp_config import EMAIL_ADDRESS, EMAIL_PASSWORD
# import google.generativeai as genai

# Add your Gemini API key here
# genai.configure(api_key="YOUR_GEMINI_API_KEY")

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Initialize DB
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    
    # Add user_details table for additional profile information
    c.execute('''CREATE TABLE IF NOT EXISTS user_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        grade TEXT,
        school TEXT,
        interests TEXT,
        language TEXT,
        bio TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

def add_avatar_column():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Add avatar column if it doesn't exist
    c.execute("PRAGMA table_info(user_details)")
    columns = [col[1] for col in c.fetchall()]
    if 'avatar' not in columns:
        c.execute("ALTER TABLE user_details ADD COLUMN avatar TEXT")
        conn.commit()
    conn.close()

add_avatar_column()

# Send OTP Email
def send_otp(email):
    otp = str(random.randint(100000, 999999))
    
    # Professional HTML email template
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VidyAI++ OTP Verification</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa; line-height: 1.6;">
        <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f7fa; padding: 20px 0;">
            <tr>
                <td align="center">
                    <table cellpadding="0" cellspacing="0" width="600" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 40px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; letter-spacing: -0.5px;">
                                    VidyAI++
                                </h1>
                                <p style="color: #ffffff; margin: 8px 0 0 0; font-size: 16px; opacity: 0.9;">
                                    Secure Access Verification
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Main Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="color: #2d3748; margin: 0 0 20px 0; font-size: 24px; font-weight: 600;">
                                    Your One-Time Password
                                </h2>
                                
                                <p style="color: #4a5568; margin: 0 0 25px 0; font-size: 16px;">
                                    Hello there,
                                </p>
                                
                                <p style="color: #4a5568; margin: 0 0 30px 0; font-size: 16px;">
                                    We've generated a secure One-Time Password (OTP) for your VidyAI++ account access. Please use the code below to complete your authentication:
                                </p>
                                
                                <!-- OTP Code Box -->
                                <table cellpadding="0" cellspacing="0" width="100%" style="margin: 30px 0;">
                                    <tr>
                                        <td align="center">
                                            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px 40px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);">
                                                <span style="color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: 4px; font-family: 'Courier New', monospace;">
                                                    {otp}
                                                </span>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #4a5568; margin: 30px 0 20px 0; font-size: 16px;">
                                    This code is valid for the next <strong>10 minutes</strong> and can only be used once.
                                </p>
                                
                                <!-- Security Notice -->
                                <div style="background-color: #fef5e7; border-left: 4px solid #f6ad55; padding: 20px; border-radius: 0 8px 8px 0; margin: 25px 0;">
                                    <h3 style="color: #c05621; margin: 0 0 10px 0; font-size: 16px; font-weight: 600;">
                                        🔒 Security Notice
                                    </h3>
                                    <p style="color: #744210; margin: 0; font-size: 14px;">
                                        For your security, never share this OTP with anyone. If you didn't request this code, please ignore this email and consider changing your account password.
                                    </p>
                                </div>
                                
                                <p style="color: #4a5568; margin: 25px 0 0 0; font-size: 16px;">
                                    Thank you for using VidyAI++!
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f7fafc; padding: 30px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="color: #718096; margin: 0 0 10px 0; font-size: 14px;">
                                    Best regards,<br>
                                    <strong>The VidyAI++ Team</strong>
                                </p>
                                
                                <div style="margin: 20px 0 0 0;">
                                    <p style="color: #a0aec0; margin: 0; font-size: 12px;">
                                        This is an automated message. Please do not reply to this email.
                                    </p>
                                    <p style="color: #a0aec0; margin: 5px 0 0 0; font-size: 12px;">
                                        © 2024 VidyAI++. All rights reserved.
                                    </p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Create message with HTML content
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "🔐 Your VidyAI++ Verification Code"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    
    # Create HTML part
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
    
    return otp

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/profile')
def profile():
    # Check if user is logged in
    if 'user' not in session:
        return redirect('/login')
    
    # Assuming you have a user_id from session or authentication
    user_id = session.get('user_id')
    
    # Query the database for user details
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    c = conn.cursor()
    
    # Query user details
    c.execute('SELECT * FROM user_details WHERE user_id = ?', (user_id,))
    user_details = c.fetchone()
    
    # If no details exist yet, provide an empty dict with default values
    if not user_details:
        user_details = {
            'bio': '',
            'grade': '',
            'school': '',
            'interests': '',
            'language': ''
        }
    else:
        # Convert Row object to dict
        user_details = dict(user_details)
    
    conn.close()
    
    return render_template('profile.html', user_details=user_details)

@app.route('/relatedvideos')
def relatedvideos():
    if 'user' not in session:
        return redirect('/login')
    return render_template('relatedvideos.html')


@app.route('/resetpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        if user:
            # Generate a random password
            new_password = str(random.randint(10000000, 99999999))
            # Update password in DB
            c.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
            conn.commit()
            # Send new password via email
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        background: #f7fafc;
                        color: #2d3748;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        background: #fff;
                        border-radius: 10px;
                        box-shadow: 0 2px 8px rgba(44,62,80,0.08);
                        padding: 2rem;
                        max-width: 500px;
                        margin: 2rem auto;
                    }}
                    .header {{
                        font-size: 1.3rem;
                        color: #34558e;
                        margin-bottom: 1rem;
                        font-weight: bold;
                    }}
                    .password-box {{
                        background: #f7fafc;
                        border: 1px solid #4299e1;
                        color: #34558e;
                        font-size: 1.2rem;
                        padding: 0.75rem 1rem;
                        border-radius: 6px;
                        margin: 1rem 0;
                        text-align: center;
                        font-weight: bold;
                        letter-spacing: 2px;
                    }}
                    .footer {{
                        margin-top: 2rem;
                        font-size: 0.95rem;
                        color: #4a5568;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">VidyaAI++ Password Reset</div>
                    <p>Dear User,</p>
                    <p>Your password has been reset. Please use the new password below to log in:</p>
                    <div class="password-box">{new_password}</div>
                    <p>For security, please change your password after logging in.</p>
                    <div class="footer">
                        If you did not request this reset, please contact our support team.<br>
                        Thank you,<br>
                        <b>VidyaAI++ Team</b>
                    </div>
                </div>
            </body>
            </html>
            """
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(
                    EMAIL_ADDRESS,
                    email,
                    f"Subject: VidyaAI++ Password Reset\nContent-Type: text/html\n\n{html_content}"
                )
            flash('A new password has been sent to your email.', 'success')
        else:
            flash('Email not found. Please check and try again.', 'error')
        conn.close()
        return render_template('forgot-password.html', reset_sent=True)
    return render_template('forgot-password.html', reset_sent=False)

@app.route('/update-password', methods=['POST'])
def update_password():
    if 'user' not in session:
        return redirect('/login')
    user_id = session['user'][0]
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE id=?", (user_id,))
    current_password = c.fetchone()[0]

    if old_password != current_password:
        flash('Old password is incorrect.', 'error')
    elif new_password != confirm_password:
        flash('New passwords do not match.', 'error')
    else:
        c.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
        conn.commit()
        flash('Password updated successfully!', 'success')
    conn.close()
    return redirect('/profile')

@app.route('/mentors')
def mentors():
    if 'user' not in session:
        return redirect('/login')
    return render_template('mentors.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect('/signup')

        otp = send_otp(email)
        session['temp_user'] = {
            'name': name,
            'email': email,
            'password': password,
            'role': role
        }
        session['otp'] = otp
        return render_template('verify.html')

    return render_template('signup.html')

@app.route('/Home')
def Home():
    return render_template('Home.html')


@app.route("/contactus", methods=["GET", "POST"])
def contactus():
    if 'user' not in session:
        return redirect('/login')
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        # Here you could save or handle the message (like saving to DB, sending email, etc.)
        return render_template("contactus.html", success=True)
    return render_template("contactus.html", success=False)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == session.get('otp'):
            user = session.get('temp_user')
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                          (user['name'], user['email'], user['password'], user['role']))
                user_id = c.lastrowid
                # Initialize empty user details
                c.execute("INSERT INTO user_details (user_id, grade, school, interests, language, bio) VALUES (?, ?, ?, ?, ?, ?)",
                          (user_id, '', '', '', 'English', ''))
                conn.commit()
                flash("Account created successfully!",'success')
            except sqlite3.IntegrityError:
                flash("Email already exists.")
                return redirect('/signup')
            finally:
                conn.close()
                session.pop('temp_user', None)
                session.pop('otp', None)
            return redirect('/login')
        else:
            flash("Invalid OTP",'error')
            return render_template('verify.html')
    return redirect('/signup')


@app.route('/aboutus')
def aboutus():
    if 'user' not in session:
        return redirect('/login')
    return render_template('aboutus.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user
            session['user_id'] = user[0]  # Store user_id separately for convenience
            return redirect('/Home')
        else:
            flash("Invalid email or password", 'error')
            return redirect('/login')
    return render_template('login.html')

   
@app.route('/main')
def main_page():
    if 'user' in session:
        return redirect('/Home')
    else:
        return redirect('/login')



@app.route('/edit-profile')
def edit_profile():
    if 'user' not in session:
        return redirect('/login')
    
    user_id = session['user'][0]
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get user details
    c.execute("SELECT * FROM user_details WHERE user_id=?", (user_id,))
    user_details = c.fetchone()
    
    conn.close()
    
    return render_template('edit_profile.html', user_details=user_details)

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/remove-avatar', methods=['POST'])
def remove_avatar():
    if 'user' not in session:
        return redirect('/login')
    user_id = session['user'][0]
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Get current avatar filename
    c.execute("SELECT avatar FROM user_details WHERE user_id=?", (user_id,))
    avatar = c.fetchone()
    if avatar and avatar[0]:
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], avatar[0])
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
        c.execute("UPDATE user_details SET avatar=NULL WHERE user_id=?", (user_id,))
        conn.commit()
        flash('Profile photo removed.', 'success')
    else:
        flash('No profile photo to remove.', 'info')
    conn.close()
    return redirect('/profile')

@app.route('/update-avatar', methods=['POST'])
def update_avatar():
    if 'user' not in session:
        return redirect('/login')
    user_id = session['user'][0]
    avatar_filename = None
    if 'avatar' in request.files:
        avatar = request.files['avatar']
        if avatar and allowed_file(avatar.filename):
            avatar_filename = secure_filename(f"user_{user_id}_" + avatar.filename)
            avatar_folder = app.config['UPLOAD_FOLDER']
            os.makedirs(avatar_folder, exist_ok=True)
            avatar.save(os.path.join(avatar_folder, avatar_filename))
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("UPDATE user_details SET avatar=? WHERE user_id=?", (avatar_filename, user_id))
            conn.commit()
            conn.close()
            flash('Profile photo updated!', 'success')
    return redirect('/profile')

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect('/login')
    user_id = session['user'][0]
    name = request.form['name']
    grade = request.form['grade']
    school = request.form['school']
    interests = request.form['interests']
    language = request.form['language']
    bio = request.form['bio']

    avatar_filename = None
    if 'avatar' in request.files:
        avatar = request.files['avatar']
        if avatar and allowed_file(avatar.filename):
            avatar_filename = secure_filename(f"user_{user_id}_" + avatar.filename)
            avatar_folder = app.config['UPLOAD_FOLDER']
            # Ensure the folder exists
            os.makedirs(avatar_folder, exist_ok=True)
            avatar.save(os.path.join(avatar_folder, avatar_filename))
    # ...rest of your code...
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Update avatar if uploaded
    if avatar_filename:
        c.execute("""UPDATE user_details SET grade=?, school=?, interests=?, language=?, bio=?, avatar=? WHERE user_id=?""",
                  (grade, school, interests, language, bio, avatar_filename, user_id))
    else:
        c.execute("""UPDATE user_details SET grade=?, school=?, interests=?, language=?, bio=? WHERE user_id=?""",
                  (grade, school, interests, language, bio, user_id))
    conn.commit()
    conn.close()
    flash('Profile updated successfully!', 'success')
    return redirect('/profile')

import google.generativeai as genai

# Add your Gemini API key here
genai.configure(api_key="AIzaSyALi92q0k7AgzG82nefkAkvjSmS8WmIkGM")

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_message = data.get('message', '')
    language = data.get('language', 'English')
    # Gemini prompt: restrict to educational content and use selected language
    system_prompt = (
        f"You are an educational assistant. Only answer questions related to educational topics. "
        f"Respond in {language}. If the user asks something not related to education, politely refuse."
    )
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([{"role": "user", "parts": [system_prompt + "\n" + user_message]}])
    reply = response.text.strip() if hasattr(response, 'text') else "Sorry, I couldn't get a response."
    return jsonify({'reply': reply})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    import json
    import re
    data = request.get_json()
    topic = data.get('topic', 'General Knowledge')
    difficulty = data.get('difficulty', 'Easy')
    language = data.get('language', 'English')
    num_questions = int(data.get('num_questions', 5))

    prompt = (
        f"Generate a {difficulty} level quiz with {num_questions} multiple-choice questions on the topic '{topic}'. "
        f"Respond in {language}. "
        f"Return ONLY the quiz as a JSON array with each question as an object: "
        f"{{'text': 'Question text', 'options': ['A', 'B', 'C', 'D'], 'answer': 'A'}}. "
        f"Do not include explanations, greetings, or any extra text. Only output the JSON array."
    )

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([{"role": "user", "parts": [prompt]}])
    print("Gemini raw response:", response.text)  # For debugging

    # Try to extract JSON array from the response robustly
    try:
        # Try direct JSON parse
        quiz_json = json.loads(response.text)
        return jsonify({'questions': quiz_json})
    except Exception:
        # Try to extract the first JSON array in the text
        match = re.search(r'(\[\s*{.*?}\s*\])', response.text, re.DOTALL)
        if match:
            try:
                quiz_json = json.loads(match.group(1))
                return jsonify({'questions': quiz_json})
            except Exception as e:
                print("JSON extraction error:", e)
        # If all fails, return error
        return jsonify({'questions': [], 'error': 'Quiz generation failed. Please try again or try a different topic.'})

if __name__ == '__main__':
    app.run(debug=True)
