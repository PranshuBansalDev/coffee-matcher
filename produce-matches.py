import os
import itertools

import pandas as pd

# convenience constants
matches = "matches"
people = "people"

# Inputs
dataset_id = 7

# Filenames
ifile_name = f'./inputs/test-dataset-{dataset_id}.csv'
ofile_dir = f'./outputs/input-{dataset_id}'

if not os.path.exists(ofile_dir):
    os.mkdir(ofile_dir)


# Header info
firstName_col = "firstName"
lastName_col = "lastName"
email_col = "email"

def i_to_str(i: int, prefix: str="Week"):
    return f'{prefix}_{i+1:03d}'

def find_first_avail_week(weeks: dict, person_a: str, person_b: str):
    for val in weeks.values():
        if (person_a not in val[people]) and (person_b not in val[people]):
            return val
    
    raise "AAHHH"


df = pd.read_csv(ifile_name)

# Extrapolated info
seenBefore_col = 'seenBefore'
mergedId_col = "mergedId"

df[mergedId_col] = df.apply(lambda row: (f"{row[email_col]}|{row[firstName_col]}|{row[lastName_col]}"), axis=1)
df[seenBefore_col] = df.apply(lambda x: [], axis=1)

# Figure out all possible pairings
combos = set(itertools.combinations(df[mergedId_col].to_list(), 2))

# max number of weeks for this to happen over (e.g. 1 match per week, but we can do better than that)
# consider these placeholders
weeks = {i_to_str(i):{matches: [], people: []} for i in range(0, len(combos))}

## core matching algorithm
used_combos = set()
available_combos = combos.difference(used_combos)
while len(available_combos) > 0:
    for combo in available_combos:
        person_a = combo[0]
        person_b = combo[1]

        person_a_seen_before = df[df[mergedId_col] == person_a].iloc[0][seenBefore_col]
        person_b_seen_before = df[df[mergedId_col] == person_b].iloc[0][seenBefore_col]

        have_met = (person_b in person_a_seen_before) or (person_a in person_b_seen_before)

        if not have_met:
            week = find_first_avail_week(weeks, person_a, person_b)
            week[people].append(person_a)
            week[people].append(person_b)
            week[matches].append(combo)
            used_combos.add(combo)
        
    available_combos = combos.difference(used_combos)

## Now that we have the matches, clean it up and make it look pretty
# Then output to csv
for week in weeks:
    ofile_name = ofile_dir + f"/{week}.csv"
    df = pd.DataFrame(weeks[week]['matches'])

    if not df.empty:
        df.columns = ['person_a', 'person_b']
        df['split_a'] = df.apply(lambda row: row['person_a'].split("|"), axis=1)
        df['split_b'] = df.apply(lambda row: row['person_b'].split("|"), axis=1)

        df['person_a_email'] = df.apply(lambda row: row['split_a'][0], axis=1)
        df['person_a_firstName'] = df.apply(lambda row: row['split_a'][1], axis=1)
        df['person_a_lastName'] = df.apply(lambda row: row['split_a'][2], axis=1)

        df['person_b_email'] = df.apply(lambda row: row['split_b'][0], axis=1)
        df['person_b_firstName'] = df.apply(lambda row: row['split_b'][1], axis=1)
        df['person_b_lastName'] = df.apply(lambda row: row['split_b'][2], axis=1)

        df['emails'] = df.apply(lambda row: row['person_a_email'] + "; " + row['person_b_email'], axis=1)
        df.drop(columns=['person_a', 'person_b', 'split_a', 'split_b'], inplace=True)
        df.to_csv(ofile_name, index=False)
