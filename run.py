import os, subprocess

if __name__ == "__main__":
    try:
        # 仮想環境のPythonインタープリタのパス
        venv_python = r'.\venv\Scripts\python.exe'
        
        # main.pyのパス
        main_script = r'src\main.py'
        
        # コマンドを組み立てる
        cmd = [venv_python, main_script]
        
        # サブプロセスとして実行
        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        os.system("pause")