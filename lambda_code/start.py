import os
import json
import requests
import boto3
import logging
from status import status_ec2

logger = logging.getLogger()
logger.setLevel("INFO")

def lambda_handler(event, context):
    logger.info("Starting start.py script")

    instance_id = os.environ["INSTANCE_ID"]
    region = os.environ["AWS_REGION"]

    # インスタンスタイプをeventから取得
    instance_type = event.get("instance_type", "t4g.small")
    application_id = event["DISCORD_APP_ID"]
    interaction_token = event["token"]

    ec2_client = boto3.client("ec2", region_name=region)
    
    # 現在のインスタンス状態を確認
    result = status_ec2(instance_id)

    if result["status"] == 1:  # 停止中 → タイプ変更＆起動
        try:
            logger.info(f"Modifying instance type to {instance_type}")
            ec2_client.modify_instance_attribute(
                InstanceId=instance_id,
                Attribute='instanceType',
                Value=instance_type
            )

            logger.info("Starting instance...")
            ec2_client.start_instances(InstanceIds=[instance_id])

            # 起動待機
            waiter = ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])
            logger.info("Instance started")

            # IP再取得
            desc = ec2_client.describe_instances(InstanceIds=[instance_id])
            public_ip = desc['Reservations'][0]['Instances'][0]['PublicIpAddress']

            message = {"content": f"Server started with `{instance_type}`\n```{public_ip}```"}
        except Exception as e:
            logger.error(f"Failed to start instance: {e}")
            message = {"content": "Error occurred during instance start."}

    elif result["status"] == 0:
        message = {"content": "Server becomes ready!\n```\n{}\n```".format(result["ip"])}
    elif result["status"] == 2:
        message = {"content": "Starting instance process failed"}
    else:
        message = {"content": "Unexpected error at starting process"}
    payload = json.dumps(message)
    r = requests.post(
        url=f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    logger.debug(r.text)
    logger.info("Finished starting script")
    return r.status_code

# def start_ec2(instance_id: str) -> dict:
#     try:
#         logger.info("Starting instance: " + str(instance_id))
#         region = os.environ["AWS_REGION"]
#         ec2_client = boto3.client("ec2", region_name=region)
#         status_response = ec2_client.describe_instances(InstanceIds=[instance_id])
#         if (status_response["Reservations"][0]["Instances"][0]["State"]["Name"] == "running"):
#             logger.info("Instance is already running: " + str(instance_id))
#             return {"status": 1, "ip": get_public_ip(status_response)}
#         else:
#             logger.info("Start instance: " + str(instance_id))
#             response = ec2_client.start_instances(InstanceIds=[instance_id])
#             logger.debug(response)
#             logger.info("Waiting for Instance to be ready: " + str(instance_id))
#             try:
#                 waiter_running = ec2_client.get_waiter("instance_running")
#                 waiter_status = ec2_client.get_waiter("instance_status_ok")
#                 waiter_running.wait(InstanceIds=[instance_id])
#                 waiter_status.wait(InstanceIds=[instance_id])
#                 logger.info("Starting instance: " + str(instance_id))
#                 return {"status": 0, "ip": get_public_ip(ec2_client.describe_instances(InstanceIds=[instance_id]))}
#             except Exception as e:
#                 logger.error("Starting instance process failed.")
#                 logger.error(str(e))
#                 return {"status": 2}
#     except Exception as e:
#         logger.error(str(e))
#         return {"status": 3}

def get_public_ip(response: dict) -> str:
    try:
        ip_address = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    except KeyError as e:
        logger.warning("Public IP not assigned yet.")
        ip_address = "IP not obtained"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        ip_address = "failed to obtain IP"
    return ip_address