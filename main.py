import requests
from datetime import datetime, timedelta

OAuth = ""
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + OAuth,
}

audit_end_date = (datetime.now() + timedelta(days=-1)).strftime('%Y-%m-%dT%H:%M:%S')
audit_init_date = (datetime.now() + timedelta(days=-31)).strftime('%Y-%m-%dT%H:%M:%S')

audit_url = "https://api.thousandeyes.com/v6/dashboards/" # + "?&from=" + audit_init_date + "&to=" +audit_end_date
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
print(clean_up)

for i in clean_up:

    if i["value"] < 100.0:

        to_mongo.setdefault(i["groupLabel"], i['value'])

for i in clean_up:

    if i["value"] == 100.0:

        to_mongo.setdefault(i["groupLabel"], i['value'])


print(to_mongo)
