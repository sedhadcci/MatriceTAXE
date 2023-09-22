import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO

# Function to create downloadable excel link
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df, filename="matrice.xlsx", text="Télécharger la matrice Excel"):
    val = to_excel(df)
    b64 = base64.b64encode(val).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'

# Streamlit app setup
st.title("Optimisation d'affectation de la taxe d'apprentissage")

# Upload Excel file
uploaded_file = st.file_uploader("Téléchargez votre fichier Excel", type=["xlsx"])

if uploaded_file:
    # Read Excel file into a DataFrame, specifying dtype for SIRET columns
    df = pd.read_excel(uploaded_file, dtype={'SIRET ENTREPRISE': str, 'SIRET ETABLISSEMENT': str, '30%': str})

    required_cols = ['SIRET ENTREPRISE', 'TA SOLDE PAIE', 'SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER', '30%']
    if all(col in df.columns for col in required_cols):
        df_enterprises = df[['SIRET ENTREPRISE', 'TA SOLDE PAIE']].drop_duplicates().sort_values(by='TA SOLDE PAIE', ascending=False)
        df_schools = df[['SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER', '30%']].drop_duplicates().sort_values(by='MONTANT A ATTRIBUER', ascending=False)

        matrix_df = pd.DataFrame(index=['Montant total TA SOLDE PAIE', 'Reste à affecter'] + df_schools['SIRET ETABLISSEMENT'].astype(str).tolist(),
                                 columns=df_enterprises['SIRET ENTREPRISE'].astype(str).values)
        matrix_df.fillna(0, inplace=True)

        matrix_df.loc['Montant total TA SOLDE PAIE'] = df_enterprises['TA SOLDE PAIE'].values

        for index_e, row_e in df_enterprises.iterrows():
            remaining_amount_e = row_e['TA SOLDE PAIE']

            for index_s, row_s in df_schools.iterrows():
                remaining_amount_s = row_s['MONTANT A ATTRIBUER']
                is_30_percent = not pd.isna(row_s['30%'])

                if remaining_amount_e == 0:
                    break

                if remaining_amount_s == 0:
                    continue

                if is_30_percent:
                    attrib_amount = min(remaining_amount_e, remaining_amount_s, int(0.3 * row_e['TA SOLDE PAIE']))
                else:
                    attrib_amount = min(remaining_amount_e, remaining_amount_s)

                remaining_amount_e -= attrib_amount
                df_schools.at[index_s, 'MONTANT A ATTRIBUER'] -= attrib_amount
                matrix_df.at[row_s['SIRET ETABLISSEMENT'], row_e['SIRET ENTREPRISE']] = attrib_amount

            matrix_df.at['Reste à affecter', row_e['SIRET ENTREPRISE']] = remaining_amount_e

        for col in df_enterprises['SIRET ENTREPRISE'].astype(str):
            total_amount = matrix_df.loc['Montant total TA SOLDE PAIE', col]
            percentage_col_name = f"{col} (%)"

            if total_amount == 0:
                matrix_df[percentage_col_name] = 0
            else:
                matrix_df[percentage_col_name] = ((matrix_df[col] / total_amount) * 100).round(8)

        new_columns_order = []
        for col in df_enterprises['SIRET ENTREPRISE'].astype(str):
            new_columns_order.append(col)
            new_columns_order.append(f"{col} (%)")

        matrix_df = matrix_df[new_columns_order]
        
        matrix_df.replace(0, None, inplace=True)

        st.write("Matrice d'affectation avec pourcentage :")
        st.write(matrix_df)
        st.markdown(get_table_download_link(matrix_df), unsafe_allow_html=True)
    else:
        st.error("Le fichier Excel doit contenir les colonnes 'SIRET ENTREPRISE', 'TA SOLDE PAIE', 'SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER' et '30%'.")
