from flask import Flask, request, render_template, url_for, redirect, session
from forms import  InputForm , element_symbols
import os
import datetime as dt
import secrets
from werkzeug.utils import secure_filename
app = Flask(__name__)

app.config['SECRET_KEY'] = '73e2889840a574502969a1ad279ef26f'

UPLOAD_FOLDER = os.path.join(app.root_path, 'Files_toprocess')

def save_file(form_file):
    current_time = dt.datetime.now()
    formatted_time = current_time.strftime('%y%m%d%H%M%S')
    filename = secure_filename(form_file.filename)
    if (not os.path.isdir(os.path.join(app.root_path, 'Files_toprocess',session['uid']))):
        os.mkdir(os.path.join(app.root_path, 'Files_toprocess',session['uid']))
    f_name, f_ext = os.path.splitext(filename)
    fname = f_name+"_"+ formatted_time+f_ext
    path_file = os.path.join(app.root_path, 'Files_toprocess',session['uid'], fname)
    form_file.save(path_file)
    return path_file
    
    

    

@app.route('/', methods = ['GET', 'POST'])
def home():
    form = InputForm()            
    if form.validate_on_submit():
        if form.input_file.data:
            uploaded_file = form.input_file.data
            file_path = save_file(uploaded_file)
            if 'file_list' in session:
                session['file_list'].append(file_path)
                return redirect(url_for('results'))
            session['file_list'] = list(file_path)        
            return redirect(url_for('results'))
        return render_template('home.html', form =form, sess = session['uid'])

    if request.method =='GET':
        if session.new:
            session['uid'] = secrets.token_hex(8)
        elif (not session.new):
            if 'uid' in session:
                pass
            else:
                session['uid'] = secrets.token_hex(8)            
        return render_template('home.html', form =form, sess = session['uid'])
    return render_template('home.html', form =form, sess = session['uid'])

@app.route('/homed3')
def homed3():
    form = InputForm()
    # form = InputForm()

    return render_template('homed3.html', form =form)

@app.route('/results')
def results():
    return render_template('results.html', title='Results')


@app.route('/docs')
def docs():
    return render_template('docs.html', title='Docs')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


if __name__ == '__main__':
    if (not os.path.isdir(os.path.join(app.root_path, 'Files_toprocess'))):
        os.mkdir(os.path.join(app.root_path, 'Files_toprocess'))
    app.run(debug=True)
