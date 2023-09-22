import streamlit as st
import pandas as pd
import numpy as np

# Streamlit app setup
st.title("Optimisation d'affectation de la taxe d'apprentissage")

# Upload Excel file
uploaded_file = st.file_uploader("Téléchargez votre fichier Excel", type=["xlsx"])

if uploaded_file:
    # Read Excel file into a DataFrame
    df = pd.read_excel(uploaded_file)
    
    # Check for column existence
    if all(col in df.columns for col in ['SIRET ENTREPRISE', 'TA SOLDE PAIE', 'SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER']):
    
        # Sort dataframes
        df_enterprises = df[['SIRET ENTREPRISE', 'TA SOLDE PAIE']].drop_duplicates().sort_values(by='TA SOLDE PAIE', ascending=False)
        df_schools = df[['SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER']].drop_duplicates().sort_values(by='MONTANT A ATTRIBUER', ascending=False)

        # Create an empty DataFrame for the matrix
        matrix_df = pd.DataFrame(index=df_schools['SIRET ETABLISSEMENT'].values, columns=df_enterprises['SIRET ENTREPRISE'].values)
        matrix_df.fillna(0, inplace=True)

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
