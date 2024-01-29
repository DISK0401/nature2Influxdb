# nature2Influxdb
telegrafを用いて、Nature Remo Eで取得した電力情報をInfluxDBへ転送する。
仕組みは単純で、curlでNature APIをコールし、jqで電力情報系のみを出力するシェル(remo.sh)を用意。
上記シェルファイル(remo.sh)をtelegrafで定期実行・influxDBへの送信(remo.conf)を行っている。


# 構築方法(概要)

概要のため、一部間違っている可能性もありますのでご注意ください。

1. jqのインストール(curlはインストールされている前提)

```sh:CentOS
sudo yum -y install jq
```

```sh:Ubuntu
sudo apt -y install jq
```

2. 各ファイルの設定を変更後、該当のディレクトリにコピー

3. telegrafサービスをリロードする


# 注意点

NatureのAPIが不安定のため、まれに取得に失敗するケースがあり、飛びデータになることがある。