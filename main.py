import requests
import json
from datetime import datetime, timedelta
from Operations import SuperCrud

# Keep Secrets Safe
with open("secrets.json") as f:

    configs = json.loads(f.read())

def get_env_var(setting, configs=configs):

    try:
        val = configs[setting]
        if val == "True":
            val = True
        elif val == "False":
            val = False

        return val

    except KeyError:

        raise NotImplementedError("secrets.json is missing")

superCrud = SuperCrud()
OAuth = get_env_var("OAuth")
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + OAuth,
}

audit_end_date = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%dT%H:%M:%S')
audit_init_date = (datetime.now() + timedelta(hours=-24)).strftime('%Y-%m-%dT%H:%M:%S')

audit_url = "https://api.thousandeyes.com/v6/dashboards/" + get_env_var("dashboardId")  + "?&from=" + audit_init_date + "&to=" +audit_end_date
audit = requests.get(url=audit_url, headers=headers).json()


clean_up = []

for mapping in audit["reportDataComponentData"]["groupLabelMaps"]:

    for label in mapping["groupLabels"]:

        for dash_info in audit["reportDataComponentData"]["data"]:

            result = {}

            for group_id in dash_info["groups"]:

                if label["groupId"] == group_id['groupValue'] and int(dash_info['value']) == 100:

                    #print(label["groupLabel"] + " : " + str(dash_info['value']))

                    result.update({"groupLabel": label["groupLabel"], "value": dash_info['value']})
                    #result.setdefault(label["groupLabel"], dash_info['value'])
                    #result[label["groupLabel"]]

                    if result not in clean_up:
                        clean_up.append(result)
                    #print(result)

                elif label["groupId"] == group_id['groupValue'] and int(dash_info['value']) < 100:

                    result.update({"groupLabel": label["groupLabel"], "value": dash_info['value']})
                    #result.setdefault(label["groupLabel"], dash_info['value'])

                    if result not in clean_up:
                        clean_up.append(result)


print(audit['from'] + " to: " +  audit['to'])
to_mongo = {}
for i in clean_up:

    if i["value"] < 100.0:

        to_mongo.setdefault(i["groupLabel"], i['value'])

for i in clean_up:

    if i["value"] == 100.0:

        to_mongo.setdefault(i["groupLabel"], i['value'])


to_mongo.update({"from": audit['from'], "to": audit['to']})


insert = superCrud.create(to_mongo, table='Platinum')
insert['id'] = str(insert['_id'])
del insert['_id']

print(insert)


