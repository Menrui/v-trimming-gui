import logging
import os
from dataclasses import dataclass
from pathlib import Path

import cv2

FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
FPS = cv2.CAP_PROP_FPS
FRAME_COUNT = cv2.CAP_PROP_FRAME_COUNT
POS_FRAMES = cv2.CAP_PROP_POS_FRAMES
POS_MSEC = cv2.CAP_PROP_POS_MSEC


@dataclass
class VideoProperty:
    is_load: bool
    height: int
    width: int
    fps: int
    frame_count: int
    playtime: float


@dataclass
class VideoPos:
    frames: float
    progress: float


@dataclass
class PlayStatus:
    is_pause: bool = True
    is_stop: bool = False
    step_forward: bool = False
    step_backward: bool = False
    play_speed: int = 0
    position: VideoPos = VideoPos(frames=0, progress=0)


class VideoOperator(object):
    def __init__(self, video_path: Path) -> None:
        super().__init__()
        # self.logger = logging.getLogger('root')
        self.is_init = True

        self.save_path = None
        self.user_save_path = None
        self.save_count = 0
        self.video_path = video_path
        self.play_status = PlayStatus()
        
        _, _ = self.load(video_path)
        
        return
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        # if self.video_property.frame_count - 1 == self.video.get(POS_FRAMES):
        #     self.set_video_pos(self.video_property.frame_count - 1)
        if self.is_init:
            self.is_init = False
            self.play_status.is_stop = False
            return self.read_frame()

        if self.play_status.is_stop:
            self.set_video_pos(0)
            self.play_status.is_stop = False
            return self.read_frame()

        if self.play_status.step_forward:
            self.play_status.step_forward = False
            self.play_status.is_pause = True
            self.set_video_pos(max(self.video.get(POS_FRAMES) - 1, 0))
            return self.read_frame()
        
        if self.play_status.step_backward:
            self.play_status.step_backward = False
            self.play_status.is_pause = True
            self.set_video_pos(max(self.video.get(POS_FRAMES) - 1, 0))
            return self.read_frame()

        if self.play_status.is_pause:
            return
        
        if not self.play_status.play_speed != 0:
            sp = self.play_status.play_speed
            if sp > 0:
                self.set_video_pos(self.video.get(POS_FRAMES) + sp)
            else:
                sp = sp - 1
                self.set_video_pos(max(self.video.get(POS_FRAMES) - sp, 0))
            return self.read_frame()
        
        return self.read_frame()
    
    def read_frame(self):
        is_read, frame = self.video.read()
        if is_read:
            # _, jpg = cv2.imencode('.jpg', frame)
            # return jpg.tobytes()
            return frame
        else:
            return
    
    def load(self, video_path):
        print(f'load: {video_path}')
        video = cv2.VideoCapture(str(video_path))
        if not video.isOpened():
            # self.logger.warning('Failed to load the file.')
            print('Failed to load the file.')
            self.video_property = VideoProperty(is_load=False)
            return False, None
        else:
            # self.logger.info('Successed to load the file.')
            print('Successed to load the file.')
        
        self.video_property = VideoProperty(
            is_load=True,
            height=video.get(FRAME_HEIGHT),
            width=video.get(FRAME_WIDTH),
            fps=video.get(FPS),
            frame_count=video.get(FRAME_COUNT),
            playtime=(video.get(FRAME_COUNT) / video.get(FPS)) * 1000,
        )
        self.video = video
        self.video_path = video_path
        self.save_count = 0
        self.is_init = True
        self.play_status.is_stop = False
        self.set_save_path(self.user_save_path)
        return True, video
    
    def stop(self):
        self.play_status.is_stop = True
        self.play_status.is_pause = True
        self._speed_reset()
    
    def pause(self):
        self.play_status.is_pause = True
        self._speed_reset()
    
    def start(self):
        self.play_status.is_pause = False
        self.play_status.is_stop = False
        self._speed_reset()

    def step_forward(self, steps=1):
        self.play_status.step_forward = True
        self._speed_reset()
        self.set_video_pos(self.get_current_pos().frames + steps)
    
    def step_backward(self, steps=-1):
        self.play_status.step_backward = True
        self._speed_reset()
        self.set_video_pos(self.get_current_pos().frames + steps)
    
    def fast(self):
        self.play_status.play_speed = 1
    
    def rewind(self):
        self.play_status.play_speed = -1
    
    def _speed_reset(self):
        self.play_status.play_speed = 0
    
    def screenshot(self):
        if self.save_path is None:
            self.set_save_path()
        else:
            self._check_save_path()
        pos = self.get_current_pos()

        is_read, screenshot = self.video.read()
        if is_read:
            img_name = f'{str(self.video_path.stem)}__{self.save_count:04}.png'
            img_path = self.save_path.joinpath(img_name)
            cv2.imwrite(str(img_path), screenshot)
            is_success = True
        else:
            is_success = False

        self.set_video_pos(pos.frames)
        is_success=True
        return is_success
        
    def get_video_property(self):
        return self.video_property

    def get_current_pos(self):
        return VideoPos(frames=self.video.get(POS_FRAMES),
                        progress=self.video.get(POS_MSEC))
    
    def get_cur_f(self):
        return self.video.get(POS_FRAMES)
    
    def set_video_pos(self, frames: int):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, frames)
    
    def _check_save_path(self):
        if list(self.save_path.glob(f'*{self.video_path.stem}*.png')):
            last_img_num_str = sorted([img_path.split('__')[-1] for img_path in self.save_path.glob(f'*{self.video_path.stem}*.png')])[-1]
            # last_num = str(last_img.stem).split('__')[-1]
            self.save_count = int(last_img_num_str) + 1
        else:
            self.save_count = 0

    def set_save_path(self, save_path=None):
        self.user_save_path = save_path
        if self.save_path is None and save_path is None:
            self.save_path = self.video_path.parent.joinpath(self.video_path.stem)
            os.makedirs(self.save_path, exist_ok=True)
        elif self.save_path is not None and save_path is None:
            os.makedirs(self.save_path, exist_ok=True)
        else:
            self.save_path = save_path
            os.makedirs(self.save_path, exist_ok=True)


    # frame = video_operator.get_frame()
    # yield (b'--frame\r\n'
    #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
