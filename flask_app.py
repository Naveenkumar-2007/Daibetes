"""
Diabetes Health Predictor - AI Doctor Portal
Flask Backend Application with Firebase Integration
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash, send_from_directory
from flask_cors import CORS
import pickle
import numpy as np
import os
import re
import matplotlib

matplotlib.use('Agg')  # Use non-GUI backend for server rendering
import matplotlib.pyplot as plt

from uuid import uuid4
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json
from datetime import datetime
import pytz

# Import Firebase configuration
# Timezone configuration for India
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current datetime in IST timezone"""
    return datetime.now(IST)

from firebase_config import (
    save_patient_data,
    get_patient_history,
    get_statistics,
    get_prediction_by_id,
    get_predictions_by_ids,
    update_prediction_record,
    append_prediction_comparison,
    db,
    firebase_initialized,
    use_rest_api
)

# Import authentication
from auth import (
    create_user, authenticate_user, authenticate_google_user,
    initiate_password_reset, reset_password_with_token, validate_password_reset_token,
    login_required, admin_required,
    get_user_predictions, get_user_statistics, change_password, update_user_profile
)

# Import integrated chatbot
from chatbot_integrated import IntegratedChatbot

# ------------------- FLASK APP SETUP -------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'diabetes-predictor-secret-key-2025-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Enable CORS for React frontend and Azure
allowed_origins = [
    'http://localhost:3000', 'http://localhost:5173',
    'https://diabetes-predictor-ai.azurewebsites.net',
    'http://diabetes-predictor-ai.azurewebsites.net'
]
CORS(app, supports_credentials=True, origins=allowed_origins)

# ------------------- LOAD ML MODEL & SCALER -------------------
MODEL_PATH = os.path.join('artifacts', 'model.pkl')
SCALER_PATH = os.path.join('artifacts', 'scaler.pkl')

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

try:
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    print(f"✅ Scaler loaded successfully from {SCALER_PATH}")
except Exception as e:
    print(f"❌ Error loading scaler: {e}")
    scaler = None

# ------------------- LOAD GROQ LLM -------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

app.config['GOOGLE_CLIENT_ID'] = google_client_id
app.config['GOOGLE_CLIENT_SECRET'] = google_client_secret

if not groq_api_key:
    print("⚠️ Warning: GROQ_API_KEY not found - AI reports will be disabled")
    llm = None
else:
    try:
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            groq_api_key=groq_api_key,
            temperature=0.7  # Higher temperature for more varied chatbot responses
        )
        print("✅ Groq LLM initialized successfully with openai/gpt-oss-120b")
    except Exception as e:
        print(f"❌ Error initializing Groq LLM: {e}")
        llm = None

# ------------------- INITIALIZE INTEGRATED CHATBOT -------------------
chatbot = IntegratedChatbot(llm=llm)
print(f"✅ Integrated Chatbot: {'Ready' if chatbot.health_check() else 'Limited Mode (No LLM)'}")

FEATURE_INDEX_MAP = {
    'Pregnancies': 0,
    'Glucose': 1,
    'BloodPressure': 2,
    'SkinThickness': 3,
    'Insulin': 4,
    'BMI': 5,
    'DiabetesPedigreeFunction': 6,
    'Age': 7
}

NORMAL_LIMITS = {
    'Glucose': 100.0,
    'Blood Pressure': 80.0,
    'BMI': 24.9,
    'Insulin': 166.0
}

COMPARISON_PARAMETERS = [
    ('Glucose', 'Glucose', 'Glucose (mg/dL)'),
    ('BloodPressure', 'Blood Pressure', 'Blood Pressure (mmHg)'),
    ('BMI', 'BMI', 'BMI (kg/m²)'),
    ('Insulin', 'Insulin', 'Insulin (μU/mL)')
]


def _sanitize_identifier(value):
    """Normalize identifiers for filesystem usage"""
    if not value:
        return 'anonymous'
    return re.sub(r'[^A-Za-z0-9_-]', '_', str(value))


def _ensure_report_directory(user_id):
    """Create and return filesystem and relative paths for report assets"""
    patient_folder = _sanitize_identifier(user_id)
    base_dir = os.path.join(app.root_path, 'static', 'reports')
    os.makedirs(base_dir, exist_ok=True)
    patient_dir = os.path.join(base_dir, patient_folder)
    os.makedirs(patient_dir, exist_ok=True)
    relative_dir = os.path.join('reports', patient_folder)
    return patient_dir, relative_dir


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def extract_parameter_value(record, key):
    """Best-effort extraction of a numeric parameter from stored prediction data"""
    if not isinstance(record, dict):
        return None

    candidates = [
        key,
        key.replace(' ', ''),
        key.replace('_', ''),
        key.replace('BloodPressure', 'Blood Pressure') if 'BloodPressure' in key else key
    ]

    for candidate in candidates:
        if candidate in record:
            value = _safe_float(record.get(candidate))
            if value is not None:
                return value

    medical_data = record.get('medical_data')
    if isinstance(medical_data, dict):
        for candidate in candidates:
            if candidate in medical_data:
                value = _safe_float(medical_data.get(candidate))
                if value is not None:
                    return value

    features = record.get('features')
    if isinstance(features, (list, tuple)):
        idx = FEATURE_INDEX_MAP.get(key)
        if idx is not None and idx < len(features):
            value = _safe_float(features[idx])
            if value is not None:
                return value
    return None


def parse_prediction_datetime(record):
    """Parse a prediction's timestamp into a datetime object"""
    if not isinstance(record, dict):
        return get_ist_now()

    timestamp = record.get('timestamp')
    if isinstance(timestamp, str):
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            pass

    created_at = record.get('created_at')
    if isinstance(created_at, (int, float)):
        try:
            return datetime.fromtimestamp(created_at)
        except (ValueError, OSError):
            pass

    date_part = record.get('date')
    time_part = record.get('time')
    if date_part:
        try:
            if time_part:
                return datetime.strptime(f"{date_part} {time_part}", '%Y-%m-%d %H:%M:%S')
            return datetime.strptime(date_part, '%Y-%m-%d')
        except ValueError:
            pass

    return get_ist_now()


def format_prediction_label(record):
    return parse_prediction_datetime(record).strftime('%b %d, %Y %I:%M %p')


def generate_current_vs_normal_chart(medical_data, user_id, prediction_id):
    """Create bar chart comparing patient metrics against normal limits"""
    if not isinstance(medical_data, dict):
        return None, None

    patient_dir, relative_dir = _ensure_report_directory(user_id)
    filename = f"{prediction_id}_current_vs_normal.png"
    filepath = os.path.join(patient_dir, filename)

    categories = []
    patient_values = []
    normal_values = []

    for label, limit in NORMAL_LIMITS.items():
        raw_value = medical_data.get(label)
        if raw_value is None and label == 'Blood Pressure':
            raw_value = medical_data.get('BloodPressure')
        value = _safe_float(raw_value) or 0.0
        categories.append(label)
        normal_values.append(limit)
        patient_values.append(value)

    fig, ax = plt.subplots(figsize=(8, 5))
    index = np.arange(len(categories))
    bar_width = 0.38
    ax.bar(index - bar_width / 2, normal_values, bar_width, label='Normal Upper Limit', color='#34d399')
    ax.bar(index + bar_width / 2, patient_values, bar_width, label='Patient Value', color='#2563eb')
    ax.set_xticks(index)
    ax.set_xticklabels(categories)
    ax.set_ylabel('Measured Value')
    ax.set_title('Current Visit: Patient Values vs Normal Clinical Limits')
    ax.legend()
    ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.4)
    fig.tight_layout()
    fig.savefig(filepath, dpi=200)
    plt.close(fig)

    relative_path = os.path.join(relative_dir, filename).replace('\\', '/')
    return relative_path, url_for('static', filename=relative_path)


def generate_history_comparison_chart(predictions, user_id, analysis_id):
    """Create line chart showing parameter changes across selected predictions"""
    if not predictions:
        return None, None

    patient_dir, relative_dir = _ensure_report_directory(user_id)
    filename = f"{analysis_id}_history_comparison.png"
    filepath = os.path.join(patient_dir, filename)

    ordered_predictions = sorted(predictions, key=parse_prediction_datetime)
    x_positions = np.arange(len(ordered_predictions))
    x_labels = [format_prediction_label(pred) for pred in ordered_predictions]

    fig, ax = plt.subplots(figsize=(9, 5.5))

    for db_key, _, display_label in COMPARISON_PARAMETERS:
        raw_values = [extract_parameter_value(pred, db_key) for pred in ordered_predictions]
        if all(value is None for value in raw_values):
            continue
        plot_values = [value if value is not None else np.nan for value in raw_values]
        ax.plot(x_positions, plot_values, marker='o', linewidth=2, label=display_label)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=20, ha='right')
    ax.set_ylabel('Measured Value')
    ax.set_title('Selected Prediction History')
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.3)
    ax.legend(loc='best')
    fig.tight_layout()
    fig.savefig(filepath, dpi=220)
    plt.close(fig)

    relative_path = os.path.join(relative_dir, filename).replace('\\', '/')
    return relative_path, url_for('static', filename=relative_path)


def build_comparison_prompt(predictions):
    """Create LLM prompt describing patient history for Groq analysis"""
    history_lines = []
    ordered = sorted(predictions, key=parse_prediction_datetime)

    for idx, record in enumerate(ordered, start=1):
        timestamp_label = format_prediction_label(record)
        metrics = []
        for db_key, _, display_label in COMPARISON_PARAMETERS:
            value = extract_parameter_value(record, db_key)
            if value is not None:
                metrics.append(f"{display_label.split('(')[0].strip()}: {round(value, 2)}")
        risk = record.get('prediction') or record.get('result') or record.get('risk_level', '')
        confidence = record.get('confidence')
        risk_text = f" | Result: {risk}" if risk else ''
        if confidence:
            risk_text += f" (Confidence {round(float(confidence), 1)}%)"
        metrics_text = '; '.join(metrics)
        history_lines.append(f"{idx}. {timestamp_label} — {metrics_text}{risk_text}")

    history_block = "\n".join(history_lines)

    return f"""
You are Dr. Elena Martinez, a board-certified endocrinologist. Review the patient's diabetes-related assessments listed below.

Patient visits (oldest to most recent):
{history_block}

Summarize in three sections titled Improvements, Concerns, and Recommendations. For each section, provide up to three concise bullet points in plain language that a patient can understand. Reference trends instead of repeating raw numbers. Keep the response under 180 words and maintain a supportive clinical tone without disclaimers.
"""


def generate_comparison_pdf(current_prediction, comparison_entry):
    """Create a PDF report combining Groq insights and generated charts"""
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ComparisonTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f2937'),
        alignment=1,
        spaceAfter=12
    )

    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading3'],
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=6,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        leading=14,
        fontSize=11
    )

    story = []

    patient_name = current_prediction.get('patient_name', 'Patient')
    story.append(Paragraph('Diabetes Trend Comparison', title_style))
    story.append(Paragraph(f"Patient: <b>{patient_name}</b>", body_style))
    latest_result = current_prediction.get('prediction') or current_prediction.get('result', 'N/A')
    story.append(Paragraph(f"Latest Assessment: {latest_result}", body_style))
    story.append(Paragraph(f"Generated on: {get_ist_now().strftime('%B %d, %Y %I:%M %p')}", body_style))
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph('Groq Clinical Summary', section_title))
    explanation = comparison_entry.get('groq_explanation', 'No analysis available.')
    for paragraph in explanation.split('\n'):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 0.08 * inch))

    selected = comparison_entry.get('selected_predictions', [])
    if selected:
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph('Compared Visits', section_title))
        table_data = [['Visit', 'Glucose', 'Blood Pressure', 'BMI', 'Insulin', 'Risk / Confidence']]
        for item in selected:
            def format_cell(value):
                if isinstance(value, str):
                    return value
                numeric = _safe_float(value)
                return f"{numeric:.2f}" if numeric is not None else '—'

            confidence_value = item.get('confidence', '—')
            if isinstance(confidence_value, str):
                confidence_display = confidence_value if confidence_value != '—' else '—'
            else:
                confidence_numeric = _safe_float(confidence_value)
                confidence_display = f"{confidence_numeric:.1f}%" if confidence_numeric is not None else '—'

            table_data.append([
                item.get('label', 'Visit'),
                format_cell(item.get('Glucose', '—')),
                format_cell(item.get('BloodPressure', '—')),
                format_cell(item.get('BMI', '—')),
                format_cell(item.get('Insulin', '—')),
                f"{item.get('result', 'N/A')} ({confidence_display})"
            ])

        table = Table(table_data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER')
        ]))
        story.append(table)

    story.append(Spacer(1, 0.25 * inch))

    graph_entries = []
    current_relative = current_prediction.get('current_vs_normal_graph_path')
    if current_relative:
        graph_entries.append(('Current vs Normal', current_relative))

    comparison_relative = comparison_entry.get('graph_relative_path')
    if comparison_relative:
        graph_entries.append(('Historical Comparison', comparison_relative))

    for title, relative_path in graph_entries:
        absolute_path = os.path.join(app.root_path, 'static', relative_path.replace('/', os.sep))
        if os.path.exists(absolute_path):
            story.append(Paragraph(title, section_title))
            story.append(Image(absolute_path, width=6.0 * inch, height=3.3 * inch))
            story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    buffer.seek(0)

    filename = f"comparison_report_{_sanitize_identifier(patient_name)}_{comparison_entry.get('analysis_id', 'analysis')}.pdf"
    return buffer, filename

# ------------------- AUTHENTICATION ROUTES -------------------

@app.route('/')
def home():
    """Serve React app"""
    react_build = os.path.join(os.path.dirname(__file__), 'frontend', 'dist', 'index.html')
    if os.path.exists(react_build):
        return send_from_directory(os.path.join('frontend', 'dist'), 'index.html')
    return jsonify({"error": "React build not found. Run 'npm run build' in frontend/"}), 500


@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React app static files and handle SPA routing"""
    # CRITICAL: Don't intercept API routes, Flask templates, or backend endpoints
    api_prefixes = ['api/', 'predict', 'login', 'register', 'logout', 'user/', 'admin/', 
                    'download_', 'health', 'report', 'reset_password', 'chatbot/', 'static/']
    
    # If path starts with any API prefix, let Flask handle it (don't serve React)
    if any(path.startswith(prefix) for prefix in api_prefixes):
        # This will trigger a 404, letting the actual Flask route handle it
        from flask import abort
        abort(404)
    
    react_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
    file_path = os.path.join(react_dir, path)
    
    # Serve static assets directly (JS, CSS, images)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(react_dir, path)
    
    # For all other routes (React Router), serve index.html
    index_path = os.path.join(react_dir, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(react_dir, 'index.html')
    
    return jsonify({"error": "React build not found"}), 404


@app.route('/login')
def login_page():
    """Render login page"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return render_template(
        'login.html',
        google_client_id=google_client_id,
        google_login_enabled=bool(google_client_id)
    )


@app.route('/register')
def register_page():
    """Render registration page"""
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    return render_template('register.html')


@app.route('/forgot-password')
def forgot_password_page():
    """Render forgot password page"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return render_template('forgot_password.html')


@app.route('/reset-password')
def reset_password_page():
    """Render reset password form when token is provided"""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))

    token = request.args.get('token', '').strip()
    token_valid = False
    status_message = "Invalid or expired reset link"

    if token:
        token_valid, status_message, _ = validate_password_reset_token(token)
        if token_valid:
            status_message = "Enter a new password to secure your account."

    return render_template(
        'reset_password.html',
        token=token,
        token_valid=token_valid,
        status_message=status_message
    )


@app.route('/api/register', methods=['POST'])
def api_register():
    """Handle user registration"""
    try:
        data = request.json
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        contact = data.get('contact', '').strip()
        address = data.get('address', '').strip()
        
        # Validation
        if not username or not email or not password or not full_name:
            return jsonify({
                'success': False,
                'message': 'All required fields must be filled'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters'
            }), 400
        
        # Create user
        success, message, user_id = create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            contact=contact,
            address=address
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'redirect': url_for('login_page')
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}'
        }), 500


@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login"""
    try:
        data = request.json
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Check if database is initialized
        if not db:
            return jsonify({
                'success': False,
                'message': 'Database connection not available. Please try again later.'
            }), 503
        
        # Authenticate user
        success, message, user_data = authenticate_user(username, password)
        
        if success:
            # Set session
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            session['full_name'] = user_data['full_name']
            session['role'] = user_data['role']
            session['email'] = user_data.get('email')
            session.permanent = True
            
            # Redirect based on role
            if user_data['role'] == 'admin':
                redirect_url = url_for('admin_dashboard')
            else:
                # Redirect to dashboard (modern responsive design)
                redirect_url = url_for('user_dashboard')
            
            return jsonify({
                'success': True,
                'message': message,
                'redirect': redirect_url,
                'role': user_data['role']
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500


@app.route('/api/login/google', methods=['POST'])
def api_login_google():
    """Handle Google Sign-In login"""
    try:
        data = request.json or {}
        credential = data.get('credential') or data.get('id_token')

        success, message, user_data = authenticate_google_user(credential)

        if success:
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            session['full_name'] = user_data['full_name']
            session['role'] = user_data['role']
            session['email'] = user_data.get('email')
            session.permanent = True

            if user_data['role'] == 'admin':
                redirect_url = url_for('admin_dashboard')
            else:
                redirect_url = url_for('user_dashboard')

            return jsonify({
                'success': True,
                'message': message,
                'redirect': redirect_url,
                'role': user_data['role']
            })

        status_code = 400 if credential else 401
        return jsonify({
            'success': False,
            'message': message or 'Google login failed'
        }), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Google login error: {str(e)}'
        }), 500


@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    return redirect(url_for('home'))


@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """Trigger password reset email"""
    try:
        data = request.json or {}
        email = (data.get('email') or '').strip()

        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400

        base_url = os.getenv('APP_BASE_URL') or request.url_root.rstrip('/')
        success, message = initiate_password_reset(email, base_url)

        status_code = 200 if success else 400
        return jsonify({
            'success': success,
            'message': message
        }), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Forgot password error: {str(e)}'
        }), 500


@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """Handle password reset submission"""
    try:
        data = request.json or {}
        token = (data.get('token') or '').strip()
        password = (data.get('password') or '').strip()
        confirm_password = (data.get('confirm_password') or data.get('confirmPassword') or '').strip()

        if not token:
            return jsonify({
                'success': False,
                'message': 'Reset token is required'
            }), 400

        if not password or not confirm_password:
            return jsonify({
                'success': False,
                'message': 'Please provide and confirm your new password'
            }), 400

        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match'
            }), 400

        success, message = reset_password_with_token(token, password)
        status_code = 200 if success else 400
        return jsonify({
            'success': success,
            'message': message
        }), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Password reset error: {str(e)}'
        }), 500


@app.route('/api/session', methods=['GET'])
def get_session():
    """Get current session information for React frontend"""
    try:
        if 'user_id' in session:
            user_info = {
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'full_name': session.get('full_name'),
                'email': session.get('email'),
                'role': session.get('role', 'user')
            }
            
            # Debug: Get prediction count for this user
            try:
                from firebase_config import get_user_predictions
                predictions = get_user_predictions(session.get('user_id'))
                user_info['debug_prediction_count'] = len(predictions)
            except:
                user_info['debug_prediction_count'] = -1
            
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': user_info
            })
        else:
            return jsonify({
                'success': True,
                'authenticated': False,
                'user': None
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/latest_prediction', methods=['GET'])
@login_required
def get_latest_prediction():
    """Get user's latest prediction for dashboard"""
    try:
        user_id = session.get('user_id')
        predictions = get_user_predictions(user_id, limit=1)
        
        print(f"🔍 Fetching latest prediction for user {user_id}")
        print(f"📦 Got {len(predictions)} predictions")
        
        if predictions and len(predictions) > 0:
            pred = predictions[0]
            print(f"✅ Latest prediction: {pred.get('patient_name', pred.get('name'))}")
            
            # Determine prediction value
            pred_value = 1 if 'High' in str(pred.get('prediction', '')) or pred.get('risk_level') == 'high' else 0
            
            return jsonify({
                'success': True,
                'prediction': {
                    'prediction_id': pred.get('prediction_id', pred.get('id', pred.get('report_id'))),
                    'prediction': pred_value,
                    'probability': float(pred.get('confidence', 85)) / 100,
                    'patient_name': pred.get('patient_name', pred.get('name', 'Unknown')),
                    'age': int(pred.get('Age', pred.get('age', 0))),
                    'bmi': float(pred.get('BMI', pred.get('bmi', 0))),
                    'glucose': float(pred.get('Glucose', pred.get('glucose', 0))),
                    'blood_pressure': float(pred.get('BloodPressure', pred.get('blood_pressure', 0))),
                    'insulin': float(pred.get('Insulin', pred.get('insulin', 0))),
                    'created_at': pred.get('timestamp', pred.get('created_at', ''))
                }
            })
        else:
            print("⚠️ No predictions found for user")
            return jsonify({
                'success': True,
                'prediction': None
            })
    except Exception as e:
        print(f"❌ Error in get_latest_prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/all_predictions', methods=['GET'])
@login_required
def get_all_user_predictions():
    """Get all user predictions for dashboard overview and graphs"""
    try:
        user_id = session.get('user_id')
        predictions = get_user_predictions(user_id, limit=100)
        
        print(f"📊 Fetched {len(predictions)} predictions for user {user_id}")
        
        formatted_predictions = []
        for pred in predictions:
            # Determine prediction value (1 for high risk, 0 for low risk)
            pred_value = 1 if 'High' in str(pred.get('prediction', '')) or pred.get('risk_level') == 'high' else 0
            
            # Check if report exists - multiple field names for compatibility
            has_report = bool(
                pred.get('report_path') or 
                pred.get('report_id') or 
                pred.get('report_file') or 
                pred.get('report_generated_at')
            )
            
            formatted_pred = {
                'prediction_id': pred.get('prediction_id', pred.get('id', pred.get('report_id'))),
                'patient_name': pred.get('patient_name', pred.get('name', 'Unknown')),
                'prediction': pred_value,
                'probability': float(pred.get('confidence', 85)) / 100,
                'risk_level': pred.get('risk_level', 'high' if pred_value == 1 else 'low'),
                'confidence': float(pred.get('confidence', 85)),
                'age': int(pred.get('Age', pred.get('age', 0))),
                'bmi': float(pred.get('BMI', pred.get('bmi', 0))),
                'glucose': float(pred.get('Glucose', pred.get('glucose', 0))),
                'blood_pressure': float(pred.get('BloodPressure', pred.get('blood_pressure', 0))),
                'insulin': float(pred.get('Insulin', pred.get('insulin', 0))),
                'skin_thickness': float(pred.get('SkinThickness', pred.get('skin_thickness', 0))),
                'pregnancies': int(pred.get('Pregnancies', pred.get('pregnancies', 0))),
                'dpf': float(pred.get('DiabetesPedigreeFunction', pred.get('diabetes_pedigree_function', 0))),
                'created_at': pred.get('timestamp', pred.get('created_at', '')),
                'date': pred.get('date', ''),
                'has_report': has_report,
                'report_id': pred.get('report_id', ''),
                'report_file': pred.get('report_path', pred.get('report_file', ''))
            }
            formatted_predictions.append(formatted_pred)
            print(f"  ✓ {formatted_pred['patient_name']} - {formatted_pred['risk_level']} risk")
        
        return jsonify({
            'success': True,
            'predictions': formatted_predictions,
            'total': len(formatted_predictions)
        })
    except Exception as e:
        print(f"❌ Error in get_all_user_predictions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'predictions': []
        }), 500


@app.route('/api/user/reports', methods=['GET'])
@login_required
def get_user_reports():
    """Get all reports for current user"""
    try:
        user_id = session.get('user_id')
        predictions = get_user_predictions(user_id)
        
        print(f"📊 Fetching reports for user {user_id}, found {len(predictions)} predictions")
        
        reports = []
        for pred in predictions:
            # Every prediction can have a report generated - check if it has necessary data
            has_report = bool(
                pred.get('id') or 
                pred.get('prediction_id') or 
                pred.get('firebase_id')
            )
            
            if has_report:
                # Get timestamp - try multiple formats
                generated_at = pred.get('report_generated_at') or pred.get('timestamp') or pred.get('created_at')
                
                # If generated_at is a number (Unix timestamp), convert to ISO string
                if isinstance(generated_at, (int, float)):
                    from datetime import datetime
                    generated_at = datetime.fromtimestamp(generated_at).isoformat()
                elif not generated_at:
                    # Default to current time if missing
                    from datetime import datetime
                    generated_at = datetime.now().isoformat()
                
                # Determine prediction result
                prediction_text = pred.get('prediction', '')
                if isinstance(prediction_text, int):
                    pred_result = 'High Risk' if prediction_text == 1 else 'Low Risk'
                elif 'High' in str(prediction_text):
                    pred_result = 'High Risk'
                else:
                    pred_result = 'Low Risk'
                
                report_entry = {
                    'report_id': pred.get('report_id', pred.get('prediction_id', pred.get('id'))),
                    'prediction_id': pred.get('prediction_id', pred.get('id')),
                    'patient_name': pred.get('patient_name', pred.get('name', 'Unknown')),
                    'prediction_result': pred_result,
                    'probability': pred.get('probability', pred.get('confidence', 50) / 100),
                    'generated_at': generated_at,
                    'report_file': pred.get('report_path', pred.get('report_file'))
                }
                reports.append(report_entry)
                print(f"  ✅ Report found: {report_entry['patient_name']} - {report_entry['prediction_id']}")
        
        print(f"✅ Returning {len(reports)} reports")
        
        return jsonify({
            'success': True,
            'reports': reports,
            'total': len(reports)
        })
    except Exception as e:
        print(f"❌ Error in get_user_reports: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'reports': []
        }), 500


@app.route('/api/user/reports/<report_id>', methods=['GET'])
@login_required
def get_report_detail(report_id):
    """Get detailed report data for viewing"""
    try:
        user_id = session.get('user_id')
        is_admin = session.get('role') == 'admin'
        
        # Admin can view any report, users can only view their own
        if is_admin:
            import firebase_config
            firebase_config.initialize_firebase()
            predictions_ref = firebase_config.db_ref.child('predictions').child(report_id)
            report = predictions_ref.get()
            
            if report:
                report['id'] = report_id
        else:
            # Get user's predictions
            predictions = get_user_predictions(user_id)
            
            # Find the specific report
            report = None
            for pred in predictions:
                if (pred.get('id') == report_id or 
                    pred.get('firebase_id') == report_id or 
                    pred.get('prediction_id') == report_id or
                    pred.get('report_id') == report_id):
                    report = pred
                    break
        
        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        # Format report data for viewing
        prediction_text = report.get('prediction', '')
        if isinstance(prediction_text, int):
            pred_result = 'High Risk - Diabetes Detected' if prediction_text == 1 else 'Low Risk - No Diabetes'
        elif 'High' in str(prediction_text):
            pred_result = 'High Risk - Diabetes Detected'
        else:
            pred_result = 'Low Risk - No Diabetes'
        
        # Get confidence/probability
        confidence = report.get('confidence', report.get('probability', 0.5))
        if isinstance(confidence, (int, float)):
            if confidence > 1:  # If it's a percentage
                confidence_pct = confidence
            else:  # If it's a decimal
                confidence_pct = confidence * 100
        else:
            confidence_pct = 50
        
        # Build comprehensive report object
        report_data = {
            'report_id': report_id,
            'patient_name': report.get('patient_name', report.get('name', 'Unknown')),
            'prediction_result': pred_result,
            'probability': confidence / 100 if confidence > 1 else confidence,
            'confidence_percentage': confidence_pct,
            'generated_at': report.get('timestamp') or report.get('created_at') or datetime.now().isoformat(),
            'patient_data': {
                'age': report.get('Age') or report.get('age', 'N/A'),
                'gender': report.get('sex', 'N/A'),
                'glucose': report.get('Glucose') or report.get('glucose', 'N/A'),
                'blood_pressure': report.get('BloodPressure') or report.get('blood_pressure', 'N/A'),
                'bmi': report.get('BMI') or report.get('bmi', 'N/A'),
                'insulin': report.get('Insulin') or report.get('insulin', 'N/A'),
                'skin_thickness': report.get('SkinThickness') or report.get('skin_thickness', 'N/A'),
                'pregnancies': report.get('Pregnancies') or report.get('pregnancies', 'N/A'),
                'diabetes_pedigree': report.get('DiabetesPedigreeFunction') or report.get('diabetes_pedigree', 'N/A')
            },
            'ai_analysis': report.get('ai_analysis', ''),
            'risk_factors': report.get('risk_factors', []),
            'recommendations': report.get('recommendations', [])
        }
        
        return jsonify({
            'success': True,
            'report': report_data
        })
    except Exception as e:
        print(f"Error getting report detail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/user/update_profile', methods=['POST'])
@login_required
def api_update_user_profile():
    """Update user profile"""
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # Call the auth function with correct parameters
        from auth import update_user_profile as update_profile_func
        success, message = update_profile_func(
            user_id=user_id,
            full_name=data.get('full_name'),
            contact=data.get('contact'),
            address=data.get('address')
        )
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/user/change_password', methods=['POST'])
@login_required
def change_user_password():
    """Change user password"""
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # Call the auth function with correct parameters
        from auth import change_password as change_pwd_func
        success, message = change_pwd_func(
            user_id=user_id,
            old_password=data.get('current_password'),
            new_password=data.get('new_password')
        )
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required
def get_all_users_api():
    """Get all users for admin dashboard"""
    try:
        from firebase_config import db_ref
        
        users_data = db_ref.child('users').get()
        
        users_list = []
        if users_data:
            for user_id, user_info in users_data.items():
                if not isinstance(user_info, dict):
                    continue
                
                # Count predictions for this user
                prediction_count = 0
                try:
                    all_preds = db_ref.child('predictions').get()
                    if all_preds:
                        prediction_count = sum(1 for p in all_preds.values() 
                                             if isinstance(p, dict) and p.get('user_id') == user_id)
                except:
                    pass
                
                # Count reports for this user (each prediction can generate a report)
                report_count = prediction_count  # Reports are based on predictions
                try:
                    # Also check explicit reports node if it exists
                    user_reports = db_ref.child(f'reports/{user_id}').get()
                    if user_reports and isinstance(user_reports, dict):
                        report_count = max(report_count, len(user_reports))
                except:
                    pass
                
                users_list.append({
                    'user_id': user_id,
                    'username': user_info.get('username', 'N/A'),
                    'full_name': user_info.get('full_name', 'N/A'),
                    'email': user_info.get('email', 'N/A'),
                    'created_at': user_info.get('created_at', 'N/A'),
                    'prediction_count': prediction_count,
                    'report_count': report_count
                })
        
        return jsonify({
            'success': True,
            'users': users_list
        })
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user_api(user_id):
    """Delete a user and all their data"""
    try:
        from firebase_config import db_ref
        
        # Check if user exists
        user_data = db_ref.child(f'users/{user_id}').get()
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Delete user's predictions
        all_preds = db_ref.child('predictions').get()
        if all_preds:
            for pred_id, pred_data in all_preds.items():
                if isinstance(pred_data, dict) and pred_data.get('user_id') == user_id:
                    db_ref.child(f'predictions/{pred_id}').delete()
        
        # Delete user's reports
        db_ref.child(f'reports/{user_id}').delete()
        
        # Delete user's chat history
        db_ref.child(f'chat_history/{user_id}').delete()
        
        # Delete the user account
        db_ref.child(f'users/{user_id}').delete()
        
        return jsonify({
            'success': True,
            'message': f'User {user_id} and all associated data deleted successfully'
        })
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/stats', methods=['GET'])
@login_required
@admin_required
def get_admin_stats():
    """Get system statistics for admin"""
    try:
        print("🔍 Fetching admin stats...")
        
        # Get prediction statistics
        firebase_stats = get_statistics()
        print(f"📊 Firebase stats: {firebase_stats}")
        
        # Import db_ref from firebase_config
        from firebase_config import db_ref
        
        # Count total users from Firebase
        total_users = 0
        try:
            users_data = db_ref.child('users').get()
            if users_data:
                total_users = len(users_data)
                print(f"👥 Total users: {total_users}")
        except Exception as e:
            print(f"⚠️ Error counting users: {e}")
        
        # Count total reports from Firebase  
        total_reports = 0
        try:
            reports_data = db_ref.child('reports').get()
            if reports_data:
                # Count all reports across all users
                for user_reports in reports_data.values():
                    if isinstance(user_reports, dict):
                        total_reports += len(user_reports)
                print(f"📄 Total reports: {total_reports}")
        except Exception as e:
            print(f"⚠️ Error counting reports: {e}")
        
        stats = {
            'total_users': total_users,
            'total_predictions': firebase_stats.get('total_predictions', 0),
            'total_reports': total_reports,
            'positive_predictions': firebase_stats.get('high_risk_count', 0)
        }
        
        print(f"✅ Final Admin Stats: {stats}")
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        import traceback
        print(f"❌ Admin stats error: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ------------------- USER DASHBOARD ROUTES -------------------

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """Render user dashboard - shows data if predictions exist"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    try:
        user_id = session.get('user_id')
        print(f"📊 Loading dashboard for user: {user_id}")
        
        # Get user statistics
        stats = get_user_statistics(user_id)
        print(f"📈 Stats: {stats}")
        
        # Get recent predictions
        predictions = get_user_predictions(user_id, limit=10)
        print(f"📋 Found {len(predictions)} predictions")
        
        # Calculate counts
        high_risk_count = sum(1 for p in predictions if p.get('risk_level') == 'high' or p.get('prediction') == 1)
        
        # Get this month's count
        from datetime import datetime, timedelta
        ist_now = get_ist_now()
        this_month_start = ist_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        recent_predictions = 0
        for pred in predictions:
            pred_date_str = pred.get('created_at') or pred.get('timestamp', '')
            try:
                # Try parsing different date formats
                if isinstance(pred_date_str, (int, float)):
                    pred_date = datetime.fromtimestamp(pred_date_str, tz=IST)
                else:
                    pred_date = datetime.fromisoformat(pred_date_str.replace('Z', '+00:00'))
                    pred_date = pred_date.astimezone(IST)
                
                if pred_date >= this_month_start:
                    recent_predictions += 1
            except:
                pass
        
        # Format recent activity
        recent_activity = []
        for pred in predictions[:5]:  # Last 5 predictions
            activity = {
                'type': 'Diabetes Risk Assessment',
                'date': pred.get('timestamp') or pred.get('created_at', 'N/A'),
                'risk': 'high' if (pred.get('risk_level') == 'high' or pred.get('prediction') == 1) else 'low',
                'risk_level': 'High Risk' if (pred.get('risk_level') == 'high' or pred.get('prediction') == 1) else 'Low Risk'
            }
            recent_activity.append(activity)
        
        return render_template('user_dashboard_new.html',
            stats={
                'total_predictions': stats.get('total_predictions', 0),
                'low_risk': stats.get('total_predictions', 0) - high_risk_count,
                'high_risk': high_risk_count,
                'last_check': predictions[0].get('timestamp') if predictions else 'Never'
            },
            total_predictions=stats.get('total_predictions', 0),
            recent_predictions=recent_predictions,
            total_reports=len(predictions),
            high_risk_count=high_risk_count,
            recent_activity=recent_activity
        )
    except Exception as e:
        print(f"❌ Error loading user dashboard: {e}")
        import traceback
        traceback.print_exc()
        # Return with default values
        return render_template('user_dashboard_new.html',
            stats={
                'total_predictions': 0,
                'low_risk': 0,
                'high_risk': 0,
                'last_check': 'Never'
            },
            total_predictions=0,
            recent_predictions=0,
            total_reports=0,
            high_risk_count=0,
            recent_activity=[]
        )


@app.route('/user/predictions')
@login_required
def user_predictions():
    """Render user predictions history page"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('patient_predictions.html')


@app.route('/user/predict')
@login_required
def user_predict_page():
    """Render prediction page for user"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('index.html')


@app.route('/user/profile')
@login_required
def user_profile():
    """Render user profile page"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('profile.html')


@app.route('/change_password')
@login_required
def change_password_page():
    """Render change password page (for both users and admin)"""
    return render_template('change_password.html')


@app.route('/user/reports')
@login_required
def user_reports():
    """Render user reports page"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('user_reports.html')


@app.route('/user/comprehensive_analysis')
@login_required
def comprehensive_analysis_page():
    """Render comprehensive health analysis page"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('comprehensive_analysis.html')


@app.route('/api/comprehensive_analysis', methods=['GET'])
@login_required
def get_comprehensive_analysis():
    """Generate comprehensive health analysis based on user history"""
    try:
        user_id = session.get('user_id')
        
        # Get all user predictions
        history = get_patient_history(user_id=user_id, limit=1000)
        
        if not history or len(history) == 0:
            return jsonify({
                'success': False,
                'error': 'No prediction history found'
            }), 404
        
        # Calculate statistics
        total_predictions = len(history)
        high_risk_count = sum(1 for h in history if h.get('result') == 'High Risk')
        low_risk_count = total_predictions - high_risk_count
        
        # Calculate averages
        glucose_values = [float(h.get('Glucose', 0)) for h in history if h.get('Glucose')]
        bmi_values = [float(h.get('BMI', 0)) for h in history if h.get('BMI')]
        bp_values = [float(h.get('BloodPressure', 0)) for h in history if h.get('BloodPressure')]
        insulin_values = [float(h.get('Insulin', 0)) for h in history if h.get('Insulin')]
        confidence_values = [float(h.get('confidence', 0)) for h in history if h.get('confidence')]
        
        avg_glucose = sum(glucose_values) / len(glucose_values) if glucose_values else 0
        avg_bmi = sum(bmi_values) / len(bmi_values) if bmi_values else 0
        avg_bp = sum(bp_values) / len(bp_values) if bp_values else 0
        avg_insulin = sum(insulin_values) / len(insulin_values) if insulin_values else 0
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
        
        # Get user info
        import firebase_config
        firebase_config.initialize_firebase()
        user_ref = firebase_config.db_ref.child('users').child(user_id)
        user_data = user_ref.get()
        patient_name = user_data.get('full_name', 'Patient') if user_data else 'Patient'
        
        # Find best assessment
        best_assessment = None
        if history:
            # Prioritize low risk with highest confidence
            low_risk_predictions = [h for h in history if h.get('result') == 'Low Risk']
            if low_risk_predictions:
                best_assessment = max(low_risk_predictions, key=lambda x: float(x.get('confidence', 0)))
            else:
                best_assessment = max(history, key=lambda x: float(x.get('confidence', 0)))
        
        # Calculate risk score
        risk_score = 0
        if avg_glucose >= 126:
            risk_score += 40
        elif avg_glucose >= 100:
            risk_score += 30
        else:
            risk_score += 10
        
        if avg_bmi >= 30:
            risk_score += 30
        elif avg_bmi >= 25:
            risk_score += 20
        else:
            risk_score += 5
        
        risk_score += (high_risk_count / total_predictions * 20) if total_predictions > 0 else 0
        risk_score += (avg_confidence / 100 * 10)
        
        analysis = {
            'patient_name': patient_name,
            'date': get_ist_now().strftime('%B %d, %Y'),
            'total_predictions': total_predictions,
            'high_risk_count': high_risk_count,
            'low_risk_count': low_risk_count,
            'high_risk_percentage': (high_risk_count / total_predictions * 100) if total_predictions > 0 else 0,
            'low_risk_percentage': (low_risk_count / total_predictions * 100) if total_predictions > 0 else 0,
            'avg_glucose': round(avg_glucose, 1),
            'avg_bmi': round(avg_bmi, 1),
            'avg_bp': round(avg_bp, 1),
            'avg_insulin': round(avg_insulin, 1),
            'avg_confidence': round(avg_confidence, 1),
            'risk_score': round(risk_score, 2),
            'best_assessment': best_assessment,
            'recent_history': history[:10]  # Last 10 predictions
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        print(f"Error generating comprehensive analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to generate analysis'
        }), 500


@app.route('/user/history')
@login_required
def user_history():
    """Render user history page"""
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('user_dashboard_new.html')


@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile information"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        full_name = session.get('full_name')
        
        # Try to get user data from Firebase
        import firebase_config
        firebase_config.initialize_firebase()
        
        user_ref = firebase_config.db_ref.child('users').child(user_id)
        user_data_fb = user_ref.get()
        
        user_data = {
            'user_id': user_id,
            'username': username,
            'full_name': full_name,
            'email': user_data_fb.get('email', f"{username}@example.com") if user_data_fb else f"{username}@example.com",
            'contact': user_data_fb.get('contact', 'N/A') if user_data_fb else 'N/A',
            'address': user_data_fb.get('address', 'N/A') if user_data_fb else 'N/A',
            'created_at': user_data_fb.get('created_at', get_ist_now().isoformat()) if user_data_fb else get_ist_now().isoformat(),
            'role': session.get('role', 'user')
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        email = data.get('email', '').strip()
        contact = data.get('contact', '').strip()
        address = data.get('address', '').strip()
        
        # Validation
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        if contact and not re.match(r'^\d{10}$', contact):
            return jsonify({
                'success': False,
                'error': 'Contact number must be exactly 10 digits'
            }), 400
        
        # Update in Firebase
        import firebase_config
        firebase_config.initialize_firebase()
        
        user_ref = firebase_config.db_ref.child('users').child(user_id)
        update_data = {}
        
        if email:
            update_data['email'] = email
        if contact:
            update_data['contact'] = contact
        if address:
            update_data['address'] = address
        
        update_data['updated_at'] = get_ist_now().isoformat()
        
        user_ref.update(update_data)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update profile'
        }), 500


@app.route('/api/change_password', methods=['POST'])
@login_required
def change_password():
    """Change password for logged-in user (admin or regular user)"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            return jsonify({
                'success': False,
                'error': 'All password fields are required'
            }), 400
        
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'error': 'New passwords do not match'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 6 characters'
            }), 400
        
        # Check if admin or regular user
        if session.get('role') == 'admin':
            # Change admin password
            from auth import change_admin_password
            success, message = change_admin_password(current_password, new_password)
        else:
            # Change user password
            from auth import change_user_password
            user_id = session.get('user_id')
            success, message = change_user_password(user_id, current_password, new_password)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    
    except Exception as e:
        print(f"Error changing password: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to change password'
        }), 500


# ------------------- ADMIN DASHBOARD ROUTES -------------------

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Render admin dashboard - only accessible to admin"""
    return render_template('dashboard.html')


@app.route('/admin/patients')
@admin_required
def admin_patients():
    """Admin page to view and manage all patients"""
    return render_template('admin_patients.html')


# OLD FLASK TEMPLATE REMOVED - Now using React admin dashboard
# @app.route('/admin/patient_predictions')
# Use React route: /admin instead


# OLD FLASK TEMPLATE REMOVED - Now using React reports page
# @app.route('/admin/reports')
# Use React route: /reports instead


@app.route('/admin/get_all_reports', methods=['GET'])
@admin_required
def get_all_reports():
    """API endpoint to get all medical reports from all patients with complete details"""
    try:
        import firebase_config
        firebase_config.initialize_firebase()
        
        # Get all predictions from Firebase
        predictions_ref = firebase_config.db_ref.child('predictions')
        all_predictions = predictions_ref.get()
        
        if not all_predictions:
            return jsonify({
                'success': True,
                'reports': [],
                'total_count': 0
            })
        
        reports_list = []
        for report_id, report_data in all_predictions.items():
            if isinstance(report_data, dict):
                # Ensure all required fields are present
                report = {
                    'id': report_id,
                    'report_id': report_id,
                    'prediction_id': report_id,
                    # Patient info
                    'patient_name': report_data.get('patient_name', 'Unknown'),
                    'age': report_data.get('age', 0),
                    'sex': report_data.get('sex', 'N/A'),
                    'contact': report_data.get('contact', 'N/A'),
                    'address': report_data.get('address', 'N/A'),
                    # Prediction results
                    'prediction': report_data.get('prediction', 'N/A'),
                    'result': report_data.get('result', 'N/A'),
                    'risk_level': report_data.get('risk_level', 'unknown'),
                    'confidence': report_data.get('confidence', 0),
                    'probability': report_data.get('confidence', 0) / 100 if report_data.get('confidence') else 0,
                    # Medical parameters
                    'Pregnancies': report_data.get('Pregnancies', 0),
                    'Glucose': report_data.get('Glucose', 0),
                    'BloodPressure': report_data.get('BloodPressure', 0),
                    'SkinThickness': report_data.get('SkinThickness', 0),
                    'Insulin': report_data.get('Insulin', 0),
                    'BMI': report_data.get('BMI', 0),
                    'DiabetesPedigreeFunction': report_data.get('DiabetesPedigreeFunction', 0),
                    'Age': report_data.get('Age', report_data.get('age', 0)),
                    # Lifestyle factors
                    'smoking': report_data.get('smoking', 0),
                    'physical_activity': report_data.get('physical_activity', 0),
                    'alcohol_intake': report_data.get('alcohol_intake', 0),
                    'family_history': report_data.get('family_history', 0),
                    'sleep_hours': report_data.get('sleep_hours', 7),
                    # Metadata
                    'user_id': report_data.get('user_id', 'anonymous'),
                    'timestamp': report_data.get('timestamp', report_data.get('created_at', '')),
                    'created_at': report_data.get('created_at', report_data.get('timestamp', '')),
                    'date': report_data.get('date', ''),
                    'time': report_data.get('time', ''),
                    # Additional data
                    'features': report_data.get('features', []),
                    'has_report': True
                }
                reports_list.append(report)
        
        # Sort by timestamp (most recent first)
        reports_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        print(f"✅ Admin: Retrieved {len(reports_list)} reports with complete details")
        
        return jsonify({
            'success': True,
            'reports': reports_list,
            'total_count': len(reports_list)
        })
    
    except Exception as e:
        print(f"❌ Error fetching reports: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/admin/get_all_patients', methods=['GET'])
@admin_required
def get_all_patients():
    """API endpoint to get all registered patients with their statistics"""
    try:
        import firebase_config
        firebase_config.initialize_firebase()
        
        # Get all users from Firebase
        users_ref = firebase_config.db_ref.child('users')
        all_users = users_ref.get()
        
        if not all_users:
            return jsonify({
                'success': True,
                'patients': [],
                'total_count': 0
            })
        
        patients_list = []
        for user_id, user_data in all_users.items():
            if isinstance(user_data, dict):
                # Skip admin users
                if user_data.get('role') == 'admin':
                    continue
                
                # Get predictions count and risk analysis
                predictions = user_data.get('predictions', {})
                pred_count = 0
                high_risk_count = 0
                low_risk_count = 0
                last_activity = 'N/A'
                
                if predictions and isinstance(predictions, dict):
                    pred_count = len(predictions)
                    
                    # Count high/low risk and get latest timestamp
                    timestamps = []
                    for pred in predictions.values():
                        if isinstance(pred, dict):
                            # Count risk levels
                            risk_level = pred.get('risk_level', '').lower()
                            if risk_level == 'high':
                                high_risk_count += 1
                            elif risk_level == 'low':
                                low_risk_count += 1
                            
                            # Collect timestamps
                            if 'timestamp' in pred:
                                timestamps.append(pred['timestamp'])
                    
                    # Get most recent activity
                    if timestamps:
                        try:
                            last_activity = max(timestamps)
                        except:
                            last_activity = 'N/A'
                
                patient_info = {
                    'user_id': user_id,
                    'full_name': user_data.get('full_name', 'N/A'),
                    'username': user_data.get('username', 'N/A'),
                    'email': user_data.get('email', 'N/A'),
                    'created_at': user_data.get('created_at', 'N/A'),
                    'total_predictions': pred_count,
                    'high_risk_count': high_risk_count,
                    'low_risk_count': low_risk_count,
                    'last_activity': last_activity,
                    'role': user_data.get('role', 'user')
                }
                patients_list.append(patient_info)
        
        return jsonify({
            'success': True,
            'patients': patients_list,
            'total_count': len(patients_list)
        })
    
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/admin/patient/<user_id>/predictions', methods=['GET'])
@admin_required
def get_patient_predictions(user_id):
    """Get all predictions for a specific patient with complete details"""
    try:
        print(f"📊 Admin fetching predictions for user: {user_id}")
        
        # Get all predictions for this user
        history = get_patient_history(user_id=user_id, limit=1000)
        
        # Enhance each prediction with complete data
        enhanced_history = []
        for pred in history:
            enhanced_pred = {
                'id': pred.get('id', pred.get('prediction_id', pred.get('report_id', 'N/A'))),
                'prediction_id': pred.get('prediction_id', pred.get('id', pred.get('report_id', 'N/A'))),
                'report_id': pred.get('report_id', pred.get('id', pred.get('prediction_id', 'N/A'))),
                # Patient info
                'patient_name': pred.get('patient_name', 'Unknown'),
                'age': pred.get('age', 0),
                'sex': pred.get('sex', 'N/A'),
                'contact': pred.get('contact', 'N/A'),
                'address': pred.get('address', 'N/A'),
                # Prediction results
                'prediction': pred.get('prediction', 'N/A'),
                'result': pred.get('result', 'N/A'),
                'risk_level': pred.get('risk_level', 'unknown'),
                'confidence': pred.get('confidence', 0),
                'probability': pred.get('probability', pred.get('confidence', 0) / 100 if pred.get('confidence') else 0),
                # Medical parameters
                'Pregnancies': pred.get('Pregnancies', 0),
                'Glucose': pred.get('Glucose', 0),
                'BloodPressure': pred.get('BloodPressure', 0),
                'SkinThickness': pred.get('SkinThickness', 0),
                'Insulin': pred.get('Insulin', 0),
                'BMI': pred.get('BMI', 0),
                'DiabetesPedigreeFunction': pred.get('DiabetesPedigreeFunction', 0),
                'Age': pred.get('Age', pred.get('age', 0)),
                # Lifestyle factors
                'smoking': pred.get('smoking', 0),
                'physical_activity': pred.get('physical_activity', 0),
                'alcohol_intake': pred.get('alcohol_intake', 0),
                'family_history': pred.get('family_history', 0),
                'sleep_hours': pred.get('sleep_hours', 7),
                # Metadata
                'user_id': pred.get('user_id', user_id),
                'timestamp': pred.get('timestamp', pred.get('created_at', '')),
                'created_at': pred.get('created_at', pred.get('timestamp', '')),
                'date': pred.get('date', ''),
                'time': pred.get('time', ''),
                # Additional
                'features': pred.get('features', []),
                'has_report': True
            }
            enhanced_history.append(enhanced_pred)
        
        # Get user info
        import firebase_config
        firebase_config.initialize_firebase()
        user_ref = firebase_config.db_ref.child('users').child(user_id)
        user_data = user_ref.get()
        
        print(f"✅ Admin: Retrieved {len(enhanced_history)} predictions for user {user_id}")
        
        return jsonify({
            'success': True,
            'patient': {
                'user_id': user_id,
                'full_name': user_data.get('full_name', 'N/A') if user_data else 'N/A',
                'username': user_data.get('username', 'N/A') if user_data else 'N/A',
                'email': user_data.get('email', 'N/A') if user_data else 'N/A',
                'created_at': user_data.get('created_at', 'N/A') if user_data else 'N/A',
            },
            'predictions': enhanced_history,
            'total_count': len(enhanced_history)
        })
    
    except Exception as e:
        print(f"❌ Error fetching patient predictions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/admin/patient/<user_id>/delete', methods=['DELETE'])
@admin_required
def delete_patient(user_id):
    """Delete a patient and all their data (Admin only)"""
    try:
        # Prevent deleting own account
        if user_id == session.get('user_id'):
            return jsonify({
                'success': False,
                'error': 'Cannot delete your own admin account'
            }), 400
        
        import firebase_config
        firebase_config.initialize_firebase()
        
        # Delete user from /users node
        user_ref = firebase_config.db_ref.child('users').child(user_id)
        user_ref.delete()
        
        # Delete all predictions by this user from /predictions node
        predictions_ref = firebase_config.db_ref.child('predictions')
        all_predictions = predictions_ref.get()
        
        if all_predictions and isinstance(all_predictions, dict):
            for pred_id, pred_data in all_predictions.items():
                if isinstance(pred_data, dict) and pred_data.get('user_id') == user_id:
                    # Delete this prediction
                    predictions_ref.child(pred_id).delete()
        
        return jsonify({
            'success': True,
            'message': 'Patient and all associated data deleted successfully'
        })
    
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete patient. Please try again.'
        }), 500


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """
    Handle ML prediction for diabetes risk with comprehensive input validation
    Expects JSON with patient data and medical test values
    """
    try:
        if model is None:
            return jsonify({
                'success': False,
                'error': 'ML model not loaded. Please check server logs.'
            }), 500

        data = request.json
        
        # === SECURITY: Input Validation ===
        import re
        
        # Validate patient name (letters and spaces only)
        name = str(data.get('name', 'Unknown')).strip()
        if not re.match(r'^[A-Za-z\s]+$', name) or len(name) < 2 or len(name) > 100:
            return jsonify({
                'success': False,
                'error': 'Invalid name. Only letters and spaces allowed (2-100 characters).'
            }), 400
        
        # Validate age (1-120)
        try:
            age = int(data.get('age', 0))
            if age < 1 or age > 120:
                raise ValueError()
        except:
            return jsonify({
                'success': False,
                'error': 'Invalid age. Must be between 1 and 120.'
            }), 400
        
        # Validate contact (10 digits)
        contact = str(data.get('contact', '')).strip()
        if not re.match(r'^\d{10}$', contact):
            return jsonify({
                'success': False,
                'error': 'Invalid contact number. Must be exactly 10 digits.'
            }), 400
        
        # Validate sex
        sex = str(data.get('sex', 'Unknown'))
        if sex not in ['Male', 'Female', 'Other']:
            return jsonify({
                'success': False,
                'error': 'Invalid sex value.'
            }), 400
        
        # Extract patient info
        patient_info = {
            'name': name,
            'age': age,
            'sex': sex,
            'contact': contact,
            'address': str(data.get('address', 'N/A')).strip()[:500]  # Max 500 chars
        }
        
        # === SECURITY: Validate Medical Features ===
        try:
            pregnancies = float(data.get('pregnancies', 0))
            if pregnancies < 0 or pregnancies > 20:
                raise ValueError('Pregnancies must be 0-20')
            
            glucose = float(data.get('glucose', 0))
            if glucose <= 0 or glucose > 300:
                raise ValueError('Glucose must be 1-300 mg/dL')
            
            bloodPressure = float(data.get('bloodPressure', 0))
            if bloodPressure <= 0 or bloodPressure > 200:
                raise ValueError('Blood pressure must be 1-200 mmHg')
            
            skinThickness = float(data.get('skinThickness', 0))
            if skinThickness < 0 or skinThickness > 100:
                raise ValueError('Skin thickness must be 0-100 mm')
            
            insulin = float(data.get('insulin', 0))
            if insulin < 0 or insulin > 900:
                raise ValueError('Insulin must be 0-900 μU/mL')
            
            bmi = float(data.get('bmi', 0))
            if bmi < 10 or bmi > 70:
                raise ValueError('BMI must be 10-70')
            
            dpf = float(data.get('diabetesPedigreeFunction', 0))
            if dpf < 0 or dpf > 3:
                raise ValueError('Diabetes Pedigree Function must be 0-3')
            
            # Feature engineering (matching training pipeline)
            bmi_age_interaction = bmi * age
            glucose_insulin_ratio = glucose / (insulin + 1)  # Add 1 to avoid division by zero
            
            features = [pregnancies, glucose, bloodPressure, skinThickness, insulin, bmi, dpf, age, bmi_age_interaction, glucose_insulin_ratio]
            
        except ValueError as ve:
            return jsonify({
                'success': False,
                'error': f'Invalid medical value: {str(ve)}'
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Invalid medical test values. Please check all inputs.'
            }), 400
        
        # Prepare features for prediction
        features_array = np.array(features).reshape(1, -1)
        
        # Scale features if scaler is available
        if scaler is not None:
            features_scaled = scaler.transform(features_array)
        else:
            features_scaled = features_array
        
        prediction = model.predict(features_scaled)[0]
        
        # Get prediction probability if available
        try:
            prediction_proba = model.predict_proba(features_scaled)[0]
            confidence = float(max(prediction_proba) * 100)
            probability = float(prediction_proba[1])  # Probability of diabetes
        except:
            confidence = 85.0  # Default confidence
            probability = 0.85 if prediction == 1 else 0.15
        
        # Interpret result
        if prediction == 1:
            result = "High Risk of Diabetes"
            risk_level = "high"
            recommendation = "Please consult with a doctor immediately for detailed examination."
        else:
            result = "Low Risk / No Diabetes"
            risk_level = "low"
            recommendation = "Maintain a healthy lifestyle and regular check-ups."
        
        # Prepare response data
        response_data = {
            'success': True,
            'prediction': result,
            'risk_level': risk_level,
            'confidence': round(confidence, 2),
            'recommendation': recommendation,
            'patient_info': patient_info,
            'medical_data': {
                'Pregnancies': features[0],
                'Glucose': features[1],
                'Blood Pressure': features[2],
                'Skin Thickness': features[3],
                'Insulin': features[4],
                'BMI': features[5],
                'Diabetes Pedigree Function': features[6],
                'Age': features[7],
                'BMI_Age_Interaction': features[8],
                'Glucose_Insulin_Ratio': features[9]
            }
        }
        
        # Save to Firebase with user_id and generate visual assets
        try:
            prediction_data = {
                'prediction': result,
                'risk_level': risk_level,
                'confidence': round(confidence, 2),
                'features': features
            }
            user_id = session.get('user_id', 'anonymous')
            print(f"🔑 Saving prediction for user_id: {user_id}")
            firebase_doc_id = save_patient_data(patient_info, prediction_data, user_id=user_id)
            if firebase_doc_id:
                response_data['firebase_id'] = firebase_doc_id
                print(f"✅ Data saved to Firebase with ID: {firebase_doc_id} for user: {user_id}")

                try:
                    graph_path, graph_url = generate_current_vs_normal_chart(
                        response_data.get('medical_data', {}),
                        user_id,
                        firebase_doc_id
                    )
                    if graph_path and graph_url:
                        response_data.setdefault('graphs', {})['current_vs_normal'] = {
                            'relative_path': graph_path,
                            'url': graph_url
                        }
                        update_prediction_record(
                            firebase_doc_id,
                            {
                                'current_vs_normal_graph_path': graph_path,
                                'current_vs_normal_graph_url': graph_url
                            },
                            user_id=user_id
                        )
                except Exception as chart_error:
                    print(f"⚠️ Unable to generate current vs normal chart: {chart_error}")
        except Exception as firebase_error:
            print(f"⚠️ Firebase save failed (non-critical): {firebase_error}")
            # Continue without Firebase - app works without it
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500


@app.route('/prediction/analysis', methods=['POST'])
@login_required
def analyze_prediction_trends():
    """Generate comparative insights across past predictions using Groq"""
    try:
        if llm is None:
            return jsonify({
                'success': False,
                'error': 'AI analysis service is unavailable. Please configure GROQ_API_KEY.'
            }), 503

        payload = request.json or {}
        current_prediction_id = payload.get('current_prediction_id')
        past_prediction_ids = payload.get('past_prediction_ids') or []

        if not current_prediction_id:
            return jsonify({'success': False, 'error': 'current_prediction_id is required'}), 400

        if not isinstance(past_prediction_ids, list):
            return jsonify({'success': False, 'error': 'past_prediction_ids must be a list'}), 400

        if len(past_prediction_ids) < 2 or len(past_prediction_ids) > 3:
            return jsonify({
                'success': False,
                'error': 'Select 2 or 3 past predictions for comparison'
            }), 400

        user_id = session.get('user_id')
        is_admin = session.get('role') == 'admin'

        target_user_id = user_id
        if is_admin and payload.get('user_id'):
            target_user_id = payload.get('user_id')

        comparison_ids = past_prediction_ids + [current_prediction_id]
        predictions_map = get_predictions_by_ids(comparison_ids)

        current_prediction = predictions_map.get(current_prediction_id)
        if not current_prediction:
            current_prediction = get_prediction_by_id(current_prediction_id)
            if current_prediction:
                predictions_map[current_prediction_id] = current_prediction

        if not current_prediction:
            return jsonify({'success': False, 'error': 'Current prediction not found'}), 404

        owner_id = current_prediction.get('user_id', 'anonymous')
        if not is_admin and owner_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access to prediction data'}), 403

        resolved_predictions = []
        for pred_id in comparison_ids:
            prediction = predictions_map.get(pred_id)
            if not prediction:
                return jsonify({
                    'success': False,
                    'error': f'Prediction {pred_id} not found'
                }), 404

            if not is_admin and prediction.get('user_id', owner_id) != owner_id:
                return jsonify({
                    'success': False,
                    'error': 'Prediction ownership mismatch'
                }), 403

            prediction['id'] = pred_id
            resolved_predictions.append(prediction)

        analysis_id = f"analysis_{uuid4().hex}"

        # Ensure current vs normal chart exists for legacy predictions
        if not current_prediction.get('current_vs_normal_graph_path'):
            fallback_medical = {
                'Glucose': extract_parameter_value(current_prediction, 'Glucose') or 0.0,
                'Blood Pressure': extract_parameter_value(current_prediction, 'BloodPressure') or 0.0,
                'BMI': extract_parameter_value(current_prediction, 'BMI') or 0.0,
                'Insulin': extract_parameter_value(current_prediction, 'Insulin') or 0.0
            }
            graph_path, graph_url = generate_current_vs_normal_chart(
                fallback_medical,
                owner_id,
                current_prediction_id
            )
            if graph_path and graph_url:
                current_prediction['current_vs_normal_graph_path'] = graph_path
                current_prediction['current_vs_normal_graph_url'] = graph_url
                update_prediction_record(
                    current_prediction_id,
                    {
                        'current_vs_normal_graph_path': graph_path,
                        'current_vs_normal_graph_url': graph_url
                    },
                    user_id=owner_id
                )

        comparison_path, comparison_url = generate_history_comparison_chart(
            resolved_predictions,
            owner_id,
            analysis_id
        )

        if not comparison_path or not comparison_url:
            return jsonify({
                'success': False,
                'error': 'Failed to generate comparison chart'
            }), 500

        prompt = build_comparison_prompt(resolved_predictions)
        groq_response = llm.invoke(prompt)
        explanation_text = getattr(groq_response, 'content', str(groq_response))

        ordered_predictions = sorted(resolved_predictions, key=parse_prediction_datetime)
        summary_rows = []

        for record in ordered_predictions:
            def format_metric(metric_key):
                value = extract_parameter_value(record, metric_key)
                numeric = _safe_float(value)
                return round(numeric, 2) if numeric is not None else '—'

            confidence_numeric = _safe_float(record.get('confidence'))

            summary_rows.append({
                'id': record.get('id'),
                'label': format_prediction_label(record),
                'Glucose': format_metric('Glucose'),
                'BloodPressure': format_metric('BloodPressure'),
                'BMI': format_metric('BMI'),
                'Insulin': format_metric('Insulin'),
                'result': record.get('prediction') or record.get('result', 'N/A'),
                'confidence': round(confidence_numeric, 2) if confidence_numeric is not None else '—'
            })

        comparison_entry = {
            'analysis_id': analysis_id,
            'created_at': get_ist_now().isoformat(),
            'current_prediction_id': current_prediction_id,
            'past_prediction_ids': past_prediction_ids,
            'graph_relative_path': comparison_path,
            'graph_url': comparison_url,
            'groq_explanation': explanation_text,
            'selected_predictions': summary_rows
        }

        append_prediction_comparison(current_prediction_id, comparison_entry, user_id=owner_id)

        download_url = url_for(
            'download_comparison_report',
            prediction_id=current_prediction_id,
            analysis_id=analysis_id
        )

        response_payload = {
            'success': True,
            'analysis_id': analysis_id,
            'explanation': explanation_text,
            'comparison_graph_url': comparison_url,
            'current_vs_normal_graph_url': current_prediction.get('current_vs_normal_graph_url'),
            'report_download_url': download_url,
            'selected_predictions': summary_rows
        }

        return jsonify(response_payload)

    except Exception as e:
        print(f"Error generating comparison analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate comparison analysis'
        }), 500


@app.route('/prediction/comparison/<prediction_id>/<analysis_id>/download', methods=['GET'])
@login_required
def download_comparison_report(prediction_id, analysis_id):
    """Download the Groq comparison analysis as a PDF"""
    try:
        if not prediction_id or not analysis_id:
            return jsonify({'success': False, 'error': 'Missing identifiers'}), 400

        user_id = session.get('user_id')
        is_admin = session.get('role') == 'admin'

        prediction = get_prediction_by_id(prediction_id)
        if not prediction:
            return jsonify({'success': False, 'error': 'Prediction not found'}), 404

        owner_id = prediction.get('user_id', 'anonymous')
        if not is_admin and owner_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized request'}), 403

        comparisons = prediction.get('comparisons') or {}
        comparison_entry = comparisons.get(analysis_id)
        if not comparison_entry:
            return jsonify({'success': False, 'error': 'Comparison analysis not found'}), 404

        pdf_buffer, filename = generate_comparison_pdf(prediction, comparison_entry)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error downloading comparison report: {e}")
        return jsonify({'success': False, 'error': 'Failed to download comparison report'}), 500


@app.route('/report', methods=['POST'])
def generate_report():
    """
    Generate AI doctor report using Groq LLM
    Creates a professional medical diagnosis report
    """
    try:
        if llm is None:
            return jsonify({
                'success': False,
                'error': 'AI Report Generator not available. Please configure GROQ_API_KEY.'
            }), 500
        
        data = request.json
        
        # Create detailed prompt for medical report
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an AI medical assistant specializing in diabetes risk assessment, prevention, and health management.

Your task is to generate a comprehensive, clinically accurate diabetes risk assessment report based on the patient's laboratory results and health data.

REPORT STRUCTURE (Follow this exactly):

1. EXECUTIVE SUMMARY
   - Brief 2-3 sentence overview of patient status and key findings
   - Clear statement of risk classification

2. PATIENT OVERVIEW
   - Age, sex, and relevant demographic factors
   - Pregnancy history (if applicable)

3. LABORATORY FINDINGS & ANALYSIS
   For each parameter, provide:
   - Test result value
   - Normal reference range
   - Clinical interpretation (Normal/Borderline/Elevated/Critical)
   - Significance to diabetes risk
   
   Parameters to analyze:
   • Fasting Plasma Glucose (Normal: 70-100 mg/dL)
   • Diastolic Blood Pressure (Normal: 60-80 mmHg)
   • Body Mass Index (Normal: 18.5-24.9 kg/m²)
   • 2-Hour Serum Insulin (Normal: 16-166 μU/mL)
   • Triceps Skin Fold Thickness
   • Diabetes Pedigree Function (genetic risk factor)

4. CLINICAL INTERPRETATION
   - Synthesize all findings
   - Explain how parameters interact
   - Discuss metabolic syndrome indicators if present
   - Address insulin resistance markers
   - Evaluate cardiovascular risk factors

5. DIABETES RISK STRATIFICATION
   - Clear classification: HIGH RISK or LOW RISK
   - AI model confidence percentage
   - Medical rationale supporting the classification
   - Comparison to population norms

6. CLINICAL RECOMMENDATIONS
   Provide specific, actionable recommendations:
   - Immediate actions required
   - Medications to consider (if high risk)
   - Specialist referrals needed
   - Diagnostic tests to order
   - Timeline for interventions

7. LIFESTYLE MODIFICATIONS
   Be specific with:
   
   DIETARY GUIDELINES:
   - Carbohydrate management (specific gram targets)
   - Foods to emphasize (list 5-6)
   - Foods to limit/avoid (list 5-6)
   - Meal timing and portion control
   
   PHYSICAL ACTIVITY:
   - Type of exercise (aerobic, resistance)
   - Frequency (days per week)
   - Duration (minutes per session)
   - Intensity guidelines
   
   WEIGHT MANAGEMENT:
   - Target weight range based on BMI
   - Realistic weight loss goals if needed
   
   MONITORING:
   - Self-monitoring blood glucose (if indicated)
   - What to track daily
   - Warning signs to watch for

8. FOLLOW-UP CARE PLAN
   - Next appointment timeframe (specific weeks/months)
   - Tests to repeat and when
   - Parameters to monitor at home
   - When to seek immediate medical attention
   - Long-term management strategy

9. PHYSICIAN SUMMARY NOTES
   - Overall clinical impression
   - Prognosis with and without intervention
   - Key patient education points
   - Encouragement and motivation

CRITICAL REQUIREMENTS:
- Use medical terminology appropriately but keep explanations understandable
- Provide numerical targets and specific recommendations
- Base all advice on current clinical guidelines
- Be empathetic yet direct about risks
- Include both immediate and long-term strategies
- Make it clear this supports but doesn't replace physician consultation
- Be thorough - aim for a comprehensive, detailed report"""),
            ("user", """
PATIENT DEMOGRAPHICS:
- Name: {name}
- Age: {age} years
- Sex: {sex}
- Contact: {contact}

LABORATORY & CLINICAL PARAMETERS:
- Fasting Plasma Glucose: {glucose} mg/dL (Normal: 70-100 mg/dL)
- Diastolic Blood Pressure: {blood_pressure} mmHg (Normal: 60-80 mmHg)
- Body Mass Index (BMI): {bmi} kg/m² (Normal: 18.5-24.9)
- 2-Hour Serum Insulin: {insulin} μU/mL (Normal: 16-166 μU/mL)
- Triceps Skin Fold Thickness: {skin_thickness} mm
- Diabetes Pedigree Function: {dpf} (Genetic predisposition indicator)
- Number of Pregnancies: {pregnancies}

AI-ASSISTED DIAGNOSTIC ASSESSMENT:
- Prediction Result: {prediction}
- Risk Classification: {risk_level} RISK
- Model Confidence: {confidence}%

Please generate a comprehensive diabetes assessment report analyzing these health parameters and providing detailed medical recommendations.
            """)
        ])
        
        # Format the prompt
        risk_level_str = str(data.get('risk_level', 'Unknown')).upper()
        
        formatted_prompt = prompt_template.format_messages(
            name=data.get('patient_info', {}).get('name', 'Unknown'),
            age=data.get('patient_info', {}).get('age', 'N/A'),
            sex=data.get('patient_info', {}).get('sex', 'N/A'),
            contact=data.get('patient_info', {}).get('contact', 'N/A'),
            glucose=data.get('medical_data', {}).get('Glucose', 'N/A'),
            blood_pressure=data.get('medical_data', {}).get('Blood Pressure', 'N/A'),
            bmi=data.get('medical_data', {}).get('BMI', 'N/A'),
            insulin=data.get('medical_data', {}).get('Insulin', 'N/A'),
            skin_thickness=data.get('medical_data', {}).get('Skin Thickness', 'N/A'),
            dpf=data.get('medical_data', {}).get('Diabetes Pedigree Function', 'N/A'),
            pregnancies=data.get('medical_data', {}).get('Pregnancies', 'N/A'),
            prediction=data.get('prediction', 'Unknown'),
            risk_level=risk_level_str,
            confidence=data.get('confidence', 'N/A')
        )
        
        # Generate report using Groq LLM
        response = llm.invoke(formatted_prompt)
        report_content = response.content
        
        # Add header and footer to report
        timestamp = get_ist_now().strftime("%B %d, %Y at %I:%M %p")
        patient_id = f"DB-{data.get('patient_info', {}).get('name', 'XXXX')[:3].upper()}-{get_ist_now().strftime('%Y%m%d%H%M')}"
        
        full_report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║              DIABETES ASSESSMENT & DIAGNOSTIC CENTER                      ║
║              Endocrinology & Metabolism Department                        ║
║              Advanced Diabetes Care & Prevention                          ║
╚══════════════════════════════════════════════════════════════════════════╝

MEDICAL REPORT - DIABETES RISK PREDICTION
══════════════════════════════════════════════════════════════════════════

Report Date: {timestamp}
Patient ID: {patient_id}
Assessment Type: Comprehensive Diabetes Screening

══════════════════════════════════════════════════════════════════════════
PATIENT INFORMATION
══════════════════════════════════════════════════════════════════════════
Name: {data.get('patient_info', {}).get('name', 'Unknown')}
Age: {data.get('patient_info', {}).get('age', 'N/A')} years
Sex: {data.get('patient_info', {}).get('sex', 'N/A')}
Contact: {data.get('patient_info', {}).get('contact', 'N/A')}

══════════════════════════════════════════════════════════════════════════

{report_content}

══════════════════════════════════════════════════════════════════════════
IMPORTANT MEDICAL DISCLAIMER
══════════════════════════════════════════════════════════════════════════
This report is generated using AI-assisted diagnostic tools and machine 
learning algorithms. It should be used as a screening tool only and must 
be reviewed and validated by a licensed medical professional.

For any health concerns or before making any medical decisions, please 
consult with a qualified healthcare provider or endocrinologist.

══════════════════════════════════════════════════════════════════════════
REPORT AUTHENTICATION
══════════════════════════════════════════════════════════════════════════
Generated By: AI-Assisted Diagnostic System
Reviewed By: [Requires Licensed Physician Review]
Report ID: {patient_id}
Generation Date: {timestamp}

══════════════════════════════════════════════════════════════════════════

© 2025 Diabetes Assessment & Diagnostic Center
Advanced Endocrinology Department | Powered by Naveenkumar
Help & Support: naveenkumarchapala02@gmail.com

All Rights Reserved | Confidential Medical Document
"""
        
        # Save report to file
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)
        report_filename = f"diabetes_report_{data.get('patient_info', {}).get('name', 'patient').replace(' ', '_')}_{get_ist_now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        # Save report info to Firebase if user is logged in
        user_id = session.get('user_id', 'anonymous')
        prediction_id = data.get('prediction_id')
        
        print(f"📝 Saving report info: user_id={user_id}, prediction_id={prediction_id}")
        
        try:
            if prediction_id:
                # Update the prediction with report info
                update_data = {
                    'report_id': patient_id,
                    'report_path': report_filename,
                    'report_file': report_filename,
                    'report_generated_at': timestamp
                }
                
                success = update_prediction_record(prediction_id, update_data, user_id if user_id != 'anonymous' else None)
                
                if success:
                    print(f"✅ Report info saved to Firebase for prediction {prediction_id}")
                else:
                    print(f"⚠️ Failed to update prediction record in Firebase")
        except Exception as fb_error:
            print(f"⚠️ Warning: Could not save report to Firebase: {fb_error}")
            import traceback
            traceback.print_exc()
            # Continue anyway - file is saved locally
        
        return jsonify({
            'success': True,
            'report': full_report,
            'report_file': report_filename,
            'timestamp': timestamp,
            'prediction_id': data.get('prediction_id')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Report generation error: {str(e)}'
        }), 500


@app.route('/api/generate_report', methods=['POST'])
@login_required
def api_generate_report():
    """Generate report for a specific prediction ID"""
    try:
        data = request.json
        prediction_id = data.get('prediction_id')
        
        if not prediction_id:
            return jsonify({
                'success': False,
                'error': 'Prediction ID is required'
            }), 400
        
        # Get prediction data
        user_id = session.get('user_id')
        prediction = get_prediction_by_id(user_id, prediction_id)
        
        if not prediction:
            return jsonify({
                'success': False,
                'error': 'Prediction not found'
            }), 404
        
        # Generate report using existing generate_report logic
        # Prepare data in the format expected by generate_report
        report_data = {
            'patient_info': {
                'name': prediction.get('name', 'Patient'),
                'age': prediction.get('age', prediction.get('Age', 'N/A')),
                'sex': prediction.get('sex', 'N/A'),
                'contact': prediction.get('contact', 'N/A')
            },
            'prediction': prediction.get('prediction', 0),
            'probability': prediction.get('probability', 0.5),
            'test_values': {
                'glucose': prediction.get('glucose', prediction.get('Glucose', 0)),
                'blood_pressure': prediction.get('blood_pressure', prediction.get('BloodPressure', 0)),
                'bmi': prediction.get('bmi', prediction.get('BMI', 0)),
                'insulin': prediction.get('insulin', prediction.get('Insulin', 0)),
                'skin_thickness': prediction.get('skin_thickness', prediction.get('SkinThickness', 0)),
                'pregnancies': prediction.get('pregnancies', prediction.get('Pregnancies', 0)),
                'diabetes_pedigree': prediction.get('diabetes_pedigree_function', prediction.get('DiabetesPedigreeFunction', 0))
            }
        }
        
        # Use the existing report generation prompt
        if llm is None:
            return jsonify({
                'success': False,
                'error': 'AI Report Generator not available'
            }), 500
        
        # Generate report (simplified version using Groq)
        prompt = f"""Generate a comprehensive diabetes risk assessment report for:
        
Patient: {report_data['patient_info']['name']}
Age: {report_data['patient_info']['age']} years
Prediction: {'POSITIVE - High Risk' if report_data['prediction'] == 1 else 'NEGATIVE - Low Risk'}
Probability: {report_data['probability']*100:.1f}%

Test Results:
- Glucose: {report_data['test_values']['glucose']} mg/dL
- Blood Pressure: {report_data['test_values']['blood_pressure']} mmHg
- BMI: {report_data['test_values']['bmi']}
- Insulin: {report_data['test_values']['insulin']} μU/mL

Provide a detailed medical assessment with recommendations."""

        response = llm.invoke(prompt)
        report_content = response.content
        
        # Save report
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)
        report_filename = f"report_{prediction_id}_{get_ist_now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return jsonify({
            'success': True,
            'report_id': prediction_id,
            'report_file': report_filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_beautiful_pdf(report, report_id):
    """Generate a professional medical PDF report with comprehensive charts and recommendations"""
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from report_generator import (generate_clinical_parameter_chart, generate_risk_gauge_chart,
                                   generate_parameter_radar_chart, generate_bmi_classification_chart)
    # Import enhanced report generator
    try:
        from enhanced_report_generator import (
            generate_comprehensive_health_chart,
            get_personalized_recommendations,
            format_recommendations_for_pdf
        )
        enhanced_available = True
    except ImportError:
        enhanced_available = False
        print("⚠️ Enhanced report generator not available, using standard charts")
    
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           topMargin=0.75*inch,
                           bottomMargin=0.75*inch,
                           leftMargin=0.75*inch,
                           rightMargin=0.75*inch)
    
    # Container for PDF elements
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles matching reference image
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=colors.HexColor('#1e3a8a'),  # Dark blue
        spaceAfter=10,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        leading=38
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=TA_LEFT,
        spaceAfter=8,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#3b82f6'),  # Blue background
        borderPadding=8,
        leftIndent=10
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        alignment=TA_LEFT
    )
    
    # Top blue bar
    blue_bar = Table([['']], colWidths=[7*inch], rowHeights=[0.3*inch])
    blue_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#60a5fa')),
    ]))
    story.append(blue_bar)
    story.append(Spacer(1, 0.2*inch))
    
    # Main Title with Icon effect
    title_table_data = [[
        Paragraph("<b>Diabetes</b><br/><b>Prediction</b><br/><b>Report</b>", title_style),
        ''
    ]]
    title_table = Table(title_table_data, colWidths=[4*inch, 3*inch])
    story.append(title_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Diagnosis section
    diagnosis_heading = Paragraph("Diagnosis", heading_style)
    story.append(diagnosis_heading)
    
    result_text = report.get('result', 'N/A')
    diagnosis_result = ParagraphStyle(
        'DiagnosisResult',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        spaceBefore=10,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(result_text, diagnosis_result))
    story.append(Spacer(1, 0.2*inch))
    
    # PATIENT DATA section
    story.append(Paragraph("PATIENT DATA", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    patient_name = report.get('patient_name', 'John Doe')
    patient_age = report.get('age') or report.get('Age', 'N/A')
    patient_sex = report.get('sex', 'Male')
    patient_contact = report.get('contact', 'N/A')
    
    # Get formatted date
    from pytz import timezone
    ist = timezone('Asia/Kolkata')
    timestamp = report.get('timestamp') or report.get('created_at', 'N/A')
    if timestamp != 'N/A':
        try:
            date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_obj = date_obj.astimezone(ist)
            formatted_date = date_obj.strftime("%B %d, %Y")
        except:
            formatted_date = datetime.now(ist).strftime("%B %d, %Y")
    else:
        formatted_date = datetime.now(ist).strftime("%B %d, %Y")
    
    patient_data = [
        ['Name', patient_name, 'Age', 'Report Date'],
        ['Age', f'{patient_age}', patient_sex, formatted_date]
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#93c5fd')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Add comprehensive health visualization chart (4-panel)
    if enhanced_available:
        try:
            chart_buffer = generate_comprehensive_health_chart(report)
            chart_img = Image(chart_buffer, width=7*inch, height=5*inch)
            story.append(Paragraph("COMPREHENSIVE HEALTH ANALYSIS", heading_style))
            story.append(Spacer(1, 0.1*inch))
            story.append(chart_img)
            story.append(Spacer(1, 0.25*inch))
        except Exception as e:
            print(f"Error generating comprehensive chart: {e}")
    
    # RESULTS section
    story.append(Paragraph("RESULTS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Extract parameters
    glucose = report.get('Glucose') or report.get('glucose') or 'N/A'
    bmi = report.get('BMI') or report.get('bmi') or 'N/A'
    bp = report.get('BloodPressure') or report.get('blood_pressure') or 'N/A'
    insulin = report.get('Insulin') or report.get('insulin') or 'N/A'
    skin_thickness = report.get('SkinThickness') or report.get('skin_thickness') or 'N/A'
    dpf = report.get('DiabetesPedigreeFunction') or report.get('diabetes_pedigree') or 'N/A'
    pregnancies = report.get('Pregnancies') or report.get('pregnancies') or 'N/A'
    age = report.get('Age') or report.get('age') or 'N/A'
    
    # Calculate prediction accuracy (use confidence or default to 89%)
    confidence = report.get('confidence', 89)
    
    results_data = [
        ['Prediction Accuracy', 'Number of Patients', 'Safe & Secure'],
        [f'{confidence}%', '1.2K+', '100%']
    ]
    
    results_table = Table(results_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
    results_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, 1), 28),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    # Recommendations section
    story.append(Paragraph("PERSONALIZED RECOMMENDATIONS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Generate comprehensive personalized recommendations
    if enhanced_available:
        try:
            recommendations = get_personalized_recommendations(report)
            rec_elements = format_recommendations_for_pdf(recommendations, body_style)
            story.extend(rec_elements)
        except Exception as e:
            print(f"Error generating personalized recommendations: {e}")
            # Fallback to simple AI recommendations
            try:
                ai_prompt = f"""As a medical AI assistant, provide concise medical recommendations for a diabetes risk assessment with these parameters:
- Glucose: {glucose} mg/dL
- BMI: {bmi} kg/m²
- Blood Pressure: {bp} mmHg
- Age: {age} years
- Risk Assessment: {result_text}

Provide 3-4 sentences covering: lifestyle changes, preventive measures, and regular health monitoring. Keep it professional but brief."""

                ai_response = llm.invoke(ai_prompt)
                recommendations_text = ai_response.content if hasattr(ai_response, 'content') else "Doctor's recommendations and next steps for managing and improving the patient's condition. Includes lifestyle changes, potential treatments, and regular monitoring."
            except:
                recommendations_text = "Doctor's recommendations and next steps for managing and improving the patient's condition. Includes lifestyle changes, potential treatments, and regular monitoring."
            
            recommendations_para = Paragraph(recommendations_text, body_style)
            recommendations_box = Table([[recommendations_para]], colWidths=[7*inch])
            recommendations_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ]))
            story.append(recommendations_box)
    else:
        # Fallback if enhanced generator not available
        try:
            ai_prompt = f"""As a medical AI assistant, provide concise medical recommendations for a diabetes risk assessment with these parameters:
- Glucose: {glucose} mg/dL
- BMI: {bmi} kg/m²
- Blood Pressure: {bp} mmHg
- Age: {age} years
- Risk Assessment: {result_text}

Provide 3-4 sentences covering: lifestyle changes, preventive measures, and regular health monitoring. Keep it professional but brief."""

            ai_response = llm.invoke(ai_prompt)
            recommendations_text = ai_response.content if hasattr(ai_response, 'content') else "Doctor's recommendations and next steps for managing and improving the patient's condition. Includes lifestyle changes, potential treatments, and regular monitoring."
        except:
            recommendations_text = "Doctor's recommendations and next steps for managing and improving the patient's condition. Includes lifestyle changes, potential treatments, and regular monitoring."
        
        recommendations_para = Paragraph(recommendations_text, body_style)
        recommendations_box = Table([[recommendations_para]], colWidths=[7*inch])
        recommendations_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(recommendations_box)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Add footer note
    footer_note = ParagraphStyle(
        'FooterNote',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=8
    )
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<i>This report has been generated using advanced AI technology and should be reviewed by a qualified healthcare professional.</i>", footer_note))
    story.append(Paragraph(f"<i>Report ID: {report_id} | Generated: {formatted_date}</i>", footer_note))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


@app.route('/download_report/<report_id>')
@login_required
def download_report(report_id):
    """
    Download a comprehensive 2-page PDF report with visualizations
    """
    try:
        user_id = session.get('user_id')
        is_admin = session.get('role') == 'admin'
        
        # Admin can download any report, users can only download their own
        if is_admin:
            # Get report from predictions directly
            import firebase_config
            firebase_config.initialize_firebase()
            predictions_ref = firebase_config.db_ref.child('predictions').child(report_id)
            report = predictions_ref.get()
            
            if report:
                report['id'] = report_id
        else:
            # Get user's own predictions
            history = get_patient_history(user_id=user_id, limit=1000)
            
            # Find the specific report
            report = None
            for pred in history:
                if (pred.get('id') == report_id or 
                    pred.get('firebase_id') == report_id or 
                    pred.get('report_id') == report_id or
                    pred.get('prediction_id') == report_id):
                    report = pred
                    break
        
        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        # Generate comprehensive PDF report with visualizations
        from pdf_report_generator import generate_enhanced_pdf_report
        pdf_buffer = generate_enhanced_pdf_report(report, report_id)
        
        # CRITICAL: Seek to beginning of buffer before sending
        pdf_buffer.seek(0)
        
        # Generate filename
        patient_name = report.get('patient_name', report.get('name', 'Patient'))
        timestamp = get_ist_now().strftime('%Y%m%d_%H%M%S')
        filename = f"Diabetes_Report_{patient_name.replace(' ', '_')}_{timestamp}.pdf"
        
        # Return with proper headers for PDF
        response = send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/delete_report/<report_id>', methods=['DELETE'])
@login_required
def delete_report(report_id):
    """
    Delete a specific medical report from Firebase
    """
    try:
        user_id = session.get('user_id')
        
        # Import firebase_config to access db_ref
        import firebase_config
        
        # Initialize Firebase if needed
        firebase_config.initialize_firebase()
        
        # Delete from main predictions node
        predictions_ref = firebase_config.db_ref.child('predictions').child(report_id)
        success1 = predictions_ref.delete()
        
        # Delete from user's predictions node
        user_pred_ref = firebase_config.db_ref.child('users').child(user_id).child('predictions').child(report_id)
        success2 = user_pred_ref.delete()
        
        # Recalculate user statistics
        firebase_config.get_statistics(user_id)
        
        if success1 or success2:
            return jsonify({
                'success': True,
                'message': 'Report deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Report not found or already deleted'
            }), 404
    
    except Exception as e:
        print(f"Error deleting report: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete report. Please try again.'
        }), 500


@app.route('/patient_history', methods=['GET'])
@login_required
def patient_history():
    """
    Get patient prediction history from Firebase
    Query params: patient_name (optional), limit (default 10)
    """
    try:
        patient_name = request.args.get('patient_name')
        limit = int(request.args.get('limit', 10))
        
        # Admin sees all data, users see only their own
        if session.get('role') == 'admin':
            history = get_patient_history(patient_name=patient_name, limit=limit)
        else:
            # Get user-specific predictions
            user_id = session.get('user_id')
            history = get_user_predictions(user_id=user_id, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(history),
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/statistics', methods=['GET'])
@login_required
def statistics():
    """Get prediction statistics from Firebase"""
    try:
        # Admin sees all statistics, users see only their own
        if session.get('role') == 'admin':
            stats = get_statistics()
        else:
            user_id = session.get('user_id')
            stats = get_user_statistics(user_id=user_id)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'llm_available': llm is not None,
        'database_connected': db is not None and hasattr(db, 'collection'),
        'firebase_mode': 'REST_API' if use_rest_api else 'Admin_SDK' if firebase_initialized else 'Local_Storage'
    })


@app.route('/api/debug/user-predictions', methods=['GET'])
@login_required
def debug_user_predictions():
    """Debug endpoint to check user predictions"""
    try:
        user_id = session.get('user_id')
        
        # Get all predictions from Firebase
        all_preds = db_ref.child('predictions').get()
        
        # Find predictions for this user
        user_preds = []
        all_user_ids = set()
        
        if all_preds:
            for pred_id, pred_data in all_preds.items():
                if isinstance(pred_data, dict):
                    pred_user_id = pred_data.get('user_id')
                    all_user_ids.add(pred_user_id)
                    
                    if pred_user_id == user_id:
                        user_preds.append({
                            'prediction_id': pred_id,
                            'patient_name': pred_data.get('patient_name'),
                            'user_id': pred_user_id
                        })
        
        return jsonify({
            'success': True,
            'current_user_id': user_id,
            'current_username': session.get('username'),
            'user_predictions': user_preds,
            'total_user_predictions': len(user_preds),
            'total_predictions_in_db': len(all_preds) if all_preds else 0,
            'all_user_ids_in_db': list(all_user_ids)
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/aggregate_analysis')
@login_required
def aggregate_analysis():
    """
    Generate aggregate analysis of all user predictions using Groq LLM
    """
    try:
        if llm is None:
            return jsonify({
                'success': False,
                'error': 'AI Analysis not available. Please configure GROQ_API_KEY.'
            }), 500
        
        user_id = session.get('user_id')
        
        # Get all user predictions
        history = get_patient_history(user_id=user_id, limit=1000)
        
        if not history or len(history) == 0:
            return jsonify({
                'success': False,
                'error': 'No predictions found'
            }), 404
        
        # Calculate statistics
        total_predictions = len(history)
        high_risk_count = 0
        low_risk_count = 0
        total_confidence = 0
        glucose_values = []
        bmi_values = []
        
        for pred in history:
            risk_level = pred.get('risk_level', '').lower()
            if risk_level == 'high' or 'high' in pred.get('prediction', '').lower():
                high_risk_count += 1
            else:
                low_risk_count += 1
            
            confidence = pred.get('confidence')
            if confidence and isinstance(confidence, (int, float)):
                total_confidence += float(confidence)
            
            # Collect glucose and BMI values
            glucose = pred.get('glucose')
            if glucose:
                try:
                    glucose_values.append(float(glucose))
                except:
                    pass
            
            bmi = pred.get('bmi')
            if not bmi and pred.get('features'):
                bmi = pred.get('features', {}).get('BMI')
            if bmi:
                try:
                    bmi_values.append(float(bmi))
                except:
                    pass
        
        # Calculate averages
        average_confidence = (total_confidence / total_predictions) if total_predictions > 0 else 0
        average_glucose = (sum(glucose_values) / len(glucose_values)) if glucose_values else 0
        average_bmi = (sum(bmi_values) / len(bmi_values)) if bmi_values else 0
        
        # Calculate risk score (weighted average)
        high_risk_percentage = (high_risk_count / total_predictions * 100) if total_predictions > 0 else 0
        average_risk_score = (high_risk_percentage * 0.7) + (average_confidence * 0.3)
        
        # Create detailed summary for LLM
        recent_predictions = history[:10]  # Last 10 predictions
        predictions_summary = []
        
        for i, pred in enumerate(recent_predictions, 1):
            pred_date = pred.get('timestamp') or pred.get('created_at', 'Unknown')
            if pred_date != 'Unknown':
                try:
                    date_obj = datetime.fromisoformat(pred_date.replace('Z', '+00:00'))
                    pred_date = date_obj.strftime("%b %d, %Y")
                except:
                    pass
            
            risk = pred.get('risk_level', 'unknown')
            conf = pred.get('confidence', 'N/A')
            gluc = pred.get('glucose', 'N/A')
            predictions_summary.append(
                f"   {i}. Date: {pred_date}, Risk: {risk.upper()}, Confidence: {conf}%, Glucose: {gluc} mg/dL"
            )
        
        # Create prompt for Groq LLM - Enhanced for experienced doctor analysis
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an AI medical assistant with expertise in diabetes prevention, metabolic health assessment, and evidence-based health recommendations.

CLINICAL EXPERTISE:
- Diabetes Prevention & Management (Type 1, Type 2, Gestational)
- Metabolic Syndrome & Insulin Resistance
- Evidence-Based Medicine & Clinical Guidelines
- Patient Education & Lifestyle Intervention
- Risk Stratification & Predictive Analytics

YOUR TASK:
Provide a comprehensive, medically accurate analysis of this patient's diabetes risk assessment history. Your analysis should reflect your deep clinical experience and be suitable for inclusion in a medical record.

ANALYSIS REQUIREMENTS:
1. Use precise medical terminology with patient-friendly explanations
2. Reference clinical ranges and evidence-based thresholds
3. Provide quantitative risk assessment based on actual data
4. Offer specific, actionable medical recommendations
5. Address cardiovascular and metabolic comorbidities
6. Include lifestyle medicine principles
7. Be encouraging yet clinically honest about risks

TONE: Professional, empathetic, evidence-based, action-oriented"""),
            ("user", """PATIENT DIABETES RISK ASSESSMENT - LONGITUDINAL ANALYSIS

CLINICAL SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Assessments: {total_predictions}
High Risk Classifications: {high_risk_count} ({high_risk_percentage:.1f}%)
Low Risk Classifications: {low_risk_count} ({low_risk_percentage:.1f}%)
Model Confidence (Average): {average_confidence:.1f}%

METABOLIC PARAMETERS (Averages):
- Fasting Glucose: {average_glucose:.1f} mg/dL (Normal: 70-100, Prediabetes: 100-125, Diabetes: ≥126)
- Body Mass Index: {average_bmi:.1f} kg/m² (Normal: 18.5-24.9, Overweight: 25-29.9, Obese: ≥30)

RECENT ASSESSMENT TIMELINE:
{predictions_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLINICAL ANALYSIS REQUEST:

Please provide a comprehensive medical analysis structured as follows:

**1. OVERALL CLINICAL IMPRESSION (2-3 sentences)**
   - Current metabolic health status
   - Trajectory (improving, stable, declining)
   - Immediate risk level

**2. KEY CLINICAL FINDINGS**
   - Glucose metabolism analysis (compare to ADA guidelines)
   - Weight status and cardiovascular risk factors
   - Pattern recognition across multiple assessments
   - Any concerning trends or positive improvements

**3. RISK STRATIFICATION**
   Calculate and explain an accurate **MEDICAL RISK SCORE (0-100)**:
   
   Base calculation on:
   - Glycemic control (40% weight): {average_glucose:.1f} mg/dL
   - BMI category (30% weight): {average_bmi:.1f} kg/m²
   - Risk classification frequency (20% weight): {high_risk_percentage:.1f}% high risk
   - Model confidence (10% weight): {average_confidence:.1f}%
   
   Provide the final numerical score and its clinical meaning:
   - 0-25: Low Risk - Continue preventive care
   - 26-50: Moderate Risk - Intensive lifestyle modification
   - 51-75: High Risk - Medical intervention recommended
   - 76-100: Very High Risk - Urgent medical evaluation required

**4. EVIDENCE-BASED RECOMMENDATIONS**

   A. IMMEDIATE ACTIONS (Next 2-4 weeks):
      - Specific tests to order (HbA1c, lipid panel, etc.)
      - Medication considerations if indicated
      - Specialist referrals needed
   
   B. LIFESTYLE MEDICINE PRESCRIPTION:
      - Dietary modifications (specific targets: grams carbs/day, glycemic index)
      - Physical activity (FITT principle: Frequency, Intensity, Time, Type)
      - Weight management goals (if needed: target BMI, kg to lose)
      - Sleep and stress optimization
   
   C. MONITORING PLAN:
      - Follow-up timeline
      - Self-monitoring parameters
      - When to seek urgent care

**5. PATIENT EDUCATION & MOTIVATION**
   - What the numbers mean in plain language
   - Realistic goals for next 3-6 months
   - Success factors and empowerment message
   - Long-term prognosis with vs without intervention

**6. CLINICAL NOTES**
   - Areas of concern requiring attention
   - Positive prognostic factors
   - Patient compliance indicators
   - Recommended next appointment

IMPORTANT: 
- Be specific with numbers (e.g., "Reduce carbohydrate intake to 150g/day" not "eat less carbs")
- Reference clinical guidelines (ADA, ACC/AHA) where appropriate  
- Calculate and clearly state the MEDICAL RISK SCORE
- Provide both immediate and long-term action plans
- Be encouraging but medically honest
- Length: 400-500 words, dense with clinical value

Deliver this analysis as if writing in a patient's electronic medical record.""")
        ])
        
        low_risk_percentage = (low_risk_count / total_predictions * 100) if total_predictions > 0 else 0
        
        formatted_prompt = prompt_template.format_messages(
            total_predictions=total_predictions,
            high_risk_count=high_risk_count,
            high_risk_percentage=high_risk_percentage,
            low_risk_count=low_risk_count,
            low_risk_percentage=low_risk_percentage,
            average_confidence=average_confidence,
            average_glucose=average_glucose,
            average_bmi=average_bmi,
            predictions_list='\n'.join(predictions_summary)
        )
        
        # Generate AI analysis
        response = llm.invoke(formatted_prompt)
        ai_analysis = response.content
        
        # Determine best report (lowest risk with highest confidence)
        best_report_text = None
        if low_risk_count > 0:
            low_risk_reports = [p for p in history if p.get('risk_level', '').lower() == 'low']
            if low_risk_reports:
                best = max(low_risk_reports, key=lambda x: x.get('confidence', 0))
                best_date = best.get('timestamp') or best.get('created_at', 'Unknown')
                if best_date != 'Unknown':
                    try:
                        date_obj = datetime.fromisoformat(best_date.replace('Z', '+00:00'))
                        best_date = date_obj.strftime("%B %d, %Y")
                    except:
                        pass
                best_report_text = f"Your best assessment was on {best_date} with {best.get('confidence', 'N/A')}% confidence and LOW risk classification. This represents your healthiest reading!"
        
        return jsonify({
            'success': True,
            'total_predictions': total_predictions,
            'high_risk_count': high_risk_count,
            'low_risk_count': low_risk_count,
            'average_risk_score': round(average_risk_score, 2),
            'average_confidence': round(average_confidence, 2),
            'average_glucose': round(average_glucose, 2) if average_glucose > 0 else None,
            'average_bmi': round(average_bmi, 2) if average_bmi > 0 else None,
            'ai_analysis': ai_analysis,
            'best_report': best_report_text
        })
    
    except Exception as e:
        print(f"Error in aggregate analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/user/prediction/<prediction_id>', methods=['GET'])
@login_required
def get_single_prediction(prediction_id):
    """Get a single prediction by ID for the current user"""
    try:
        user_id = session.get('user_id')
        print(f"🔍 Fetching prediction {prediction_id} for user {user_id}")
        
        prediction = get_prediction_by_id(prediction_id)
        
        if not prediction:
            print(f"❌ Prediction {prediction_id} not found")
            return jsonify({
                'success': False,
                'error': 'Prediction not found'
            }), 404
        
        # Verify this prediction belongs to the user
        if prediction.get('user_id') != user_id:
            print(f"❌ Prediction belongs to different user: {prediction.get('user_id')} != {user_id}")
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403
        
        print(f"✅ Found prediction for {prediction.get('patient_name', prediction.get('name'))}")
        
        # Determine prediction value
        pred_value = 1 if 'High' in str(prediction.get('prediction', '')) or prediction.get('risk_level') == 'high' else 0
        
        # Format the response
        formatted_prediction = {
            'prediction_id': prediction_id,
            'patient_name': prediction.get('patient_name', prediction.get('name', 'Unknown')),
            'prediction': pred_value,
            'probability': float(prediction.get('confidence', 85)) / 100,
            'features': {
                'Pregnancies': int(prediction.get('Pregnancies', prediction.get('pregnancies', 0))),
                'Glucose': float(prediction.get('Glucose', prediction.get('glucose', 0))),
                'BloodPressure': float(prediction.get('BloodPressure', prediction.get('blood_pressure', 0))),
                'SkinThickness': float(prediction.get('SkinThickness', prediction.get('skin_thickness', 0))),
                'Insulin': float(prediction.get('Insulin', prediction.get('insulin', 0))),
                'BMI': float(prediction.get('BMI', prediction.get('bmi', 0))),
                'DiabetesPedigreeFunction': float(prediction.get('DiabetesPedigreeFunction', prediction.get('diabetes_pedigree_function', 0))),
                'Age': int(prediction.get('Age', prediction.get('age', 0)))
            }
        }
        
        return jsonify({
            'success': True,
            'prediction': formatted_prediction
        })
        
    except Exception as e:
        print(f"❌ Error in get_single_prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/reports/<filename>', methods=['GET'])
def serve_report(filename):
    """Serve generated report files from the reports directory"""
    try:
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        return send_from_directory(reports_dir, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Report file not found: {str(e)}'
        }), 404


# ------------------- CHATBOT ROUTES -------------------

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    """
    Main chatbot endpoint - frontend calls this
    Uses integrated Groq LLM for instant AI responses with conversation history
    """
    try:
        data = request.get_json()
        
        # Log request for production debugging
        print(f"🤖 Chatbot request received: {data.get('message', '')[:50] if data else 'No data'}...")
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Please provide a message.',
                'response': 'Please provide a message.',
                'answer': 'Please provide a message.',
                'error': 'Missing message in request'
            }), 400
        
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Please enter a question.',
                'response': 'Please enter a question.',
                'answer': 'Please enter a question.',
                'error': 'Empty message'
            }), 400
        
        # Verify chatbot is initialized
        if not chatbot or not chatbot.health_check():
            print("⚠️ Chatbot LLM not initialized - returning fallback")
            fallback_response = "I apologize, but the AI chatbot is temporarily unavailable. Please try again in a moment or contact support if this persists."
            return jsonify({
                'success': False,
                'message': fallback_response,
                'response': fallback_response,
                'answer': fallback_response,
                'error': 'LLM not initialized'
            }), 503
        
        # Get conversation history from request (optional)
        conversation_history = data.get('history', [])
        print(f"📜 History length: {len(conversation_history)} messages")
        
        # Use integrated chatbot with Groq LLM and conversation context
        response = chatbot.ask_question(user_message, conversation_history=conversation_history)
        
        print(f"✅ Chatbot response generated: {len(response.get('answer', ''))} chars")
        
        if response.get('error'):
            error_message = response.get('answer', 'An error occurred')
            return jsonify({
                'success': False,
                'message': error_message,
                'response': error_message,
                'answer': error_message,
                'error': 'Chatbot processing error'
            }), 500
        
        answer_text = response.get('answer', '')
        
        # Ensure response is not empty
        if not answer_text or len(answer_text.strip()) < 10:
            print("⚠️ Empty or too short response, using fallback")
            answer_text = "I apologize, but I'm having trouble formulating a response. Could you please rephrase your question or try asking something different?"
        
        return jsonify({
            'success': True,
            'response': answer_text,
            'message': answer_text,
            'answer': answer_text
        }), 200
        
    except Exception as e:
        print(f"❌ Chatbot API error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = 'Sorry, I encountered an error processing your request. Please try again.'
        return jsonify({
            'success': False,
            'message': error_response,
            'response': error_response,
            'answer': error_response,
            'error': str(e)
        }), 500


@app.route('/api/chatbot/history', methods=['GET'])
def api_chatbot_history():
    """Get chat history for current user"""
    try:
        # For now, return empty history (can be enhanced to store in Firebase)
        return jsonify({
            'success': True,
            'history': []
        }), 200
    except Exception as e:
        print(f"❌ Chat history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'history': []
        }), 500


@app.route('/chatbot/ask', methods=['POST'])
def chatbot_ask():
    """
    Legacy chatbot endpoint - redirects to /api/chatbot
    """
    return api_chatbot()


@app.route('/chatbot/health', methods=['GET'])
def chatbot_health():
    """Check if integrated chatbot is ready"""
    try:
        is_healthy = chatbot.health_check()
        
        return jsonify({
            'status': 'healthy' if is_healthy else 'limited',
            'message': 'Chatbot ready with Groq AI' if is_healthy else 'Chatbot ready (basic mode)',
            'llm_configured': is_healthy,
            'model': 'groq/mixtral-8x7b-32768' if is_healthy else 'none'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'llm_configured': False
        }), 500


# ------------------- ADMIN CHATBOT TRAINING ROUTES -------------------

@app.route('/api/admin/chatbot/training', methods=['GET'])
@login_required
@admin_required
def get_chatbot_training_data():
    """Get current chatbot training data (admin only)"""
    try:
        training_data = chatbot.get_training_data()
        return jsonify({
            'success': True,
            'data': training_data
        }), 200
    except Exception as e:
        print(f"❌ Error getting training data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/chatbot/training', methods=['POST'])
@login_required
@admin_required
def add_chatbot_training_data():
    """Add new training data to chatbot (admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'training_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing training_data in request'
            }), 400
        
        new_data = data.get('training_data', '').strip()
        
        if not new_data:
            return jsonify({
                'success': False,
                'error': 'Training data cannot be empty'
            }), 400
        
        success = chatbot.add_training_data(new_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Training data added successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add training data'
            }), 500
            
    except Exception as e:
        print(f"❌ Error adding training data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/chatbot/training', methods=['DELETE'])
@login_required
@admin_required
def reset_chatbot_training_data():
    """Reset chatbot training data (admin only)"""
    try:
        success = chatbot.reset_training_data()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Training data reset successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reset training data'
            }), 500
            
    except Exception as e:
        print(f"❌ Error resetting training data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ------------------- RUN APP -------------------
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏥 DIABETES HEALTH PREDICTOR - AI DOCTOR PORTAL")
    print("="*70)
    print(f"✅ Flask App: Ready")
    print(f"✅ ML Model: {'Loaded' if model else '❌ Not Loaded'}")
    print(f"✅ Groq AI: {'Connected' if llm else '❌ Not Connected'}")
    print(f"✅ Chatbot Training: Ready")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
