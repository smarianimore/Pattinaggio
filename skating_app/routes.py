from skating_app import skating_app
from flask import render_template, request
import pandas as pd


sheet_name = "test parimeriti"  # TODO should be a parameter
header_row_idx = 0  # which row contains the header
data_columns = "A:N"
n_skaters = 11  # TODO should be a parameter
decimal_separator = ','

programs = [
        {'name': "PROGRAMMMA BREVE PER SINGOLI"},
        {'name': "COPPIE ARTISTICO"},
        {'name': "GRUPPI SPETTACOLO"},
        {'name': "SINCRONIZZATO"},
        {'name': "STYLE DANCE COPPIE DANZA e SOLO DANCE"},
        {'name': "FINALE SOLO DANCE (Cat. Senza Style Dance)"}
    ]


# A common pattern with decorators is to use them to register functions as callbacks for certain events. In this case,
# the @app.route decorator creates an association between the URL given as an argument and the function
@skating_app.route('/')
@skating_app.route('/index')
def index():
    return render_template('index.html',
                           home_title="Libertas Pattinaggio Forlì",
                           sub_title="Trofeo Primavera 2024",
                           programs=programs)


@skating_app.post('/')
#@skating_app.route('/', methods=['POST'])
def upload():
    # Read the File using Flask request
    file = request.files['file']
    # save file in local directory
    file.save(file.filename)

    # Parse the data as a Pandas DataFrame type
    df = pd.read_excel(file,
                       sheet_name,
                       header=header_row_idx,
                       usecols=data_columns,
                       nrows=n_skaters,
                       decimal=decimal_separator)

    # Return HTML snippet that will render the table
    html_df = df.to_html(classes='table table-stripped')
    return render_template('index.html',
                           home_title="Libertas Pattinaggio Forlì",
                           sub_title="Trofeo Primavera 2024",
                           programs=programs,
                           table=html_df)
