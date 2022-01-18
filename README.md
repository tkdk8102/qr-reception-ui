# qr-reception-ui
結婚式当日の受付で、スマートフォンやタブレットのカメラでQRコードを読み取り、出席登録を行うためのWebUI

## 必要環境
- Docker Engine
    - https://docs.docker.com/engine/install/
- Docker Compose
    - https://docs.docker.com/compose/install/

## 使い方
1. `mysql.env` に任意のパスワードを設定    
    `MYSQL_ROOT_PASSWORD=$任意のパスワード$`
2. `web/cert` に証明書を設置    
    ※ 証明書/鍵ファイル名の指定は `web/default.conf` を編集    
    ※ HTTP で良い場合は `web/default.conf` の SSL 関連設定を消して `listen 443;` を `80;` に変更
3. 起動    
    `docker-compose up -d --build`
4. 管理ユーザの追加    
    `docker-compose exec qr-app python add_host_account.py -a $任意のアカウント名$ -p $任意のパスワード$`
5. アクセス確認(スマホ・タブレットで Chrome 推奨)    
    `https://$host$`

- 停止    
    `docker-compose down`
- 停止(DB初期化)    
    `docker-compose down -v`

### 構成画面
- メニュー画面：`/`
    - QRコード読み取り(フロントカメラ)：`/reader?camera=front`
        - スマホ・タブレットのフロントカメラで QRコードを読み取り対象者を出席登録する
    - QRコード読み取り(リアカメラ)：`/reader?camera=rear`
        - スマホ・タブレットのリアカメラで QRコードを読み取り対象者を出席登録する
    - 招待者一覧：`/guests`
        - 式への招待者の登録や編集、出欠状況や名前等の情報を一覧表示する管理画面
        - CSVによる一括登録にも対応 ※ 後述
    - QRコード全件ダウンロード：`/download`
        - 招待者一覧にて登録された招待者ごとに割当られた QR コードを全件ダウンロード
- ログイン画面：`/login`
- ログアウト：`/logout` ※ ログイン画面へリダイレクト

#### 一括登録用CSV
- Web招待状サービス https://weddingday.jp/ の出欠一覧CSVに準拠
- カラム構成    
    ```
    出欠,姓,名,姓（ふりがな）,名（ふりがな）
    ご出席,山田,太郎,やまだ,たろう
    欠席,山田,花子,やまだ,はなこ
    ご出席,佐藤,次郎,さとう,じろう
    ```
    ※ 出欠カラムが `ご出席` の行のみ取り込み    
    ※ カラムの並び順は不同で問題なく、その他のカラムがあっても無視

## 参考にしたサイト
- QRコードの生成と保存 | Python学習講座
    - https://www.python.ambitious-engineer.com/archives/3654
- Webの技術だけで作るQRコードリーダー - Qiita
    - https://qiita.com/kan_dai/items/4331aae12f5f2d3ad18d
- 効果音ラボ
    - https://soundeffect-lab.info/    
    ※ QRコード読み取り時の効果音に使用
