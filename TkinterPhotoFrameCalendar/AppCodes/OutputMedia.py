#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageTk, ImageOps
import os
import pyaudio
import shutil
import threading
import wave

from AppCodes.BaseLibrary import *


class SoundSpeaker:
    ''' 音声出力クラス
    '''
    def __init__(self, sound_file):
        '''コンストラクタ
        '''
        self.__sound = "./sounds/" + sound_file
        self.__is_running = False
        self.__speaker_thread = None

    def __del__(self):
        '''デストラクタ
        '''
        self.stop_thread()

    def go_off(self):
        '''アラーム停止後、直ちにスレッド再開
        '''
        self.stop_thread()
        self.start_thread()

    def start_thread(self):
        '''スレッド開始
        '''
        self.__is_running = True
        if self.__speaker_thread is None:
            self.__speaker_thread = threading.Thread(target=self.__sound_speaker)
            self.__speaker_thread.start()

    def stop_thread(self):
        '''スレッド停止
        '''
        self.__is_running = False
        if self.__speaker_thread is not None:
            self.__speaker_thread.join()
            self.__speaker_thread = None

    def __sound_speaker(self):
        '''サウンド再生
        '''
        while self.__is_running:
            wf = wave.open(self.__sound, 'r')
            audio = pyaudio.PyAudio()
            stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True)
            data = wf.readframes(1024)
            while data != b'' and self.__is_running:
                stream.write(data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
            audio.terminate()
            wf.close()

            
class ImageView(BaseCanvas):
    ''' 画像表示クラス
    '''
    def __init__(self, master, height:int, width:int):
        '''コンストラクタ
        Param: マスター、表示用キャンバス長
        '''
        super().__init__(master=master, height=height, width=width)     # 表示用キャンバス設定
        self._inside_folder = ""
        self._show_image = None
        
    def _set_folder_path(self, folder_name:str):
        '''表示画像を格納するフォルダのパスを設定
        Param: 画像格納フォルダ名
        '''
        self._inside_folder = "./images/" + folder_name
        
    def _set_image_plot_to_all_canvas(self, image_name:str):
        '''画像をキャンバス全体へプロット
        Param: 画像ファイル名
        '''
        open_img = Image.open(self._inside_folder + "/" + image_name)
        # 画像の縦横比を崩さずにcanvasのサイズ全体に画像をリサイズ（余白を追加）
        open_img = ImageOps.pad(open_img, (self._width, self._height), color=self._bg_color)
        self._show_image = ImageTk.PhotoImage(open_img, master=self)


class ImageSynchronize:
    ''' フォルダ間画像同期クラス
    '''
    def __init__(self, inside_folder:str):
        '''コンストラクタ
        Param: 内部側フォルダ
        '''
        self._inside_folder = inside_folder
    
    def synchronize(self, outside_folders:list):
        '''外部側フォルダと内部側フォルダの画像を同期
        Param: 外部側フォルダリスト
        ※外部Web APIを使用しない場合
        '''
        # 外部側フォルダの画像を取得
        outside_list = []
        for outside_folder in outside_folders:
            for dirpath, dirnames, images in os.walk(outside_folder):
                for image in images:
                    name = os.path.basename(image)
                    outside_list.append(self.ImageName(outside_folder, name))
        # 内部側フォルダの画像を取得
        inside_list = []
        for dirpath, dirnames, images in os.walk(self._inside_folder):
            for image in images:
                name = os.path.basename(image)
                inside_list.append(self.ImageName(self._inside_folder, name))
        # 両者を比較
        for inside_img in inside_list:
            for outside_img in outside_list:
                if (inside_img.name == outside_img.name):
                    inside_img.flag = True
                    outside_img.flag = True
        # 外部側フォルダにない画像を削除
        for inside_img in inside_list:
            if inside_img.flag == False:
                os.remove(self._inside_folder + "/" + inside_img.name)
        # 内部側フォルダにない画像をコピー
        for outside_img in outside_list:
            if outside_img.flag == False:
                copy_image = os.path.basename(self.move_image(outside_img.folder + "/" + outside_img.name))
                
    def move_image(self, src_path:str) -> str:
        '''表示画像を内部側フォルダへコピー
        Param:  コピー元画像ファイルパス
        Return: コピー先画像ファイルパス
        '''
        return shutil.copy(src_path, self._inside_folder)

    def images_remove(self):
        '''内部側フォルダの画像を全て破棄
        '''
        shutil.rmtree(self._inside_folder) # フォルダごと画像を削除
        os.mkdir(self._inside_folder)      # フォルダを作り直す

    class ImageName:
        def __init__(self, folder:str, name:str):
            self.flag = False
            self.folder = folder
            self.name = name
