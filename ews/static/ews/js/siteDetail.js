document.addEventListener('DOMContentLoaded', function() {

    document.querySelector('#helptext_upload').style.display = "none"

    help_toggler = document.querySelector('#helptext_upload_switch')
    help_toggler.checked = false
    help_toggler.addEventListener('change', () => show_helptext())

    append_helptext()    

    function append_helptext() {
        IDdiv = document.querySelector("#helptext_upload")
        IDdiv.className = "alert-primary m-3 p-3"
        IDdiv.style.borderRadius = "2rem"

        text = document.createElement('div')
        text.innerHTML = get_helptext_training();
        IDdiv.append(text)
    }
})

function get_helptext_training() {
    return `For training a machine learning model input data for the target variable (FIB concentrations) and 
    predictor variables (rainfall, wwtp, network, Riverflow are required). The data for each variable have to be uploaded as ".csv-file" 
    with 'comma' as column separator. For the data upload to work the "csv-file" and the data have to be in a specific format.

    <table class = "table alert-primary">
    <thead>
    <tr>
    <th scope="col">Column name</th>
    <th scope="col">Format</th>
    <th scope="col">Comment</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <th scope="row">date</th>
    <td> YYYY-MM-DD hh:mm:ss </td>
    <td> check that timezones are in the same format </td>
    </tr>
    <tr>
    <th scope="row">value</th>
    <td>numeric (decimal separator: period '.')</td>
    <td>Only untransformed data should be uploaded</td>
    </tr>
    </tbody>
    </table>
    `;
}

function show_helptext() {
    brokerDiv = document.querySelector('#helptext_upload');
    var checked = document.querySelector('#helptext_upload_switch').checked;
    console.log(checked);
    brokerDiv.style.display = (checked ? "block" : "none");
}
