import os
import datetime as dt
import secrets
from flask import Flask, request, render_template, url_for, redirect, session
from werkzeug.utils import secure_filename
from forms import  InputForm , elem_symb


app = Flask(__name__)
app.config['SECRET_KEY'] = '73e2889840a574502969a1ad279ef26f'

UPLOAD_FOLDER = os.path.join(app.root_path, 'Files_toprocess')

def save_file(form_file):
    current_time = dt.datetime.now()
    formatted_time = current_time.strftime('%y%m%d%H%M%S')
    filename = secure_filename(form_file.filename)
    if (not os.path.isdir(os.path.join(app.root_path, 'Files_toprocess',session['uid']))):
        os.mkdir(os.path.join(UPLOAD_FOLDER,session['uid']))
        os.mkdir(os.path.join(UPLOAD_FOLDER,session['uid'],'output'))
    f_name, f_ext = os.path.splitext(filename)
    fname = f_name+"_"+ formatted_time+f_ext
    path_file = os.path.join(UPLOAD_FOLDER,session['uid'], fname)
    if 'file_list' in session:
        file_list = session.get('file_list')
        file_list.append(fname)
        session['file_list'] = file_list
    else:
        session['file_list'] = [fname]
    form_file.save(path_file)
    return fname

def process_file(filename):
    file_path= os.path.join(UPLOAD_FOLDER, session['uid'],'output',filename)



@app.route('/', methods = ['GET', 'POST'])
def home():
    form = InputForm()
    if form.validate_on_submit():
        if form.input_file.data:
            uploaded_file = form.input_file.data
            file_name = save_file(uploaded_file)
            selected_symbols = form.selected_elements.data
            # selected_names = [element_symbols[symbol] for symbol in selected_symbols]
            session['recent_file'] = file_name
            session['log'][file_name] = {
                'lower_wave':form.lower_wave.data,
                'upper_wave' :form.upper_wave.data,
                'baseline_intensity':form.baseline_intensity.data,
                'r_cutoff':form.r_cutoff.data,
                'l_cutoff':form.l_cutoff.data,
                'n_peaks':form.n_peaks.data,
                'selected_elements':selected_symbols,
                'PS':form.PS.data
                }
            return redirect(url_for('results'))
        return render_template('home.html', form =form, sess = session['uid'])

    if request.method =='GET':
        if (not 'log' in session):
            session['log'] = dict()
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
    return render_template('homed3.html', form =form)


@app.route('/results')
def results():
    if 'file_list' in session:
        file_list = session['file_list']
        rec_file = session['recent_file']
        user_data = {
            'file_list' : file_list,
            'rec_file':rec_file,
            'log_data':session['log'][rec_file]
        }
        return render_template('results.html', title='Results', user_data = user_data)
        #file_list = file_list, rec_file=rec_file, log_data=session['log'][rec_file])
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
