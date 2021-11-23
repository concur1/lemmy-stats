import json
import datetime
import aiohttp
import asyncio


async def fetch(url, session):
    try:
        async with session.get(f"{url}/api/v3/site") as response:
            api_json_text = await response.text()
    except Exception as e:
        # print(f"{url}/api/v3/site" + " "*(60-len(url)) + "(Failed)")
        return {"timestamp": str(timestamp), "status": "No Response", "url": url, "Exception": str(e), "json": None}
    if api_json_text is None:
        # print(f"{url}/api/v3/site" + " " * (60 - len(url)) + "(Failed)")
        return {"timestamp": str(timestamp), "status": "No API", "url": url, "Exception": None,  "json": None}
    else:
        try:
            api_json = json.loads(api_json_text)
        except:
            # print(f"{url}/api/v3/site" + " " * (60 - len(url)) + "(Failed)")
            return {"timestamp": str(timestamp), "status": "Could not parse API", "url": url, "Exception": None, "json": None}

    json_filtered = {}
    json_filtered['site_view'] = api_json['site_view']
    json_filtered['online'] = api_json['online']
    json_filtered['version'] = api_json['version']
    json_filtered['federated_instances'] = api_json['federated_instances']

    # print(f"{url}/api/v3/site" + " " * (60 - len(url)) + "(Success)")
    return {"timestamp": str(timestamp), "status": "Success", "url": url, "Exception": None, "json": json_filtered}


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for site in sites:
            tasks.append(asyncio.create_task(fetch(site, session)))
        response = await asyncio.gather(*tasks)
    return response


timestamp = datetime.datetime.now()
timestamp_str = str(timestamp)
print(timestamp_str)
f = open("known_instances.txt", "r")
sites = f.read().splitlines()
f.close()
html_pages = asyncio.run(main())
rows = []
for page in html_pages:
    rows.append(page)

with open(f'data/raw_json/{timestamp_str} - lemmy instances stats.json', 'w') as f:
    json.dump(rows, f)

print(f"fetch and save runtime: {datetime.datetime.now() - timestamp}")
