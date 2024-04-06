import math
from decimal import Decimal, ROUND_HALF_UP

from skating_app import skating_app
from flask import render_template, request
import pandas as pd


header_row_idx = 0  # which row contains the header
data_columns = "A:N"
header_score_tech = "DIFFICOLTA"
header_score_art = "STILE"
entrance_order = "INGRESSO"
decimal_separator = ','

n_judges = 3
majority_threshold = 1.5

programs = [
        {'name': "PROGRAMMMA BREVE PER SINGOLI"},
        {'name': "COPPIE ARTISTICO"},
        {'name': "GRUPPI SPETTACOLO"},
        {'name': "SINCRONIZZATO"},
        {'name': "STYLE DANCE COPPIE DANZA e SOLO DANCE"},
        {'name': "FINALE SOLO DANCE (Cat. Senza Style Dance)"}
    ]

filename = None
df = None


# A common pattern with decorators is to use them to register functions as callbacks for certain events. In this case,
# the @app.route decorator creates an association between the URL given as an argument and the function
@skating_app.route('/')
@skating_app.route('/index')
def index():
    return render_template('index.html',
                           home_title="Libertas Pattinaggio Forlì",
                           sub_title="Trofeo Primavera 2024",
                           programs=programs)


@skating_app.post('/file_upload')
def upload():
    # Read the File using Flask request
    file = request.files['file']
    # save file in local directory
    file.save(file.filename)
    global filename
    filename = file.filename

    # Return HTML snippet that will render the table
    return render_template('index.html',
                           home_title="Libertas Pattinaggio Forlì",
                           sub_title="Trofeo Primavera 2024",
                           programs=programs,
                           upload_ok=file.filename)


@skating_app.post('/config_sheet')
def config_sheet():
    # Parse the data as a Pandas DataFrame type
    global filename
    global df
    df = pd.read_excel(filename,
                       request.form['sheet_name'],
                       header=header_row_idx,
                       usecols=data_columns,
                       nrows=int(request.form['n_skaters']),
                       decimal=decimal_separator)

    # Return HTML snippet that will render the table
    html_df = df.to_html(classes='table table-striped table-bordered table-hover table-sm')
    return render_template('index.html',
                           home_title="Libertas Pattinaggio Forlì",
                           sub_title="Trofeo Primavera 2024",
                           programs=programs,
                           table=html_df,
                           upload_ok=filename)


@skating_app.get('/standings')
def standings():
    global df
    #########################################
    # 1-2) CALCOLO MATRICE VITTORIE, CASO B #
    #########################################

    victories_matrix = {}  # dict with {skater: {competitor: victories}}
    print("==========> Victories matrix:")
    for skater_ref in df.itertuples():
        victories_matrix[int(df.loc[skater_ref.Index, entrance_order])] = {}
        print(f"{df.loc[skater_ref.Index, entrance_order]} vs:")
        for skater_vs in df.itertuples():
            victories = 0
            if df.loc[skater_ref.Index, entrance_order] != df.loc[
                skater_vs.Index, entrance_order]:  # NOT comparing skater with herself
                for idx in range(1, n_judges + 1):
                    if math.isclose(df.loc[skater_ref.Index, f'TOTALE {idx}'],
                                    df.loc[skater_vs.Index, f'TOTALE {idx}']):
                        if math.isclose(df.loc[skater_ref.Index, f'{header_score_art} {idx}'],
                                        df.loc[skater_vs.Index, f'{header_score_art} {idx}']):
                            victories += 0.5
                        elif df.loc[skater_ref.Index, f'{header_score_art} {idx}'] > df.loc[
                            skater_vs.Index, f'{header_score_art} {idx}']:
                            victories += 1
                    elif df.loc[skater_ref.Index, f'TOTALE {idx}'] > df.loc[skater_vs.Index, f'TOTALE {idx}']:
                        victories += 1
                victories_matrix[int(df.loc[skater_ref.Index, entrance_order])][
                    int(df.loc[skater_vs.Index, entrance_order])] = victories
                print(f"\t{df.loc[skater_vs.Index, entrance_order]}: {victories}", end="")
        print()
    # print(json.dumps(victories_matrix, indent=4))

    ######################################
    # 3) CALCOLO VITTORIE DI MAGGIORANZA #
    ######################################

    majorities_per_skater = {}  # dict with {skater: majority score}
    for skater_ref in victories_matrix:
        majorities = 0
        for skater_vs in victories_matrix[skater_ref]:
            if math.isclose(victories_matrix[skater_ref][skater_vs], majority_threshold):
                majorities += 0.5
            elif victories_matrix[skater_ref][skater_vs] > majority_threshold:
                majorities += 1
        majorities_per_skater[skater_ref] = majorities
    print(f"{majorities_per_skater=}")

    #################
    # 4) CLASSIFICA #
    #################

    standings_majorities = sorted(majorities_per_skater.items(), key=lambda x: x[1], reverse=True)
    print(f"{standings_majorities=}")
    print("==========> Classifica per voti di maggioranza (step 4):")
    for pos, skater in zip(range(1, len(standings_majorities) + 1), standings_majorities):
        tot_rounded = Decimal(df.loc[skater[0] - 1, 'TOTALE'])
        tot_rounded = tot_rounded.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
        print(f"{pos}°) {df.loc[skater[0] - 1, 'NOME']} {df.loc[skater[0] - 1, 'COGNOME']} (#ingresso: {df.loc[skater[0] - 1, entrance_order]}, majorities: {skater[1]}, punteggio: {tot_rounded})")
    standings_majorities = [skater[0] for skater in standings_majorities]
    print(f"{standings_majorities=}")

    ########################################################
    # 5) RISOLUZIONE PARIMERITI IN VITTORIE DI MAGGIORANZA #
    ########################################################

    separate_victories_per_skater = {}  # dict with {skater: (victories, [competitors])}
    first = -1
    for skater_ref in majorities_per_skater:
        victories = 0
        competitors = []
        for skater_vs in majorities_per_skater:
            if skater_ref != skater_vs and math.isclose(majorities_per_skater[skater_ref], majorities_per_skater[skater_vs]):
                if first == -1:
                    first = skater_ref
                victories += victories_matrix[skater_ref][skater_vs]
                competitors.append(skater_vs)
        if victories > 0:
            separate_victories_per_skater[skater_ref] = (victories, competitors)

    if first != -1:
        print(f"{separate_victories_per_skater=}")
        standings_peer_majorities = sorted(separate_victories_per_skater.items(), key=lambda x: x[1][0], reverse=True)
        print(f"{standings_peer_majorities=}")
        standings_peer_majorities = [skater[0] for skater in standings_peer_majorities]
        #standings_peer_majorities = [10, 11, 9]  # force test
        print(f"{standings_peer_majorities=}")

        fix_point = standings_majorities.index(first)
        for idx in range(len(standings_peer_majorities)):
            standings_majorities[fix_point + idx] = standings_peer_majorities[idx]
        print(f"{standings_majorities=}")
        print("==========> Classifica con parimeriti per voti di maggioranza risolti (step 5):")
        standings_to_html = []
        for pos, skater in zip(range(1, len(standings_majorities) + 1), standings_majorities):
            tot_rounded = Decimal(df.loc[skater - 1, 'TOTALE'])
            tot_rounded = tot_rounded.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
            next_standing = f"{pos}°) {df.loc[skater - 1, 'NOME']} {df.loc[skater - 1, 'COGNOME']} (#ingresso: {df.loc[skater - 1, entrance_order]}, majorities: {majorities_per_skater[skater]}, punteggio: {tot_rounded})"
            standings_to_html.append(next_standing)
            print(next_standing)

    html_df = df.to_html(classes='table table-striped table-bordered table-hover table-sm')
    return render_template('index.html',
                           home_title="Libertas Pattinaggio Forlì",
                           sub_title="Trofeo Primavera 2024",
                           programs=programs,
                           table=html_df,
                           upload_ok=filename,
                           standings=standings_to_html)
