# AWS-EC2-discordbot
## 説明
AWSのEC2上に置いたminecraft serverを起動するdiscordBOTを作る。
環境変数.envはセキュリティ上gitには置かない。 \
中身は
- INSTANCE_ID
- AWS_RESION
- PUBLIC_KEY
- DISCORD_BOT_TOKEN
- APPLICATION_ID
を記載。

## 構成
AWS-EC2-discordbot/ \
　　├ README.md \
　　├ MCEC2.py \
　　├ .env \
　　├ lambda_code \
　　　　├ app.py \
　　　　├ start.py \
　　　　├ stop.py \
　　　　└ status.py \
    ├ S3 \
        ├ lambda \
            ├ lambda_code.zip \
            └ layer.zip \
        └ yaml \
            └ CloudFormation.yaml \
    ├ CloudWatch \
        └ custom_config.json \
    └ instance \
        ├ backup_world.sh \
        ├ gen_env.sh \
        └ minecraft.service
## botの設定
S3にlayer.zip、discord-bot.zip、CloudFormation.yamlをcopy
### S3内の構成
fabric-mcserver \
　　├ lambda/ \
　　　　├ lambda_code.zip \
　　　　└ layer.zip \
　　└ yaml/ \
　　　　└ CloudFormation.yaml
### 注意点
- layer.zipの作成はPython3.13で実行した。
- それに伴いCloudFormation.yaml内のRuntimeも3.13を指定した。
- discord-bot.zipの圧縮はapp.pyがrootになくてはならないのでlambda_codeを圧縮するのではなく4つの.pyを一気に圧縮する。
- 圧縮の際winでは文字化けなどの影響があるみたいなのでlinux環境で圧縮した。

### コマンド
- start
    - type
        - small
        - medium
        - large
- status
- stop
    - backup
        - off
        - on
startはインスタンスを起動し、IPアドレスを返す。typeを指定するとインスタンスタイプを起動時に変更できる。コマンド時にtypeを選択しない場合はデフォルトにsmallが設定されている。 \
statusはインスタンスの現在の状態を返す。 \
stopはインスタンスを停止させる。backup onを選択するとbackupをS3に保存した後にインスタンスを停止させる。コマンド時にtypeを選択しない場合はデフォルトにoffが設定されている。

## インスタンス起動で自動でserverも起動する設定
### 構成
1. .serviceを配置
    - /etc/systemd/system/minecraft.serviceを作成
    - /home/ec2-user/gen_env.shを作成
    - chmod +x /home/ec2-user/gen_env.sh
2. 自動起動を有効に
    - $ sudo systemctl daemon-reload
    - $ sudo systemctl start minecraft.service
### 説明
minecraft.serviceによってインスタンスが起動された時、自動的にminecraft serverが起動される。
インスタンスタイプによってメモリの使用量を変更するために、gen_env.shによってインスタンスの全メモリを取得し、.envに使用率をMax9割、min7割の数値を入力し、それによってserverが起動するようになっている。
## CloudWatchの設定
custom_config.jsonを \
/opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-agent.json \
に置く。

## 参考
https://blog.usize-tech.com/discord-manage-ec2/#toc3 \
https://qiita.com/unichiku/items/616edc2f41801d8594a3