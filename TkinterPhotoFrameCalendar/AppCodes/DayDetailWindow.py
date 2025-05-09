#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from AppCodes.BaseLibrary import BaseWindow, BaseFrame, BaseButton, ButtonConfig, ShowDateCanvas
from AppCodes.Configuration import EventNameConfig, JapanDaysConfig, Kyureki
from AppCodes.ImportCommon import *
from AppCodes.OutputMedia import ImageView


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
            

class DayDetailInfo(ShowDateCanvas):
    ''' 日付詳細説明設計クラス
    '''
    def __init__(self, master, height:int, width:int):
        super().__init__(master=master, height=height, width=width)
        global detail
        detail = self.create_text(20, 20, text="", anchor=tk.NW, font=self._set_font(18), fill=self._fg_color)
        self._jp_days_conf = JapanDaysConfig()
        self.__event_config = EventNameConfig()

    def update_show_date(self, show_date:dt.date):
        '''詳細表示年月日を更新
        '''
        show_date_label = self._show_date_label(show_date.year, show_date.month, show_date.day)
        holiday = ""
        holiday_list = self._jp_days_conf.get_japan_holiday_list(show_date.year, show_date.month)
        if (show_date.day in holiday_list.keys()):
            holiday = holiday_list[show_date.day]
        kanshi = "年干支：" + self._jp_days_conf.get_zodiac(show_date.year)
        getsumei = "月和暦：" + self._jp_days_conf.get_tsukiwamei(show_date.month)
        wareki = "　和暦：" + self._jp_days_conf.convert_to_wareki(show_date) + str(show_date.month) + "月" + str(show_date.day) + "日"
        lunar_date = Kyureki.from_ymd(show_date.year, show_date.month, show_date.day)
        kyureki = "　旧暦：" + str(lunar_date)
        rokuyo = "　六曜：" + lunar_date.rokuyou
        term = "　　　　" + self._jp_days_conf.check_solar_terms_in_date(show_date)
        day_text = show_date_label + "\n" + holiday + "\n" + kanshi + "\n" + getsumei + "\n" + wareki + "\n" + kyureki + "\n" + rokuyo + "\n" + term
        day_events = self.__event_config.get_event_name(show_date.month, show_date.day)
        if (len(day_events) > 0):
            for event_name in day_events:
                day_text = day_text + "\n" + event_name
        self.itemconfig(detail, text=day_text)
        

class AnalogClock(ImageView):
    ''' アナログ時計設計クラス
    '''

    ### 定数
    __OVAL_RAD = 200
    __OVAL_RAD_H = 210  # 短針端点の半径
    __OVAL_RAD_M = 220  # 長針端点の半径
    __OVAL_RAD_S = 230  # 秒針端点の半径
    __EDGE_H = 100      # 短針の端点
    __EDGE_M = 70       # 長針の端点
    __EDGE_S = 40       # 秒針の端点
    __W_TAG = "needle"  # ウィジェットタグ
    
    def __init__(self, master, height:int, width:int):
        '''コンストラクタ
        Param: マスター、表示用キャンバス高さ、幅
        '''
        super().__init__(master, height, width)
        self.__C = [int(width/2), int(height/2)]    # アナログ時計中心
        # 文字盤を表示（from : https://illustimage.com/?id=11732）
        self._set_folder_path("AnalogClock")
        self._set_image_plot_to_all_canvas("clock_oval.jpg")
        self.create_image(self.__C[0], self.__C[1], image=self._show_image)
        self.__create_clock_oval(self.__OVAL_RAD_S)
        self.__create_clock_oval(self.__OVAL_RAD_M)
        self.__create_clock_oval(self.__OVAL_RAD_H)
        self.__create_clock_oval(self.__OVAL_RAD)
        
    def __create_clock_oval(self, rad:int):
        '''アナログ時計の文字盤の外周を描画
        '''
        self.create_oval((self.__C[0]-rad), (self.__C[1]-rad), (self.__C[0]+rad), (self.__C[1]+rad), width=1.5, fill=None)

    def clock_update(self, now:dt.time):
        '''アナログ時計の針を描画
        '''
        # 針を初期化
        self.delete(self.__W_TAG)
        # 各針の角度算出
        angle_h = math.radians(float(90 - 30 * now.hour - (now.minute / 2)))    # 時
        angle_m = math.radians(float(90 - 6 * now.minute))                      # 分
        angle_s = math.radians(float(90 - 6 * now.second))                      # 秒
        # 針の終端位置
        pos_hx = [self.__C[0]+round(math.cos(angle_h)*self.__EDGE_H), self.__C[0]+round(math.cos(angle_h)*self.__OVAL_RAD_H)] # 時のX座標
        pos_hy = [self.__C[1]-round(math.sin(angle_h)*self.__EDGE_H), self.__C[1]-round(math.sin(angle_h)*self.__OVAL_RAD_H)] # 時のY座標
        pos_mx = [self.__C[0]+round(math.cos(angle_m)*self.__EDGE_M), self.__C[0]+round(math.cos(angle_m)*self.__OVAL_RAD_M)] # 分のX座標
        pos_my = [self.__C[1]-round(math.sin(angle_m)*self.__EDGE_M), self.__C[1]-round(math.sin(angle_m)*self.__OVAL_RAD_M)] # 分のY座標
        pos_sx = [self.__C[0]+round(math.cos(angle_s)*self.__EDGE_S), self.__C[0]+round(math.cos(angle_s)*self.__OVAL_RAD_S)] # 秒のX座標
        pos_sy = [self.__C[1]-round(math.sin(angle_s)*self.__EDGE_S), self.__C[1]-round(math.sin(angle_s)*self.__OVAL_RAD_S)] # 秒のY座標
        # 針を描画（外側から針を向けるイメージ）
        self.create_line(pos_hx[0], pos_hy[0], pos_hx[1], pos_hy[1], width=10, tags=self.__W_TAG)
        self.create_line(pos_mx[0], pos_my[0], pos_mx[1], pos_my[1], width=5, tags=self.__W_TAG)
        self.create_line(pos_sx[0], pos_sy[0], pos_sx[1], pos_sy[1], width=2, tags=self.__W_TAG)
        