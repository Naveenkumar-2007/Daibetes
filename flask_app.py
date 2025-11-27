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

# ------------------- LOAD GROQ LLM (LAZY LOADING) -------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

app.config['GOOGLE_CLIENT_ID'] = google_client_id
app.config['GOOGLE_CLIENT_SECRET'] = google_client_secret

# Use lazy loading for LLM to speed up startup
llm = None
_llm_initialized = False

def get_llm():
    """Lazy load LLM only when needed"""
    global llm, _llm_initialized
    
    if _llm_initialized:
        return llm
    
    if not groq_api_key:
        print("⚠️ Warning: GROQ_API_KEY not found - AI reports will be disabled")
        _llm_initialized = True
        return None
    
    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=groq_api_key,
            temperature=0.4,
            timeout=30
        )
        print("✅ Groq LLM initialized successfully")
        _llm_initialized = True
        return llm
    except Exception as e:
        print(f"❌ Error initializing Groq LLM: {e}")
        _llm_initialized = True
        return None

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

@app.route('/health')
def health_check():
    """Health check endpoint for Azure App Service"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'firebase': firebase_initialized,
            'model_loaded': model is not None,
            'scaler_loaded': scaler is not None
        }), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/')
def home():
    """Serve React app in production or landing page in development"""
    # Check if React build exists (production mode)
    react_build = os.path.join(os.path.dirname(__file__), 'static', 'app', 'index.html')
    if os.path.exists(react_build):
        return send_from_directory(os.path.join('static', 'app'), 'index.html')
    
    # Development mode - use Flask templates
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        # Redirect to prediction page first (hospital theme)
        return redirect(url_for('user_predict_page'))
    return render_template(
        'landing.html',
        google_client_id=google_client_id,
        google_login_enabled=bool(google_client_id)
    )


@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React app static files in production"""
    react_dir = os.path.join(os.path.dirname(__file__), 'static', 'app')
    if os.path.exists(os.path.join(react_dir, path)):
        return send_from_directory(react_dir, path)
    # For React Router - serve index.html for any unknown route
    if os.path.exists(os.path.join(react_dir, 'index.html')):
        return send_from_directory(react_dir, 'index.html')
    # Fallback to 404
    return "Not Found", 404


# Login page removed - React handles all frontend routes


# Register page removed - React handles all frontend routes


# Forgot password page removed - React handles all frontend routes


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
                # Redirect to prediction page (hospital theme)
                redirect_url = url_for('user_predict_page')
            
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
                redirect_url = url_for('user_predict_page')

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
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': {
                    'user_id': session.get('user_id'),
                    'username': session.get('username'),
                    'full_name': session.get('full_name'),
                    'email': session.get('email'),
                    'role': session.get('role', 'user')
                }
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
                'has_report': bool(pred.get('report_path') or pred.get('report_id'))
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
        
        reports = []
        for pred in predictions:
            if pred.get('report_id') or pred.get('report_path'):
                reports.append({
                    'report_id': pred.get('report_id', pred.get('prediction_id')),
                    'prediction_id': pred.get('prediction_id'),
                    'patient_name': pred.get('name', 'Unknown'),
                    'prediction_result': 'Positive' if pred.get('prediction') == 1 else 'Negative',
                    'probability': pred.get('probability', 0.5),
                    'generated_at': pred.get('created_at', pred.get('timestamp')),
                    'report_file': pred.get('report_path')
                })
        
        return jsonify({
            'success': True,
            'reports': reports
        })
    except Exception as e:
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
        import firebase_config
        firebase_config.initialize_firebase()
        
        # Get all users from Firebase
        users_ref = firebase_config.db_ref.child('users')
        users_data = users_ref.get()
        
        users = []
        if users_data:
            for user_id, user_info in users_data.items():
                # Get prediction count for this user
                predictions_ref = firebase_config.db_ref.child('predictions')
                all_predictions = predictions_ref.get() or {}
                
                prediction_count = sum(1 for pred in all_predictions.values() 
                                     if isinstance(pred, dict) and pred.get('user_id') == user_id)
                
                # Count reports
                report_count = sum(1 for pred in all_predictions.values() 
                                 if isinstance(pred, dict) and pred.get('user_id') == user_id 
                                 and (pred.get('report_id') or pred.get('report_path') or pred.get('report_generated_at')))
                
                users.append({
                    'user_id': user_id,
                    'username': user_info.get('username', 'N/A'),
                    'full_name': user_info.get('full_name', 'Unknown'),
                    'email': user_info.get('email', 'N/A'),
                    'created_at': user_info.get('created_at', datetime.now().isoformat()),
                    'prediction_count': prediction_count,
                    'report_count': report_count
                })
        
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        print(f"Error fetching users: {e}")
        import traceback
        traceback.print_exc()
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
        import firebase_config
        firebase_config.initialize_firebase()
        
        # Get users count
        users_ref = firebase_config.db_ref.child('users')
        users_data = users_ref.get() or {}
        total_users = len(users_data) if users_data else 0
        
        # Get predictions
        predictions_ref = firebase_config.db_ref.child('predictions')
        predictions_data = predictions_ref.get() or {}
        total_predictions = len(predictions_data) if predictions_data else 0
        
        # Count positive predictions and reports
        positive_predictions = 0
        total_reports = 0
        
        if predictions_data:
            for pred in predictions_data.values():
                if isinstance(pred, dict):
                    # Count high risk predictions
                    if (pred.get('risk_level') == 'high' or 
                        pred.get('prediction') == 1 or 
                        'high' in str(pred.get('prediction', '')).lower()):
                        positive_predictions += 1
                    
                    # Count reports
                    if (pred.get('report_id') or pred.get('report_path') or 
                        pred.get('report_generated_at') or pred.get('report_file')):
                        total_reports += 1
        
        stats = {
            'total_users': total_users,
            'total_predictions': total_predictions,
            'total_reports': total_reports,
            'positive_predictions': positive_predictions
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        print(f"Error fetching stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user and all their associated data"""
    try:
        import firebase_config
        firebase_config.initialize_firebase()
        
        print(f"🗑️ Attempting to delete user: {user_id}")
        
        # First verify the user exists
        users_ref = firebase_config.db_ref.child('users')
        user_data = users_ref.child(user_id).get()
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        username = user_data.get('username', 'Unknown')
        print(f"👤 Found user: {username}")
        
        # Delete all predictions for this user
        predictions_ref = firebase_config.db_ref.child('predictions')
        all_predictions = predictions_ref.get() or {}
        
        deleted_predictions = 0
        deleted_reports = 0
        
        for pred_id, pred_data in all_predictions.items():
            if isinstance(pred_data, dict) and pred_data.get('user_id') == user_id:
                # Delete prediction record
                predictions_ref.child(pred_id).delete()
                deleted_predictions += 1
                
                # Delete associated report file if it exists
                report_path = pred_data.get('report_path') or pred_data.get('report_file')
                if report_path:
                    try:
                        full_path = os.path.join(os.path.dirname(__file__), report_path.lstrip('/'))
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            deleted_reports += 1
                            print(f"🗑️ Deleted report file: {report_path}")
                    except Exception as e:
                        print(f"⚠️ Could not delete report file {report_path}: {e}")
        
        # Delete the user account
        users_ref.child(user_id).delete()
        
        print(f"✅ Deleted user {username} ({user_id})")
        print(f"📊 Deleted {deleted_predictions} predictions")
        print(f"📄 Deleted {deleted_reports} report files")
        
        return jsonify({
            'success': True,
            'message': f'User {username} deleted successfully',
            'deleted': {
                'predictions': deleted_predictions,
                'reports': deleted_reports
            }
        })
        
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        import traceback
        traceback.print_exc()
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
        
        return render_template('user_dashboard.html',
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
        return render_template('user_dashboard.html',
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
    return render_template('user_dashboard.html')


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


@app.route('/admin/patient_predictions')
@admin_required
def patient_predictions():
    """Admin page to view a specific patient's predictions"""
    return render_template('patient_predictions.html')


@app.route('/admin/reports')
@admin_required
def admin_all_reports():
    """Admin page to view all medical reports from all patients"""
    return render_template('admin_reports.html')


@app.route('/admin/get_all_reports', methods=['GET'])
@admin_required
def get_all_reports():
    """API endpoint to get all medical reports from all patients"""
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
                report_data['id'] = report_id
                report_data['report_id'] = report_id
                reports_list.append(report_data)
        
        # Sort by timestamp (most recent first)
        reports_list.sort(key=lambda x: x.get('created_at', 0), reverse=True)
        
        return jsonify({
            'success': True,
            'reports': reports_list,
            'total_count': len(reports_list)
        })
    
    except Exception as e:
        print(f"Error fetching reports: {e}")
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
    """Get all predictions for a specific patient"""
    try:
        # Get all predictions for this user
        history = get_patient_history(user_id=user_id, limit=1000)
        
        # Get user info
        import firebase_config
        firebase_config.initialize_firebase()
        user_ref = firebase_config.db_ref.child('users').child(user_id)
        user_data = user_ref.get()
        
        return jsonify({
            'success': True,
            'patient': {
                'user_id': user_id,
                'full_name': user_data.get('full_name', 'N/A') if user_data else 'N/A',
                'username': user_data.get('username', 'N/A') if user_data else 'N/A',
                'email': user_data.get('email', 'N/A') if user_data else 'N/A',
            },
            'predictions': history
        })
    
    except Exception as e:
        print(f"Error fetching patient predictions: {e}")
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
        current_llm = get_llm()
        if current_llm is None:
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
        groq_response = current_llm.invoke(prompt)
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
        current_llm = get_llm()
        if current_llm is None:
            return jsonify({
                'success': False,
                'error': 'AI Report Generator not available. Please configure GROQ_API_KEY.'
            }), 500
        
        data = request.json
        
        # Create detailed prompt for medical report
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are Dr. Sarah Mitchell, MD, a board-certified endocrinologist with 15 years of experience specializing in diabetes care and prevention at a leading medical center.

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
        response = current_llm.invoke(formatted_prompt)
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
        try:
            if 'user_id' in session and data.get('prediction_id'):
                user_id = session.get('user_id')
                prediction_id = data.get('prediction_id')
                
                # Update the prediction with report info
                update_data = {
                    'report_id': patient_id,
                    'report_path': report_filename,
                    'report_generated_at': timestamp
                }
                update_prediction_record(prediction_id, update_data, user_id)
                print(f"✅ Report saved to Firebase for prediction {prediction_id}")
        except Exception as fb_error:
            print(f"Warning: Could not save report to Firebase: {fb_error}")
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
        current_llm = get_llm()
        if current_llm is None:
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

        response = current_llm.invoke(prompt)
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
    """Generate a professional medical PDF report with Groq AI analysis and clinical charts"""
    from io import BytesIO
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from report_generator import (generate_clinical_parameter_chart, generate_risk_gauge_chart,
                                   generate_parameter_radar_chart, generate_bmi_classification_chart)
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           topMargin=0.5*inch,
                           bottomMargin=0.6*inch,
                           leftMargin=0.75*inch,
                           rightMargin=0.75*inch)
    
    # Container for PDF elements
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.white,
        spaceAfter=10,
        spaceBefore=14,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#2b98c9'),
        borderPadding=6,
        leftIndent=8
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        alignment=TA_JUSTIFY
    )
    
    # Header - Hospital Letterhead
    story.append(Paragraph("⚕️ CITY GENERAL HOSPITAL", title_style))
    story.append(Paragraph("Department of Endocrinology & Metabolic Disorders", subtitle_style))
    story.append(Paragraph("Advanced Diabetes Assessment & Management Center", subtitle_style))
    story.append(Paragraph("123 Medical Plaza, Healthcare District | Tel: (555) 123-4567", subtitle_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Divider line
    line_data = [['━' * 100]]
    line_table = Table(line_data, colWidths=[6.5*inch])
    line_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Report Title
    report_title = Paragraph("COMPREHENSIVE DIABETES RISK ASSESSMENT", heading_style)
    story.append(report_title)
    story.append(Spacer(1, 0.15*inch))
    
    # Report metadata and doctor info side by side
    from pytz import timezone
    ist = timezone('Asia/Kolkata')
    timestamp = report.get('timestamp') or report.get('created_at', 'N/A')
    if timestamp != 'N/A':
        try:
            date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_obj = date_obj.astimezone(ist)
            formatted_date = date_obj.strftime("%B %d, %Y")
            formatted_time = date_obj.strftime("%I:%M %p IST")
        except:
            formatted_date = datetime.now(ist).strftime("%B %d, %Y")
            formatted_time = datetime.now(ist).strftime("%I:%M %p IST")
    else:
        formatted_date = datetime.now(ist).strftime("%B %d, %Y")
        formatted_time = datetime.now(ist).strftime("%I:%M %p IST")
    
    metadata_data = [
        ['Report ID:', report_id, 'Attending Physician:', 'Dr. Sarah Mitchell, MD, FACP'],
        ['Date of Assessment:', formatted_date, 'Specialization:', 'Endocrinology & Diabetes Care'],
        ['Time:', formatted_time, 'License No:', 'MD-2025-456789'],
        ['Report Type:', 'AI-Assisted Analysis', 'Contact:', 'smitchell@cityhospital.com']
    ]
    
    metadata_table = Table(metadata_data, colWidths=[1.3*inch, 1.9*inch, 1.3*inch, 2*inch])
    metadata_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Information
    story.append(Paragraph("PATIENT INFORMATION", heading_style))
    story.append(Spacer(1, 0.08*inch))
    
    patient_name = report.get('patient_name', 'N/A')
    patient_age = report.get('age') or report.get('Age', 'N/A')
    patient_sex = report.get('sex', 'N/A')
    patient_contact = report.get('contact', 'N/A')
    
    patient_data = [
        ['Full Name:', patient_name, 'Age:', f"{patient_age} years"],
        ['Gender:', patient_sex, 'Contact:', patient_contact],
        ['Patient ID:', session.get('user_id', 'N/A')[:16], 'Assessment Date:', formatted_date]
    ]
    
    patient_table = Table(patient_data, colWidths=[1.2*inch, 2.1*inch, 1.2*inch, 2*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#475569')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#475569')),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Clinical Parameters
    story.append(Paragraph("LABORATORY FINDINGS & CLINICAL PARAMETERS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Extract parameters with fallbacks
    glucose = report.get('Glucose') or report.get('glucose') or 'N/A'
    bmi = report.get('BMI') or report.get('bmi') or 'N/A'
    bp = report.get('BloodPressure') or report.get('blood_pressure') or 'N/A'
    insulin = report.get('Insulin') or report.get('insulin') or 'N/A'
    skin_thickness = report.get('SkinThickness') or report.get('skin_thickness') or 'N/A'
    dpf = report.get('DiabetesPedigreeFunction') or report.get('diabetes_pedigree') or 'N/A'
    pregnancies = report.get('Pregnancies') or report.get('pregnancies') or 'N/A'
    age = report.get('Age') or report.get('age') or 'N/A'
    
    # Determine colors based on values
    def get_glucose_color(val):
        try:
            v = float(val)
            if v < 100: return colors.HexColor('#10b981')
            elif v < 126: return colors.HexColor('#f59e0b')
            else: return colors.HexColor('#ef4444')
        except: return colors.black
    
    def get_bmi_color(val):
        try:
            v = float(val)
            if v < 18.5: return colors.HexColor('#3b82f6')
            elif v < 25: return colors.HexColor('#10b981')
            elif v < 30: return colors.HexColor('#f59e0b')
            else: return colors.HexColor('#ef4444')
        except: return colors.black
    
    clinical_data = [
        ['Parameter', 'Value', 'Normal Range', 'Status'],
        ['Fasting Glucose', f'{glucose} mg/dL', '70-100 mg/dL', '●'],
        ['Blood Pressure', f'{bp} mmHg', '60-80 mmHg', '●'],
        ['Body Mass Index (BMI)', f'{bmi} kg/m²', '18.5-24.9', '●'],
        ['Serum Insulin', f'{insulin} μU/mL', '16-166 μU/mL', '●'],
        ['Skin Thickness', f'{skin_thickness} mm', '10-50 mm', '●'],
        ['Diabetes Pedigree', f'{dpf}', '0.0-2.5', '●'],
        ['Pregnancies', f'{pregnancies}', 'N/A', '●'],
        ['Age', f'{age} years', 'N/A', '●'],
    ]
    
    clinical_table = Table(clinical_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 0.7*inch])
    clinical_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Data rows
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(clinical_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Risk Assessment
    risk_level = report.get('risk_level', 'Unknown')
    confidence = report.get('confidence', 'N/A')
    
    risk_color = colors.HexColor('#ef4444') if risk_level == 'high' else colors.HexColor('#10b981')
    risk_bg = colors.HexColor('#fef2f2') if risk_level == 'high' else colors.HexColor('#f0fdf4')
    
    story.append(Paragraph("AI-ASSISTED DIAGNOSTIC ASSESSMENT", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    risk_data = [
        ['Risk Classification:', risk_level.upper() + ' RISK'],
        ['Model Confidence:', f'{confidence}%'],
        ['Assessment Model:', 'Advanced Machine Learning Algorithm']
    ]
    
    risk_table = Table(risk_data, colWidths=[2.5*inch, 3.5*inch])
    risk_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, 0), risk_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), risk_bg),
        ('BOX', (0, 0), (-1, -1), 2, risk_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Add Clinical Visualizations
    story.append(Paragraph("CLINICAL DATA VISUALIZATION & ANALYSIS", heading_style))
    story.append(Spacer(1, 0.15*inch))
    
    try:
        # Chart 1: Risk Gauge
        risk_gauge_buffer = generate_risk_gauge_chart(confidence, risk_level)
        risk_gauge_img = Image(risk_gauge_buffer, width=5*inch, height=3*inch)
        story.append(risk_gauge_img)
        story.append(Spacer(1, 0.2*inch))
        
        # Chart 2: Clinical Parameters Bar Chart
        param_chart_buffer = generate_clinical_parameter_chart(report)
        param_chart_img = Image(param_chart_buffer, width=6.5*inch, height=4*inch)
        story.append(param_chart_img)
        story.append(Spacer(1, 0.2*inch))
        
        # Page break for next charts
        story.append(PageBreak())
        
        # Chart 3: Parameter Radar Chart
        radar_chart_buffer = generate_parameter_radar_chart(report)
        radar_chart_img = Image(radar_chart_buffer, width=5.5*inch, height=5.5*inch)
        story.append(radar_chart_img)
        story.append(Spacer(1, 0.2*inch))
        
        # Chart 4: BMI Classification
        bmi_chart_buffer = generate_bmi_classification_chart(bmi)
        bmi_chart_img = Image(bmi_chart_buffer, width=6.5*inch, height=2*inch)
        story.append(bmi_chart_img)
        story.append(Spacer(1, 0.3*inch))
        
    except Exception as chart_error:
        print(f"Chart generation error: {str(chart_error)}")
        story.append(Paragraph(f"<i>Note: Some visualizations could not be generated.</i>", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Page break before physician's analysis
    story.append(PageBreak())
    
    # AI-Generated Medical Analysis and Recommendations
    story.append(Paragraph("PHYSICIAN'S MEDICAL ASSESSMENT & RECOMMENDATIONS", heading_style))
    story.append(Spacer(1, 0.08*inch))
    
    # Get LLM instance
    current_llm = get_llm()
    if current_llm is None:
        # LLM not available - provide a basic template
        story.append(Paragraph("<i>AI-powered analysis is currently unavailable. Please consult with your healthcare provider for detailed recommendations.</i>", body_style))
        story.append(Spacer(1, 0.3*inch))
    else:
    
    try:
        # Generate AI-powered personalized analysis using Groq
        ai_prompt = f"""You are Dr. Sarah Mitchell, MD, FACP, a board-certified endocrinologist with 15 years of experience in diabetes care and metabolic disorders at City General Hospital.

PATIENT CLINICAL DATA:
- Age: {age} years
- BMI: {bmi} kg/m²
- Fasting Plasma Glucose: {glucose} mg/dL (Normal: 70-100 mg/dL)
- Diastolic Blood Pressure: {bp} mmHg (Normal: 60-80 mmHg)
- 2-Hour Serum Insulin: {insulin} μU/mL (Normal: 16-166 μU/mL)
- Triceps Skin Thickness: {skin_thickness} mm
- Diabetes Pedigree Function: {dpf} (Genetic Risk Factor)
- Pregnancy History: {pregnancies}
- **AI RISK CLASSIFICATION: {risk_level.upper()} RISK**
- **MODEL CONFIDENCE: {confidence}%**

Generate a comprehensive, detailed medical assessment report with these exact sections:

**1. CLINICAL IMPRESSION** (4-5 sentences)
Provide a thorough summary analyzing the patient's overall metabolic health, diabetes risk profile, cardiovascular status, and the clinical significance of their laboratory values. Discuss how their parameters correlate with established diabetes risk criteria. Mention specific concerns based on their age and clinical profile.

**2. DETAILED LABORATORY ANALYSIS** (Analyze each parameter with 2-3 sentences each)
For EACH clinical parameter, provide:
• **Fasting Glucose ({glucose} mg/dL)**: Clinical interpretation, comparison to diagnostic thresholds (100-125 mg/dL prediabetes, ≥126 diabetes), metabolic implications, and immediate concerns if elevated.
• **BMI ({bmi} kg/m²)**: Classify (underweight/normal/overweight/obese), discuss cardiovascular and metabolic risk, visceral adiposity concerns, and relationship to insulin resistance.
• **Blood Pressure ({bp} mmHg)**: Evaluate cardiovascular risk, discuss hypertension staging if applicable, relationship to metabolic syndrome, and kidney function implications.
• **Insulin Level ({insulin} μU/mL)**: Assess for hyperinsulinemia or insulin resistance, discuss pancreatic beta-cell function, and relationship to glucose metabolism.
• **Diabetes Pedigree Function ({dpf})**: Explain genetic predisposition significance, family history implications, and how this affects long-term risk stratification.

**3. RISK FACTORS IDENTIFIED** (List 6-8 specific factors with explanations)
• Modifiable risk factors (lifestyle, diet, exercise, weight) with detailed explanations
• Non-modifiable risk factors (age, genetics, family history) with clinical context
• Emerging risk indicators from the clinical data
• Explain HOW each factor contributes to diabetes development

**4. METABOLIC SYNDROME ASSESSMENT** (3-4 sentences)
Evaluate if patient meets metabolic syndrome criteria (3 of 5: elevated glucose, high BP, elevated triglycerides, low HDL, abdominal obesity). Discuss implications for cardiovascular disease risk and diabetes progression.

**5. COMPREHENSIVE MEDICAL RECOMMENDATIONS** (12-15 specific, actionable items organized by category)

**IMMEDIATE ACTIONS** (Within 1-2 weeks):
• Specific laboratory tests to order (HbA1c, lipid panel, kidney function, etc.)
• Specialist referrals needed (endocrinologist, dietitian, etc.)
• Baseline assessments required

**PHARMACOTHERAPY CONSIDERATIONS** (If high risk):
• Metformin initiation criteria and dosing
• Other medications to discuss with physician
• Medication timing and precautions

**DIETARY MODIFICATIONS** (Very specific):
• Daily carbohydrate targets in grams (breakfast, lunch, dinner, snacks)
• Specific foods to emphasize (list 8-10 with portions)
• Foods to eliminate or limit (list 8-10)
• Meal timing strategies
• Glycemic index education
• Portion control guidelines
• Sample meal plan suggestions

**EXERCISE PRESCRIPTION** (Detailed protocol):
• Aerobic exercise: type, frequency (days/week), duration (minutes), intensity (heart rate zones)
• Resistance training: exercises, sets, reps, frequency
• Flexibility and balance work
• Progression timeline over 3 months
• Safety precautions specific to patient's condition

**WEIGHT MANAGEMENT** (If applicable):
• Target weight based on ideal BMI
• Realistic timeline (pounds per week/month)
• Caloric deficit recommendations
• Behavioral strategies

**MONITORING PROTOCOLS**:
• Self-monitoring blood glucose: timing, frequency, target ranges
• Daily health tracking (weight, BP, exercise, diet)
• Symptom diary instructions
• Technology tools (apps, devices)

**LIFESTYLE MODIFICATIONS**:
• Sleep hygiene (7-9 hours nightly)
• Stress management techniques
• Smoking cessation if applicable
• Alcohol consumption guidelines
• Hydration targets

**6. CRITICAL WARNING SIGNS** (8-10 specific symptoms requiring immediate medical attention)
List symptoms of hyperglycemia, hypoglycemia (if on medication), diabetic emergencies, cardiovascular events, and other urgent concerns with clear action steps.

**7. FOLLOW-UP CARE PLAN** (Detailed timeline)
• Next appointments: specific timing (weeks/months) and purpose
• Laboratory test schedule with specific dates
• Reassessment points for treatment efficacy
• Long-term management milestones (3 months, 6 months, 1 year)
• Criteria for escalating or de-escalating treatment

**8. PROGNOSIS AND PATIENT EDUCATION** (3-4 sentences)
Discuss expected outcomes with intervention vs. without, emphasize reversibility of prediabetes with lifestyle changes, provide realistic expectations, and motivate patient with evidence-based success rates.

**9. PHYSICIAN'S CLOSING NOTES** (2-3 sentences)
Professional summary emphasizing the importance of adherence, partnership in care, and encouragement for the patient's health journey.

CRITICAL REQUIREMENTS:
- Write as if directly addressing the patient in second person where appropriate
- Use specific numbers, percentages, and quantifiable targets throughout
- Base all recommendations on current ADA, AACE, and USPSTF guidelines
- Make every recommendation actionable with clear "how-to" steps
- Be thorough and comprehensive - this is a professional medical document
- Maintain empathetic yet direct professional tone
- Include medical rationale for each major recommendation
- Format with clear section headers using **bold** text
- Use bullet points for lists (•)
- Minimum 2000 words of detailed medical analysis"""

        # Call Groq AI for analysis
        ai_response = current_llm.invoke(ai_prompt)
        ai_analysis = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)
        
        # Format the AI response with proper styling
        analysis_paragraphs = ai_analysis.split('\n')
        
        for para in analysis_paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if it's a heading (contains ** or starts with number followed by period/dot)
            if '**' in para or (para and para[0].isdigit() and '.' in para[:5]):
                # Remove ** markers and format as section heading
                clean_heading = para.replace('**', '').strip()
                section_heading_style = ParagraphStyle(
                    'AIHeading',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#1e40af'),
                    fontName='Helvetica-Bold',
                    spaceAfter=6,
                    spaceBefore=12,
                    leftIndent=0
                )
                story.append(Paragraph(clean_heading, section_heading_style))
            else:
                # Regular paragraph or bullet point
                content_style = ParagraphStyle(
                    'AIContent',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    textColor=colors.HexColor('#1e293b'),
                    alignment=TA_JUSTIFY if not para.startswith(('•', '-', '*')) else TA_LEFT,
                    leftIndent=10 if para.startswith(('•', '-', '*')) else 0,
                    spaceAfter=4
                )
                story.append(Paragraph(para, content_style))
        
    except Exception as e:
        # Fallback recommendations if AI fails
        print(f"AI generation failed: {str(e)}, using fallback recommendations")
        
        fallback_style = ParagraphStyle('Fallback', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'))
        
        story.append(Paragraph("<b>CLINICAL IMPRESSION:</b>", fallback_style))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph(
            f"Based on comprehensive metabolic assessment, the patient presents with {risk_level.lower()} for developing Type 2 Diabetes Mellitus. "
            f"The clinical parameters including fasting glucose of {glucose} mg/dL and BMI of {bmi} kg/m² warrant careful monitoring and proactive intervention.",
            fallback_style
        ))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>KEY FINDINGS:</b>", fallback_style))
        story.append(Spacer(1, 0.05*inch))
        findings = [
            f"• Fasting glucose level of {glucose} mg/dL {'exceeds normal range' if glucose != 'N/A' and float(glucose) > 100 else 'within normal limits'}",
            f"• BMI of {bmi} kg/m² indicates {'overweight status requiring intervention' if bmi != 'N/A' and float(bmi) > 25 else 'healthy weight range'}",
            f"• Blood pressure reading of {bp} mmHg requires {'close monitoring' if bp != 'N/A' and float(bp) > 80 else 'routine observation'}",
            f"• Diabetes pedigree function of {dpf} suggests {'significant familial predisposition' if dpf != 'N/A' and float(dpf) > 0.5 else 'moderate genetic risk'}"
        ]
        for finding in findings:
            story.append(Paragraph(finding, fallback_style))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>PERSONALIZED RECOMMENDATIONS:</b>", fallback_style))
        story.append(Spacer(1, 0.05*inch))
        if risk_level.lower() == 'high':
            recs = [
                "• <b>Urgent:</b> Schedule appointment with endocrinologist within 1-2 weeks",
                "• Complete comprehensive metabolic panel including HbA1c, lipid profile, and kidney function tests",
                "• Implement carbohydrate-controlled diet (45-60g per meal) with emphasis on low glycemic index foods",
                "• Begin supervised exercise program: 30 minutes moderate-intensity aerobic activity, 5 days/week",
                "• Daily self-monitoring of blood glucose (fasting and 2-hour postprandial)",
                "• Consider metformin therapy pending physician evaluation",
                "• Weight reduction target: 7-10% of current body weight over 6 months",
                "• Consultation with certified diabetes educator for comprehensive education"
            ]
        else:
            recs = [
                "• Schedule follow-up appointment in 3-6 months for reassessment",
                "• Annual comprehensive metabolic screening recommended",
                "• Maintain balanced Mediterranean-style diet rich in vegetables, fruits, whole grains, and lean proteins",
                "• Regular physical activity: minimum 150 minutes moderate-intensity exercise per week",
                "• Monitor fasting glucose quarterly with home glucometer",
                "• Maintain healthy weight through balanced nutrition and regular activity",
                "• Annual eye examination and foot care assessment",
                "• Continue current preventive health measures"
            ]
        for rec in recs:
            story.append(Paragraph(rec, fallback_style))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>IMPORTANT PRECAUTIONS:</b>", fallback_style))
        story.append(Spacer(1, 0.05*inch))
        precautions = [
            "• Monitor for symptoms of hyperglycemia: increased thirst, frequent urination, unexplained fatigue, blurred vision",
            "• Avoid prolonged fasting or extreme dietary restrictions without medical supervision",
            "• Report any unusual symptoms, wounds that heal slowly, or recurrent infections immediately",
            "• Maintain adequate hydration (8-10 glasses of water daily)",
            "• Avoid high-sugar beverages and processed foods with added sugars"
        ]
        for precaution in precautions:
            story.append(Paragraph(precaution, fallback_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Doctor's Signature Section
    signature_heading = Paragraph("PHYSICIAN AUTHENTICATION", heading_style)
    story.append(signature_heading)
    story.append(Spacer(1, 0.1*inch))
    
    signature_data = [
        ['Electronically Signed By:', 'Dr. Sarah Mitchell, MD, FACP'],
        ['Board Certification:', 'Endocrinology, Diabetes & Metabolism'],
        ['License Number:', 'MD-2025-456789'],
        ['Date Signed:', formatted_date],
        ['Digital Signature:', '✓ Verified - AI-Assisted Medical Report']
    ]
    
    signature_table = Table(signature_data, colWidths=[2*inch, 4*inch])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2b98c9')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(signature_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Medical Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_JUSTIFY,
        leading=11,
        leftIndent=10,
        rightIndent=10
    )
    
    story.append(Paragraph("MEDICAL DISCLAIMER & LEGAL NOTICE", heading_style))
    story.append(Spacer(1, 0.08*inch))
    
    disclaimer_text = """This diabetes risk assessment report has been generated using advanced artificial intelligence and machine learning 
    algorithms trained on extensive clinical datasets. The analysis incorporates your clinical parameters with validated predictive models 
    to provide risk stratification. <b>This report is intended for educational and informational purposes only and does not constitute 
    medical advice, diagnosis, or treatment.</b> The AI-assisted recommendations should be considered as supplementary information to support, 
    not replace, the relationship that exists between you and your healthcare provider. All medical decisions should be made in consultation 
    with qualified healthcare professionals who have access to your complete medical history. If you have any concerns about your health or 
    the information in this report, please consult with your physician or another qualified healthcare provider immediately. Do not disregard 
    professional medical advice or delay seeking it because of information presented in this report. The predictive accuracy of the model is 
    based on population-level data and individual outcomes may vary. In case of medical emergency, please call emergency services or visit 
    the nearest emergency department immediately."""
    
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    story.append(Spacer(1, 0.25*inch))
    
    # Confidentiality Notice
    confidentiality_style = ParagraphStyle(
        'Confidential',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#7f1d1d'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph(
        "⚠️ CONFIDENTIAL MEDICAL DOCUMENT - Protected Health Information (PHI) ⚠️",
        confidentiality_style
    ))
    story.append(Spacer(1, 0.05*inch))
    
    privacy_style = ParagraphStyle(
        'Privacy',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        leading=10
    )
    
    story.append(Paragraph(
        "This document contains confidential patient information protected under HIPAA regulations. "
        "Unauthorized disclosure or distribution is strictly prohibited.",
        privacy_style
    ))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Professional Footer
    footer_line_data = [['━' * 100]]
    footer_line_table = Table(footer_line_data, colWidths=[6.5*inch])
    footer_line_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(footer_line_table)
    story.append(Spacer(1, 0.08*inch))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        leading=10
    )
    
    from pytz import timezone as tz
    ist_tz = tz('Asia/Kolkata')
    current_time = datetime.now(ist_tz).strftime('%B %d, %Y at %I:%M %p IST')
    
    story.append(Paragraph(
        "<b>⚕️ CITY GENERAL HOSPITAL - DEPARTMENT OF ENDOCRINOLOGY</b>",
        footer_style
    ))
    story.append(Paragraph(
        "Advanced Diabetes Assessment & Management Center",
        footer_style
    ))
    story.append(Paragraph(
        "123 Medical Plaza, Healthcare District | Phone: (555) 123-4567 | Fax: (555) 123-4568",
        footer_style
    ))
    story.append(Paragraph(
        f"Email: diabetes-care@cityhospital.com | 24/7 Patient Care Hotline: (555) 911-CARE",
        footer_style
    ))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(
        f"<i>Report Generated: {current_time} | Powered by AI Medical Analysis System v2.0</i>",
        footer_style
    ))
    story.append(Paragraph(
        f"<i>Document ID: {report_id} | Page 1 of 1</i>",
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


@app.route('/download_report/<report_id>')
@login_required
def download_report(report_id):
    """
    Download a specific medical report as beautiful PDF
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
                if pred.get('id') == report_id or pred.get('firebase_id') == report_id or pred.get('report_id') == report_id:
                    report = pred
                    break
        
        if not report:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        # Generate beautiful PDF report
        pdf_buffer = generate_beautiful_pdf(report, report_id)
        
        # Generate filename
        patient_name = report.get('patient_name', 'Patient')
        timestamp = get_ist_now().strftime('%Y%m%d_%H%M%S')
        filename = f"diabetes_report_{patient_name.replace(' ', '_')}_{timestamp}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
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


# ============================================
# AI HEALTH CHATBOT ENDPOINTS
# ============================================

# Store chat history in memory (use Redis or Firebase for production)
chat_histories = {}

@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot():
    """
    AI Health Assistant Chatbot - Provides personalized health guidance
    """
    try:
        current_llm = get_llm()
        if current_llm is None:
            return jsonify({
                'success': False,
                'error': 'AI Assistant not available. Please configure GROQ_API_KEY.'
            }), 503
        
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user_id = session.get('user_id')
        full_name = session.get('full_name', 'User')
        
        # Initialize chat history for this user
        if user_id not in chat_histories:
            chat_histories[user_id] = []
        
        # Get user's health context
        try:
            history = get_patient_history(user_id=user_id, limit=5)  # Last 5 predictions
            
            # Build user health context
            health_context = ""
            if history and len(history) > 0:
                latest = history[0]
                health_context = f"""
USER HEALTH PROFILE:
- Patient Name: {full_name}
- Latest Risk Assessment: {latest.get('prediction', 'N/A')}
- Risk Level: {latest.get('risk_level', 'N/A')}
- Confidence: {latest.get('confidence', 'N/A')}%
- Assessment Date: {latest.get('timestamp', 'N/A')}

RECENT HEALTH METRICS:
- Glucose Level: {latest.get('Glucose', 'N/A')} mg/dL
- Blood Pressure: {latest.get('BloodPressure', 'N/A')} mm Hg
- BMI: {latest.get('BMI', 'N/A')}
- Age: {latest.get('Age', 'N/A')} years
- Total Assessments: {len(history)}
"""
            else:
                health_context = f"""
USER HEALTH PROFILE:
- Patient Name: {full_name}
- Status: No health assessments yet
- Recommendation: Complete a diabetes risk assessment to get personalized insights
"""
        except Exception as e:
            print(f"Error getting health context: {e}")
            health_context = f"USER: {full_name}"
        
        # Get knowledge base context
        knowledge_context = ""
        try:
            if chatbot_knowledge_base:
                # Simple keyword matching to find relevant documents
                user_message_lower = user_message.lower()
                keywords = ['diabetes', 'glucose', 'blood', 'sugar', 'insulin', 'bmi', 'diet', 'exercise', 
                           'prevention', 'symptoms', 'treatment', 'risk', 'health']
                
                relevant_docs = []
                for doc in chatbot_knowledge_base:
                    doc_content = doc.get('content', '')
                    # Check if any keyword appears in both user message and document
                    if any(keyword in user_message_lower for keyword in keywords):
                        if any(keyword in doc_content.lower() for keyword in keywords):
                            relevant_docs.append(doc)
                
                if relevant_docs:
                    knowledge_context = "\n\nADDITIONAL MEDICAL KNOWLEDGE:\n"
                    for doc in relevant_docs[:2]:  # Limit to 2 most relevant docs
                        content_preview = doc.get('content', '')[:500]
                        knowledge_context += f"\n{content_preview}...\n"
        except Exception as e:
            print(f"Error getting knowledge base context: {e}")
        
        # Build conversation history
        conversation_context = "\n".join([
            f"{'USER' if msg['role'] == 'user' else 'ASSISTANT'}: {msg['content']}"
            for msg in chat_histories[user_id][-6:]  # Last 3 exchanges
        ])
        
        # Create AI prompt
        system_prompt = """You are Dr. Sarah Mitchell, MD, a compassionate and knowledgeable AI health assistant specializing in diabetes prevention and metabolic health. You provide:

🎯 CORE RESPONSIBILITIES:
- Answer health questions with empathy and medical accuracy
- Explain diabetes risk factors and prevention strategies
- Provide lifestyle guidance (diet, exercise, stress management)
- Help users understand their health metrics
- Encourage proactive health management

⚕️ COMMUNICATION STYLE:
- Warm, empathetic, and encouraging
- Use simple language, avoid excessive medical jargon
- Be supportive yet medically accurate
- Provide actionable, specific advice
- Always remind users to consult healthcare providers for medical decisions

🚫 IMPORTANT LIMITATIONS:
- You cannot diagnose medical conditions
- You cannot prescribe medications
- You cannot replace professional medical advice
- Always recommend consulting a doctor for serious concerns

Keep responses concise (2-4 paragraphs) unless detailed explanation is requested."""

        user_prompt = f"""{health_context}
{knowledge_context}

CONVERSATION HISTORY:
{conversation_context if conversation_context else 'New conversation'}

CURRENT USER MESSAGE:
{user_message}

Respond naturally as Dr. Sarah Mitchell. Be helpful, empathetic, and medically accurate. If additional medical knowledge is provided above, incorporate it naturally into your response."""

        # Get AI response using Groq
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        chain = prompt | llm
        response = chain.invoke({})
        
        ai_message = response.content
        
        # Update chat history
        chat_histories[user_id].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        chat_histories[user_id].append({
            'role': 'assistant',
            'content': ai_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 messages
        if len(chat_histories[user_id]) > 20:
            chat_histories[user_id] = chat_histories[user_id][-20:]
        
        return jsonify({
            'success': True,
            'message': ai_message,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Chatbot error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to get response: {str(e)}'
        }), 500


@app.route('/api/chatbot/history', methods=['GET'])
@login_required
def chatbot_history():
    """
    Get chat history for the current user
    """
    try:
        user_id = session.get('user_id')
        
        if user_id not in chat_histories:
            return jsonify({
                'success': True,
                'messages': []
            })
        
        return jsonify({
            'success': True,
            'messages': chat_histories[user_id]
        })
    
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chatbot/clear', methods=['POST'])
@login_required
def clear_chatbot_history():
    """
    Clear chat history for the current user
    """
    try:
        user_id = session.get('user_id')
        
        if user_id in chat_histories:
            chat_histories[user_id] = []
        
        return jsonify({
            'success': True,
            'message': 'Chat history cleared'
        })
    
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# END AI HEALTH CHATBOT ENDPOINTS
# ============================================


# ============================================
# ADMIN CHATBOT KNOWLEDGE BASE MANAGEMENT
# ============================================

# Store for chatbot knowledge base documents
chatbot_knowledge_base = []
UPLOAD_FOLDER = 'chatbot_documents'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'ppt', 'pptx', 'doc', 'docx', 'md'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/admin/chatbot/documents', methods=['GET'])
@login_required
@admin_required
def get_chatbot_documents():
    """Get list of uploaded documents for chatbot knowledge base"""
    try:
        import firebase_config
        firebase_config.initialize_firebase()
        
        docs_ref = firebase_config.db_ref.child('chatbot_documents')
        documents = docs_ref.get() or {}
        
        doc_list = []
        if documents:
            for doc_id, doc_data in documents.items():
                doc_list.append({
                    'id': doc_id,
                    'filename': doc_data.get('filename', 'Unknown'),
                    'type': doc_data.get('type', 'Unknown'),
                    'content': doc_data.get('content', ''),
                    'url': doc_data.get('url', ''),
                    'uploaded_at': doc_data.get('uploaded_at', ''),
                    'size': doc_data.get('size', 0)
                })
        
        return jsonify({
            'success': True,
            'documents': doc_list
        })
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/chatbot/upload', methods=['POST'])
@login_required
@admin_required
def upload_chatbot_document():
    """Upload document or URL to chatbot knowledge base"""
    try:
        import firebase_config
        firebase_config.initialize_firebase()
        
        # Check if it's a file upload or URL
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = file.filename
                file_ext = filename.rsplit('.', 1)[1].lower()
                
                # Read file content
                content = ""
                if file_ext == 'txt' or file_ext == 'md':
                    content = file.read().decode('utf-8')
                elif file_ext == 'pdf':
                    try:
                        import PyPDF2
                        pdf_reader = PyPDF2.PdfReader(file)
                        content = "\n".join([page.extract_text() for page in pdf_reader.pages])
                    except:
                        content = "PDF processing not available. Install PyPDF2."
                elif file_ext in ['doc', 'docx', 'ppt', 'pptx']:
                    content = f"Document uploaded: {filename}. Content extraction requires additional libraries."
                
                # Save to Firebase
                doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                docs_ref = firebase_config.db_ref.child('chatbot_documents').child(doc_id)
                docs_ref.set({
                    'filename': filename,
                    'type': 'file',
                    'file_type': file_ext,
                    'content': content[:10000],  # Limit to 10KB
                    'uploaded_at': datetime.now().isoformat(),
                    'uploaded_by': session.get('user_id'),
                    'size': len(content)
                })
                
                # Add to in-memory knowledge base
                chatbot_knowledge_base.append({
                    'id': doc_id,
                    'filename': filename,
                    'content': content
                })
                
                return jsonify({
                    'success': True,
                    'message': f'Document "{filename}" uploaded successfully',
                    'document_id': doc_id
                })
        
        elif request.json and request.json.get('url'):
            # URL upload
            url = request.json.get('url')
            try:
                import requests
                response = requests.get(url, timeout=10)
                content = response.text[:10000]  # Limit to 10KB
                
                doc_id = f"url_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                docs_ref = firebase_config.db_ref.child('chatbot_documents').child(doc_id)
                docs_ref.set({
                    'url': url,
                    'type': 'url',
                    'content': content,
                    'uploaded_at': datetime.now().isoformat(),
                    'uploaded_by': session.get('user_id'),
                    'size': len(content)
                })
                
                chatbot_knowledge_base.append({
                    'id': doc_id,
                    'url': url,
                    'content': content
                })
                
                return jsonify({
                    'success': True,
                    'message': 'URL content added successfully',
                    'document_id': doc_id
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to fetch URL: {str(e)}'
                }), 400
        
        elif request.json and request.json.get('text'):
            # Direct text upload
            text = request.json.get('text')
            title = request.json.get('title', 'Custom Text')
            
            doc_id = f"text_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            docs_ref = firebase_config.db_ref.child('chatbot_documents').child(doc_id)
            docs_ref.set({
                'filename': title,
                'type': 'text',
                'content': text[:10000],
                'uploaded_at': datetime.now().isoformat(),
                'uploaded_by': session.get('user_id'),
                'size': len(text)
            })
            
            chatbot_knowledge_base.append({
                'id': doc_id,
                'title': title,
                'content': text
            })
            
            return jsonify({
                'success': True,
                'message': 'Text added successfully',
                'document_id': doc_id
            })
        
        return jsonify({
            'success': False,
            'error': 'No valid file, URL, or text provided'
        }), 400
        
    except Exception as e:
        print(f"Error uploading document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/chatbot/documents/<doc_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_chatbot_document(doc_id):
    """Delete a document from chatbot knowledge base"""
    try:
        import firebase_config
        firebase_config.initialize_firebase()
        
        docs_ref = firebase_config.db_ref.child('chatbot_documents').child(doc_id)
        docs_ref.delete()
        
        # Remove from in-memory knowledge base
        global chatbot_knowledge_base
        chatbot_knowledge_base = [doc for doc in chatbot_knowledge_base if doc.get('id') != doc_id]
        
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        })
    except Exception as e:
        print(f"Error deleting document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# END ADMIN CHATBOT KNOWLEDGE BASE MANAGEMENT
# ============================================


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
            ("system", """You are Dr. Sarah Mitchell, MD, FACP, a board-certified endocrinologist with 15 years of clinical experience specializing in diabetes prevention, metabolic disorders, and evidence-based patient care at Johns Hopkins Medical Center.

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
        current_llm = get_llm()
        if current_llm is None:
            ai_analysis = "AI analysis service is currently unavailable. Please consult with your healthcare provider for a detailed assessment of your test results."
        else:
            response = current_llm.invoke(formatted_prompt)
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


# ------------------- RUN APP -------------------
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏥 DIABETES HEALTH PREDICTOR - AI DOCTOR PORTAL")
    print("="*70)
    print(f"✅ Flask App: Ready")
    print(f"✅ ML Model: {'Loaded' if model else '❌ Not Loaded'}")
    print(f"✅ Groq AI: {'Connected' if llm else '❌ Not Connected'}")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
