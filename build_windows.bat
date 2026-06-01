@echo off
chcp 65001 > nul
echo ============================================================
echo  モーリス 福祉情報トラッカー — Windows ビルドスクリプト
echo ============================================================
echo.

:: Step 1: 必要ライブラリをインストール
echo [1/4] ライブラリをインストールしています...
pip install pyinstaller flask requests beautifulsoup4 pillow
echo.

:: Step 2: アイコン生成
echo [2/4] アイコンを生成しています...
python create_icon.py
echo.

:: Step 3: PyInstaller でexeをビルド
echo [3/4] アプリをexeに変換しています（数分かかります）...
pyinstaller mhlw_tracker.spec --clean --noconfirm
echo.

:: Step 4: 完了メッセージ
echo [4/4] ビルド完了！
echo.
echo ============================================================
echo  出力先: dist\MorrisWelfareTracker\MorrisWelfareTracker.exe
echo.
echo  次のステップ:
echo  Inno Setup をインストールして installer\setup.iss を実行すると
echo  配布用インストーラー（Setup.exe）が作成されます。
echo  https://jrsoftware.org/isdl.php
echo ============================================================
echo.
pause
