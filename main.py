# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import math

pd.set_option('display.max_columns', None)

excel_file_path = "/mnt/c/Users/stefa/OneDrive/Documents/2023_05_06-Trofeo_Primavera_2.xlsx"
sheet_name = "AZZURRI START test"
header_row_idx = 1
columns = "A:J"
n_skaters = 14
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

    #print(df.head(n_skaters))
    for idx in range(1, n_judges+1):
        df[f'Totale {idx}'] = df[f'CONTENUTO TECNICO {idx}'] + df[f'CONTENUTO ARTISTICO {idx}']
    df['Totale'] = sum([df[f'Totale {idx}'] for idx in range(1, n_judges+1)])
    #print(df.head(n_skaters))

    victories = []
    for reference in df.itertuples():
        victories.append([])
        for competitor in df.itertuples():
            victory = 0
            if df.loc[reference.Index, 'ORDINE INGRESSO IN PISTA'] == df.loc[competitor.Index, 'ORDINE INGRESSO IN PISTA']:
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

    placement = sorted(majorities, key=lambda d: d['majority'], reverse=True)
    #print(placement)
    placement_dict = {placement[p]['id']: p+1 for p in range(len(placement))}
    #print(placement_dict)

    # punto 5) manuale TBD

    print("==========> VICTORIES ==========>")
    print("   | ", end="")
    for idx in range(len(victories)):
        print(f"{idx+1:02d}", end="    | ")
    print("MAJORITY")
    for ref in range(len(victories)):
        print(f"{ref+1:02d} | ", end="")
        for vs in range(len(victories[ref])):
            print(f"{victories[ref][vs]['victory']: 2.2f}", end=" | ")
        print(f"{majorities[ref]['majority']: 2.2f}   | {placement_dict[ref+1]}°")
    print("<========== VICTORIES <==========")

    print("==========> STANDINGS ==========>")
    for p in range(len(placement)):
        print(f"{p+1}°) {df.loc[placement[p]['id']-1, 'NOME']} {df.loc[placement[p]['id']-1, 'COGNOME']} "
              f"(#pista: {df.loc[placement[p]['id']-1, 'ORDINE INGRESSO IN PISTA']}, punteggio: {df.loc[placement[p]['id']-1, 'Totale']})")
    print("<========== STANDINGS <==========")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
