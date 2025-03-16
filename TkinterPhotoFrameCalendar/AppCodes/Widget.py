#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import os
import re
import random

from AppCodes.BaseLibrary import *
from AppCodes.OutputMedia import ImageView, ImageSynchronize


class Calendar(BaseFrame):
    ''' カレンダー設計クラス
    '''
    def __init__(self, master, init_date:dt.date):
        '''コンストラクタ
        Param: 画面生成日時
        '''
        super().__init__(master=master)
        self._is_shown = False
        self._set_calendar_config()                 # カレンダー表示設定
        # カレンダー生成時の日時を初期値として設定
        self.current_date_callback(init_date)
        self.__select_date = [init_date.year, init_date.month, init_date.day]
        # 各フレームを生成
        self.__create_select_frame()                # 年月選択フレームを生成
        self.__create_weekday_frame()               # 曜日フレームを生成
        self.__create_show_calendar_frame()         # 選択年月カレンダー表示フレームを生成
        self._is_shown = True
        self.date_selected = False
        
    def __del__(self):
        '''デストラクタ
        '''
        self._is_shown = False

    def _set_calendar_config(self):
        '''カレンダー表示設定
        '''
        self.__config = CalendarConfig()
        self._week_texts = self.__config.get_week_texts()
        self._month_texts = self.__config.get_month_texts()

    def current_date_callback(self, now:dt.date):
        '''現在の年月日外部から取得
        '''
        self.__current_date = now
        self.__show_today()

    def select_date_send(self) -> dt.date:
        '''選択した年月日を外部へ渡す
        '''
        return dt.date(self.__select_date[0], self.__select_date[1], self.__select_date[2])

    def __create_select_frame(self):
        '''年月選択フレームを生成
        Param:
            super_frame: 親フレーム
        '''
        select_frame = BaseFrame(master=self)
        select_frame.pack()
        # 今日の年月に戻すボタン
        today_button = BaseButton(select_frame, ButtonConfig("today", 16, 2, 4))
        today_button.bind("<1>", self.__show_today_event)
        today_button.pack(side=tk.LEFT)
        # 前月表示ボタン
        prev_month_button = BaseButton(select_frame, ButtonConfig("<", 16, 2, 2))
        prev_month_button.bind("<1>",self.__change_month)
        prev_month_button.pack(side=tk.LEFT)
        # 月選択ボックス
        self.__select_month_box = MonthSelectBox(select_frame)
        self.__select_month_box.set(self._month_texts[self.__select_date[1]])
        self.__select_month_box.bind('<<ComboboxSelected>>', self.__change_month)
        self.__select_month_box.pack(side=tk.LEFT)
        # 年選択ボックス
        self.__select_year_box = self.__create_year_select_box(select_frame)
        self.__select_year_box.set(self.__select_date[0])
        self.__select_year_box.pack(side=tk.LEFT)
        # 次月表示ボタン
        next_month_button = BaseButton(select_frame, ButtonConfig(">", 16, 2, 2))
        next_month_button.bind("<1>",self.__change_month)
        next_month_button.pack(side=tk.LEFT)

    def __show_today_event(self, event):
        self.__show_today()
        
    def __create_year_select_box(self, super_frame:tk.Frame) -> ttk.Spinbox:
        '''年選択ボックス生成
        Param:
            super_frame: 親フレーム
        Return:
            ttk.Spinbox
        Note:
            選択範囲は西暦1900年～2100年
        '''
        select_box = ttk.Spinbox(master=super_frame, textvariable=tk.StringVar(), font=self._set_font(24), width=6,
                                 from_=1900, to=2100, foreground=self._fg_color, background=self._bg_color, command=lambda: self.__change_year())
        return select_box

    def __create_weekday_frame(self):
        '''曜日表示フレームを生成
        '''
        weekday_frame = BaseFrame(master=self)
        weekday_frame.pack()
        label_week = {}     # 曜日ボタンを格納する変数をdict型で作成
        f_color = [2, 0, 0, 0, 0, 0, 1]
        for index in range(7):
            label_week[index] = DayButton(weekday_frame, self._week_texts[index], f_color[index])
            label_week[index].grid(row=0, column=index)
        
    def __create_show_calendar_frame(self):
        '''カレンダー表示部分を生成
        '''
        self.__show_calendar_frame = BaseFrame(master=self)
        self.__show_calendar_frame.pack()
        self.__show_select_calendar(self.__select_date[0], self.__select_date[1])
        
    def __show_select_calendar(self, year, month):
        '''指定した年月のカレンダー表示
        Param: 指定年月
        '''
        try:
            for key,item in button_day.items():
                item.destroy()
        except:
            pass
        days = self.__config.get_monthcalendar(year, month)
        holiday_list = self.__config.get_holiday_list(year, month)  # 祝日リストを取得
        button_day = {}     # 日付ボタンを格納する変数をdict型で作成
        f_color = 0
        b_color = 0
        # 日付ボタンを生成
        for index in range(0, 42):
            day_text = ""
            col = index - (7 * int(index/7))
            row = int(index/7)
            try:
                if (days[row][col] != 0):
                    day_text = str(days[row][col])      # ボタンに日付を記入（0でない場合）
                    if (col == 0):
                        f_color = 2         # 日曜日
                    elif (col == 6):
                        if days[row][col] in holiday_list.keys():
                            f_color = 2     # 祝日
                        else:
                            f_color = 1     # 通常の土曜日
                    else:
                        if days[row][col] in holiday_list.keys():
                            f_color = 2     # 祝日
                        else:
                            f_color = 0     # 平日
                    # 今日の日付のボタンのみ背景を変える
                    if (days[row][col] != self.__current_date.day):
                        b_color = 0
                    else:
                        if ((year==self.__current_date.year) and (month==self.__current_date.month)):
                            b_color = 1
                        else:
                            b_color = 0
                else:
                    day_text = ""
                    f_color = 0
                    b_color = 0
            except:
                # 月によってはindex=41まで日付がないため、日付がないindexのエラー回避が必要
                day_text = ""
                f_color = 0
                b_color = 0
            button_day[index] = DayButton(self.__show_calendar_frame, day_text, f_color, b_color)
            if (day_text!=""):
                button_day[index].bind('<ButtonPress>', self.__set_select_day)
            button_day[index].grid(row=row, column=col)
        self.__select_date[0] = year
        self.__select_date[1] = month
        
    def __set_select_day(self, event):
        '''選択した日付を設定
        '''
        self.__select_date[2] = int(event.widget.cget("text"))
        self.date_selected = True

    def __show_today(self):
        '''表示カレンダーを今日の年月のものに戻す
        '''
        if (self._is_shown == True):
            self.__select_year_box.set(self.__current_date.year)                        # 現在の年
            self.__select_month_box.set(self._month_texts[self.__current_date.month])   # 現在の月
            self.__show_select_calendar(self.__current_date.year, self.__current_date.month)

    def __change_year(self):
        '''表示年を変更
        '''
        self.__select_date[0] = int(self.__select_year_box.get())
        # 表示カレンダーを選択した年のものに変更
        self.__select_year_box.set(self.__select_date[0])
        self.__show_select_calendar(self.__select_date[0], self.__select_date[1])

    def __change_month(self, event):
        '''表示月を変更
        '''
        if (event.widget["text"] == "<"):
            self.__select_date[1] -= 1          # 前月表示ボタン押下
        elif (event.widget["text"] == ">"):
            self.__select_date[1] += 1          # 次月表示ボタン押下
        else:
            self.__select_date[1] = int(self.__select_month_box.current())  # 月選択ボックスで異なる月を選択
        if (self.__select_date[1] < 1):
            # 1月表示時に前月を表示させようとした場合
            self.__select_date[0] -= 1
            self.__select_date[1] = 12
        elif (self.__select_date[1] > 12):
            # 12月表示時に次月を表示させようとした場合
            self.__select_date[0] += 1
            self.__select_date[1] = 1
        # 表示カレンダーを選択した年月のものに変更
        self.__select_year_box.set(self.__select_date[0])
        self.__select_month_box.set(self._month_texts[self.__select_date[1]])
        self.__show_select_calendar(self.__select_date[0], self.__select_date[1])
        

class ShowDateCanvas(BaseCanvas):
    ''' 日時表示キャンバス設計クラス
    '''
    def __init__(self, master, height:int, width:int):
        super().__init__(master=master, height=height, width=width)

    def _show_date_label(self, year:int, month:int, day:int):
        return "{:04} / {:02} / {:02}".format(year, month, day)

    def _show_time_label(self, hour:int, minute:int, second:int):
        return "{:02} : {:02} : {:02}".format(hour, minute, second)


class DigitalClock(ShowDateCanvas):
    ''' デジタル時計設計クラス
    '''
    def __init__(self, master, height:int, width:int):
        '''コンストラクタ
        Param: マスター、表示用キャンバス高さ、幅
        '''
        super().__init__(master, height, width)
        global digital
        digital = self.create_text(width/2, height/2, font=self._set_font(28), fill=self._fg_color)

    def clock_update(self, now:dt.datetime):
        '''ディジタル時計更新
        '''
        datetime_show = self._show_date_label(now.year, now.month, now.day) + " " + self._show_time_label(now.hour, now.minute, now.second)
        self.itemconfig(digital, text=datetime_show)
        

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
        

class SlideShow(ImageView):
    ''' 外部格納画像表示クラス
    '''
    
    ### 定数
    _INIT_IMAGE_PATH = "./images/top_sample.jpg"    # 初期画像

    def __init__(self, master, length:int, interval:int):
        '''コンストラクタ
        Param: マスター、表示用キャンバス長、画像切り替え間隔[s]
        '''
        super().__init__(master, length, length)
        self._set_folder_path("SlideShow")
        self.__syn_pcs = ImageSynchronize(self._inside_folder)
        # アプリ起動時に表示する初期画像設定
        init_image = os.path.basename(self.__syn_pcs.move_image(self._INIT_IMAGE_PATH))
        self._set_image_plot_to_all_canvas(init_image)
        global slide
        slide = self.create_image(0, 0, image=self._show_image, anchor=tk.NW)
        # スライドショー設定
        self._outside_folders = []
        self._show_list = []
        self._show_index = 0
        self.__interval_sec = interval
        
    def __del__(self):
        '''デストラクタ
        '''
        self.__syn_pcs.images_remove()
        
    def change_src_folder(self, folders:list):
        '''スライドショー表示画像が格納されている外部側フォルダを変更
        '''
        self._outside_folders = folders
        self.__syn_pcs.synchronize(folders)     # 外部側フォルダと内部側フォルダの画像を同期
        self._show_images_shuffle()             # 表示画像の順番をシャッフル
        self._show_index = 0
        
    def change_show_image(self, second:int):
        '''スライドショー表示画像の変更
        Param: 秒
        '''
        if ((second % self.__interval_sec)==0):
            self._set_image_plot_to_all_canvas(self._show_list[self._show_index])
            self.itemconfig(slide, image=self._show_image)
            self._show_index = self._show_index + 1
        elif (self._show_index >= len(self._show_list)):
            self.__syn_pcs.synchronize(self._outside_folders)   # 外部側フォルダと内部側フォルダの画像を同期
            self._show_images_shuffle()     # 表示画像の順番をシャッフル
            self._show_index = 0
            
    def _show_images_shuffle(self):
        '''表示画像の順番をシャッフル
        '''
        self._show_list.clear()
        for dirpath, dirnames, images in os.walk(self._inside_folder):
            for image in images:
                if re.search('.+\.(jpg|JPG)', image) == None:
                    # 画像の形式がJPEGでない場合、JPEG変換
                    self.__change_to_jpeg(image)
                self._show_list.append(image)
        # リスト内の画像をシャッフル
        random.shuffle(self._show_list)
    
    def __change_to_jpeg(self, src_image:str):
        '''画像をJPEG形式へ変換
        '''
        src_path = self._inside_folder + "/" + src_image
        img_name = os.path.splitext(os.path.basename(src_image))
        dst_path = self._inside_folder + "/" + img_name + '.jpg'
        img = Image.open(src_path)
        img = img.convert('RGB')
        img.save(dst_path, "JPEG", quality=95)
        os.remove(src_path)
        