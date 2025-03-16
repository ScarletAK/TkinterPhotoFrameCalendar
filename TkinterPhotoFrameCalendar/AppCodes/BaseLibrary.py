#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyautogui as pag
import tkinter as tk
import tkinter.ttk as ttk

from dataclasses import dataclass

from AppCodes.Configuration import *


### 定数
BROWN = "#512007"
BEIGE = "#f5f5dc"
FONT = "Times"      # 文字フォント


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


class DayButton(tk.Button):
    ''' 日付ボタン設計クラス
    '''
    ### 定数
    # 文字色（0:通常, 1:所定休日（主に土曜）, 2:法定休日（主に日曜、祝日））
    _fg_color = [BROWN, "#0000cc", "#cc0000"]
    # 背景色（0:通常, 1:現在年月日）
    _bg_color = [BEIGE, "#00aa00"]

    def __init__(self, master=None, text:str="", fg:int=0, bg:int=0):
        super().__init__(master=master)
        self.configure(font=(FONT, 14), height=2, width=4, relief=tk.RAISED, text=text,
                       foreground=self._fg_color[fg], background=self._bg_color[bg])


class MonthSelectBox(ttk.Combobox):
    '''月選択ボックス設計
    '''
    def __init__(self, master=None):
        super().__init__(master=master)
        self.configure(textvariable=tk.StringVar(), font=(FONT, 24), height=40, width=10,
                       values=CalendarConfig().get_month_texts(), foreground=BROWN, background=BEIGE)
