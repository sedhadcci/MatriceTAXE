import streamlit as st
import pandas as pd
import numpy as np

# Streamlit app setup
st.title("Optimisation d'affectation de la taxe d'apprentissage")

# Upload Excel file
uploaded_file = st.file_uploader("Téléchargez votre fichier Excel", type=["xlsx"])

if uploaded_file:
    # Read Excel file into a DataFrame, specifying dtype for SIRET columns
    df = pd.read_excel(uploaded_file, dtype={'SIRET ENTREPRISE': str, 'SIRET ETABLISSEMENT': str})

    # Check for column existence
    if all(col in df.columns for col in ['SIRET ENTREPRISE', 'TA SOLDE PAIE', 'SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER']):
        # Sort dataframes
        df_enterprises = df[['SIRET ENTREPRISE', 'TA SOLDE PAIE']].drop_duplicates().sort_values(by='TA SOLDE PAIE', ascending=False)
        df_schools = df[['SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER']].drop_duplicates().sort_values(by='MONTANT A ATTRIBUER', ascending=False)

        # Create an empty DataFrame for the matrix, converting SIRET to str
matrix_df = pd.DataFrame(index=['Montant Initial', 'Reste à Affecter'] + list(df_schools['SIRET ETABLISSEMENT'].astype(str).values),
                         columns=df_enterprises['SIRET ENTREPRISE'].astype(str).values)
matrix_df.fillna(0, inplace=True)

# Initialize the "Montant Initial" and "Reste à Affecter" rows with the TA SOLDE PAIE amounts
initial_amounts = df_enterprises.set_index('SIRET ENTREPRISE')['TA SOLDE PAIE'].to_dict()
matrix_df.loc['Montant Initial'] = initial_amounts
matrix_df.loc['Reste à Affecter'] = initial_amounts

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
                matrix_df.at[row_s['SIRET ETABLISSEMENT'], row_e['SIRET ENTREPRISE']] = attrib_amount

        st.write("Matrice d'affectation :")
        st.write(matrix_df)
    else:
        st.error("Le fichier Excel doit contenir les colonnes 'SIRET ENTREPRISE', 'TA SOLDE PAIE', 'SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER'.")
