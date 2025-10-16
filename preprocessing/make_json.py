import pandas as pd
import json
import re
df_EVADES = pd.read_csv('EVADES.csv')
def process_row(row):
    # Initialize the item dictionary
    item = {
        'defences': []
    }
    
    # Process Counteracting defence and Defence finder link
    if pd.notna(row['Counteracting defence']) and pd.notna(row['Defence finder link']):
        defences = row['Counteracting defence'].split(';')
        links = row['Defence finder link'].split(';')
        
        # Ensure we have matching counts (trim if necessary)
        min_length = min(len(defences), len(links))
        defences = defences[:min_length]
        links = links[:min_length]
        
        for defence, link in zip(defences, links):
            item['defences'].append({
                'defence_name': defence.strip(),
                'link': link.strip()
            })
    
    # Process Protein source
    protein_source = str(row['Protein source']) if pd.notna(row['Protein source']) else ''
    link_match = re.search(r'\((https?://[^)]+)\)', protein_source)
    
    if link_match:
        item['Protein source'] = {
            'name': re.sub(r'\s*\(https?://[^)]+\)', '', protein_source).strip(),
            'link': link_match.group(1)
        }
    else:
        item['Protein source'] = {
            'name': protein_source.strip(),
            'link': None
        }
    
    # Add other columns (adjust as needed)
    for col in row.index:
        if col not in ['Counteracting defence', 'Defence finder link', 'Protein source']:
            item[col] = row[col] if pd.notna(row[col]) else None
    
    return item

# Convert DataFrame to JSON
result = [process_row(row) for _, row in df_EVADES.iterrows()]
json_output = json.dumps(result, indent=2)

# Save to file or use as needed
with open('EVADES.json', 'w') as f:
    f.write(json_output)
