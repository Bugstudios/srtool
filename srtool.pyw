import sys
import os
import json
import requests
import pickle
import subprocess
from datetime import datetime
import webbrowser
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QInputDialog, 
                             QGridLayout, QGraphicsDropShadowEffect, QLineEdit, 
                             QTextEdit, QMessageBox, QTextBrowser)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QFontDatabase, QColor, QBrush, QPalette, QPainter, QFontMetrics
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QTimer, QUrl

SAVE_DIR = "./saves/players"
CONFIG_DIR = "./config/software/"
ELEMENT_COLOR_FILE = os.path.join(CONFIG_DIR, "elementcolor.json")
PATHS_MAPPING_FILE = os.path.join(CONFIG_DIR, "pathsmapping.json")

# 加载元素颜色配置
def load_element_colors():
    if not os.path.exists(ELEMENT_COLOR_FILE):
        return {}
    with open(ELEMENT_COLOR_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载路径映射配置
def load_paths_mapping():
    if not os.path.exists(PATHS_MAPPING_FILE):
        return {}
    with open(PATHS_MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

class CharacterDetailWindow(QWidget):
    def __init__(self, character, element_colors, paths_mapping):
        super().__init__()
        self.character = character
        self.element_colors = element_colors
        self.paths_mapping = paths_mapping
        self.rarity_colors = self.load_rarity_colors()
        self.affix_mapping = self.load_affix_mapping()
        self.initUI()

    def load_affix_mapping(self):
        file_path = os.path.join("config", "software", "affixmapping.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    def load_rarity_colors(self):
        file_path = os.path.join("config", "software", "raritycoloring.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    def get_gradient_style(self, rarity):
        colors = self.rarity_colors
        if str(rarity) in colors:
            start = colors[str(rarity)]['start']
            end = colors[str(rarity)]['end']
            return f"background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 {start}, stop:1 {end});"
        return ""

    def initUI(self):
        self.setWindowTitle(f"{self.character['name']} - 详细信息")
        self.showMaximized()
        self.set_background()

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(50, 50, 50, 50)

        # 添加角色立绘
        splashart_path = f"image/splashart/{self.character['id']}.png"
        splashart_pixmap = QPixmap(splashart_path).scaled(768, 768, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splashart_label = QLabel(container)
        splashart_label.setPixmap(splashart_pixmap)
        layout.addWidget(splashart_label, alignment=Qt.AlignLeft | Qt.AlignTop)

        path_name = self.character['path']['name'].lower()
        path_icon_key = self.paths_mapping.get(path_name, None)
        if path_icon_key:
            path_icon_path = f"image/path/{path_icon_key}.png"
            path_pixmap = QPixmap(path_icon_path).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            path_icon_label = QLabel(splashart_label)
            path_icon_label.setPixmap(path_pixmap)
            path_icon_label.move(10, 10)

        # 整个光锥和信息的表格
        light_cone_frame = LightConeFrame(self.character, self.affix_mapping, container)
        light_cone_frame.setFixedSize(896, 576)
        layout.addWidget(light_cone_frame, alignment=Qt.AlignTop)

        light_cone_layout = QVBoxLayout(light_cone_frame)
        light_cone_layout.setContentsMargins(0, 0, 0, 0)

        # 上部信息部分
        top_section = QWidget(light_cone_frame)
        top_section.setFixedHeight(192)
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧光锥图片和渐变背景
        light_cone = self.character.get('light_cone')
        if light_cone:
            rarity = light_cone['rarity']
            cone_id = light_cone['id']
            gradient_style = self.get_gradient_style(rarity)
            cone_name = light_cone['name']
            cone_level = light_cone['level']
            cone_rank = light_cone['rank']
        else:
            rarity = 0
            cone_id = 'unequip'
            gradient_style = "background-color: #444444;"
            cone_name = "未佩戴光锥"
            cone_level = "N/A"
            cone_rank = "N/A"

        gradient_section = QWidget(top_section)
        gradient_section.setFixedSize(192, 192)
        gradient_section.setStyleSheet(gradient_style + "border-top-left-radius: 15px;")

        # 在渐变背景中居中显示光锥图
        gradient_layout = QVBoxLayout(gradient_section)
        gradient_layout.setContentsMargins(0, 0, 0, 0)

        lightcone_pixmap = QPixmap(f"image/lightcone/{cone_id}.png").scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        lightcone_label = QLabel()
        lightcone_label.setPixmap(lightcone_pixmap)
        lightcone_label.setAlignment(Qt.AlignCenter)

        gradient_layout.addWidget(lightcone_label)
        top_layout.addWidget(gradient_section)

        # 右侧信息区域
        right_section = QWidget(top_section)
        right_layout = QVBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 光锥名称
        colors = self.rarity_colors.get(str(rarity), {})
        end_color = colors.get("end", "#ffffff")

        name_label = QLabel(cone_name, right_section)
        name_label.setFixedHeight(72)
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_label.setStyleSheet(f"color: {end_color}; font-size: 36px; font-weight: bold; padding: 0px 2px;")
        right_layout.addWidget(name_label)

        # 第二行: 光锥命途图标、等级、叠影数量
        second_row = QWidget(right_section)
        second_row.setFixedHeight(64)
        second_row_layout = QHBoxLayout(second_row)
        second_row_layout.setContentsMargins(0, 0, 0, 0)

        # 设置布局的对齐方式为左对齐
        second_row_layout.setAlignment(Qt.AlignLeft)

        path_icon_label = QLabel(second_row)
        path_icon_label.setPixmap(QPixmap(path_icon_path).scaled(64, 64, Qt.KeepAspectRatio))
        path_icon_label.setFixedSize(64, 64)
        second_row_layout.addWidget(path_icon_label)

        level_label = QLabel(f"等级 {cone_level}", second_row)
        level_label.setFixedSize(128, 64)
        level_label.setAlignment(Qt.AlignCenter)
        level_label.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        second_row_layout.addWidget(level_label)

        rank_roman = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ"]
        rank_label = QLabel(rank_roman[int(cone_rank) - 1] if cone_rank != "N/A" else "N/A", second_row)
        rank_label.setFixedSize(64, 64)
        rank_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        rank_label.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        second_row_layout.addWidget(rank_label)

        right_layout.addWidget(second_row)

        # 稀有度一行
        font_id = QFontDatabase.addApplicationFont("fonts/hsr-icon.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        star_label = QLabel("b" * rarity, right_section)
        star_label.setFixedHeight(66)
        star_label.setAlignment(Qt.AlignLeft)

        custom_font = QFont(font_family, 16)
        star_label.setFont(custom_font)

        star_label.setStyleSheet(
            f"color: {end_color}; font-weight: bold; "
            f"margin: 0px 0px 0px 0px;"
        )
        right_layout.addWidget(star_label)

        top_layout.addWidget(right_section)
        light_cone_layout.addWidget(top_section)

        # 下方滚动区域
        bottom_section = QScrollArea(light_cone_frame)
        bottom_section.setMinimumHeight(384)
        bottom_section.setWidgetResizable(True)
        bottom_section.setStyleSheet("background-color: transparent; border: none;")
        bottom_section.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bottom_section.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        bottom_content = QWidget()
        bottom_layout = QVBoxLayout(bottom_content)

        if light_cone:
            lightcone_data = self.load_lightcone_data(cone_id)
            if lightcone_data:
                description_browser = QTextBrowser(bottom_content)
                description_browser.setStyleSheet("background-color: transparent; color: white; font-weight: bold;")
                self.populate_lightcone_description(description_browser, lightcone_data)
                bottom_layout.addWidget(description_browser)
        else:
            description_browser = QTextBrowser(bottom_content)
            description_browser.setStyleSheet("color: white; font-weight: bold;")
            description_browser.append("未佩戴光锥")
            bottom_layout.addWidget(description_browser)

        bottom_section.setWidget(bottom_content)
        light_cone_layout.addWidget(bottom_section)

    def load_lightcone_data(self, lightcone_id):
        file_path = os.path.join("config", "lightcone", f"{lightcone_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return None

    def populate_lightcone_description(self, text_browser, data):
        rarity = self.character['light_cone']['rank']

        skill_description = data.get("combined_skill_description", "").replace("\n", "<br>")
        light_cone_description = data.get("light_cone_description", "").replace("\n", "<br>")

        text_browser.clear()

        # Skill name and rarity level line
        skill_name = data.get("skill_name", "")
        text_browser.append(f"{skill_name} - 等级 {rarity}")

        # Skill description with highlighting
        skill_text = ""
        start_marker = '[['
        end_marker = ']]'

        start = skill_description.find(start_marker)
        while start != -1:
            end = skill_description.find(end_marker, start)
            if end != -1:
                actual_start = start + len(start_marker)
                actual_end = end

                skill_text += skill_description[:start]

                # Highlight the number according to rarity
                numbers_str = skill_description[actual_start:actual_end].split(',')
                if 1 <= rarity <= len(numbers_str):
                    number_to_highlight = numbers_str[rarity - 1].strip()
                    skill_text += f"<span style='color:orange;'>{number_to_highlight}</span>"

                skill_description = skill_description[end + len(end_marker):]
                start = skill_description.find(start_marker)
            else:
                break

        skill_text += skill_description
        text_browser.append(skill_text)

        # 添加空行
        text_browser.append("<br>")

        # Light cone description in gray
        text_browser.append(f"<div style='color:grey;'>{light_cone_description}</div>")

    def set_background(self):
        palette = self.palette()
        background_pixmap = QPixmap("image/gui/background.jpeg").scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(background_pixmap))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background()
        super().resizeEvent(event)


class LightConeFrame(QWidget):
    def __init__(self, character, affix_mapping, parent=None, bg_color="#262634"):
        super().__init__(parent)
        self.bg_color = bg_color
        self.character = character
        self.affix_mapping = affix_mapping

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # 填充背景色
        painter.fillRect(rect, QColor(self.bg_color))

        # 绘制右侧分割线
        pen = painter.pen()
        pen.setWidth(2)
        pen.setColor(QColor('#444444'))
        painter.setPen(pen)

        # 计算分割线的起始和终止点位置
        x_position = rect.width() - 320
        y_end = 192
        painter.drawLine(x_position, 0, x_position, y_end)

        # 绘制表格框线
        pen.setWidth(5)
        pen.setColor(QColor('#444444'))
        painter.setPen(pen)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 30, 30)

        # 绘制水平分割线
        horizontal_line_y_position = 192
        painter.drawLine(0, horizontal_line_y_position, rect.width(), horizontal_line_y_position)

        # 在这里添加检测光锥是否存在并绘制属性图标、名称及数值
        light_cone = self.character.get('light_cone')
        attributes = light_cone.get('attributes', []) if light_cone else []
        for idx, attribute in enumerate(attributes):
            attr_name = attribute['name']
            attr_value = float(attribute['value'])
            attr_display = f"{attr_value:.3f}"

            icon_file = self.affix_mapping.get(attr_name, None)
            if icon_file:
                icon_path = f"image/buffdata/{icon_file}.png"
                if os.path.exists(icon_path):
                    icon_pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    # 下调图标1px
                    icon_y = (idx * 64) - 4 + 1

                    # 绘制图标：与框线对齐
                    painter.drawPixmap(x_position + 10, icon_y, icon_pixmap)

                    # 设置淡灰色
                    light_gray = QColor(169, 169, 169)
                    painter.setPen(light_gray)

                    # 绘制属性名称，向下移动1像素
                    font = painter.font()
                    font.setBold(True)
                    font.setPointSize(10)
                    painter.setFont(font)

                    # 设置属性名称的位置（向下移动1像素）
                    name_x = x_position + 80
                    name_y = (idx * 64) + (64 + self.fontMetrics().height()) // 2 + 1
                    attr_abbr = self.affix_mapping.get(attr_name, attr_name)
                    painter.drawText(QRect(name_x, (idx * 64) + 1, 150, 64), Qt.AlignVCenter | Qt.AlignLeft, attr_abbr)

                    # 计算数字的宽度并调整位置
                    font.setBold(True)
                    font.setPointSize(11)
                    painter.setFont(font)
                    int_width = self.fontMetrics().width(str(int(attr_value)))

                    # 设置小数部分的颜色和字体
                    darker_gray = QColor(105, 105, 105)
                    decimal_font = QFont(font)
                    decimal_font.setPointSize(8)

                    decimal_width = QFontMetrics(decimal_font).width(f".{attr_display.split('.')[1]}")

                    total_width = int_width + decimal_width
                    text_x = rect.width() - total_width - 19

                    # 将所有数字上移6像素
                    int_y = icon_y + (64 + self.fontMetrics().height()) // 2 - 6

                    # 绘制整数部分，右移一些
                    offset = 2
                    painter.drawText(QPoint(text_x + offset, int_y), str(int(attr_value)))

                    # 绘制小数部分
                    painter.setFont(decimal_font)
                    painter.setPen(darker_gray)
                    painter.drawText(QPoint(text_x + int_width + offset, int_y), f".{attr_display.split('.')[1]}")

        super().paintEvent(event)


class HSRToolApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.current_player = None  
        self.element_colors = load_element_colors()
        self.paths_mapping = load_paths_mapping()
        self.detail_windows = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("HSR Toolkit")
        self.setWindowIcon(QIcon("image/gui/icon.ico"))
        self.setGeometry(0, 0, 800, 600)
        self.showMaximized()

        layout = QHBoxLayout(self)

        self.left_frame = QFrame()
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignTop)

        self.add_player_button = QPushButton("添加玩家数据")
        self.add_player_button.setIcon(QIcon("image/gui/add.svg"))
        self.add_player_button.setIconSize(QSize(24, 24))
        self.add_player_button.setFixedWidth(600)
        self.add_player_button.setStyleSheet(""" 
            QPushButton {
                border: 2px solid black; 
                border-radius: 10px; 
                color: gray; 
                background-color: white; 
                padding: 8px;
                font-weight: bold; 
            }
            QPushButton:hover {
                background-color: lightblue;
                color: black;
            }
        """)
        self.add_player_button.setToolTip("点击添加玩家数据")
        self.add_player_button.clicked.connect(self.prompt_for_uid)
        self.left_layout.addWidget(self.add_player_button, alignment=Qt.AlignTop)

        self.player_buttons_frame = QVBoxLayout()
        self.player_buttons_frame.setAlignment(Qt.AlignTop)
        self.left_layout.addLayout(self.player_buttons_frame)

        self.cmd_button = QPushButton()
        self.gold_ticket_button = QPushButton()
        self.silver_ticket_button = QPushButton()

        cmd_pixmap = QPixmap("image/gui/cmd.png").scaled(80, 80, Qt.KeepAspectRatio)
        gold_ticket_pixmap = QPixmap("image/gui/GoldTicket.png").scaled(80, 80, Qt.KeepAspectRatio)
        silver_ticket_pixmap = QPixmap("image/gui/SilverTicket.png").scaled(80, 80, Qt.KeepAspectRatio)

        self.cmd_button.setIcon(QIcon(cmd_pixmap))
        self.cmd_button.setIconSize(cmd_pixmap.size())
        self.cmd_button.setFixedSize(80, 80)

        self.gold_ticket_button.setIcon(QIcon(gold_ticket_pixmap))
        self.gold_ticket_button.setIconSize(gold_ticket_pixmap.size())
        self.gold_ticket_button.setFixedSize(80, 80)

        self.silver_ticket_button.setIcon(QIcon(silver_ticket_pixmap))
        self.silver_ticket_button.setIconSize(silver_ticket_pixmap.size())
        self.silver_ticket_button.setFixedSize(80, 80)

        self.cmd_button.clicked.connect(self.open_cmd)
        self.gold_ticket_button.clicked.connect(self.open_gold_ticket_simulator)
        self.silver_ticket_button.clicked.connect(self.open_silver_ticket_simulator)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.cmd_button)
        bottom_layout.addWidget(self.gold_ticket_button)
        bottom_layout.addWidget(self.silver_ticket_button)

        self.stellar_jade_button = QPushButton()
        stellar_jade_pixmap = QPixmap("image/gui/stellarjade.png").scaled(80, 80, Qt.KeepAspectRatio)
        self.stellar_jade_button.setIcon(QIcon(stellar_jade_pixmap))
        self.stellar_jade_button.setIconSize(stellar_jade_pixmap.size())
        self.stellar_jade_button.setFixedSize(80, 80)
        self.stellar_jade_button.clicked.connect(self.open_stellar_jade_website)

        bottom_layout.addWidget(self.stellar_jade_button)

        self.left_layout.addStretch()
        self.left_layout.addLayout(bottom_layout)

        self.left_frame.setLayout(self.left_layout)

        layout.addWidget(self.left_frame, stretch=22)

        self.right_frame = QFrame()
        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignTop)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_widget)
        self.right_layout.addWidget(self.scroll_area)

        self.right_frame.setLayout(self.right_layout)

        layout.addWidget(self.right_frame, stretch=78)

        self.setLayout(layout)

        font_path = "fonts/SDK_SC_Web65.ttf"
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            QApplication.setFont(QFont(font_family))

        self.load_player_list()

    def load_player_list(self):
        for i in reversed(range(self.player_buttons_frame.count())):
            widget = self.player_buttons_frame.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if os.path.exists(SAVE_DIR):
            for uid in os.listdir(SAVE_DIR):
                player_dir = os.path.join(SAVE_DIR, uid)
                if os.path.isdir(player_dir):
                    with open(os.path.join(player_dir, "player_data.json"), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        player_name = data['player']['nickname']
                        player_level = data['player']['level']

                        player_widget = QFrame()
                        player_layout = QHBoxLayout(player_widget)

                        player_button = QPushButton(f"{player_name} Lv.{player_level}")
                        player_button.setFixedWidth(350)
                        player_button.setFixedHeight(80)
                        player_button.setStyleSheet(""" 
                            QPushButton {
                                border: 1px solid black; 
                                border-radius: 10px;
                                padding: 8px; 
                                background-color: white;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: lightgray;
                            }
                        """)

                        view_icon = QIcon("image/gui/open.png")
                        player_button.setIcon(view_icon)
                        player_button.setIconSize(QSize(40, 40))

                        player_button.clicked.connect(lambda _, uid=uid: self.load_player_data(uid))

                        refresh_button = QPushButton()
                        refresh_button.setIcon(QIcon("image/gui/update.png"))
                        refresh_button.setIconSize(QSize(40, 40))
                        refresh_button.setFixedSize(60, 60)
                        refresh_button.setContentsMargins(5, 0, 5, 0)
                        refresh_button.clicked.connect(lambda _, uid=uid: self.refresh_player_data(uid))

                        refresh_button.setStyleSheet(""" 
                            QPushButton {
                                border: none; 
                                background-color: transparent;
                                padding: 0px;
                            }
                            QPushButton:hover {
                                background-color: rgba(0, 0, 255, 0.3);
                            }
                        """)

                        delete_button = QPushButton()
                        delete_button.setIcon(QIcon("image/gui/delete.png"))
                        delete_button.setIconSize(QSize(40, 40))
                        delete_button.setFixedSize(60, 60)
                        delete_button.setContentsMargins(5, 0, 5, 0)

                        delete_button.setStyleSheet(""" 
                            QPushButton {
                                border: none; 
                                background-color: transparent;
                                padding: 0px;
                            }
                            QPushButton:hover {
                                background-color: rgba(255, 0, 0, 0.3);
                            }
                        """)

                        delete_button.clicked.connect(lambda _, uid=uid: self.delete_player_data(uid))

                        player_layout.addWidget(player_button)
                        player_layout.addWidget(refresh_button)
                        player_layout.addWidget(delete_button)

                        self.player_buttons_frame.addWidget(player_widget)

    def load_player_data(self, uid):
        player_dir = os.path.join(SAVE_DIR, uid)
        if os.path.exists(player_dir):
            self.current_data = []
            for file_name in os.listdir(player_dir):
                if file_name.endswith('.pkl'):
                    with open(os.path.join(player_dir, file_name), 'rb') as f:
                        character_data = pickle.load(f)
                        self.current_data.append(character_data)

            with open(os.path.join(player_dir, "player_data.json"), 'r', encoding='utf-8') as f:
                self.current_player = json.load(f)['player']
            
            self.display_player_data(self.current_data)

    def refresh_player_data(self, uid):
        self.fetch_data(uid)
        self.load_player_data(uid)

    def clear_right_layout(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    while sub_layout.count():
                        sub_item = sub_layout.takeAt(0)
                        sub_widget = sub_item.widget()
                        if sub_widget:
                            sub_widget.deleteLater()
                    sub_layout.deleteLater()

    def delete_player_data(self, uid):
        player_dir = os.path.join(SAVE_DIR, uid)
        if os.path.exists(player_dir):
            import shutil
            shutil.rmtree(player_dir)
            self.load_player_list()

    def prompt_for_uid(self):
        uid, ok = QInputDialog.getText(self, "输入 UID", "请输入玩家 UID：")
        if ok and uid:
            self.fetch_data(uid.strip())

    def fetch_data(self, uid):
        if len(uid) != 9 or not uid.isdigit() or uid.startswith('0'):
            QMessageBox.critical(self, "Invalid UID", "<b>UID必须是9位数字且不能以 '0' 开头。请重试。</b>")
            return

        url = f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=cn"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            self.save_data(uid, data)
            self.load_player_list()
        except requests.RequestException:
            QMessageBox.critical(self, "Fetch Failed", "<b>无法获取数据，请检查UID或网络连接。</b>")

    def save_data(self, uid, data):
        player_dir = os.path.join(SAVE_DIR, uid)
        os.makedirs(player_dir, exist_ok=True)

        for character in data['characters']:
            char_file_path = os.path.join(player_dir, f"{character['id']}.pkl")
            with open(char_file_path, 'wb') as f:
                pickle.dump(character, f)

        with open(os.path.join(player_dir, "player_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f)

        software_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        software_file_path = os.path.join(player_dir, "software.json")
        with open(software_file_path, "w", encoding='utf-8') as f:
            json.dump(software_data, f)

    def load_software_data(self, uid):
        software_file_path = os.path.join(SAVE_DIR, uid, "software.json")
        if os.path.exists(software_file_path):
            with open(software_file_path, 'r', encoding='utf-8') as f:
                software_data = json.load(f)
                return software_data.get('last_updated', '未更新')
        return '未更新'

    def display_player_data(self, characters):
        self.clear_right_layout()

        if self.current_player:
            last_updated_time = self.load_software_data(self.current_player['uid'])
            player_info = QLabel(f"<b style='font-size:48px;'>{self.current_player['nickname']}</b><br>"
                                 f"<b style='font-size:26px; font-weight:bold;'>UID:</b> "
                                 f"<b style='font-size:35px; font-weight:bold;'>{self.current_player['uid']}</b><br>"
                                 f"<b style='font-size:26px; font-weight:bold;'>上次刷新时间:</b> "
                                 f"<b style='font-size:26px; font-weight:bold;'>{last_updated_time}</b><br><br>")
            self.scroll_layout.addWidget(player_info)

        grid_layout = QGridLayout()
        spacing = 20
        grid_layout.setSpacing(spacing)

        button_width = 280
        image_width = 280
        image_height = 384

        available_width = self.scroll_area.width() - (spacing * 2)
        buttons_per_row = max(1, available_width // (button_width + spacing))

        for index, character in enumerate(characters):
            char_button = QPushButton()
            char_pixmap = QPixmap(f"image/avataricon/{character['id']}.png").scaled(image_width, image_height, Qt.KeepAspectRatio)
            char_button.setIcon(QIcon(char_pixmap))
            char_button.setIconSize(QSize(image_width, image_height))
            char_button.setFixedSize(image_width, image_height)

            element = character['element']['name']
            border_color = self.element_colors.get(element, '#000000')

            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(border_color))
            shadow.setOffset(0, 0)

            char_button.setGraphicsEffect(shadow)
            char_button.setStyleSheet(f"""
                QPushButton {{
                    border: 5px solid {border_color};
                    border-radius: 15px;
                    background-color: transparent;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                }}
            """)

            char_button.clicked.connect(lambda _, char=character: self.show_character_details(char))

            row = index // buttons_per_row
            column = index % buttons_per_row
            grid_layout.addWidget(char_button, row, column)

        self.scroll_layout.addLayout(grid_layout)

    def show_character_details(self, character):
        detail_window = CharacterDetailWindow(character, self.element_colors, self.paths_mapping)
        self.detail_windows.append(detail_window)
        detail_window.show()

    def open_cmd(self):
        os.system("start cmd")

    def open_gold_ticket_simulator(self):
        self.gold_window = GoldTicketWindow()
        self.gold_window.show()

    def open_silver_ticket_simulator(self):
        self.silver_window = SilverTicketWindow()
        self.silver_window.show()

    def open_stellar_jade_website(self):
        reply = QMessageBox.question(self, "即将打开第三方抽卡模拟网站", 
                                     "本网站和工具箱作者无关，是否确定要打开网站？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            webbrowser.open("https://hsr.wishsimulator.app")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_data:
            self.display_player_data(self.current_data)

class GoldTicketWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("期望计算")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.role_count_input = QLineEdit(self)
        self.role_count_input.setPlaceholderText("你想要多少限定角色？")
        layout.addWidget(self.role_count_input)

        self.weapon_count_input = QLineEdit(self)
        self.weapon_count_input.setPlaceholderText("你想要多少限定光锥？")
        layout.addWidget(self.weapon_count_input)

        self.simulate_button = QPushButton("开始模拟", self)
        self.simulate_button.clicked.connect(self.simulate)
        layout.addWidget(self.simulate_button)

        self.result_display = QTextEdit(self)
        self.result_display.setPlaceholderText("模拟结果")
        layout.addWidget(self.result_display)

        self.setLayout(layout)

    def simulate(self):
        role_count = self.role_count_input.text().strip()
        weapon_count = self.weapon_count_input.text().strip()

        if not all(x.isdigit() for x in [role_count, weapon_count]):
            QMessageBox.critical(self, "输入无效", "请确保所有输入都是有效数字。")
            return

        command = (f"expansions\\ratecalc.exe -average {role_count} {weapon_count} ")

        try:
            output = "期望抽数 " + subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
            self.result_display.setPlainText(output)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "调用失败", f"错误信息:\n{e.output}")

class SilverTicketWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("概率计算")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.role_count_input = QLineEdit(self)
        self.role_count_input.setPlaceholderText("你要抽多少限定角色?")
        layout.addWidget(self.role_count_input)

        self.weapon_count_input = QLineEdit(self)
        self.weapon_count_input.setPlaceholderText("你要抽多少限定光锥?")
        layout.addWidget(self.weapon_count_input)

        self.items_input = QLineEdit(self)
        self.items_input.setPlaceholderText("你还有多少抽?(需要折合你的星琼数)")
        layout.addWidget(self.items_input)

        self.initial_role_pulls_input = QLineEdit(self)
        self.initial_role_pulls_input.setPlaceholderText("角色池已垫抽数")
        layout.addWidget(self.initial_role_pulls_input)

        self.initial_weapon_pulls_input = QLineEdit(self)
        self.initial_weapon_pulls_input.setPlaceholderText("光锥池已垫抽数")
        layout.addWidget(self.initial_weapon_pulls_input)

        self.major_pity_role_input = QLineEdit(self)
        self.major_pity_role_input.setPlaceholderText("角色池大保底 (1=是, 0=否)")
        layout.addWidget(self.major_pity_role_input)

        self.major_pity_weapon_input = QLineEdit(self)
        self.major_pity_weapon_input.setPlaceholderText("武器池大保底 (1=是, 0=否)")
        layout.addWidget(self.major_pity_weapon_input)

        self.simulate_button = QPushButton("开始模拟", self)
        self.simulate_button.clicked.connect(self.simulate)
        layout.addWidget(self.simulate_button)

        self.result_display = QTextEdit(self)
        self.result_display.setPlaceholderText("模拟结果")
        layout.addWidget(self.result_display)

        self.setLayout(layout)

    def simulate(self):
        role_count = self.role_count_input.text().strip()
        weapon_count = self.weapon_count_input.text().strip()
        items = self.items_input.text().strip()
        initial_role_pulls = self.initial_role_pulls_input.text().strip()
        initial_weapon_pulls = self.initial_weapon_pulls_input.text().strip()
        major_pity_role = self.major_pity_role_input.text().strip()
        major_pity_weapon = self.major_pity_weapon_input.text().strip()

        if (not all(x.isdigit() for x in [role_count, weapon_count, items, 
                                            initial_role_pulls, initial_weapon_pulls]) or 
            major_pity_role not in ["0", "1"] or major_pity_weapon not in ["0", "1"]):
            QMessageBox.critical(self, "输入无效", "请确保所有输入都是有效数字。")
            return

        command = (f"expansions\\ratecalc.exe -simulate {role_count} {weapon_count} {items} "
                   f"{initial_role_pulls} {initial_weapon_pulls} {major_pity_role} {major_pity_weapon}")

        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
            self.result_display.setPlainText(output)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "调用失败", f"错误信息:\n{e.output}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("image/gui/icon.ico"))
    window = HSRToolApp()
    window.show()
    sys.exit(app.exec_())