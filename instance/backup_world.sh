#!/bin/bash

WORLD_DIR="/home/ec2-user/fabric-server/world"
BUCKET_NAME="fabric-mcserver"
REGION="ap-south-1"
TIMESTAMP=$(date '+%Y%m%d%H%M%S')
FILE_NAME="full_backup_${TIMESTAMP}.tar.gz"

# サーバー停止
echo "[INFO] Minecraftサーバーを停止します..."
sudo systemctl stop minecraft

sleep 10  # 安全に待機

# 圧縮＆S3直送
echo "[INFO] 圧縮してS3へアップロード中..."
tar -cz -C "$WORLD_DIR" . | aws s3 cp - "s3://$BUCKET_NAME/full/$FILE_NAME" --region "$REGION"
echo "[INFO] バックアップ完了 → $FILE_NAME"

