import os
import json
import requests
import boto3
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

def lambda_handler(event, context):
    logger.info("Starting script")
    instance_id = os.environ["INSTANCE_ID"]
    result = status_ec2(instance_id)
    application_id = event["DISCORD_APP_ID"]
    interaction_token = event["token"]
    message = {}
    if result["status"] == 1:
        message = {"content": "Server: Stopped"}
    elif result["status"] == 0:
        message = {"content": "Server: Running\n```\n{}\n```".format(result["ip"])}
    elif result["status"] == 2:
        message = {"content": "Server: Pending"}
    elif result["status"] == 3:
        message = {"content": "Unexpected instance status"}
    else:
        message = {"content": "Unexpected error at status check process"}
    payload = json.dumps(message)
    r = requests.post(
        url=f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    logger.debug(r.text)
    logger.info("Finished status checking script")
    return r.status_code

def status_ec2(instance_id: str) -> None:
    result = {}
    try:
        region = os.environ["AWS_REGION"]
        ec2_client = boto3.client("ec2", region_name=region)
        status_response = ec2_client.describe_instances(InstanceIds=[instance_id])
        status = status_response["Reservations"][0]["Instances"][0]["State"]["Name"]
        if (status == "running"):
            logger.info("Instance is running: " + str(instance_id))
            result["status"] = 0
            result["ip"] = status_response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        elif (status == "stopping" or status == "stopped"):
            logger.info("Instance is stoppping: " + str(instance_id))
            result["status"] = 1
        elif (status == "pending"):
            logger.info("Instance is pending: " + str(instance_id))
            result["status"] = 2
        else:
            logger.warning("Unexpected instance status")
            result["status"] = 3
        return result
    except Exception as e:
        logger.error(str(e))
        result["status"] = 4
        return result