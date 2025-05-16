import os
import pandas as pd
import zipfile
import json

class DataTransformer:
    def __init__(self, input_folder):
        self.input_folder = input_folder
        print(f"🕮️ Chargement des fichiers sources depuis : {self.input_folder}")
        if not os.path.exists(self.input_folder):
            raise FileNotFoundError(f"Dossier introuvable : {self.input_folder}")
        self.dataframes = self.load_dataframes()

    def get_all_files(self):
        return [
            os.path.join(self.input_folder, f)
            for f in os.listdir(self.input_folder)
            if not f.endswith(".zip")  
        ]

    def read_file(self, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
            elif ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.json_normalize(data)
            elif ext in ['.csv', '.txt']:
                try:
                    df = pd.read_csv(file_path, sep=',', engine='python', encoding='utf-8', nrows=10000)
                    if df.shape[1] <= 1:
                        df = pd.read_csv(file_path, sep=';', engine='python', encoding='utf-8', nrows=10000)
                except Exception:
                    try:
                        df = pd.read_csv(file_path, sep=';', engine='python', encoding='latin1', nrows=10000)
                    except Exception as inner_e:
                        print(f" Erreur secondaire pour {file_path} : {inner_e}")
                        return None
            else:
                print(f" Extension non supportée : {file_path}")
                return None

            if df.shape[1] > 1000:
                print(f" Trop de colonnes, ignoré : {file_path} (shape: {df.shape})")
                return None

            print(f" Chargé : {file_path} - Shape: {df.shape}")
            return df
        except Exception as e:
            print(f" Erreur lors de la lecture de {file_path} : {e}")
            return None

    def load_dataframes(self):
        dataframes = []
        max_rows = 1000000
        for file_path in self.get_all_files():
            df = self.read_file(file_path)
            if df is not None and not df.empty and df.shape[0] < max_rows:
                dataframes.append(df)
        return dataframes

    def clean_merge(self):
        print(" Nettoyage et fusion des données...")
        cleaned_dfs = []
        for df in self.dataframes:
            df_clean = df.copy()
            df_clean.columns = [c.strip().lower().replace(' ', '_')[:50] for c in df_clean.columns]
            df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]
            cleaned_dfs.append(df_clean)

        if not cleaned_dfs:
            raise ValueError("Aucun dataframe propre à fusionner.")

        merged_df = pd.concat(cleaned_dfs, ignore_index=True, sort=False)
        print(f"Fusion terminée. Shape finale : {merged_df.shape}")
        return merged_df

    def save_sql_files(self, df, train_ratio=0.8, output_dir='output_sql'):
        print("Génération des fichiers SQL...")
        os.makedirs(output_dir, exist_ok=True)

        df = df.dropna(how='all')

        # Conversion des colonnes contenant des listes ou des dictionnaires en chaînes de caractères
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, list) or isinstance(x, dict)).any():
                df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)

        df = df.drop_duplicates()

        df_train = df.sample(frac=train_ratio, random_state=42)
        df_test = df.drop(df_train.index)

        def df_to_sql_insert(df_part, table_name, file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                for _, row in df_part.iterrows():
                    columns = ', '.join([str(col) for col in df_part.columns])
                    values = []
                    for val in row:
                        if pd.isna(val):
                            values.append("NULL")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            safe_val = str(val).replace("'", "''")
                            values.append(f"'{safe_val}'")
                    values_str = ', '.join(values)
                    f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});\n")

        df_to_sql_insert(df_train, "election_result_train", os.path.join(output_dir, "train.sql"))
        df_to_sql_insert(df_test, "election_result_test", os.path.join(output_dir, "test.sql"))
        print(" SQL export terminé : train.sql et test.sql")

if __name__ == '__main__':
    input_folder = 'C:/Users/richa/Documents/cous_master_1/MSPR1/Scrapping/election_dataset'
    transformer = DataTransformer(input_folder)
    merged_df = transformer.clean_merge()
    transformer.save_sql_files(merged_df)
