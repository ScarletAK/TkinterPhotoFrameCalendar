#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import calendar as cal
import csv
import datetime as dt
import json

from qreki import Kyureki


### 定数
# ※実行環境に応じて変更すること
APP_ROOT = "C:/XXX/TkinterPhotoFrameCalendar/TkinterPhotoFrameCalendar/"


class JsonFileConfig:
    '''アプリ全体設定
    ※JSONファイルから読み込み
    '''
    def __init__(self, item_name:str):
        '''コンストラクタ
        '''
        try:
            with open(APP_ROOT + "settings/Configure.json",'r') as f:
                load_config = json.load(f)
                self._get_setting = load_config[item_name]
        except FileNotFoundError:
            self._get_setting = None


class SoundConfig(JsonFileConfig):
    '''音声出力設定
    '''
    def __init__(self, sound_type_name:str):
        '''コンストラクタ
        '''
        super().__init__(item_name=sound_type_name)
        self.__get_init_values()
        if self._get_setting is None:
            self.__get_default_values(sound_type_name)
        else:
            self.__get_file_values()
        
    def __get_init_values(self):
        '''初期設定
        '''
        self.file_name = ""     # 渓流音ファイル名
        self.times = []         # 渓流音出力時刻

    def __get_file_values(self):
        '''ファイル設定
        '''
        self.file_name = self._get_setting["FileName"]
        self.times = [self._get_setting["Start"], self._get_setting["End"]]

    def __get_default_values(self, sound_type_name:str):
        '''デフォルト設定
        '''
        if (sound_type_name == "StreamSound"):
            self.file_name = "stream.wav"       # 引用元：https://soundeffect-lab.info/sound/environment/ 「渓流」(wav変換)
            self.times = ["00:00", "03:00"]


class SlideShowConfig(JsonFileConfig):
    '''スライドショー設定
    '''
    def __init__(self):
        '''コンストラクタ
        '''
        super().__init__(item_name="SlideShow")
        self.__get_init_values()
        if self._get_setting is None:
            self.__get_default_values()
        else:
            self.__get_file_values()
        
    def __get_init_values(self):
        '''初期設定
        '''
        self.interval = 0               # スライドショー時間間隔
        self.root_folder = ""           # 外部画像フォルダ
        self.month_common_folders = {}  # 月共通画像フォルダ
        
    def __get_file_values(self):
        '''ファイル設定
        '''
        self.interval = self._get_setting["Interval"]
        self.root_folder = self._get_setting["BaseFolder"]
        self.month_common_folders = self._get_setting["MonthComm"]

    def __get_default_values(self):
        '''デフォルト設定
        '''
        self.interval = 10
        self.root_folder = "C:/Users/ITO TOMOAKI/GitProjects/TkinterPhotoFrameCalendar/sampleimages/"
        self.month_common_folders = {"1":"01_Common_Jan",
                                     "2":"02_Common_Feb",
                                     "3":"03_Common_Mar",
                                     "4":"04_Common_Apr",
                                     "5":"05_Common_May",
                                     "6":"06_Common_Jun",
                                     "7":"07_Common_Jul",
                                     "8":"08_Common_Aug",
                                     "9":"09_Common_Sep",
                                     "10":"10_Common_Oct",
                                     "11":"11_Common_Nov",
                                     "12":"12_Common_Dec"}


class EventConfig:
    '''日毎イベントの設定基幹クラス
    ※CSV形式のデータベース読み込み
    '''
    def __init__(self):
        '''コンストラクタ
        '''
        with open(APP_ROOT + "settings/EventsDB.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self._db = [row for row in reader]  # イベントのDB設定


class EventNameConfig(EventConfig):
    '''日毎イベント名の設定
    '''
    def __init__(self):
        '''コンストラクタ
        '''
        super().__init__()

    def get_event_name(self, month:int, day:int) -> list:
        '''指定月日に設定されたイベントの名称を全て取得
        Param:  月日
        Return: イベントの名称
        '''
        names = []
        for event_row in self._db:
            if ((event_row['Month'] == str(month)) and (event_row['Day'] == str(day))):
                names.append(event_row['Name'])
        if ((month == 2) and (day == 22)):
            names.append("竹島の日")
        if ((month == 2) and (day == 28)):
            names.append("二・二八事件")
        if ((month == 6) and (day == 4)):
            names.append("六四天安門事件")
        return names
    

class EventFolderConfig(EventConfig):
    '''日毎イベントフォルダの設定
    '''
    def __init__(self):
        '''コンストラクタ
        '''
        super().__init__()
        self.__config = SlideShowConfig()
        self.interval = self.__config.interval
        self.__outside_image_folder = self.__config.root_folder             # 外部画像フォルダ
        self.__month_common_folders = self.__config.month_common_folders    # 月共通画像フォルダ

    def get_event_folder(self, month:int, day:int) -> list:
        '''指定月日に設定されたイベントの画像格納フォルダを全て取得
        Param:  指定月日、外部画像フォルダパス
        Return: イベントの画像格納フォルダ
        '''
        folders = []
        folder_path = ""
        for event_row in self._db:
            if ((event_row['Month'] == str(month)) and (event_row['Day'] == str(day))):
                if (event_row['ImageFolder'] != ""):
                    folder_path = self.__outside_image_folder + event_row['ImageFolder']
                    folders.append(folder_path)
        # 指定月日にイベントが設定されていない場合、月共通イベントを設定
        if (len(folders) < 1):
            folder_path = self.__outside_image_folder + self.__month_common_folders[str(month)]
            folders.append(folder_path)
        return folders


class CalendarConfig:
    '''カレンダー表示設定クラス
    ※将来的には外部ファイルから設定したい
    '''
    def __init__(self):
        '''コンストラクタ
        '''
        cal.setfirstweekday(cal.SUNDAY)   # 曜日の始まりを日曜日に設定

    def get_week_texts(self):
        return [cal.day_abbr[6]] + [cal.day_abbr[w] for w in range(6)]

    def get_month_texts(self):
        return [cal.month_name[m] for m in range(13)]

    def get_monthcalendar(self, year:int, month:int):
        '''指定年月のカレンダー配列を取得
        '''
        return cal.monthcalendar(year, month)

    def get_holiday_list(self, year:int, month:int):
        '''指定年月の祝日リストを取得
        '''
        return JapanDaysConfig().get_japan_holiday_list(year, month)


class JapanDaysConfig:
    '''日本の祝日などの設定クラス
    '''
    def __init__(self):
        '''コンストラクタ
        '''
        # 和暦
        self.wareki_start = {'令和':dt.date(2019,5,1),
                             '平成':dt.date(1989,1,8),
                             '昭和':dt.date(1926,12,25),
                             '大正':dt.date(1912,7,30),
                             '明治':dt.date(1868,10,23)}
        # 二十四節季
        # from : http://addinbox.sakura.ne.jp/sekki24_topic.htm
        self.terms_data = [{'name':'小寒', 'month':1, 'd':6.3811, 'a':0.242778, 'deltaYear':-1},
                           {'name':'大寒', 'month':1, 'd':21.1046, 'a':0.242765, 'deltaYear':-1},
                           {'name':'立春', 'month':2, 'd':4.8693, 'a':0.242713, 'deltaYear':-1},
                           {'name':'雨水', 'month':2, 'd':19.7062, 'a':0.242627, 'deltaYear':-1},
                           {'name':'啓蟄', 'month':3, 'd':6.3968, 'a':0.242512, 'deltaYear':0},
                           {'name':'春分', 'month':3, 'd':21.4471, 'a':0.242377, 'deltaYear':0},
                           {'name':'清明', 'month':4, 'd':5.6280, 'a':0.242231, 'deltaYear':0},
                           {'name':'穀雨', 'month':4, 'd':20.9375, 'a':0.242083, 'deltaYear':0},
                           {'name':'立夏', 'month':5, 'd':6.3771 , 'a':0.241945, 'deltaYear':0},
                           {'name':'小満', 'month':5, 'd':21.9300, 'a':0.241825, 'deltaYear':0},
                           {'name':'芒種', 'month':6, 'd':6.5733, 'a':0.241731, 'deltaYear':0},
                           {'name':'夏至', 'month':6, 'd':22.2747, 'a':0.241669, 'deltaYear':1},
                           {'name':'小暑', 'month':7, 'd':8.0091, 'a':0.241642, 'deltaYear':0},
                           {'name':'大暑', 'month':7, 'd':23.7317, 'a':0.241654, 'deltaYear':0},
                           {'name':'立秋', 'month':8, 'd':8.4102, 'a':0.241703, 'deltaYear':0},
                           {'name':'処暑', 'month':8, 'd':24.0125, 'a':0.241786, 'deltaYear':0},
                           {'name':'白露', 'month':9, 'd':8.5186, 'a':0.241898, 'deltaYear':0},
                           {'name':'秋分', 'month':9, 'd':23.8896, 'a':0.242032, 'deltaYear':0},
                           {'name':'寒露', 'month':10, 'd':9.1414, 'a':0.242179 , 'deltaYear':0},
                           {'name':'霜降', 'month':10, 'd':24.2487, 'a':0.242328, 'deltaYear':0},
                           {'name':'立冬', 'month':11, 'd':8.2396, 'a':0.242469 , 'deltaYear':0},
                           {'name':'小雪', 'month':11, 'd':23.1189, 'a':0.242592, 'deltaYear':0},
                           {'name':'大雪', 'month':12, 'd':7.9152, 'a':0.242689, 'deltaYear':0},
                           {'name':'冬至', 'month':12, 'd':22.6587, 'a':0.242752, 'deltaYear':0}]
            
    def convert_to_wareki(self, era_date:dt.date) -> str:
        '''西暦の年月日を和暦の年に変換
        '''
        try:
            era_str = self.__get_wareki(era_date)
            if era_str != '':
                reiwa_year = self.wareki_start[era_str].year
                year = (era_date.year - reiwa_year) + 1
                if year == 1:
                    year = '元'
                return era_str + str(year) + '年'
            else:
                return '明治以前'
        except ValueError as e:
            raise e

    def __get_wareki(self, enter_date:dt.date) -> str:
        '''西暦の年月日から和暦を算出
        '''
        try:
            if self.wareki_start['令和'] <= enter_date:
                return '令和'
            elif self.wareki_start['平成'] <= enter_date:
                return '平成'
            elif self.wareki_start['昭和'] <= enter_date:
                return '昭和'
            elif self.wareki_start['大正'] <= enter_date:
                return '大正'
            elif self.wareki_start['明治'] <= enter_date:
                return '明治'
            else:
                return ''
        except ValueError as e:
            raise e
        
    def get_solar_terms_in_year(self, year:int) -> dict:
        '''入力年の二十四節季を算出
        from : http://addinbox.sakura.ne.jp/sekki24_topic.htm
        '''
        terms = {}
        for term in self.terms_data:
            name = term['name']
            month = term['month']
            d = term['d']
            a = term['a']
            delta_year = term['deltaYear']
            day = int(d + (a * (year + delta_year - 1900))) - int((year + delta_year - 1900) / 4)
            terms[name] = dt.date(year, month, day)
        return terms
        
    def check_solar_terms_in_date(self, enter_date:dt.date) -> str:
        '''入力した日付が二十四節季に相当するか確認
        '''
        try:
            solar_terms = self.get_solar_terms_in_year(enter_date.year)     # 入力年の二十四節季を取得
            term_names = [k for k, v in solar_terms.items() if v ==enter_date]
            if term_names == []:
                return ''
            else:
                return term_names[0]
        except ValueError as e:
            raise e
        
    def get_zodiac(self, year:int) -> str:
        '''年干支を算出
        '''
        KAN = {4:'甲',5:'乙',6:'丙',7:'丁',8:'戊',9:'己',0:'庚',1:'辛',2:'壬',3:'癸'}
        SHI = {4:'子',5:'丑',6:'寅',7:'卯',8:'辰',9:'巳',10:'午',11:'未',0:'申',1:'酉',2:'戌',3:'亥'}
        index_kan = year % 10
        index_shi = year % 12
        return (KAN[index_kan]+SHI[index_shi])
        
    def get_tsukiwamei(self, month:int) -> str:
        '''月和名を算出
        '''
        M = {1:"睦月",2:"如月",3:"弥生",4:"卯月",5:"皐月",6:"水無月",7:"文月",8:"葉月",9:"長月",10:"神無月",11:"霜月",12:"師走"}
        return M[month]

    def get_japan_holiday_list(self, year:int, month:int) -> dict:
        '''入力年月の、日本における祝日リストを取得
        '''
        solar_terms = self.get_solar_terms_in_year(year)    # 入力年の二十四節季を取得
        self._holiday_list = {}                             # 入力月の休日リスト
        if month == 1:
            # １月
            self.__check_substitute_holiday(year, month, 1, "元日")
            if year >= 1948 and year < 2000:
                self.__check_substitute_holiday(year, month, 15, "成人の日（小正月）")
            else:
                self.__get_happy_monday_holiday(year, month, 2, 1, "成人の日")
        elif month == 2:
            # ２月
            holiday_name = ""
            if year <= 1948:
                self.__check_substitute_holiday(year, month, 11, "紀元節")
            elif year >= 1967:
                self.__check_substitute_holiday(year, month, 11, "建国記念の日\n紀元節")
            if self.__get_wareki(dt.date(year, month, 23)) == '令和':
                self.__check_substitute_holiday(year, month, 23, "天皇誕生日\n天長節")
        elif month == 3:
            # ３月
            VED = solar_terms['春分'].day     # 春分日を算出
            holiday_name = ""
            if year <= 1948:
                holiday_name = "春季皇霊祭"
            else:
                holiday_name = "春分の日\n春季皇霊祭"
            self.__check_substitute_holiday(year, month, VED, holiday_name)
        elif month == 4:
            # ４月
            if year > self.wareki_start['昭和'].year:
                holiday_name = ""
                if year < self.wareki_start['平成'].year:
                    holiday_name = "天皇誕生日\n天長節"
                elif year < 2007:
                    holiday_name = "みどりの日"
                else:
                    holiday_name = "昭和の日"
                self.__check_substitute_holiday(year, month, 29, holiday_name)
                if year == self.wareki_start['令和'].year:
                    self._holiday_list[30] = "国民の休日"
        elif month == 5:
            # ５月
            if year >= 1948:
                self._holiday_list[3] = "憲法記念日"
                self._holiday_list[5] = "こどもの日"
                if year >= 1988:
                    if year < 2007:
                        self._holiday_list[4] = "みどりの日"
                    else:
                        self._holiday_list[4] = "国民の休日"
                        if year == self.wareki_start['令和'].year:
                            self._holiday_list[1] = "新天皇即位日"
                            self._holiday_list[2] = "国民の休日"
                    if year >= 1973:
                        if cal.weekday(year, month, 3) == 6 or cal.weekday(year, month, 4) == 6 or cal.weekday(year, month, 5) == 6:
                            self._holiday_list[6] = "振替休日"
        elif month == 6:
            # ６月
            pass  # 祝日なし
        elif month == 7:
            # ７月
            if year >= 1996:
                if year < 2003:
                    self.__check_substitute_holiday(year, month, 20, "海の日")
                elif year == 2020:
                    # 東京五輪による祝日移動（東京五輪は2021年に延期）
                    self._holiday_list[23] = "海の日"
                    self._holiday_list[24] = "スポーツの日"
                elif year == 2021:
                    # 東京五輪による祝日移動
                    self._holiday_list[22] = "海の日"
                    self._holiday_list[23] = "スポーツの日"
                else:
                    self.__get_happy_monday_holiday(year, month, 3, 1, "海の日")
        elif month == 8:
            # ８月
            if year >= 2016:
                mountain_day = 0
                if year == 2020:
                    mountain_day = 10   # 東京五輪による祝日移動（東京五輪は2021年に延期）
                elif year == 2021:
                    mountain_day = 8    # 東京五輪による祝日移動
                else:
                    mountain_day = 11
                self.__check_substitute_holiday(year, month, mountain_day, "山の日")
        elif month == 9:
            # ９月
            AED = solar_terms['秋分'].day     # 秋分日を算出
            holiday_name = ""
            if year <= 1948:
                holiday_name = "秋季皇霊祭"
            else:
                holiday_name = "秋分の日\n秋季皇霊祭"
            self.__check_substitute_holiday(year, month, AED, holiday_name)
            # 敬老の日
            if year >= 1966:
                if year < 2003:
                    self.__check_substitute_holiday(year, month, 15, "敬老の日")
                else:
                    self.__get_happy_monday_holiday(year, month, 3, 1, "敬老の日")
                    # シルバーウイークが出現するか算出
                    holidays = list(self._holiday_list.keys())
                    if abs(holidays[1] - holidays[0]) == 2:
                        self._holiday_list[AED-1] = "国民の休日"
        elif month == 10:
            # 10月
            if year >= 1966:
                if year < 2000:
                    self.__check_substitute_holiday(year, month, 10, "体育の日")
                elif year < 2020:
                    self.__get_happy_monday_holiday(year, month, 2, 1, "体育の日")
                    if year == self.wareki_start['令和'].year:
                        self._holiday_list[22] = "即位礼正殿の儀"
                elif year >= 2020 and year <= 2021:
                    pass      # 東京五輪による祝日移動のためなし
                else:
                    self.__get_happy_monday_holiday(year, month, 2, 1, "スポーツの日")
        elif month == 11:
            # 11月
            holiday_names = []
            if year < 1948:
                holiday_names = ["明治節", "新嘗祭"]
            else:
                holiday_names = ["文化の日\n明治節", "勤労感謝の日\n新嘗祭"]
            self.__check_substitute_holiday(year, month, 3, holiday_names[0])
            self.__check_substitute_holiday(year, month, 23, holiday_names[1])
        elif month == 12:
            # 12月
            if self.__get_wareki(dt.date(year, month, 23)) == '平成':
                self.__check_substitute_holiday(year, month, 23, "天皇誕生日\n天長節")
        return self._holiday_list

    def __check_substitute_holiday(self, year:int, month:int, day:int, holiday_name:str):
        '''1973年以降において、祝日が日曜日の場合、翌日を振替休日として算出
        '''
        self._holiday_list[day] = holiday_name
        if year >= 1973 and cal.weekday(year, month, day) == 6:
            self._holiday_list[day+1] = holiday_name + "　振替休日"

    def __get_happy_monday_holiday(self, year:int, month:int, week:int, weekday:int, holiday_name:str):
        '''ハッピーマンデー制度による祝日取得
        '''
        lines = cal.monthcalendar(year, month)
        if cal.weekday(year, month, 1) > 0 and cal.weekday(year, month, 1) < 6:
            week = week + 1
        days = lines[week-1]
        self._holiday_list[days[weekday]] = holiday_name
        