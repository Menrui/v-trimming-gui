import numpy as np
import os
import PySimpleGUI as sg
import cv2
from pathlib import Path
import re

from video_operator import VideoOperator

folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

video_re ='.+\.(mp4|MP4|avi|AVI|flv|FLV|wmv|WMV|mov|MOV)'


# ツリーデータ作成用関数
def get_tree_data(parent, dirname):
    treedata = sg.TreeData()

    # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Tree_Element.py#L26
    def add_files_in_folder(parent, dirname):

        files = os.listdir(dirname)
        for f in files:
            fullname = os.path.join(dirname, f)
            if os.path.isdir(fullname):
                treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
                add_files_in_folder(fullname, fullname)
            else:
                if re.search(video_re, f):
                    treedata.Insert(parent, fullname, f, values=[
                                    os.stat(fullname).st_size], icon=file_icon)

    add_files_in_folder(parent, dirname)

    return treedata

class Main:
    def __init__(self):
        # self.d_path = directory_read()
        self.d_path = Path(sg.popup_get_folder('Folder to display'))
        print(self.d_path)
        self.f_list = [p for p in self.d_path.glob('**/*') if re.search(video_re, str(p.name))]
        self.f_path = self.f_list[0]
        self.operator = VideoOperator(self.f_path)
        self.load_check()


    def load_check(self):
        # 取得可能かの確認
        if self.operator.video_property.is_load:

            self.operator.set_video_pos(0)
            # 動画情報の取得
            self.fps = self.operator.video_property.fps
            self.width = self.operator.video_property.width
            self.height = self.operator.video_property.height
            self.total_count = self.operator.video_property.frame_count

            # フレーム関係
            self.frame_count = 0
            self.s_frame = 0
            self.e_frame = self.total_count

            cv2.namedWindow("Movie")

        else:
            sg.Popup("ファイルの読込に失敗しました。")
            return

    
    def run(self):
        # GUI #######################################################
        # GUIのレイアウト
        
        layout = [
            [sg.Slider(
                (0, self.total_count - 1),
                0,
                1,
                orientation='h',
                size=(50, 15),
                key='-PROGRESS SLIDER-',
                enable_events=True
            )],
            [
                sg.Button('<<<', size=(5, 1)),
                sg.Button('<<', size=(5, 1)),
                sg.Button('<', size=(5, 1)),
                sg.Button('Play / Stop', size=(9, 1)),
                sg.Button('Reset', size=(7, 1)),
                sg.Button('>', size=(5, 1)),
                sg.Button('>>', size=(5, 1)),
                sg.Button('>>>', size=(5, 1))
            ],
            [
                sg.Text("Speed", size=(6, 1)),
                sg.Slider(
                    (0, 240),
                    10,
                    10,
                    orientation='h',
                    size=(19.4, 15),
                    key='-SPEED SLIDER-',
                    enable_events=True
                ),
                sg.Text("Skip", size=(6, 1)),
                sg.Slider(
                    (0, 300),
                    0,
                    1,
                    orientation='h',
                    size=(19.4, 15),
                    key='-SKIP SLIDER-',
                    enable_events=True
                ),
                sg.Button('screenshot', size=(5, 1))
            ],
            [sg.HorizontalSeparator()],
            [sg.Output(size=(65, 5), key='-OUTPUT-')],
            [sg.Button('Clear'), sg.Button("Quit"), sg.Button("Save Dir"), sg.InputText("", key="s_path")]
        ]

        # Windowを生成
        window = sg.Window('OpenCV Integration', layout, 
                            location=(0, 0), 
                            return_keyboard_events=True, 
                            use_default_focus=False)
        # 動画情報の表示
        self.event, values = window.read(timeout=0)
        print("ファイルが読み込まれました。")
        print("File Path: " + str(self.f_path))
        print("fps: " + str(int(self.fps)))
        print("width: " + str(self.width))
        print("height: " + str(self.height))
        print("frame count: " + str(int(self.total_count)))


        treedata = get_tree_data("", str(self.d_path))
        menu_def = [["File", ["Open Folder"]]]
        layout2 = [[sg.Menu(menu_def)],
            [sg.Text('File and folder browser')],
            [sg.Tree(data=treedata,
                headings=['Size', ],
                auto_size_columns=True,
                num_rows=24,
                col0_width=40,
                key="-TREE-",
                show_expanded=True,
                enable_events=True)]]
        tree_window = sg.Window("Directory Viewer", layout2, 
                                element_justification="center", 
                                font="Monospace 10", 
                                resizable=True, 
                                return_keyboard_events=True, 
                                use_default_focus=False)



# メインループ #########################################################
        try:
            while True:
                self.event, values = window.read(timeout=values["-SPEED SLIDER-"])

                tree_event, tree_values = tree_window.read(timeout=values["-SPEED SLIDER-"])
                if tree_event == "Open Folder":
                    # 表示するフォルダを変更する
                    starting_path = sg.popup_get_folder("Folder to display")
                    treedata = get_tree_data("", starting_path)
                    tree_window["-TREE-"].update(values=treedata)
                
                if tree_event == "-TREE-":
                    try:
                        for fname in tree_values["-TREE-"]:
                            print(fname)
                            if not os.path.isdir(fname):
                                self.operator.load(Path(fname))
                                self.operator.set_video_pos(0)
                                self.f_path = Path(fname)
                                self.load_check()
                                print(self.operator.play_status)
                                
                                # print("ファイルが読み込まれました。")
                                # self.event, values = tree_window.read(timeout=0)
                                print("File Path: " + str(self.f_path))
                                print("fps: " + str(int(self.fps)))
                                print("width: " + str(self.width))
                                print("height: " + str(self.height))
                                print("frame count: " + str(int(self.total_count)))
                                self.frame = self.operator.get_frame()
                                self.display_process()
                                window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())
                    except Exception as e:
                        sg.Print(e)
                    continue

                if self.event == 'screenshot' or self.event == 'Return:36' or self.event == 'Shift_R:62':
                    self.operator.screenshot()

                if self.event == "Clear":
                    pass
                    
                if self.event == "Quit":
                    pass
                
                if self.event == "Save Dir":
                    # print(window['s_path'].get())
                    if window['s_path'].get() == '':
                        path = Path(sg.popup_get_folder('Save Folder'))
                    else:
                        path = Path(window['s_path'].get())
                        if not path.parent.exists():
                            path = Path(sg.popup_get_folder('Save Folder'))
                    self.operator.set_save_path(path)
                    window['s_path'].update(str(path))

                if self.event != "__TIMEOUT__":
                    print(self.event)
                # Exitボタンが押されたら、またはウィンドウの閉じるボタンが押されたら終了
                if self.event in ('Exit', sg.WIN_CLOSED, None):
                    break

                # 動画の再読み込み
                # スタートフレームを設定していると動く
                if self.event == 'Reset':
                    self.operator.stop()
                    self.frame_count = self.s_frame
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

                    # Progress sliderへの変更を反映させるためにcontinue
                    continue

                # フレーム操作 ################################################
                # スライダを直接変更した場合は優先する
                if self.event == '-PROGRESS SLIDER-':
                    # フレームカウントをプログレスバーに合わせる
                    self.frame_count = int(values['-PROGRESS SLIDER-'])
                    self.operator.set_video_pos(self.frame_count)
                    if values['-PROGRESS SLIDER-'] > values['-END FRAME SLIDER-']:
                        window['-END FRAME SLIDER-'].update(
                            values['-PROGRESS SLIDER-'])

                if self.event == '<<<':
                    self.frame_count = np.maximum(0, self.frame_count - 150)
                    self.operator.step_backward(-150)
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

                if self.event == '<<':
                    self.frame_count = np.maximum(0, self.frame_count - 30)
                    self.operator.step_backward(-30)
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

                if self.event == '<' or self.event == 'Left:100':
                    self.frame_count = np.maximum(0, self.frame_count - 1)
                    self.operator.step_backward(-1)
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

                if self.event == '>' or self.event == 'Right:102':
                    self.frame_count = self.frame_count + 1
                    self.operator.step_forward(1)
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())
                    # cv2.imwrite('./sample_.png', self.frame)

                if self.event == '>>':
                    self.frame_count = self.frame_count + 30
                    self.operator.step_forward(30)
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

                if self.event == '>>>':
                    self.frame_count = self.frame_count + 150
                    self.operator.step_forward(150)
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

                # カウンタがエンドフレーム以上になった場合、スタートフレームから再開
                if self.operator.get_cur_f() >= self.total_count:
                    self.operator.set_video_pos(0)
                    self.operator.stop()
                    self.frame_count = 0
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())
                    continue

                # ストップボタンで動画の読込を一時停止
                if self.event == 'Play / Stop' or self.event == 'space:65' or self.event == 'Control_L:37':
                    self.operator.play_status.is_pause = not self.operator.play_status.is_pause
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

                # ストップフラグが立っており、eventが発生した場合以外はcountinueで
                # 操作を停止しておく

                # ストップボタンが押された場合は動画の処理を止めるが、何らかの
                # eventが発生した場合は画像の更新のみ行う
                # mouse操作を行っている場合も同様
                if self.operator.play_status.is_pause and self.event == "__TIMEOUT__":
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

                # スキップフレーム分とばす
                if not self.operator.play_status.is_pause and values['-SKIP SLIDER-'] != 0:
                    self.frame_count += values["-SKIP SLIDER-"]
                    self.operator.set_video_pos(self.frame_count)

                # フレームの読込 ##############################################
                self.frame = self.operator.get_frame()
                if self.frame is None:
                    continue


                # # 画像を表示
                self.display_process()

                if self.operator.play_status.is_pause:
                    pass
                    # self.operator.set_video_pos(self.frame_count)

                else:
                    # self.frame_count += 1
                    window['-PROGRESS SLIDER-'].update(self.operator.get_cur_f())

        finally:
            cv2.destroyWindow("Movie")
            window.close()
            tree_window.close()
    
    def display_process(self):
        # 以降にフレームに対する処理を記述 ##################################
        # frame全体に対する処理をはじめに実施 ##############################
        # フレーム数と経過秒数の表示
        self.v_frame = self.frame
        cv2.putText(
            self.v_frame, str("framecount: {0:.0f}".format(self.frame_count)), (
                15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 230, 0), 1, cv2.LINE_AA
        )
        cv2.putText(
            self.v_frame, str("time: {0:.1f} sec".format(
                self.frame_count / self.fps)), (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 230, 0), 1, cv2.LINE_AA
        )

        # 画像を表示
        cv2.imshow("Movie", cv2.resize(self.v_frame, (1280, int(1280*(self.height/self.width)))))
        cv2.waitKey(1)



if __name__ == '__main__':
    Main().run()