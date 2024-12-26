import asyncio
import os
import urllib.request
import zipfile
import io

# Python実行ファイルのバージョンと場所を指定
PYTHON_VERSION = "312"
PYTHON_PATH = (
    rf"%USERPROFILE%\AppData\Local\Programs\Python\Python{PYTHON_VERSION}\python.exe"
)

# ダウンロードするファイルのURL
YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"


async def create_subprocess(cmd):
    # サブプロセスを作成し、標準出力と標準エラー出力をパイプで接続
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # 出力を逐次的に読み取って表示
    while True:
        # cp65001(UTF-8)でデコードし、右側の空白を削除
        stdout = (await proc.stdout.readline()).decode("cp65001", "ignore").rstrip()
        if len(stdout):
            # 出力がある場合は表示（flush=Trueでバッファリングせずに即時出力）
            print(stdout, end="\n", flush=True)
        else:
            break


def download_and_setup_binaries():
    # binディレクトリが存在しない場合は作成
    os.makedirs("./bin", exist_ok=True)

    # yt-dlp.exeをダウンロード
    print("Downloading yt-dlp.exe...")
    urllib.request.urlretrieve(YTDLP_URL, "./bin/yt-dlp.exe")

    # FFmpegをダウンロードして解凍
    print("Downloading and extracting FFmpeg...")
    response = urllib.request.urlopen(FFMPEG_URL)
    with zipfile.ZipFile(io.BytesIO(response.read())) as zip_ref:
        # ffmpeg.exeとffprobe.exeのみを抽出
        for file in zip_ref.namelist():
            if file.endswith(("ffmpeg.exe", "ffprobe.exe")):
                # ファイルを./bin/に展開
                with zip_ref.open(file) as source, open(
                    f"./bin/{os.path.basename(file)}", "wb"
                ) as target:
                    target.write(source.read())


async def main():
    # バイナリファイルのダウンロードとセットアップ
    download_and_setup_binaries()

    # 仮想環境を作成
    await create_subprocess(f"{PYTHON_PATH} -m venv venv")

    # 仮想環境をアクティベートし、pipをアップグレードして必要なパッケージをインストール
    await create_subprocess(
        r".\venv\Scripts\activate.bat && python -m pip install --upgrade pip && pip install -r requirements.txt"
    )

    # 実行終了後にコンソールを一時停止
    os.system("PAUSE")


try:
    # メイン処理を非同期で実行
    asyncio.run(main())
except Exception as e:
    # エラーが発生した場合は表示して一時停止
    print(e)
    os.system("PAUSE")
