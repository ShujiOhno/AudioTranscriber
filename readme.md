# 音声/動画文字起こしアプリケーション

## 概要
本アプリケーションは、Gemini 2.0 Flash APIを使用して、音声ファイルやYouTube動画の文字起こしを行うプログラムです。Windows環境での実行を想定しています。

## セットアップ手順

1. **Python環境の構築**
   - [Python 3.12.8](https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe)をインストール
   - インストール時に「Add Python 3.12 to PATH」にチェックを入れてください

2. **APIキーの設定**
   - [Google AI Studio](https://aistudio.google.com/apikey)からGemini APIキーを取得
   - `.env`ファイルを開き、`GEMINI_API_KEY=`の後ろに取得したAPIキーを貼り付けて保存

3. **環境構築**
   - `create_venv.py`をダブルクリックで実行
   - 以下が自動的に行われます：
     - 仮想環境の構築
     - 必要なパッケージのインストール
     - ffmpegなどの関連ツールのダウンロード、./binフォルダへの配置

4. **起動確認**
   - `run.py`をダブルクリックして実行
   - アプリケーションが正常に起動することを確認