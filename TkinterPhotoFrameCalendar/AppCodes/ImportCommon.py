#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import calendar as cal
import csv
import datetime as dt
import json
import math
import os
import random
import re
import shutil
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk

from dataclasses import dataclass


### 定数
HEIGHT = 550        # 画面出力高さ
WIDTH = 980         # 画面出力幅
BROWN = "#512007"   # ブラウン（主に文字色で使用）
BEIGE = "#f5f5dc"   # ベージュ（主に背景色で使用）
FONT = "Times"      # 文字フォント
