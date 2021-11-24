import os
import json
import csv
import sqlite3
from zipfile import ZipFile
import datetime


def load_from_json_dir(raw_json_dir):
    all_json_data = []
    for file in os.listdir(raw_json_dir):
        if file.endswith(".json"):
            with open(f"{raw_json_dir}/{file}", "r") as f:
                all_json_data.append(json.load(f))
    return all_json_data


def process_json_data(all_json_data):
    processed_json_data = []
    for file in all_json_data:
        for instance in file:
            if instance["status"] == "Success":
                row = {"timestamp": instance["timestamp"],
                     "url": instance["url"],
                     "status": instance["status"],
                     "name": instance["json"]["site_view"]["site"]["name"],
                     "online": instance["json"]["online"],
                     "version": instance["json"]["version"],
                     "description": instance["json"]["site_view"]["site"]["description"],
                     "users": instance["json"]["site_view"]["counts"]["users"],
                     "posts": instance["json"]["site_view"]["counts"]["posts"],
                     "comments": instance["json"]["site_view"]["counts"]["comments"],
                     "communities": instance["json"]["site_view"]["counts"]["communities"],
                     "users_active_day": instance["json"]["site_view"]["counts"]["users_active_day"],
                     "users_active_week": instance["json"]["site_view"]["counts"]["users_active_week"],
                     "users_active_month": instance["json"]["site_view"]["counts"]["users_active_month"],
                     "users_active_half_year": instance["json"]["site_view"]["counts"]["users_active_half_year"],
                     "updated": instance["json"]["site_view"]["site"]["updated"],
                     "linked_federated_instances": instance["json"]["federated_instances"]["linked"],
                     "allowed_federated_instances": instance["json"]["federated_instances"]["allowed"]
                       }
                processed_json_data.append(row)
            else:
                row = {"timestamp": instance["timestamp"],
                       "url": instance["url"],
                       "status": instance["status"],
                       "name": None,
                       "online": None,
                       "version": None,
                       "description": None,
                       "users": None,
                       "posts": None,
                       "comments": None,
                       "communities": None,
                       "users_active_day": None,
                       "users_active_week": None,
                       "users_active_month": None,
                       "users_active_half_year": None,
                       "updated": None,
                       "linked_federated_instances": None,
                       "allowed_federated_instances": None
                       }
                processed_json_data.append(row)
    return processed_json_data


def write_historical_csv(processed_json_data):
    for row in processed_json_data:
        fieldnames = row.keys()
        instance = row['url'].replace('https://', '')
        write_path = f"data/historical_csvs/{instance}.csv"
        if not os.path.isfile(write_path):
            with open(write_path, "w") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
                writer.writeheader()
                writer.writerow(row)
        else:
            with open(write_path, "a") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
                writer.writerow(row)


def zip_json_files(raw_json_dir):
    for file in os.listdir(raw_json_dir):
        if file.endswith(".json"):
            json_file_path = f'{raw_json_dir}/{file}'
            zip_file_path = f'{raw_json_dir}/hist_json_archive.zip'
            if not os.path.isfile(zip_file_path):
                with ZipFile(zip_file_path, 'w') as zipObj2:
                    zipObj2.write(json_file_path)
            else:
                with ZipFile(zip_file_path, 'a') as zipObj2:
                    zipObj2.write(json_file_path)
            os.remove(json_file_path)


def find_all_instances(processed_json_data):
    all_instances = set()
    for row in processed_json_data:
        linked = row["linked_federated_instances"]
        if linked is not None:
            all_instances.update(linked)
        allowed = row["allowed_federated_instances"]
        if allowed is not None:
            all_instances.update(allowed)
    return list(all_instances)


def find_metadata_instances():
    f = open("known_instances.txt", "r")
    metadata_instances = set(f.read().splitlines())
    f.close()
    return list(metadata_instances)


def save_instance_categories():
    all_instances = find_all_instances(processed_json_data)
    metadata_instances = find_metadata_instances()
    instance_dict = {"all_instances": all_instances,
    "metadata_instances": metadata_instances,
    "unknown_instances": find_unknown_instances(metadata_instances, all_instances)}
    with open(f'data/instance_categories/{str(timestamp)}.json', 'w') as f:
        json.dump(instance_dict, f)


def find_unknown_instances(metadata_instances, all_instances):
    return [f"https://{instance}" for instance in all_instances if f"https://{instance}" not in metadata_instances]


def create_or_append_sqllite_tables(processed_json_data):
    con = sqlite3.connect('data/lemmy.db')
    cur = con.cursor()
    schema = "timestamp text, url text, status text, name text, online integer, version text, description text, " \
             "users integer, posts integer, comments integer, communities integer, users_active_day integer, users_active_week " \
             "integer, users_active_month integer, users_active_half_year integer, updated text, " \
             "linked_federated_instances text, allowed_federated_instances text"
    cur.execute(f'''CREATE TABLE IF NOT EXISTS historical ({schema})''')
    for row in processed_json_data:
        values_to_insert = []
        for item in row.values():
            if not isinstance(item, int):
                item = str(item).replace("""'""", """''""")
                values_to_insert.append(f"'{item}'")
            else:
                values_to_insert.append(str(item))

        values_to_insert_string = ", ".join(values_to_insert)
        insert_string = f"INSERT INTO historical VALUES ({values_to_insert_string})"
        cur.execute(insert_string)
        con.commit()
    con.close()

timestamp = datetime.datetime.now()
raw_json_dir = "data/raw_json"

all_json_data = load_from_json_dir(raw_json_dir)
processed_json_data = process_json_data(all_json_data)
create_or_append_sqllite_tables(processed_json_data)
save_instance_categories()
zip_json_files(raw_json_dir)
print(f"convert and load to historical table: {datetime.datetime.now() - timestamp}")
