import sys
sys.path.insert(0, "package/")
import json
import requests
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_service_event(event, service="Service"):
    
    return [
        {
            "name": service,
            "value": event["Trigger"]["Dimensions"][0]["value"],
            "inline": "True"
        },
        {
            "name": "Alarme",
            "value": event["AlarmName"],
            "inline": "True"
        },
        {
            "name": "Descricao",
            "value": event["AlarmDescription"],
            "inline": "True"
        },
        {
            "name": "Status Anterior",
            "value": event["OldStateValue"]  ,
            "inline": "True"
        },
        {
            "name": "Gatilho",
            "value": event["Trigger"]["MetricName"],
            "inline": "True"
        },
        {
            "name": "Motivo",
            "value": event["NewStateReason"],
            "inline": "False"
        },
        {
            "name": "Aviso!",
            "value": aviso,
            "inline": "False"
        }
    ]

def handler(event, context):
    webhook_url = os.getenv("WEBHOOK_URL")
    parsed_message = []
    for record in event.get("Records", []):
        sns_message = json.loads(record["Sns"]["Message"])
        global aviso
        if sns_message.get("OldStateValue") == "OK":
            embedColor = 16711680
            aviso = "O tempo de delay está maior que "+ str((sns_message['Trigger']['Threshold']) / 60) + " minutos!"
        else:
            embedColor = 3066993
            aviso = "O tempo de delay está dentro dos limites aceitaveis!👍"
        is_alarm = sns_message.get("Trigger", None)
        if is_alarm:
            if (is_alarm["Namespace"] == "AWS/SQS"):
                logging.info("Alarm from SQS")
                parsed_message = parse_service_event(sns_message,"SQS")
        if not parsed_message:
            parsed_message = [{
                "name": "Something not parsed happened",
                "value": json.dumps(sns_message)
            }]

        discord_data = {
            "username": "AWS",
            "avatar_url": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
            "embeds": [{
                "color": embedColor,
                "fields": parsed_message
            }]
        }
        print(json.dumps(discord_data))
        
        headers = {"content-type": "application/json"}
        response = requests.post(webhook_url, data=json.dumps(discord_data), headers=headers)

        logging.info(f"Discord response: {response.status_code}")
        logging.info(response.content)