# This is a sample Python script.
import json

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import math
from decimal import Decimal, ROUND_HALF_UP

pd.set_option('display.max_columns', None)

##############################################
# CONFIGURAZIONE FOGLIO DATI E NUMERO ATLETE #
##############################################

excel_file_path = "/mnt/c/Users/stefa/OneDrive/Documents/2024-trofeo-primavera.xlsx"
sheet_name = "AZZURRI START (M)"  # "promo B femminile"
header_row_idx = 1  # which row contains the header
data_columns = "A:N"
header_score_tech = "DIFFICOLTA"
header_score_art = "STILE"
entrance_order = "INGRESSO"
n_skaters = 11
decimal_separator = ','

n_judges = 3
if n_judges == 3:
    majority_threshold = 1.5
elif n_judges == 5:
    majority_threshold = 2.5
else:
    raise ValueError("Number of judges admissible values: 3, 5")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df = pd.read_excel(excel_file_path,
                       sheet_name,
                       header=header_row_idx,
                       usecols=data_columns,
                       nrows=n_skaters,
                       decimal=decimal_separator)

    print(df.head(n_skaters))

    #########################################
    # 1-2) CALCOLO MATRICE VITTORIE, CASO B #
    #########################################

    victories_matrix = {}  # dict with {skater: {competitor: victories}}
    print("==========> Victories matrix:")
    for skater_ref in df.itertuples():
        victories_matrix[int(df.loc[skater_ref.Index, entrance_order])] = {}
        print(f"{df.loc[skater_ref.Index, entrance_order]} vs:")
        for skater_vs in df.itertuples():
            victories = 0.0
            if df.loc[skater_ref.Index, entrance_order] != df.loc[skater_vs.Index, entrance_order]:  # NOT comparing skater with herself
                for idx in range(1, n_judges + 1):
                    if math.isclose(df.loc[skater_ref.Index, f'TOTALE {idx}'], df.loc[skater_vs.Index, f'TOTALE {idx}']):
                        if math.isclose(df.loc[skater_ref.Index, f'{header_score_art} {idx}'], df.loc[skater_vs.Index, f'{header_score_art} {idx}']):
                            victories += 0.5
                        elif df.loc[skater_ref.Index, f'{header_score_art} {idx}'] > df.loc[skater_vs.Index, f'{header_score_art} {idx}']:
                            victories += 1.0
                    elif df.loc[skater_ref.Index, f'TOTALE {idx}'] > df.loc[skater_vs.Index, f'TOTALE {idx}']:
                        victories += 1.0
                victories_matrix[int(df.loc[skater_ref.Index, entrance_order])][int(df.loc[skater_vs.Index, entrance_order])] = victories
                print(f"\t{df.loc[skater_vs.Index, entrance_order]}: {victories}", end="")
        print()
    #print(json.dumps(victories_matrix, indent=4))

    ######################################
    # 3) CALCOLO VITTORIE DI MAGGIORANZA #
    ######################################

    majorities_per_skater = {}  # dict with {skater: majority score}
    for skater_ref in victories_matrix:
        majorities = 0.0
        for skater_vs in victories_matrix[skater_ref]:
            if math.isclose(victories_matrix[skater_ref][skater_vs], majority_threshold):
                majorities += 0.5
            elif victories_matrix[skater_ref][skater_vs] > majority_threshold:
                majorities += 1.0
        majorities_per_skater[skater_ref] = majorities
    print(f"{majorities_per_skater=}")

    #################
    # 4) CLASSIFICA #
    #################

    standings_majorities = sorted(majorities_per_skater.items(), key=lambda x: x[1], reverse=True)
    print(f"{standings_majorities=}")
    print("==========> Classifica per voti di maggioranza (step 4):")
    for pos, skater in zip(range(1, len(standings_majorities) + 1), standings_majorities):
        tot_rounded = Decimal(float(df.loc[skater[0]-1, 'TOTALE']))
        tot_rounded = tot_rounded.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
        print(f"{pos}°) {df.loc[skater[0]-1, 'NOME']} {df.loc[skater[0]-1, 'COGNOME']} "
              f"(#ingresso: {df.loc[skater[0]-1, entrance_order]}, majorities: {skater[1]}, punteggio: {tot_rounded})")
    standings_majorities = [skater[0] for skater in standings_majorities]
    print(f"{standings_majorities=}")

    ########################################################
    # 5) RISOLUZIONE PARIMERITI IN VITTORIE DI MAGGIORANZA #
    ########################################################

    separate_victories_per_skater = {}  # dict with {skater: (victories, [competitors])}
    first = -1
    for skater_ref in majorities_per_skater:
        victories = 0.0
        competitors = []
        for skater_vs in majorities_per_skater:
            if skater_ref != skater_vs and math.isclose(majorities_per_skater[skater_ref], majorities_per_skater[skater_vs]):
                if first == -1:
                    first = skater_ref
                victories += victories_matrix[skater_ref][skater_vs]
                competitors.append(skater_vs)
        if victories > 0.0:
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
        for pos, skater in zip(range(1, len(standings_majorities) + 1), standings_majorities):
            tot_rounded = Decimal(float(df.loc[skater-1, 'TOTALE']))
            tot_rounded = tot_rounded.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
            print(f"{pos}°) {df.loc[skater-1, 'NOME']} {df.loc[skater-1, 'COGNOME']} "
                  f"(#ingresso: {df.loc[skater-1, entrance_order]}, majorities: {majorities_per_skater[skater]}, punteggio: {tot_rounded})")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
