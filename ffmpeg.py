# An accurate mpeg frame-level reader that wraps ffmpeg
# Author: Sameh Khamis (sameh@umiacs.umd.edu)
# License: BSDv2 for non-commercial research purposes only

from __future__ import division
import numpy as np
import subprocess
import json

class FFmpeg:
    def __init__(self, filename):
        self.filename = filename
        self.proc = None
        self.__set_video_info()
    
    def get_video_info(self):
        return (self.h, self.w, self.fps)
    
    def __set_video_info(self):
        cmd = 'ffmpeg/ffprobe -v quiet -print_format json -show_streams ..\%s.avi' % self.filename
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        info = json.loads(proc.stdout.read())
        self.h = info['streams'][0]['height']
        self.w = info['streams'][0]['width']
        fps = info['streams'][0]['r_frame_rate'].split('/')
        self.fps = int(fps[0]) / int(fps[1])
        self.nframes = int(info['streams'][0]['nb_frames'])
    
    def get_frame_by_number(self, f):
        cmd = 'ffmpeg/ffmpeg -i ../%s.avi -v quiet -f rawvideo -pix_fmt rgb24 -ss %f -vframes 1 -' % (self.filename, f / self.fps)
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        im = np.fromstring(proc.stdout.read(), dtype='uint8')
        im.shape = (self.h, self.w, 3)
        return im
    
    def get_first_frame(self):
        if self.proc:
            self.proc.kill()
        cmd = 'ffmpeg/ffmpeg -i ../%s.avi -v quiet -f rawvideo -pix_fmt rgb24 -' % self.filename
        self.proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        return self.get_next_frame()
    
    def get_next_frame(self):
        if self.proc:
            im = np.fromstring(self.proc.stdout.read(self.h * self.w * 3), dtype='uint8')
            if im.size == 0:
                self.proc = None
                return None
            return im.reshape(self.h, self.w, 3)
        else:
            return self.get_first_frame()
    
    def close(self):
        if self.proc:
            self.proc.kill()
            self.proc = None

