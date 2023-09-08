import os
import datetime as dt
import secrets
import json
from zipfile import ZipFile
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
from scipy.signal import find_peaks
from flask import Flask, request, render_template, url_for, redirect, session, send_file
from werkzeug.utils import secure_filename
from OpenLIBS.analysis import element_list_comparison
from forms import InputForm, elem_symb

app = Flask(__name__)
app.config['SECRET_KEY'] = '73e2889840a574502969a1ad279ef26f'

UPLOAD_FOLDER = os.path.join(app.root_path, 'session_files')


def save_file(form_file):
    current_time = dt.datetime.now()
    formatted_time = current_time.strftime('%y%m%d%H%M%S')
    filename = secure_filename(form_file.filename)
    if not os.path.isdir(os.path.join(UPLOAD_FOLDER, session['uid'])):
        os.mkdir(os.path.join(UPLOAD_FOLDER, session['uid']))
        os.mkdir(os.path.join(UPLOAD_FOLDER, session['uid'], 'output'))
    f_name, f_ext = os.path.splitext(filename)
    fname = f_name + "_" + formatted_time + f_ext
    path_file = os.path.join(UPLOAD_FOLDER, session['uid'], fname)
    if 'file_list' in session:
        file_list = session.get('file_list')
        file_list.append(fname)
        session['file_list'] = file_list
    else:
        session['file_list'] = [fname]
    form_file.save(path_file)
    return fname


def libs_analysis(filename, element_list, lower_wavelength_limit, upper_wavelength_limit, baseline_intensity,
                  line_type='P', lower_error=0.2, upper_error=0.2, match_threshold=3):
    data_path = os.path.join(UPLOAD_FOLDER, session['uid'], filename)
    filename_no_extension, f_ext = os.path.splitext(filename)
    comparison_log_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"Full_Comparison_{filename_no_extension}.json")
    simulation_log_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"Simulation_Details_{filename_no_extension}.log")

    data = np.genfromtxt(data_path, delimiter=',')

    if line_type:
        line_type = 'P'
    else:
        line_type = 'S'

    # Filter data based on wavelength limits

    data = data[(data[:, 0] >= lower_wavelength_limit) &
                (data[:, 0] <= upper_wavelength_limit)]

    peak_indices, _ = find_peaks(data[:, 1], height=baseline_intensity)

    # Initialize the list of peaks using the number of rows
    peak_list = np.zeros((len(peak_indices), 2))

    # Copy X Y values based on calculated indices.
    j = 0
    for i in peak_indices:
        peak_list[j, 0] = data[i, 0]
        peak_list[j, 1] = data[i, 1]
        j += 1

    # Perform element comparison using element_list_comparison function

    out = element_list_comparison(peak_data=peak_list,
                                  element_list=element_list,
                                  line_type=line_type,
                                  lower_error=lower_error,
                                  upper_error=upper_error,
                                  match_threshold=match_threshold)

    # Save the comparison results to a JSON file
    with open(comparison_log_path, 'w') as log_file:
        json.dump(out, log_file)

    # Extract the detected element list based on 'is_match' key in the 'out' dictionary
    detected_element_list = [element for element,
                                         result in out.items() if result['is_match']]

    # Write the detected element list to the log file
    with open(simulation_log_path, 'w') as log_file:
        log_file.write('Simulation Logs\n')
        log_file.write(f'lower_wavelength_limit :: {lower_wavelength_limit}\n')
        log_file.write(f'upper_wavelength_limit :: {upper_wavelength_limit}\n')
        log_file.write(f'baseline_intensity :: {baseline_intensity}\n')
        log_file.write(f'lower_error :: {lower_error}\n')
        log_file.write(f'upper_error :: {upper_error}\n')
        log_file.write(f'line_type :: {line_type}\n')
        log_file.write(f'match_threshold :: {match_threshold}\n')
        log_file.write(f"Compared Elements :: {element_list}\n")
        log_file.write(f'Detected Elements :: {detected_element_list}\n')

    return comparison_log_path, simulation_log_path


def resultplotter(data_fileloc, log_fileloc, result_fileloc, output_fileloc, annotations=True):

    data = pd.read_csv(data_fileloc, header=None)

    # First column is 'wavelength' and the second column is 'intensity'
    data.columns = ['wavelength', 'intensity']

    # Extract 'wavelength' and 'intensity' values
    wavelength_data = data['wavelength']
    intensity_data = data['intensity']

    # Plotting the input data
    fig_1 = go.Figure()
    fig_1.add_trace(go.Scatter(x=wavelength_data, y=intensity_data, mode="lines", name='Input Data'))
    fig_1.update_xaxes(title_text='Wavelength')
    fig_1.update_yaxes(title_text='Intensity')
    min_intensity = intensity_data.max() * 0.1

    # Read log file and extract lower_wavelength_limit, upper_wavelength_limit and baseline_intensity for plotting
    infile = rf'{log_fileloc}'

    graph_parameters = []
    keep_phrases = ["lower_wavelength_limit :: ", "upper_wavelength_limit :: ", "baseline_intensity :: "]
    with open(infile) as f:
        file_csv = f.readlines()
        
    for line in file_csv:
        for phrase in keep_phrases:
            if phrase in line:
                graph_parameters.append(line.split(' :: ')[1])
                break

    # Opening JSON file
    with open(result_fileloc, "r") as file_json:
        # Returns JSON object as a dictionary
        data = json.load(file_json)

    # Initialisation
    annotation_arrow_length = -40  # For controlling the annotation arrow length

    for key in data:
        sub_dict = data[key]
        if sub_dict["is_match"] == True:
            matched_peaks = sub_dict["matched_peaks"]
            peak = []
            standard_wavelength = []
            intensity = []
            std_wl = []
            inten = []
            inten_modified = []
            for small_dict in matched_peaks:
                std_wv = small_dict["Standard_Wavelength"]
                intensity_1 = small_dict["Intensity"]
                peak_1 = small_dict["Peak"]
                standard_wavelength.append(std_wv)
                intensity.append(intensity_1)
                peak.append(peak_1)
            for num in intensity:
                if num <= min_intensity:
                    inten.append(min_intensity)
                else:
                    inten.append(num)
            for number in standard_wavelength:
                std_wl.append(number)
                std_wl.append(number)
                std_wl.append(number)
            for num in inten:
                inten_modified.append(0)
                inten_modified.append(num)
                inten_modified.append(0)

            fig_1.add_trace(go.Scatter(x=std_wl, y=inten_modified, mode="lines", name=key))
            if annotations:
                for i in range(len(peak)):
                    fig_1.add_annotation(x=peak[i], y=intensity[i], text=key, showarrow=True, arrowhead=2, arrowsize=1,
                                         arrowwidth=1, ay=annotation_arrow_length)
            annotation_arrow_lenght = annotation_arrow_length - 30

    fig_1.add_trace(
        go.Scatter(x=[float(graph_parameters[0]), float(graph_parameters[0]), float(graph_parameters[1]),
                      float(graph_parameters[1]), float(graph_parameters[0])],
                   y=[float(graph_parameters[2]), intensity_data.max() * 1.01, intensity_data.max() * 1.01,
                      float(graph_parameters[2]), float(graph_parameters[2])],
                   mode='lines',
                   name='Selected Region',
                   line=dict(color="red", width=2, dash='dash'),
                   connectgaps=False))

    fig_1.write_html(output_fileloc)

    fig_1.update_xaxes(range=[float(graph_parameters[0]), float(graph_parameters[1])])  # Adjust the X-axis range
    fig_1.update_yaxes(range=[0 - (intensity_data.max() * 0.01), intensity_data.max() * 1.01])
    fig_1.update_layout(width=1200, height=600)
    div_str = pio.to_html(fig_1, full_html=False)
    return div_str


@app.route('/', methods=['GET', 'POST'])
def home():
    form = InputForm()
    if form.validate_on_submit():
        if form.input_file.data:
            uploaded_file = form.input_file.data
            file_name = save_file(uploaded_file)
            selected_symbol = form.selected_elements.data
            # selected_symbol = [elem_symb[ list(elem_symb.values()).index(symbol) ] for symbol in selected_names]
            session['recent_file'] = file_name
            session['log'][file_name] = {
                'lower_wave': form.lower_wave.data,
                'upper_wave': form.upper_wave.data,
                'baseline_intensity': form.baseline_intensity.data,
                'r_cutoff': form.r_cutoff.data,
                'l_cutoff': form.l_cutoff.data,
                'n_peaks': form.n_peaks.data,
                'selected_elements': selected_symbol,
                'PS': form.PS.data
            }
            comp, log = libs_analysis(filename=file_name,
                                      element_list=session['log'][file_name]['selected_elements'],
                                      lower_wavelength_limit=session['log'][file_name]['lower_wave'],
                                      upper_wavelength_limit=session['log'][file_name]['upper_wave'],
                                      baseline_intensity=session['log'][file_name]['baseline_intensity'],
                                      line_type=session['log'][file_name]['PS'],
                                      lower_error=session['log'][file_name]['l_cutoff'],
                                      upper_error=session['log'][file_name]['r_cutoff'],
                                      match_threshold=session['log'][file_name]['n_peaks'])
            session['log'][file_name]['output'] = comp, log
            return redirect(url_for('results'))
        return render_template('home.html', form=form, sess=session['uid'])

    if request.method == 'GET':
        form.r_cutoff.data = 0.2
        form.l_cutoff.data = 0.2
        form.n_peaks.data = 3

        if not 'log' in session:
            session['log'] = dict()
        if session.new:
            session['uid'] = secrets.token_hex(8)
        elif not session.new:
            if 'uid' in session:
                pass
            else:
                session['uid'] = secrets.token_hex(8)
        return render_template('home.html', form=form, sess=session['uid'])
    return render_template('home.html', form=form, sess=session['uid'])


@app.route('/results')
def results():
    filename = session['recent_file']
    filename_no_extension, f_ext = os.path.splitext(filename)
    comparison_log_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"Full_Comparison_{filename_no_extension}.json")
    simulation_log_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"Simulation_Details_{filename_no_extension}.log")
    input_data_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], f"{filename}")
    result_html_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"Results_{filename_no_extension}.html")

    with open(comparison_log_path, 'r') as f:
        json_output = f.read()

    plotly_div = resultplotter(data_fileloc=input_data_path, log_fileloc=simulation_log_path,
                               result_fileloc=comparison_log_path, output_fileloc=result_html_path, annotations=False)
    output = {
        'comp': comparison_log_path,
        'log': simulation_log_path,
        'plotly_div': plotly_div,
        'data': json_output
    }
    return render_template('results.html', output=output)


@app.route('/docs')
def docs():
    return render_template('docs.html', title='Docs')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/download')
def download_file():
    filename = session['recent_file']
    filename_no_extension, f_ext = os.path.splitext(filename)
    comparison_log_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"Full_Comparison_{filename_no_extension}.json")
    simulation_log_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"Simulation_Details_{filename_no_extension}.log")
    input_data_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], f"{filename}")
    result_html_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"Results_{filename_no_extension}.html")

    zip_path = os.path.join(
        UPLOAD_FOLDER, session['uid'], 'output', f"{filename_no_extension}_output.zip")

    with ZipFile(zip_path, 'w') as zf:
        zf.write(comparison_log_path, os.path.basename(comparison_log_path))
        zf.write(simulation_log_path, os.path.basename(simulation_log_path))
        zf.write(input_data_path, os.path.basename(input_data_path))
        zf.write(result_html_path, os.path.basename(result_html_path))

    return send_file(zip_path, as_attachment=True)


if __name__ == '__main__':
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    app.run(debug=True)
