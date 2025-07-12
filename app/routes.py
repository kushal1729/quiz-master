from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Subject, Chapter, Quiz, Question, Score  
from app import db
from datetime import datetime 
import json
import re  # For validation
from flask import Blueprint
from app import db


main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/initdb')
def initdb():
    db.create_all()
    return "Database tables created"
    
@main.route('/initadmin')
def init_admin():
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123'),
            full_name='Admin User',
            qualification='Admin',
            dob='2005-04-15',
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        return "✅ Admin created with username: admin and password: admin123"
    return "Admin already exists"

@main.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    search_query = request.args.get('search', '')
    if search_query:
        users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) | 
            (User.full_name.ilike(f'%{search_query}%')) | 
            (User.qualification.ilike(f'%{search_query}%'))
        ).all()
        subjects = Subject.query.filter(
            (Subject.name.ilike(f'%{search_query}%')) | 
            (Subject.description.ilike(f'%{search_query}%'))
        ).all()
        quizzes = Quiz.query.join(Chapter).filter(
            (Quiz.date_of_quiz.ilike(f'%{search_query}%')) | 
            (Chapter.name.ilike(f'%{search_query}%')) | 
            (Chapter.description.ilike(f'%{search_query}%'))
        ).all()
        chapters = Chapter.query.filter(
            (Chapter.name.ilike(f'%{search_query}%')) | 
            (Chapter.description.ilike(f'%{search_query}%'))
        ).all()
    else:
        users = User.query.filter(User.is_admin == False).all()
        subjects = Subject.query.all()
        quizzes = Quiz.query.all()
        chapters = Chapter.query.all()
    
    # Fetch all questions and group them by quiz
    questions_by_quiz = {}
    for quiz in quizzes:
        questions_by_quiz[quiz.id] = quiz.questions
    
    # Calculate total score for each user
    user_scores = {}
    for user in users:
        scores = Score.query.filter_by(user_id=user.id).all()
        user_scores[user.id] = scores
    
    user_chart_data = []
    for user in users:
        total_score = sum(score.total_scored for score in user_scores.get(user.id, []))
        user_chart_data.append({
            'username': user.username,
            'total_score': total_score
        })
    
    total_users = len(users)
    total_quizzes = len(quizzes)
    total_subjects = len(subjects)
    
    return render_template(
        'admin_dashboard.html',
        users=users,
        subjects=subjects,
        quizzes=quizzes,
        chapters=chapters,
        user_scores=user_scores,
        search_query=search_query,
        total_users=total_users,
        total_quizzes=total_quizzes,
        total_subjects=total_subjects,
        user_chart_data=json.dumps(user_chart_data),
        questions_by_quiz=questions_by_quiz  # Pass questions grouped by quiz
    )


@main.route('/user/dashboard')
@login_required
def user_dashboard():
    subjects = Subject.query.all()
    return render_template('user_dashboard.html', subjects=subjects)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):  
            login_user(user)
            if user.is_admin:
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.user_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        qualification = request.form.get('qualification', '').strip()
        dob = request.form.get('dob', '').strip()
        if not username or not password or not full_name or not qualification or not dob:
            flash('All fields are required.', 'error')
            return redirect(url_for('main.register'))
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('main.register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('main.register'))
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            full_name=full_name,
            qualification=qualification,
            dob=dob
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/check-username')
def check_username():
    username = request.args.get('username')
    exists = User.query.filter_by(username=username).first() is not None
    return jsonify({'exists': exists})

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/create-subject', methods=['POST'])
@login_required
def create_subject():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    subject = Subject(
        name=request.form.get('subject_name'),
        description=request.form.get('subject_description')
    )
    db.session.add(subject)
    db.session.commit()
    flash('Subject created successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/edit-subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        subject.name = request.form.get('subject_name')
        subject.description = request.form.get('subject_description')
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('edit_subject.html', subject=subject)

@main.route('/delete-subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    subject = Subject.query.get_or_404(subject_id)
    
    # Delete all related chapters, quizzes, scores, and questions
    for chapter in subject.chapters:
        for quiz in chapter.quizzes:
            Score.query.filter_by(quiz_id=quiz.id).delete()
            Question.query.filter_by(quiz_id=quiz.id).delete()
            db.session.delete(quiz)
        db.session.delete(chapter)
    
    # Now delete the subject
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/create-chapter', methods=['GET', 'POST'])
@login_required
def create_chapter():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    subjects = Subject.query.all()
    if request.method == 'POST':
        chapter_name = request.form.get('chapter_name')
        chapter_description = request.form.get('chapter_description')
        subject_id = request.form.get('subject_id')
        if not chapter_name or not chapter_description or not subject_id:
            flash('All fields are required.', 'error')
            return redirect(url_for('main.create_chapter'))
        chapter = Chapter(
            name=chapter_name,
            description=chapter_description,
            subject_id=subject_id
        )
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter created successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('admin_dashboard.html', subjects=subjects)

@main.route('/edit-chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    chapter = Chapter.query.get_or_404(chapter_id)
    subjects = Subject.query.all()
    if request.method == 'POST':
        chapter.name = request.form.get('chapter_name')
        chapter.description = request.form.get('chapter_description')
        chapter.subject_id = request.form.get('subject_id')
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('edit_chapter.html', chapter=chapter, subjects=subjects)

@main.route('/delete-chapter/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    chapter = Chapter.query.get_or_404(chapter_id)
    
    # Delete all related quizzes and their scores and questions
    for quiz in chapter.quizzes:
        Score.query.filter_by(quiz_id=quiz.id).delete()
        Question.query.filter_by(quiz_id=quiz.id).delete()
        db.session.delete(quiz)
    
    # Now delete the chapter
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))
    
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/create-quiz', methods=['POST'])
@login_required
def create_quiz():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    chapter_id = request.form.get('quiz_chapter_id')
    date_of_quiz = request.form.get('quiz_date')
    time_duration = request.form.get('quiz_duration')
    if not chapter_id or not date_of_quiz or not time_duration:
        flash('All fields are required.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    quiz = Quiz(
        chapter_id=chapter_id,
        date_of_quiz=date_of_quiz,
        time_duration=time_duration
    )
    db.session.add(quiz)
    db.session.commit()
    flash('Quiz created successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/edit-quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    quiz = Quiz.query.get_or_404(quiz_id)
    chapters = Chapter.query.all()
    if request.method == 'POST':
        quiz.chapter_id = request.form.get('quiz_chapter_id')
        quiz.date_of_quiz = request.form.get('quiz_date')
        quiz.time_duration = request.form.get('quiz_duration')
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)

@main.route('/delete-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Delete all related scores
    Score.query.filter_by(quiz_id=quiz.id).delete()
    
    # Delete all related questions
    Question.query.filter_by(quiz_id=quiz.id).delete()
    
    # Now delete the quiz
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/add-question', methods=['POST'])
@login_required
def add_question():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    quiz_id = request.form.get('quiz_id')
    question_statement = request.form.get('question_statement')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4 = request.form.get('option4')
    correct_option = request.form.get('correct_option')
    question = Question(
        quiz_id=quiz_id,
        question_statement=question_statement,
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        correct_option=correct_option
    )
    db.session.add(question)
    db.session.commit()
    flash('Question added successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        question.question_statement = request.form.get('question_statement')
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = request.form.get('correct_option')
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('edit_question.html', question=question)

@main.route('/delete-question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))
@main.route('/quiz/<int:quiz_id>/questions')
@login_required
def quiz_questions(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    return render_template('quiz_questions.html', quiz=quiz, questions=questions)

@main.route('/attempt-quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    if request.method == 'POST':
        total_score = 0
        for question in questions:
            selected_option = request.form.get(f'question_{question.id}')
            if selected_option == question.correct_option:
                total_score += 1
        score = Score(
            quiz_id=quiz_id,
            user_id=current_user.id,
            time_stamp_of_attempt=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_scored=total_score
        )
        db.session.add(score)
        db.session.commit()
        flash(f'Quiz submitted! Your score: {total_score}/{len(questions)}', 'success')
        return redirect(url_for('main.subject_quizzes', subject_id=quiz.chapter.subject_id))
    return render_template('attempt_quiz.html', quiz=quiz, questions=questions)

@main.route('/results/<int:quiz_id>')
@login_required
def results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first()
    return render_template('results.html', quiz=quiz, score=score)

@main.route('/subject/<int:subject_id>/quizzes')
@login_required
def subject_quizzes(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    quizzes = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject_id).all()
    user_scores = {}
    for quiz in quizzes:
        score = Score.query.filter_by(quiz_id=quiz.id, user_id=current_user.id).first()
        user_scores[quiz.id] = score.total_scored if score else None
    return render_template(
        'subject_quizzes.html',
        subject=subject,
        quizzes=quizzes,
        user_scores=user_scores 
    )

@main.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'error')
        return redirect(url_for('main.home'))
    user = User.query.get_or_404(user_id)
    Score.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects])

@main.route('/api/chapters', methods=['GET'])
def get_chapters():
    chapters = Chapter.query.all()
    return jsonify([{'id': c.id, 'name': c.name, 'description': c.description, 'subject_id': c.subject_id} for c in chapters])

@main.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    quizzes = Quiz.query.all()
    return jsonify([{'id': q.id, 'chapter_id': q.chapter_id, 'date_of_quiz': q.date_of_quiz, 'time_duration': q.time_duration} for q in quizzes])

@main.route('/api/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify([{
        'id': q.id,
        'quiz_id': q.quiz_id,
        'question_statement': q.question_statement,
        'option1': q.option1,
        'option2': q.option2,
        'option3': q.option3,
        'option4': q.option4,
        'correct_option': q.correct_option
    } for q in questions])

@main.route('/api/scores', methods=['GET'])
def get_scores():
    scores = Score.query.all()
    return jsonify([{
        'id': s.id,
        'quiz_id': s.quiz_id,
        'user_id': s.user_id,
        'time_stamp_of_attempt': s.time_stamp_of_attempt,
        'total_scored': s.total_scored
    } for s in scores])
