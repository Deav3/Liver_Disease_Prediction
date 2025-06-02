from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import create_table, add_users as add_user, get_users as get_user
import os
import joblib

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a secure, random key

# Load the model once globally
MODEL_PATH = 'a_model.pkl'
try:
    liver_model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    liver_model = None
    print(f"Error: Model file '{MODEL_PATH}' not found.")

create_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aboutus', methods=['GET', 'POST']) 
def about_us():
    return render_template('aboutus.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Received signup request: Username={username}, Password={password}")

        if get_user(username):  # Check if the user already exists
            flash('Username already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        try:
            # Add new user to the database
            add_user(username, password)
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error in signup route: {e}")
            flash('An error occurred during signup. Please try again.', 'danger')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user(username)
        print(f"Retrieved user: {user}")  # Debugging line

        if user and user['password'] == password:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('predict'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')



@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        flash('You must be logged in to access the prediction page.', 'warning')
        return redirect(url_for('login'))
    
    username = session['user']

    if request.method == 'POST':
        try:
            # Extract and convert form inputs
            name = request.form['name']
            age = float(request.form['age'])
            gender = 1 if request.form['gender'].lower() == 'female' else 0
            bilirubin = float(request.form['bilirubin'])
            alkaline = float(request.form['alkaline'])
            alt = float(request.form['alt'])
            ast = float(request.form['ast'])
            protein = float(request.form['protein'])
            albumin = float(request.form['albumin'])
            agr = float(request.form['agr'])

            # Create feature vector for the model
            feature_vector = [[age, gender, bilirubin, alkaline, alt, ast, protein, albumin, agr]]

            # Model prediction
            if liver_model:
                prediction_result = liver_model.predict(feature_vector)[0]
                detailed_results = [
                    
                    {"field": "Bilirubin", "value": bilirubin, "min":0.2,"max":1.3, "symptoms": "Jaundice risk"},
                    {"field": "Alkaline Phosphatase", "value": alkaline, "min": 70,"max":110, "symptoms": "Liver cancer, Bone disorders"},
                    {"field": "ALT", "value": alt, "min": 5,"max":40, "symptoms": "Diabetes, Obesity"},
                    {"field": "AST", "value": ast, "min": 5,"max":40, "symptoms": "Vomitings, Skin and Eye Disease"},
                    {"field": "Total Protein", "value": protein, "min": 6.4,"max":8.3, "symptoms": "Weight loss, Difficulty Breathing"},
                    {"field": "Albumin", "value": albumin, "min": 3.5,"max":5.2, "symptoms": "Diarrhea, Fever, Weight Loss"},
                    {"field": "Albumin/Globulin Ratio", "value": agr, "min": 1,"max":2, "symptoms": "Fluid buildup in Stomach, Itchy skin"},
                ]

                abnormal_results = [
                    item for item in detailed_results
                    if item['value'] < item['min'] or item['value'] > item['max']
                ]
                return render_template('result.html', prediction=prediction_result, results=abnormal_results,name=name,age=age,username=username)
            else:
                flash("Model not available. Prediction cannot be performed.", 'danger')
        except Exception as e:
            flash(f"Error during prediction: {e}", 'danger')

    return render_template('predict.html',username=username)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
