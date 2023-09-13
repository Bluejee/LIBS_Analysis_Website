function plotGraph() {
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    const file_input = file.name;    
    document.getElementById('filetext').innerHTML = file_input;



    if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
            const content = event.target.result;
            // const lines = content.split('\n');
            const lines = d3.csvParseRows(content);
            const x_list = [];
            const y_list = [];
            for (let i = 0; i < lines.length; i++) {  // Start from index 1 to skip header
                x_list.push(lines[i][0]);
                y_list.push(lines[i][1]);
            }
            max_wavelength = Math.max.apply(Math,x_list);
            min_wavelength =Math.min.apply(Math,x_list);
            document.getElementById('lower_wave').value = min_wavelength;
            document.getElementById('upper_wave').value = max_wavelength;

            var trace1 = {
                x: x_list,
                y: y_list,
                type: 'line',
                line: {
                    color: 'rgb(236, 177, 35)',
                    width: 3
                  }

            };
            var layout = {
                plot_bgcolor: 'transparent', // Set the background color
                paper_bgcolor: 'transparent', // Set the paper (outer) background color
                title: {
                    text: file_input,
                    font:{
                        color:'rgb(255,255,255)'
                    }
                },
                xaxis: {
                    title: {
                        text: 'wavelength',
                        font: {
                            color:'rgb(204, 204, 204)'
                        }
                    },
                    gridcolor: 'rgba(161, 161, 161, .5)',
                    tickfont: {
                        color: '#rgb(204, 204, 204)' // Set x-axis tick label color
                    }
                },
                yaxis: {
                    title:{ 
                        text:'Intensity',
                        font:{
                            color: '#rgb(204, 204, 204)'
                        }
                    },
                    gridcolor: '#a1a1a1',
                    tickfont: {
                        color: '#rgb(204, 204, 204)' // Set y-axis tick label color
                    }
                }
            };
            drawChart("graphContainer", trace1, layout);
        };
        reader.readAsText(file);

    }
}

function drawChart(id_plot, data, layout) {

    Plotly.newPlot(document.getElementById(id_plot), [data], layout, {
        margin: { t: 0 }
    });
    document.getElementById("section-2").scrollIntoView();
}
