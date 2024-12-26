import flet as ft
from audio_processor import AudioProcessor


def main(page: ft.Page):
    """
    アプリケーションのメインエントリーポイント
    YouTube動画や音声ファイルから文字起こしを行うGUIアプリケーションを構築します。

    Args:
        page (ft.Page): Fletフレームワークのページオブジェクト
    """
    # ページの基本設定
    # ウィンドウサイズ、テーマ、背景色などの基本的なUIプロパティを設定
    page.title = "音声文字起こしアプリ"
    page.window.width = 1000
    page.window.height = 950
    page.window.center()  # ウィンドウを画面中央に配置
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.GREY_900

    # 音声処理用のクラスをインスタンス化
    audio_processor = AudioProcessor()

    # ----------------------
    # UI コンポーネントの定義
    # ----------------------

    # YouTubeのURL入力フィールド
    youtube_url = ft.TextField(
        label="YouTube URL",
        hint_text="https://www.youtube.com/watch?v=...",
        bgcolor=ft.Colors.GREY_800,
        border_color=ft.Colors.BLUE_200,
        text_size=16,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_200),
    )

    # 処理進行状況を表示するプログレスバー
    progress_bar = ft.ProgressBar(
        width=400,
        color=ft.Colors.BLUE_200,
        bgcolor=ft.Colors.GREY_700,
        visible=False,  # 初期状態では非表示
    )

    # 選択されたファイルのパスを表示するテキスト
    file_path_text = ft.Text(
        value="選択されたファイル: なし", size=14, color=ft.Colors.GREY_400
    )

    # 処理状況を表示するステータステキスト
    status_text = ft.Text(
        value="URLを入力するか、ファイルを選択してください",
        size=16,
        color=ft.Colors.BLUE_200,
        weight=ft.FontWeight.W_500,
    )

    # プリセットプロンプトの定義
    preset_prompts = {
        "標準": "日本語の音声ファイルの文字起こしをしてください。",
        "詳細": "日本語の音声ファイルを文字起こしし、話者の感情や口調も含めて詳細に書き起こしてください。",
        "要約": "日本語の音声ファイルを文字起こしし、内容を3行程度で要約してください。",
        "箇条書き": "日本語の音声ファイルを文字起こしし、主要なポイントを箇条書きでまとめてください。",
    }

    # プロンプト入力フィールド
    prompt_text = ft.TextField(
        value=preset_prompts["標準"],  # デフォルトの指示を設定
        label="プロンプト",
        multiline=True,
        min_lines=3,
        max_lines=5,
        helper_text="文字起こしの指示を入力してください",
        bgcolor=ft.Colors.GREY_800,
        border_color=ft.Colors.BLUE_200,
        text_size=16,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_200),
    )

    # 文字起こし結果を表示するテキストフィールド
    result_text = ft.TextField(
        multiline=True,
        min_lines=12,
        max_lines=12,
        read_only=True,  # 編集不可
        label="文字起こし結果",
        value=" ",
        bgcolor=ft.Colors.GREY_800,
        border_color=ft.Colors.BLUE_200,
        text_size=16,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_200),
    )

    # ----------------------
    # コールバック関数の定義
    # ----------------------

    def process_youtube(_):
        """
        YouTubeの動画を処理するコールバック関数

        1. URLのバリデーション
        2. 動画のダウンロードと音声抽出
        3. Gemini 2.0 Flashによる文字起こし
        4. 結果の表示

        Args:
            _ : ボタンクリックイベント（未使用）
        """
        # URLが入力されているか確認
        if not youtube_url.value:
            status_text.value = "URLを入力してください"
            page.update()
            return

        # UI要素の状態を更新
        progress_bar.visible = True
        status_text.value = "動画をダウンロード中..."
        page.update()

        # ./cacheフォルダに音声ファイルを保存
        cache_dir = "./cache/"
        audio_path, error = audio_processor.download_youtube_audio(
            youtube_url.value, cache_dir
        )

        if error:
            status_text.value = f"ダウンロードエラー: {error}"
            progress_bar.visible = False
            page.update()
            return

        # 文字起こしの実行
        status_text.value = "文字起こしを実行中..."
        page.update()

        result, error = audio_processor.transcribe_audio(audio_path, prompt_text.value)
        if error:
            status_text.value = f"処理エラー: {error}"
        else:
            result_text.value = result
            status_text.value = "文字起こしが完了しました"

        # 処理完了後のUI更新
        progress_bar.visible = False
        page.update()

    def pick_files_result(e: ft.FilePickerResultEvent):
        """
        ファイル選択後の処理を行うコールバック関数

        Args:
            e (ft.FilePickerResultEvent): ファイル選択イベント
        """
        if e.files:
            selected_file = e.files[0]
            # 選択されたファイル名を表示
            file_path_text.value = f"選択されたファイル: {selected_file.name}"
            status_text.value = "文字起こしを開始します..."
            progress_bar.visible = True
            page.update()

            # 文字起こしを実行
            result, error = audio_processor.transcribe_audio(
                selected_file.path, prompt_text.value
            )
            if error:
                status_text.value = f"エラーが発生しました: {error}"
                result_text.value = ""
            else:
                result_text.value = result
                status_text.value = "文字起こしが完了しました"

            # 処理完了後のUI更新
            progress_bar.visible = False
            page.update()

    # ----------------------
    # ボタンコンポーネントの設定
    # ----------------------

    # YouTube処理用ボタン
    youtube_button = ft.ElevatedButton(
        "YouTubeから文字起こし",
        icon=ft.Icons.ONDEMAND_VIDEO,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_700, padding=20
        ),
        on_click=process_youtube,
    )

    # ファイル選択用ピッカー
    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)

    # ファイル選択ボタン
    select_button = ft.ElevatedButton(
        "音声ファイルを選択",
        icon=ft.Icons.UPLOAD_FILE,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700, padding=20
        ),
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=[
                "mp3",
                "wav",
                "m4a",
                "aac",
                "ogg",
                "flac",
                "opus",
            ]  # 許可する音声ファイルの拡張子
        ),
    )

    def apply_preset(e):
        """
        プリセットプロンプトを適用するコールバック関数

        Args:
            e: ボタンクリックイベント
        """
        prompt_text.value = preset_prompts[e.control.text]
        page.update()

    # ----------------------
    # セクションのレイアウト定義
    # ----------------------

    input_section = ft.Row(
        controls=[
            # YouTubeセクション: URL入力とダウンロードボタン
            ft.Container(
                content=ft.Column(
                    [
                        youtube_url,
                        youtube_button,
                    ]
                ),
                padding=20,
                bgcolor=ft.Colors.GREY_800,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.Colors.BLACK54,
                ),
                margin=ft.margin.only(right=20),
                expand=3,  # 横幅の割合
            ),
            # ファイル選択セクション: ファイル選択ボタン
            ft.Container(
                content=ft.Column(
                    [
                        select_button,
                        file_path_text,
                    ]
                ),
                padding=20,
                bgcolor=ft.Colors.GREY_800,
                border_radius=10,
                expand=1,  # 横幅の割合
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # プリセットプロンプトのボタングループ
    preset_buttons = ft.Row(
        controls=[
            ft.ElevatedButton(
                text=name,
                on_click=apply_preset,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_700),
            )
            for name in preset_prompts.keys()
        ],
        wrap=True,
        spacing=10,
    )

    # プロンプト入力セクション: プリセットボタンとプロンプト入力フィールド
    prompt_section = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "プロンプトプリセット",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.BLUE_200,
                ),
                preset_buttons,
                ft.Container(height=10),
                prompt_text,
            ]
        ),
        padding=20,
        margin=ft.margin.only(bottom=20),
        bgcolor=ft.Colors.GREY_800,
        border_radius=10,
    )

    # ステータステキストとプログレスバーのセクション
    status_section = ft.Container(
        content=ft.Column([status_text, progress_bar]),
        padding=ft.padding.symmetric(vertical=10),
        alignment=ft.alignment.center,
    )

    # 結果表示セクション
    result_section = ft.Container(
        content=result_text, padding=20, bgcolor=ft.Colors.GREY_800, border_radius=10
    )

    # メインレイアウトの構築と表示
    # 各セクションを縦に配置
    page.add(ft.Column([input_section, status_section, prompt_section, result_section]))


if __name__ == "__main__":
    ft.app(target=main)
