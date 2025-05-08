import pandas as pd
import glob

csv_files = glob.glob('./csv/**/*.csv', recursive=True)
dfs = [pd.read_csv(file) for file in csv_files]
combined_df = pd.concat(dfs, ignore_index=True)
combined_df = combined_df.drop_duplicates(subset=['position', 'candidate'])

combined_df.to_csv('candidate.csv', index=False)
