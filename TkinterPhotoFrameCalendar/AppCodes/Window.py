#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from AppCodes.Configuration import EventFolderConfig, dt
from AppCodes.Widget import *


### 定数
HEIGHT = 550
WIDTH = 980


class BaseWindow(BaseFrame):
    ''' 画面用基底フレーム設計クラス
    '''
    ### 定数
    _MAIN_L = HEIGHT

    def __init__(self, master=None):
        '''コンストラクタ
        '''
        super().__init__(master=master)
        self.grid(row=0, column=0, sticky="nsew")
        self._is_window = True      # 画面が表示されているか
        
    def __del__(self):
        '''デストラクタ
        '''
        self._is_window = False
        

class Window1(BaseWindow):
    ''' カレンダー／デジタル時計／スライドショー画面設計クラス
    '''
    def __init__(self, master, init_date:dt.datetime):
        '''コンストラクタ
        Param: 画面生成日時
        '''
        super().__init__(master=master)
        self.__current_date = init_date
        self.__folder_config = EventFolderConfig()
        # カレンダーとディジタル時計表示部分
        self._create_datetime_frame(init_date)
        # スライドショー表示部分
        self._create_slideshow_frame(init_date.date())
        # メイン画面生成時の日時を設定
        self.current_datetime_callback(now=init_date)
        
    def __del__(self):
        '''デストラクタ
        '''
        super().__del__()
        
    def _create_datetime_frame(self, init_date:dt.datetime):
        '''カレンダーとディジタル時計表示フレーム生成
        '''
        datetime_frame = BaseFrame(master=self)
        datetime_frame.pack(side=tk.LEFT)
        # カレンダー表示部分生成
        self._cal = Calendar(master=datetime_frame, init_date=init_date.date())     # カレンダーオブジェクト生成
        self._cal.pack()
        self.update()
        # ディジタル時計表示部分生成
        d_clock_height =self._MAIN_L - self._cal.winfo_height()
        d_clock_width = self._cal.winfo_width()
        self._d_clock = DigitalClock(master=datetime_frame, height=d_clock_height, width=d_clock_width)
        self._d_clock.pack(fill = tk.BOTH)
        self.update()

    def _create_slideshow_frame(self, init_date:dt.date):
        '''スライドショー表示フレーム生成
        '''
        slideshow_frame = BaseFrame(master=self)
        slideshow_frame.pack(side=tk.LEFT)
        self._slideshow_view = SlideShow(master=slideshow_frame, length=self._MAIN_L, interval=self.__folder_config.interval)
        self._slideshow_view.pack(fill = tk.BOTH)
        self.update()
        # スライドショー画像フォルダ初期値設定
        self._slideshow_view.change_src_folder(self.__folder_config.get_event_folder(init_date.month, init_date.day))
        
    def current_datetime_callback(self, now:dt.datetime):
        '''現在日時を更新
        '''
        if (self._is_window == True):
            self._d_clock.clock_update(now)                     # ディジタル時計更新
            self._slideshow_view.change_show_image(now.second)  # スライドショー画像更新
            if (self.__current_date != now.date()):
                # 日付が進んだ場合
                self._cal.current_date_callback(now.date())     # カレンダー更新
                self._slideshow_view.change_src_folder(self.__folder_config.get_event_folder(now.month, now.day))   # スライドショー画像フォルダ変更
                self.__current_date = now.date()
            
    def send_date_select_flag(self) -> bool:
        return self._cal.date_selected

    def date_select_flag_down(self):
        self._cal.date_selected = False

    def send_selected_date(self) -> dt.date:
        return self._cal.select_date_send()


class Window2(BaseWindow):
    ''' アナログ時計／日付詳細画面設計クラス
    '''
    def __init__(self, master, init_date:dt.datetime):
        '''コンストラクタ
        Param: 画面生成日時
        '''
        super().__init__(master=master)
        # 日付詳細情報の表示
        self._create_date_detail_frame()
        # アナログ時計表示部分
        self._create_time_frame()
        # 面生成時の日時を設定
        self.select_date_callback(select_date=init_date.date())
        self.current_time_callback(now=init_date.time())
        
    def __del__(self):
        '''デストラクタ
        '''
        super().__del__()
        
    def _create_date_detail_frame(self):
        '''日付詳細情報の表示フレーム生成
        '''
        detail_frame = BaseFrame(master=self)
        detail_frame.pack(side=tk.LEFT)
        # 日付詳細情報の表示部分
        self._day_detail = DayDetailInfo(detail_frame, (self._MAIN_L - 20), int(WIDTH / 2))
        self._day_detail.pack(fill = tk.BOTH)
        self.__create_select_frame(detail_frame)
        self.update()
        
    def __create_select_frame(self, master:BaseFrame):
        '''年月選択フレームを生成
        Param:
            super_frame: 親フレーム
        '''
        select_frame = BaseFrame(master=master)
        select_frame.pack()
        # 前日表示ボタン
        yesterday_button = BaseButton(select_frame, ButtonConfig("<", 20, 2, 4))
        yesterday_button.bind("<1>", self.__change_day)
        yesterday_button.pack(side=tk.LEFT)
        # 翌日表示ボタン
        tomorrow_button = BaseButton(select_frame, ButtonConfig(">", 20, 2, 4))
        tomorrow_button.bind("<1>", self.__change_day)
        tomorrow_button.pack(side=tk.LEFT)
        
    def _create_time_frame(self):
        '''アナログ時計表示フレーム生成
        '''
        time_frame = BaseFrame(master=self)
        time_frame.pack(side=tk.LEFT)
        # アナログ時計表示部分生成
        self._a_clock = AnalogClock(time_frame, self._MAIN_L, int(WIDTH / 2))
        self._a_clock.pack(fill = tk.BOTH)
        self.update()
        
    def __change_day(self, event):
        '''表示日を変更
        '''
        if (event.widget["text"] == "<"):
            self.__select_date = self.__select_date - dt.timedelta(days=1)  # 前日表示ボタン押下
        elif (event.widget["text"] == ">"):
            self.__select_date = self.__select_date + dt.timedelta(days=1)  # 翌日表示ボタン押下
        self.select_date_callback(self.__select_date)       # 日付詳細情報を選択した年月日のものに変更
        
    def select_date_callback(self, select_date:dt.date):
        '''選択した年月日を取得
        '''
        self._day_detail.update_show_date(select_date)
        self.__select_date = select_date
        
    def current_time_callback(self, now:dt.time):
        '''現在日時を更新
        '''
        if (self._is_window == True):
            # アナログ時計更新
            self._a_clock.clock_update(now)
            