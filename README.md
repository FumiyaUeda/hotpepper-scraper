# HotPepper Scraper

## 日本語

### 概要
HotPepper の東京エリア飲食店ページから以下の情報をスクレイピングする Python スクリプトと、取得した 50 件分のサンプル CSV データを含むリポジトリです。  
- 店舗名  
- エリア  
- ディナー予算  
- ランチ予算  
- URL  

### 前提条件
- Python 3.7 以上  
- ChromeDriver（`chromedriver.exe`）をスクリプトと同じフォルダに配置  
- 必要なライブラリ  
  ```bash
  pip install selenium
