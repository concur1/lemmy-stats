import os
import json
import csv
from zipfile import ZipFile


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
                     "description": instance["json"]["site_view"]["site"]["description"],
                     "users": instance["json"]["site_view"]["counts"]["users"],
                     "posts": instance["json"]["site_view"]["counts"]["posts"],
                     "comments": instance["json"]["site_view"]["counts"]["comments"],
                     "communities": instance["json"]["site_view"]["counts"]["communities"],
                     "users_active_day": instance["json"]["site_view"]["counts"]["users_active_day"],
                     "users_active_week": instance["json"]["site_view"]["counts"]["users_active_week"],
                     "users_active_month": instance["json"]["site_view"]["counts"]["users_active_month"],
                     "users": instance["json"]["site_view"]["counts"]["users"],
                     "users_active_half_year": instance["json"]["site_view"]["counts"]["users_active_half_year"],
                     "updated": instance["json"]["site_view"]["site"]["updated"],
                     "linked_federated_instances": instance["json"]["federated_instances"]["linked"],
                     "allowed_federated_instances": instance["json"]["federated_instances"]["allowed"]
                       }
                processed_json_data.append(row)
    return processed_json_data


def write_historical_csv(processed_json_data):
    for row in processed_json_data:
        fieldnames = row.keys()
        if not os.path.isfile(historical_filepath):
            with open(f"data/historical.csv", "w") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
                writer.writeheader()
                writer.writerow(row)
        else:
            with open(f"data/historical.csv", "a") as csvfile:
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


def check_processed_json_for_new_instances(processed_json_data):
    f = open("known_instances.txt", "r")
    metadata_instances = set(f.read().splitlines())
    f.close()
    all_instances = set()
    for row in processed_json_data:
        linked = row["linked_federated_instances"]
        if linked is not None:
            all_instances.update(linked)
        allowed = row["allowed_federated_instances"]
        if allowed is not None:
            all_instances.update(allowed)
    unknown_instances = [f"https://{instance}" for instance in all_instances if f"https://{instance}" not in metadata_instances]
    print(f"Instances not in known_instances.txt: \n{unknown_instances}\n\n")


historical_filepath = "data/historical.csv"
raw_json_dir = "data/raw_json"

all_json_data = load_from_json_dir(raw_json_dir)
processed_json_data = process_json_data(all_json_data)
check_processed_json_for_new_instances(processed_json_data)
write_historical_csv(processed_json_data)
zip_json_files(raw_json_dir)

