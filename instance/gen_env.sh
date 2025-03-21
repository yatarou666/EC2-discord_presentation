#!/bin/bash

# 総メモリ取得（MB単位）
TOTAL_MEM=$(free -m | awk '/Mem:/ {print $2}')

# 最大メモリ = 90% 割り当て
MAX_MEM=$(echo "$TOTAL_MEM*0.9" | bc | awk '{printf "%d", $1}')

# 最小メモリ = 70% 割り当て
MIN_MEM=$(echo "$TOTAL_MEM*0.7" | bc | awk '{printf "%d", $1}')

# JAVA_MEM 環境変数を .env に保存
echo "JAVA_MEM=-Xmx${MAX_MEM}M -Xms${MIN_MEM}M" > /home/ec2-user/fabric-server/.env
