# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import math

pd.set_option('display.max_columns', None)

excel_file_path = "/mnt/c/Users/stefa/OneDrive/Documents/2023_05_06-Trofeo_Primavera_2.xlsx"
sheet_name = "test"
n_skaters = 5

header_row_idx = 1
columns = "A:J"
decimal = ','

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
                             usecols=columns,
                             nrows=n_skaters,
                             decimal=decimal)

    ################################
    # AGGIUNTA PUNTEGGIO A DATASET #
    ################################
    #print(df.head(n_skaters))
    for idx in range(1, n_judges+1):
        df[f'Totale {idx}'] = df[f'CONTENUTO TECNICO {idx}'] + df[f'CONTENUTO ARTISTICO {idx}']
    df['Totale'] = sum([df[f'Totale {idx}'] for idx in range(1, n_judges+1)])
    #print(df.head(n_skaters))

    #################################
    # 1-2) CALCOLO MATRICE VITTORIE #
    #################################
    victories = []
    for reference in df.itertuples():
        victories.append([])
        for competitor in df.itertuples():
            victory = 0
            if df.loc[reference.Index, 'ORDINE INGRESSO IN PISTA'] == df.loc[competitor.Index, 'ORDINE INGRESSO IN PISTA']:  # comparing skater with herself
                victory = -1
            else:
                # print(f"reference={df.loc[reference.Index, 'COGNOME']} {df.loc[reference.Index, 'NOME']}, "
                #       f"competitor={df.loc[competitor.Index, 'COGNOME']} {df.loc[competitor.Index, 'NOME']}")
                for idx in range(1, n_judges + 1):
                    if df.loc[reference.Index, f'Totale {idx}'] > df.loc[competitor.Index, f'Totale {idx}']:
                        victory += 1
                    elif math.isclose(df.loc[reference.Index, f'Totale {idx}'], df.loc[competitor.Index, f'Totale {idx}']):
                        victory += 0.5
            victories[-1].append({
                'ref': f"{df.loc[reference.Index, 'COGNOME']} {df.loc[reference.Index, 'NOME']}",
                'vs': f"{df.loc[competitor.Index, 'COGNOME']} {df.loc[competitor.Index, 'NOME']}",
                'victory': victory
            })

    ######################################
    # 3) CALCOLO VITTORIE DI MAGGIORANZA #
    ######################################
    majorities = []
    for ref in range(len(victories)):
        maj = 0
        for vs in range(len(victories[ref])):
            if victories[ref][vs]['victory'] > majority:
                maj += 1
            elif math.isclose(victories[ref][vs]['victory'], majority):
                maj += 0.5
        majorities.append({
            'id': ref+1,
            'majority': maj
        })

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
                  f"(#pista: {df.loc[p['id']-1, 'ORDINE INGRESSO IN PISTA']}, punteggio: {df.loc[p['id']-1, 'Totale']})")
            standing += 1
        else:
            if p['majority'] not in skip:
                skip.append(p['majority'])  # avoid expanding sub_sep_vic moultiple times
                for e in separate_victories[p['majority']]:
                    print(
                        f"{standing}°) {df.loc[placement[e['peer']]['id']-1, 'NOME']} {df.loc[placement[e['peer']]['id']-1, 'COGNOME']} "
                        f"(#pista: {df.loc[placement[e['peer']]['id']-1, 'ORDINE INGRESSO IN PISTA']}, punteggio: {df.loc[placement[e['peer']]['id']-1, 'Totale']})")
                    standing += 1
    print("<========== STANDINGS <==========")

    ###################################################
    # 6) CALCOLO PIAZZAMENTO (parimeriti impossibili) #
    ###################################################



    #########################################
    # VISUALIZZAZIONE CLASSIFICA DEFINITIVA #
    #########################################



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
