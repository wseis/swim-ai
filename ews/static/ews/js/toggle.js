var layout = {
    autosize: true,
    height: 400,
    margin: {
        l: 50,
        r: 20,
        b: 30,
        t: 10,
        pad: 4
    },
    paper_bgcolor: "rgb(255,255,255)", 
    plot_bgcolor: "rgb(255,255,255)",
    showlegend: true,
    legend: {
        x: 0,
        y: 1.3,
        traceorder: 'normal',
        orientation: 'h',
        font: {
            family: 'sans-serif',
            size: 12,
            color: '#000'
        },
        bgcolor: 'rgb(255,255,255)',
        bordercolor: '#E2E2E2',
        borderwidth: 2
    },
    xaxis: {
        gridcolor: "rgb(229, 229, 229)", 
        //range: [1, 10], 
        showgrid: true, 
        showline: false, 
        showticklabels: true, 
        tickcolor: "rgb(127,127,127)", 
        ticks: "outside", 
        zeroline: false
    }, 
    yaxis: {
        title: {
            text: "E.coli lg[MPN/100mL]"
        }
    }
};

function traces(type) {
    var traces = {
        prediction_interval: {
            fill: "tozerox", 
            fillcolor: "rgba(117,117,117,0.3)", 
            line: {color: "transparent"}, 
            name: "Prediction intervall", 
            showlegend: true, 
            type: "scatter"
        },
        /* {
            line: {color: "#75C3FF"}, 
            mode: "lines", 
            name: "lower prediction intervall", 
            type: "scatter"
        };*/
        predicted_geomean: {
            line: {color: "rgba(0,86,110,1)"}, 
            mode: "lines", 
            name: "Predicted geomean", 
            type: "scatter"
        },
        upper_prediction_interval: {
            line: {color: "#75C3FF"}, 
            mode: "lines", 
            name: "Upper prediciton interval", 
            type: "scatter"
        },
        measurements: {
            line: {color: "#3185ff"}, 
            mode: "markers", 
            name: "Measurements", 
            type: "scatter"
        }
    };

    // Base object with properties x and y
    var xy = {x: [], y: []};

    // Add properties based on the given type using "object spread"
    return {...xy, ...traces[type]};
}

function toFullEndpoint(name, model_id) {
    return `/${name}/${model_id}`;
}

function apiEndpointGetPredictions(model_id) {
    return toFullEndpoint('api-get-predictions', model_id);
}

function apiEndpointPredictionSwitch(model_id) {
    return toFullEndpoint('prediction_switch', model_id);
}

function apiEndpointGetBrokerUrls(model_id) {
    return toFullEndpoint('api-get-broker-urls', model_id);
}

function urlBrokerEntityAttributes(id) {
    return `https://www.c-broker.xyz/v2/entities/${id}/attrs`;
}

function htmlStrong(x) {
    return `<strong>${x}</strong>`;
}

function predictionsToPlotData(predictions) {
    
    var trace1 = traces('prediction_interval');
    var trace2 = traces('predicted_geomean');
    var trace3 = traces('upper_prediction_interval');
    var trace4 = traces('measurements');
    
    predictions.forEach(function(val) {
        var date = new Date(val["date"]);
        trace1.x.push(date);
        trace1.y.push(val["P2_5"]);
        trace2.x.push(date);
        trace2.y.push(val["mean"]);
        trace3.x.push(date);
        trace3.y.push(val["P90"]);
        trace4.x.push(date);
        trace4.y.push(Math.log10(val["value"]));
        //console.log(val["date"]);
        //console.log(val["mean"]);
    });
    
    predictions.reverse().forEach(function(val) {
        trace1.x.push(new Date(val["date"]));
        trace1.y.push(val["P90"]);
        //console.log(val["date"]);
        //console.log(val["mean"]);
    });
    
    return [trace1, trace2, trace4];
}

document.addEventListener('DOMContentLoaded', function() {
    
    document.querySelector('#brokerIDs').style.display = "none";
    
    toggler = document.querySelector('#customSwitches');
    toggler.checked = (toggler.dataset.predict === "True");
    toggler.addEventListener('change', () => toggle_prediction(toggler.dataset.post));
    
    // Use buttons to toggle between views
    //document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    
    id_toggler = document.querySelector('#broker_id_switch');
    append_broker_ids(id_toggler.dataset.post);
    id_toggler.checked = false;
    id_toggler.addEventListener('change', () => show_broker_ids());
    //id_toggler.addEventListener('change', () => show_broker_ids(id_toggler.dataset.post));
    
    form = document.querySelector('#dateform');
    form.onsubmit = (event) => {
        event.preventDefault();
        create_plot();
        return false;
    }
    
    create_plot();
});

function create_plot() {
    
    start_date = document.querySelector("#id_date_start").value;
    end_date = document.querySelector("#id_date_end").value;
    model_id = document.querySelector('#modelID').value;
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log(csrftoken);
    
    const request = new Request(apiEndpointGetPredictions(model_id), {
        headers: {'X-CSRFToken': csrftoken}
    });
    
    fetch(request, {
        method: 'POST',
        body: JSON.stringify({
            start_date: start_date,
            end_date: end_date
        }),
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(predictions => {
        console.log(predictions);
        Plotly.newPlot('myDiv', predictionsToPlotData(predictions), layout);
    })
}

function toggle_prediction(model_id) {
    fetch(apiEndpointPredictionSwitch(model_id))
    .then(response => response.json())
    .then(entity => {
        console.log(entity.entities)
    });
}

function submit_form() {
    document.querySelector('#dateform').submit();
}

function get_helptext_context_broker() {
    return `<h4>Context Broker IDS</h4> <br>
    For real time predictions the model requires the latest data from all predictor variables used for model calibration. 
    This data transfer is implemented via the FIWARE Orion Context Broker. In the Context Broker every site is an entity, which
    collects and provides data. For transferring the data, the values for "DateObserved" and the value of predictor variable 
    ("flow" (WWWTP, Network, Riverflow), "precipitation" (Rainfall)) have to be updated using a PATCH request. 
    An example can be found 
    <a href="https://fiware-orion.readthedocs.io/en/1.13.0/user/walkthrough_apiv2/index.html#update-entity"> <strong>here</strong></a>
    using the NGSI-v2. The relevant URL for the predictor variables of this specific model are: <hr>`;
}

function append_broker_ids(model_id) {
    brokerIDdiv = document.querySelector("#brokerIDs");
    brokerIDdiv.className = "alert-primary m-3 p-3";
    
    text = document.createElement('div');
    text.innerHTML = get_helptext_context_broker();
    brokerIDdiv.append(text);
    
    fetch(apiEndpointGetBrokerUrls(model_id))
    .then(response => response.json())
    .then(entity => {
        entity.forEach(element => {
            d = document.createElement('div'); 
            d.innerHTML = htmlStrong(element.name + ': ');
            d.innerHTML += urlBrokerEntityAttributes(element.ID);
            d.innerHTML += '<hr>';
            brokerIDdiv.append(d);
        });
    });
}

function show_broker_ids() {
    brokerDiv = document.querySelector('#brokerIDs');
    brokerDiv.style.borderRadius = '2rem';
    var checked = document.querySelector('#broker_id_switch').checked;
    console.log(checked);
    brokerDiv.style.display = (checked ? "block" : "none");
}

// call Api endpoint for creating entities in the Orion context Broker
function createEntities(model_id) {
    fetch(apiEndpointPredictionSwitch(model_id))
    .then(response => response.json())
    .then(prediction => {
        console.log("ok")
    });
}