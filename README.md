# z_fighter_server


[z_fighter](https://github.com/iisyos/z_fighter) のためのバックエンドです。
主に画像urlを受け取り、機械学習の結果を返します。


## 使用パッケージ
<img align="right" src="https://docs-assets.developer.apple.com/turicreate/turi-dog.svg" alt="Turi Create" width="100">

### [Turi Create](https://apple.github.io/turicreate/docs/userguide/)
[Image Classification](https://apple.github.io/turicreate/docs/userguide/image_classifier/) を使用し、画像類似度判定のモデルを作成

<img align="right" src="https://rightcode.co.jp/wp-content/uploads/2019/11/FastAPI.png" alt="FastAPI" width="100">

### [FastAPI](https://fastapi.tiangolo.com/ja/)
PythonでAPIサーバーをたてるために使用

<img align="right" src="https://user-images.githubusercontent.com/67086449/196201756-ef81a353-0cc3-4733-a7f4-00b1681c89d1.png" alt="FastAPI" width="100">

### [Serverless Framework](https://www.serverless.com/)
- ECRにimageをpush
- lambdaにデプロイ
- APIGatewayに紐付け
等をCIするために使用

## 使用法

1. コンテナのビルド
```zsh
$ docker-comopose up -d --build
```

2.学習データの収集

```zsh
$ docker-comopose exec lambda_api /bin/zsh
$ python src/script/zFIghtersImageCollector.py
```

3.学習モデルの作成

```zsh
$ python src/script/createModel.py
```

4.localでAPI起動
```zsh
$ python src/app.py
```

5.テスト

```zsh
$ curl -X 'POST' \
  'http://localhost:8081/v1/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "url"
}'
```

