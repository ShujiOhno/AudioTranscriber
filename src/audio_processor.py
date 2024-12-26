from google import genai
from google.genai import types
from dotenv import load_dotenv
import os, re, subprocess
from typing import Tuple, Optional


class AudioProcessor:
    def __init__(self):
        """
        音声処理クラスの初期化
        """
        load_dotenv()
        self.model_name = "gemini-2.0-flash-exp"
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        # 念のためコンテンツフィルタを無効化
        self.generate_config = types.GenerateContentConfig(
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"
                ),
            ]
        )

    def download_youtube_audio(
        self, url: str, output_dir: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        YouTubeの動画から音声を抽出する
        Args:
            url: YouTube URL
            output_dir: 出力先ディレクトリパス
        Returns:
            Tuple[Optional[str], Optional[str]]: (音声ファイルパス, エラーメッセージ)
        """
        try:
            # /shorts/ を /watch?v= に置換
            url = url.replace("/shorts/", "/watch?v=")

            # video_idを取得
            video_id = re.search(r"v=([^&]+)", url).group(1)

            # フォルダが存在しない場合は作成
            os.makedirs(output_dir, exist_ok=True)

            # ファイルがすでに存在する場合はそれを返す
            audio_path = self.get_audio_path(output_dir, video_id)
            if audio_path:
                return audio_path, None

            # 存在しない場合はyt-dlpを使って音声をダウンロード
            # 出力ファイル名のテンプレート
            output_template = os.path.join(output_dir, "%(title)s_%(id)s.%(ext)s")

            command = [
                "bin/yt-dlp.exe",  # yt-dlpの実行ファイル
                "-x",  # 音声の抽出
                "-o",
                output_template,  # 出力先の指定
                url,  # YouTube URL
            ]

            process = subprocess.run(command, capture_output=True, text=True)

            if process.returncode != 0:
                return None, f"yt-dlpエラー: {process.stderr}"

            # ダウンロードしたファイルのパスを取得
            audio_path = self.get_audio_path(output_dir, video_id)
            if not audio_path:
                return None, "音声ファイルが見つかりませんでした"
            return audio_path, None

        except Exception as ex:
            return None, str(ex)

    def get_audio_path(self, output_dir: str, video_id: str) -> Optional[str]:
        """
        音声ファイルのパスを取得する
        Args:
            output_dir: 出力先ディレクトリパス
            video_id: YouTube動画のID
        Returns:
            Optional[str]: 音声ファイルのパス
        """
        audio_files = [f for f in os.listdir(output_dir) if video_id in f]
        if not audio_files:
            return None
        return os.path.join(output_dir, audio_files[0])

    def transcribe_audio(
        self, audio_path: str, prompt: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        音声ファイルを文字起こしする
        Args:
            audio_path: 音声ファイルのパス
            prompt: 文字起こしの指示プロンプト
        Returns:
            Tuple[Optional[str], Optional[str]]: (文字起こし結果, エラーメッセージ)
        """
        try:
            audio = self.client.files.upload(path=audio_path)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_uri(audio.uri, audio.mime_type),
                    types.Part.from_text(prompt),
                ],
                config=self.generate_config,
            )

            return response.text, None
        except Exception as ex:
            return None, str(ex)
