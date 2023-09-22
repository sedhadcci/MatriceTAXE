import streamlit as st
import pandas as pd
import numpy as np

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)

    # Separate into two different DataFrames and sort them
    df_enterprises = df[['SIRET ENTREPRISE', 'TA SOLDE PAIE']].drop_duplicates().sort_values(by='TA SOLDE PAIE', ascending=False)
    df_schools = df[['SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER']].drop_duplicates().sort_values(by='MONTANT A ATTRIBUER', ascending=False)

    # Create an empty DataFrame for the matrix
    matrix_df = pd.DataFrame(index=['Montant total TA SOLDE PAIE', 'Reste à affecter'] + df_schools['SIRET ETABLISSEMENT'].astype(str).tolist(),
                             columns=df_enterprises['SIRET ENTREPRISE'].astype(str).values)
    matrix_df.fillna(0, inplace=True)

    # Fill the "Montant total TA SOLDE PAIE" row
    matrix_df.loc['Montant total TA SOLDE PAIE'] = df_enterprises['TA SOLDE PAIE'].values

    # Start attributing amounts
    for index_e, row_e in df_enterprises.iterrows():
        remaining_amount_e = row_e['TA SOLDE PAIE']

        for index_s, row_s in df_schools.iterrows():
            remaining_amount_s = row_s['MONTANT A ATTRIBUER']

            if remaining_amount_e == 0:
                break

            if remaining_amount_s == 0:
                continue

            # Calculate the amount to be attributed
            attrib_amount = min(remaining_amount_e, remaining_amount_s)

            # Update remaining amounts and the matrix
            remaining_amount_e -= attrib_amount
            df_schools.at[index_s, 'MONTANT A ATTRIBUER'] -= attrib_amount
            matrix_df.at[str(row_s['SIRET ETABLISSEMENT']), str(row_e['SIRET ENTREPRISE'])] = attrib_amount

        # Fill the "Reste à affecter" row
        matrix_df.at['Reste à affecter', str(row_e['SIRET ENTREPRISE'])] = remaining_amount_e

    st.write("Matrice d'affectation :")
    st.write(matrix_df)
