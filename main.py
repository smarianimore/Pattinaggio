# This is a sample Python script.
import json

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import math

pd.set_option('display.max_columns', None)

###############################
# FOGLIO DATI E NUMERO ATLETE #
###############################

excel_file_path = "/mnt/c/Users/stefa/OneDrive/Documents/Pattinaggio-Lugo-20240303.xlsx"
sheet_name = "promo B femminile"
header_row_idx = 0  # which row contains the header
data_columns = "A:N"
header_score_1 = "DIFFICOLTA"
header_score_2 = "STILE"
entrance_order = "INGRESSO"
n_skaters = 11
decimal_separator = ','

n_judges = 3
if n_judges == 3:
    majority = 1.5
elif n_judges == 5:
    majority = 2.5
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

    #################################
    # 1-2) CALCOLO MATRICE VITTORIE #
    #################################

    victories_matrix = {}  # dict with {skater: {competitor: victories}}
    for reference in df.itertuples():
        victories_matrix[int(df.loc[reference.Index, entrance_order])] = {}
        print(f"{df.loc[reference.Index, entrance_order]} vs:")
        for competitor in df.itertuples():
            victories = 0
            if df.loc[reference.Index, entrance_order] != df.loc[competitor.Index, entrance_order]:  # NOT comparing skater with herself
                for idx in range(1, n_judges + 1):
                    if math.isclose(df.loc[reference.Index, f'TOTALE {idx}'], df.loc[competitor.Index, f'TOTALE {idx}']):
                        victories += 0.5
                    elif df.loc[reference.Index, f'TOTALE {idx}'] > df.loc[competitor.Index, f'TOTALE {idx}']:
                        victories += 1
                victories_matrix[int(df.loc[reference.Index, entrance_order])][int(df.loc[competitor.Index, entrance_order])] = victories
                print(f"\t{df.loc[competitor.Index, entrance_order]}: {victories}", end="")
        print()
    #print(json.dumps(victories_matrix, indent=4))

    ######################################
    # 3) CALCOLO VITTORIE DI MAGGIORANZA #
    ######################################

    majorities = {}  # dict with {skater: majority score}
    for ref in victories_matrix:
        maj = 0
        for vs in victories_matrix[ref]:
            if math.isclose(victories_matrix[ref][vs], majority):
                maj += 0.5
            elif victories_matrix[ref][vs] > majority:
                maj += 1
        majorities[ref] = maj
    print(f"{majorities=}")

    ################################################
    # 4) CALCOLO PIAZZAMENTO (parimeriti possibili #
    ################################################
    placement = sorted(majorities, key=lambda d: d['majority'], reverse=True)  # list of {id: majority}
    print(f"{placement=}")

    ########################
    # VISUALIZZAZIONE VOTI #
    ########################

    placement_dict = {placement[p]['id']: p + 1 for p in range(len(placement))}  # dict of {id: placement}
    print(f"{placement_dict=}")
    print("==========> SCORES ==========>")
    print("   | ", end="")
    for idx in range(len(victories)):
        print(f"{idx + 1:02d}", end="    | ")
    print("MAJORITY", "STANDING", sep=" | ")
    for ref in range(len(victories)):
        print(f"{ref + 1:02d} | ", end="")
        for vs in range(len(victories[ref])):
            print(f"{victories[ref][vs]['victory']: 2.2f}", end=" | ")
        print(f"{majorities[ref]['majority']: 2.2f}    | {placement_dict[ref + 1]}°")
    print("<========== SCORES <==========")

    #######################################################################
    # 5) CALCOLO PIAZZAMENTO (parimeriti improbabili ma ancora possibili) #
    #######################################################################
    parities = {}  # who has same majority? ({majority: [peers]}) --- peer is idx of placement (sorted) list!
    separate_victories = {}  # victories against peers (dict {majority: [{peer: victories}, ...]})
    for idx_ref in range(len(placement)):
        if placement[idx_ref]['majority'] not in parities:
            parities[placement[idx_ref]['majority']] = [idx_ref]
            for idx_other in range(len(placement)):
                if idx_ref != idx_other and math.isclose(placement[idx_ref]['majority'], placement[idx_other]['majority']):
                    parities[placement[idx_ref]['majority']].append(idx_other)
    for maj in parities:
        if len(parities[maj]) != 1:  # otherwise nobody has same majority of that only guy
            separate_victories[maj] = []
            for one in parities[maj]:
                wins = 0
                for other in parities[maj]:
                    if one != other:
                        wins += victories[placement[one]['id']-1][placement[other]['id']-1]['victory']
                separate_victories[maj].append(
                    {
                        'peer': one,
                        'wins': wins
                    }
                )
    print(f"{parities=}")
    print(f"{separate_victories}")
    for maj in separate_victories:  # for each parity (same majority), order those peers according to vs. wins
        print(f"{maj=}", end=") ")
        sub_sep_vic = sorted(separate_victories[maj], key=lambda d: d['wins'], reverse=True)
        print(f"{sub_sep_vic=}")

    # order placement sub-list (of parities) according to this separate victories ordering
    print("==========> STANDINGS ==========>")
    skip = []
    standing = 1
    for p in placement:
        if p['majority'] not in separate_victories:
            print(f"{standing}°) {df.loc[p['id']-1, 'NOME']} {df.loc[p['id']-1, 'COGNOME']} "
                  f"(#pista: {df.loc[p['id']-1, entrance_order]}, punteggio: {df.loc[p['id'] - 1, 'Totale']})")
            standing += 1
        else:
            if p['majority'] not in skip:
                skip.append(p['majority'])  # avoid expanding sub_sep_vic moultiple times
                for e in separate_victories[p['majority']]:
                    print(
                        f"{standing}°) {df.loc[placement[e['peer']]['id']-1, 'NOME']} {df.loc[placement[e['peer']]['id']-1, 'COGNOME']} "
                        f"(#pista: {df.loc[placement[e['peer']]['id']-1, entrance_order]}, punteggio: {df.loc[placement[e['peer']]['id'] - 1, 'Totale']})")
                    standing += 1
    print("<========== STANDINGS <==========")

    ###################################################
    # 6) CALCOLO PIAZZAMENTO (parimeriti impossibili) #
    ###################################################

    more_parities = {}  # dict of {majorities: {wins: [peers]}} --- peer is idx of placement (sorted) list!
    for m in separate_victories:
        more_parities[m] = {}
        for idx_ref in range(len(separate_victories[m])):
            for idx_other in range(len(separate_victories[m])):
                if idx_ref != idx_other and math.isclose(separate_victories[m][idx_ref]['wins'], separate_victories[m][idx_other]['wins']):
                    if separate_victories[m][idx_ref]['wins'] not in more_parities[m]:
                        more_parities[m][separate_victories[m][idx_ref]['wins']] = [separate_victories[m][idx_ref]['peer']]
                    if separate_victories[m][idx_other]['peer'] not in more_parities[m][separate_victories[m][idx_ref]['wins']]:
                        more_parities[m][separate_victories[m][idx_ref]['wins']].append(separate_victories[m][idx_other]['peer'])
    print(f"{more_parities}")

    #########################################
    # VISUALIZZAZIONE CLASSIFICA DEFINITIVA #
    #########################################



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
