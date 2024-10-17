import pandas as pd

data = pd.read_csv("./output_with_colors2.tsv", sep='\t')

new_colors = pd.read_csv("./colors2.tsv", sep='\t')

# match labels to new color

data['Color'] = data['Lineage'].map(new_colors.set_index('Lineage')['Color'])

# save to new file
data.to_csv("./output_with_colors3.tsv", sep='\t', index=False)