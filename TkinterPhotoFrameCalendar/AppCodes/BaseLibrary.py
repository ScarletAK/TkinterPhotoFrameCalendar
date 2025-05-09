#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from AppCodes.ImportCommon import *


class BaseFrame(tk.Frame):
    ''' フレーム設計クラス
    '''
    def __init__(self, master=None):
        super().__init__(master=master)
        self._fg_color = BROWN
        self._bg_color = BEIGE
        
    def _set_font(self, font_size:int):
        '''フォント設定
        '''
        return (FONT, font_size)
        

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
        

class BaseCanvas(tk.Canvas):
    ''' キャンバス設計クラス
    '''
    def __init__(self, master=None, height=1, width=1):
        super().__init__(master=master, height=height, width=width, bg=BEIGE)
        self._height = height
        self._width = width
        self._fg_color = BROWN
        self._bg_color = BEIGE
        
    def _set_font(self, font_size:int):
        '''フォント設定
        '''
        return (FONT, font_size)
        

class ShowDateCanvas(BaseCanvas):
    ''' 日時表示キャンバス設計クラス
    '''
    def __init__(self, master, height:int, width:int):
        super().__init__(master=master, height=height, width=width)

    def _show_date_label(self, year:int, month:int, day:int):
        return "{:04} / {:02} / {:02}".format(year, month, day)

    def _show_time_label(self, hour:int, minute:int, second:int):
        return "{:02} : {:02} : {:02}".format(hour, minute, second)


@dataclass
class ButtonConfig:
    text: str       # 表示テキスト
    text_size: int  # テキストサイズ
    height: int     # 高さ
    width: int      # 幅


class BaseButton(tk.Button):
    ''' ボタン設計クラス
    '''
    def __init__(self, master=None, config:ButtonConfig=None):
        super().__init__(master=master)
        self.configure(font=(FONT, config.text_size), height=config.height, width=config.width, relief=tk.RAISED,
                       text=config.text, foreground=BROWN, background=BEIGE)
