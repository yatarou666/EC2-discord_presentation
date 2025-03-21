import boto3
import os
import time
import json
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INSTANCE_ID = os.environ["INSTANCE_ID"]

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    backup = event.get("backup", "off")

    # backupが'on'の場合のみ、バックアップ処理を実施する
    if backup == "on":
        commands = [
            "sudo systemctl stop minecraft",
            "/home/ec2-user/backup_world.sh"
        ]

        command_id = send_commands(commands)
        status = wait_for_command(command_id, INSTANCE_ID)

        if status != "Success":
            logger.error(f"Backup failed with status: {status}")
            send_discord_message(event, f"バックアップに失敗しました: {status}")
            return {"status": 2, "reason": f"バックアップに失敗 ({status})"}

        logger.info("バックアップ成功")

    # EC2インスタンス停止処理
    stop_result = stop_ec2(INSTANCE_ID)

    if stop_result["status"] == 0:
        send_discord_message(event, "Server stopped!")
    elif stop_result["status"] == 1:
        send_discord_message(event, "Server is already stopped")
    else:
        send_discord_message(event, "Server stop failed")

    return {"status": "completed"}

def send_commands(commands):
    ssm_client = boto3.client("ssm")
    response = ssm_client.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands}
    )
    return response['Command']['CommandId']

def check_command_status(command_id):
    ssm_client = boto3.client("ssm")
    try:
        response = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=INSTANCE_ID
        )
        return response["Status"]
    except ssm_client.exceptions.InvocationDoesNotExist:
        # コマンドがまだ反映されていない → Pendingとして待機継続
        logger.info("Command not yet available, retrying...")
        return "Pending"

def wait_for_command(command_id, instance_id, timeout=600, interval=10):
    elapsed_time = 0
    while elapsed_time < timeout:
        status = check_command_status(command_id)
        logger.info(f"Command status: {status}")
        if status in ["Success", "Failed", "TimedOut", "Cancelled"]:
            return status
        time.sleep(interval)
        elapsed_time += interval
    return "Timeout"

def stop_ec2(instance_id: str) -> dict:
    try:
        ec2_client = boto3.client("ec2")
        status_response = ec2_client.describe_instances(InstanceIds=[instance_id])

        if status_response["Reservations"][0]["Instances"][0]["State"]["Name"] == "stopped":
            return {"status": 1}

        ec2_client.stop_instances(InstanceIds=[instance_id])

        waiter_stopped = ec2_client.get_waiter("instance_stopped")
        waiter_stopped.wait(InstanceIds=[instance_id])

        return {"status": 0}

    except Exception as e:
        logger.error("Stopping instance failed: " + str(e))
        return {"status": 2} 

def send_discord_message(event, message_text):
    application_id = event["DISCORD_APP_ID"]
    interaction_token = event["token"]
    message = {"content": message_text}

    r = requests.post(
        url=f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}",
        data=json.dumps(message),
        headers={"Content-Type": "application/json"},
    )

    logger.debug(r.text)
    return r.status_code
