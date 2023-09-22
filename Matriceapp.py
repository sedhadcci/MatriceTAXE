import streamlit as st
import pandas as pd

# Streamlit app setup
st.title("Optimisation d'affectation de la taxe d'apprentissage")

# Upload Excel file
uploaded_file = st.file_uploader("Téléchargez votre fichier Excel", type=["xlsx"])

if uploaded_file:
    # Read Excel file into a DataFrame
    df = pd.read_excel(uploaded_file)
    
    # Show uploaded data
    st.write("Données uploadées :")
    st.write(df)
    
    # Sort dataframes
    df_enterprises = df[['SIRET ENTREPRISE', 'TA SOLDE PAIE']].drop_duplicates().sort_values(by='TA SOLDE PAIE', ascending=False)
    df_schools = df[['SIRET ETABLISSEMENT', 'MONTANT A ATTRIBUER']].drop_duplicates().sort_values(by='MONTANT A ATTRIBUER', ascending=False)
    
    # Initialize results list
    results = []
    
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
            
            # Update remaining amounts
            remaining_amount_e -= attrib_amount
            df_schools.at[index_s, 'MONTANT A ATTRIBUER'] -= attrib_amount
            
            # Store the result
            results.append({
                'SIRET ENTREPRISE': row_e['SIRET ENTREPRISE'],
                'SIRET ETABLISSEMENT': row_s['SIRET ETABLISSEMENT'],
                'MONTANT ATTRIBUE': attrib_amount
            })
    
    # Display results
    st.write("Résultats de l'optimisation :")
    st.write(pd.DataFrame(results))
