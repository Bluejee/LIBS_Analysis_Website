function plotGraph() {
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    const file_input = file.name;

    if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
            const content = event.target.result;
            // const lines = content.split('\n');
            const lines = d3.csvParseRows(content);
            const x_list = [];
            const y_list = [];
            for (let i = 1; i < lines.length; i++) {  // Start from index 1 to skip header
                x_list.push(lines[i][0]);
                y_list.push(lines[i][1]);
            }
            var trace1 = {
                x: x_list,
                y: y_list,
                type: 'line',
                line: {
                    color: 'rgb(255, 0, 255)',
                    width: 3
                  }

            };
            var layout = {
                plot_bgcolor: 'transparent', // Set the background color
                paper_bgcolor: 'transparent', // Set the paper (outer) background color
                title: {
                    text: file_input,
                    font:{
                        color:'blue'
                    }
                },
                xaxis: {
                    title: {
                        text: lines[0][0],
                        font: {
                            color:'#00FF00'
                        }
                    },
                    gridcolor: '#a1a1a1',
                    tickfont: {
                        color: '#98FB98' // Set x-axis tick label color
                    }
                },
                yaxis: {
                    title:{ 
                        text:lines[0][1],
                        font:{
                            color: '#00FF00'
                        }
                    },
                    gridcolor: '#a1a1a1',
                    tickfont: {
                        color: '#98FB98' // Set y-axis tick label color
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
