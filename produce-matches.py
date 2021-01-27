import itertools
import csv

import pandas as pd

empty_slot = "-"

def i_to_str(i: int, prefix: str="Week"):
    return f'{prefix}_{i+1:03d}'

def get_email_arr(file_path: str, header: str) -> set:
    rv = set()
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rv.add(row[header])

    return rv       

def generate_table(emails: list, combos: list):
    weeks = [i_to_str(i) for i in range(0, len(combos))]
    d = {week: [empty_slot for email in emails] for week in weeks}
    d["Emails"] = emails
    df = pd.DataFrame(data=d)
    df.set_index("Emails", inplace=True)

    df = df.reindex(sorted(df.columns), axis=1)
    df = df.sort_index()

    return df

def fill_table(table: pd.DataFrame, combos: list):
    for i in range(len(combos)):
        combo = combos[i]
        person_a = combo[0]
        person_b = combo[1]
        
        person_a_free_slots = table.loc[person_a, :] == empty_slot
        person_b_free_slots = table.loc[person_b, :] == empty_slot

        free_slots = person_a_free_slots & person_b_free_slots
        first_free_slot = free_slots[free_slots == True].index[0]

        table.loc[person_a, first_free_slot] = person_b
        table.loc[person_b, first_free_slot] = person_a

    return table

def drop_empty_cells(table: pd.DataFrame):
    empty_cols = [col for col in table.columns if all(table[col] == empty_slot)]
    table.drop(empty_cols, axis=1, inplace=True)
    return table

dataset_id = 7
ifile_name = f'./inputs/test-dataset-{dataset_id}.csv'
ofile_name = f'./outputs/output-dataset-{dataset_id}.csv'

emails = list(get_email_arr(ifile_name, 'Email'))
combos = list(itertools.combinations(emails, 2))

table = generate_table(emails, combos)
table = fill_table(table, combos)
table = drop_empty_cells(table)

table.to_csv(ofile_name)
