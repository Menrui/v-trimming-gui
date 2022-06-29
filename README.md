# v-trimming-gui
A GUI application for cropping images from videos.  
動画をシークバーで操作しながらスクリーンショットを撮るためのアプリ。

# Screenshot
### Startup Window
![image](https://user-images.githubusercontent.com/50891743/151005614-809746b5-bb9f-4bf6-a858-78bd60d1c5b7.png)
### Select the directory
![image](https://user-images.githubusercontent.com/50891743/151006562-feb1f06b-2333-4980-b751-518f0f69a9b0.png)
### Main UI
* Movie Window : Video Preview
* Video Operation Window : Video Operation UI
* Directry Viewer Window : Select Video File UI (Sub-directories can also be loaded.)
![image](https://user-images.githubusercontent.com/50891743/151013258-b5bff0bb-3c1e-4e67-b5b2-eaef9abf08ad.png)

# Requirement
* Python >=3.7
* opencv-python ^4.5.5
* PySimpleGUI ^4.56.0

Environments under [Poetry >= 1.0.0](https://python-poetry.org/)
```bash
pip install poetry  # if you are not using poetry
poetry config virtualenvs.in-project true

poetry install  # if you want to build by pyinstaller
poetry install --no-dev  # If you want to run from python
```

When using conda:
```bash
conda create -n {environmment name} pip
conda activate {environment name}
pip install poetry
poetry config virtualenvs.in-project true

poetry install  # if you want to build by pyinstaller
poetry install --no-dev  # If you want to run from python
```

# Usage
Run  
```bash
python main.py
```
起動時のディレクトリは動画が入っている場所を選ぶ。

| Shortcut Key | Feature |
| ------------- | ------------- |
| Ctrl-L  | Play & Pause  |
| Shift-R  | Screenshot  |
| →  | frame advance  |
| ←  | frame playback  |

| GUI Button | Feature |
| ------------- | ------------- |
| Play / Stop  | 再生・一時停止  |
| Reset  | 先頭に戻る  |
| <  | 1コマ戻る  |
| <<  | 30コマ戻る  |
| <<<  | 30コマ戻る  |
| >  | 1コマ進む  |
| >>  | 30コマ進む  |
| >>>  | 150コマ進む  |
| screenshot  | スクショを保存する。"動画ファイル名+__0000.png"。保存先が指定されていない場合は動画と同じディレクトリにファイル名でフォルダを作成する。  |
| Save Dir  | スクリーンショットの保存先の設定。pathを打ち込めばそこにディレクトリを作成する(作成できる深さは1階層まで)。  |
| Clear  | 何も起こらない  |
| Quit  | 何も起こらない  |
| File Tree Window  | 選択した動画を読み込む。画面が変わらない場合はPlay/Stop連打で切り替わる。はず。  |


# Note
Bug Fixing
