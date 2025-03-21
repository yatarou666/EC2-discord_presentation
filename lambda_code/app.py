import os
import json
import boto3
import logging
from nacl.signing import VerifyKey
logger = logging.getLogger()
logger.setLevel("INFO")

def lambda_handler(event: dict, context: dict):
    try:
        headers: dict = {k.lower(): v for k, v in event["headers"].items()}
        rawBody: str = event.get("body", "")
        signature: str = headers.get("x-signature-ed25519", "")
        timestamp: str = headers.get("x-signature-timestamp", "")
        if not verify(signature, timestamp, rawBody):
            return {
                "cookies": [],
                "isBase64Encoded": False,
                "statusCode": 401,
                "headers": {},
                "body": "",
            }
        
        req: dict = json.loads(rawBody)

        if req["type"] == 1:
            return {"type": 1}
        
        elif req["type"] == 2:
            command_name = req.get("data", {}).get("name", "")
            token = req.get("token", "")
            application_id = os.environ["APPLICATION_ID"]

            if command_name == "start":
                instance_type = "t4g.small"  # Default instance type
                options = req.get("data", {}).get("options", [])
                for opt in options:
                    if opt.get("name") == "type":
                        instance_type = opt.get("value", "t4g.small")
                
                parameter = {
                    "token": token,
                    "DISCORD_APP_ID": application_id,
                    "instance_type": instance_type
                    }
                
                payload = json.dumps(parameter)

                boto3.client("lambda").invoke(
                    FunctionName="DiscordSlashCommandController-Start",
                    InvocationType="Event",
                    Payload=payload,
                )

            elif command_name == "stop":
                options = req.get("data", {}).get("options", [])
                backup = "off" # Default

                for option in options:
                    if option["name"] == "backup":
                        backup = option["value"]
                        break

                parameter = {
                    "token": token,
                    "DISCORD_APP_ID": application_id,
                    "backup": backup,
                }

                payload = json.dumps(parameter)

                boto3.client("lambda").invoke(
                    FunctionName="DiscordSlashCommandController-Stop",
                    InvocationType="Event",
                    Payload=payload,
                )

            elif command_name == "status":
                parameter = {
                    "token": token,
                    "DISCORD_APP_ID": application_id,
                }
                payload = json.dumps(parameter)

                boto3.client("lambda").invoke(
                    FunctionName="DiscordSlashCommandController-Status",
                    InvocationType="Event",
                    Payload=payload,
                )

            else:
                raise Exception("Unexpected Command: {command_name}")
        return {
            "type": 5, # Acknowledge interaction
        }
    except Exception as e:
        logger.error(f"Exception: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def verify(signature: str, timestamp: str, body: str) -> bool:
    PUBLIC_KEY = os.environ["PUBLIC_KEY"]
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    try:
        verify_key.verify(
            f"{timestamp}{body}".encode(), bytes.fromhex(signature)
        )
    except Exception as e:
        logger.warning(f"failed to verify request: {e}")
        return False
    return True