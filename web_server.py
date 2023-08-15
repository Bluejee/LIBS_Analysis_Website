from flask import Flask, render_template, url_for
from forms import PreInputForm, InputForm 

app = Flask(__name__)

app.config['SECRET_KEY'] = '73e2889840a574502969a1ad279ef26f'



@app.route('/')
@app.route('/home')
def home():
    pre_form = PreInputForm()
    # form = InputForm()

    return render_template('home.html', pre_form =pre_form)


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
    app.run(debug=True)
