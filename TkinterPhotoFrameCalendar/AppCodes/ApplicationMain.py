#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from AppCodes.Configuration import APP_ROOT_FILE, SoundConfig
from AppCodes.ImportCommon import *
from AppCodes.OutputMedia import SoundSpeaker

## 各画面オブジェクト設計モジュール
from AppCodes.CalendarWindow import Window1
from AppCodes.DayDetailWindow import Window2

## 音声スケジューリング用ライブラリ
import schedule as sd

## 画面表示サイズ設定用ライブラリ
import pyautogui as pag


class ApplicationMain:
    ''' アプリケーションメインクラス
    '''
    def __init__(self, app_root:str):
        '''コンストラクタ
        Param:  アプリ実行フォルダ絶対パス
        '''
        self.__set_app_root(app_root)   # アプリ実行フォルダ絶対パスをテキストファイルへ記憶
        self._root = tk.Tk()
        self._root.title("TkinterPhotoFrameCalendar")       # ウィンドウタイトル
        scr_w, scr_h = pag.size()
        if ((scr_w==1920) and (scr_h==1080)):
            self._root.geometry('980x580+100+100')
        else:
            self._root.attributes("-fullscreen", True)      # GUI全画面表示（Raspberry Piのみ）
        # rootのメインウィンドウのグリッドを 1x1 にする
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)
        # 各画面オブジェクト生成
        # 0: カレンダー／デジタル時計／スライドショー画面
        # 1: アナログ時計／日付詳細画面
        self._windows = [Window1(self._root, self._get_current_datetime()),
                         Window2(self._root, self._get_current_datetime())]
        # 各種設定画面
        self._set_sounds()              # 音設定
        self._create_menu_bar()         # メニューバー生成
        self._is_app = True
        self._datetime_thread = None    # 現在日時更新スレッド
        self._start_datetime_thread()   # 現在日時更新スレッド開始
        self._select_window(0)          # メイン画面を一番上に表示
        self._root.mainloop()
        
    def __del__(self):
        '''デストラクタ
        '''
        self._stop_datetime_thread()    # 現在日時更新スレッド終了
        
    def __set_app_root(self, app_root:str):
        '''アプリ実行フォルダ絶対パスをテキストファイルへ記憶
        '''
        if os.path.isfile(APP_ROOT_FILE):
            os.remove(APP_ROOT_FILE)    # テキストファイルが存在する場合、削除
        else:
            with open(APP_ROOT_FILE, 'x') as f:
                f.write(app_root + "/")

    def _set_sounds(self):
        '''音設定
        '''
        sound_config = SoundConfig("StreamSound")
        self._stream_sound = SoundSpeaker(sound_config.file_name)   # 安眠用渓流音
        global stream_start, stream_end
        stream_start = sound_config.times[0]    # 渓流音開始時刻
        stream_end = sound_config.times[1]      # 渓流音終了時刻

    def _create_menu_bar(self):
        '''メニューバー生成
        '''
        self._menu_bar = tk.Menu(self._root)
        self._root.config(menu=self._menu_bar)
        window_menu = tk.Menu(self._menu_bar)
        close_menu = tk.Menu(self._menu_bar)
        self._menu_bar.add_cascade(label='Window', menu=window_menu)
        self._menu_bar.add_cascade(label='Close', menu=close_menu)
        window_menu.add_command(label='Calendar', command=lambda: self._select_window(0))   # カレンダー／デジタル時計／スライドショー画面表示
        window_menu.add_command(label='DayDetail', command=lambda: self._select_window(1))  # アナログ時計／日付詳細画面表示
        close_menu.add_command(label='Screen Close', command=self.__window_all_close)       # 画面を閉じる
        
    def _select_window(self, window_no:int):
        '''表示画面選択
            0: カレンダー／デジタル時計／スライドショー画面
            1: アナログ時計／日付詳細画面
        '''
        self._windows[window_no].tkraise()
        
    def __window_all_close(self):
        '''全ての画面を閉じる
        '''
        self._is_app = False
        self._root.destroy()
        self._stop_datetime_thread()    # 現在日時更新スレッド終了

    def _get_current_datetime(self) -> dt.datetime:
        '''現在日時取得
        '''
        return dt.datetime.now()

    def _start_datetime_thread(self):
        '''現在日時更新スレッド開始
        '''
        if self._datetime_thread is None:
            self._datetime_thread = threading.Thread(target=self._update_current_datetime, daemon=True)
            self._datetime_thread.start()

    def _stop_datetime_thread(self):
        '''現在日時更新スレッド終了
        '''
        if self._datetime_thread is not None:
            self._datetime_thread.join()
            self._datetime_thread = None

    def _update_current_datetime(self):
        '''現在日時更新
        '''
        self.__sound_scheduling()               # 音声出力スケジュール
        while self._is_app:
            now = self._get_current_datetime()  # 現在日時を取得
            sd.run_pending()
            # カレンダー／デジタル時計／アナログ時計更新
            self._windows[0].current_datetime_callback(now)
            self._windows[1].current_time_callback(now.time())
            # 日時選択確認
            if self._windows[0].send_date_select_flag():
                self._windows[1].select_date_callback(self._windows[0].send_selected_date())
                self._windows[0].date_select_flag_down()
                self._select_window(1)
            time.sleep(1)

    def __sound_scheduling(self):
        '''音声出力スケジュール
        '''
        # 安眠用渓流音を流す
        sd.every().day.at(stream_start).do(self._stream_sound.start_thread)
        # 安眠用渓流音を停止
        sd.every().day.at(stream_end).do(self._stream_sound.stop_thread)
        