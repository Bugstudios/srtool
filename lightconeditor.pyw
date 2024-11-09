import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog
)
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor

class LightConeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Light Cone Editor")
        self.setGeometry(300, 300, 800, 800)  # Adjust height to accommodate more fields
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Light Cone ID input
        id_layout = QHBoxLayout()
        id_label = QLabel("光锥ID:")
        self.id_input = QLineEdit()
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)

        # Star level input
        star_level_layout = QHBoxLayout()
        star_level_label = QLabel("光锥星级:")
        self.star_level_input = QLineEdit()
        star_level_layout.addWidget(star_level_label)
        star_level_layout.addWidget(self.star_level_input)
        layout.addLayout(star_level_layout)

        # Skill name input
        skill_name_layout = QHBoxLayout()
        skill_name_label = QLabel("技能名称:")
        self.skill_name_input = QLineEdit()
        skill_name_layout.addWidget(skill_name_label)
        skill_name_layout.addWidget(self.skill_name_input)
        layout.addLayout(skill_name_layout)

        # Combined skill description input
        combined_skill_layout = QHBoxLayout()
        combined_skill_label = QLabel("技能描述（带标记）:")
        self.combined_skill_input = QTextEdit()
        combined_skill_layout.addWidget(combined_skill_label)
        combined_skill_layout.addWidget(self.combined_skill_input)
        layout.addLayout(combined_skill_layout)

        # Connect the text change signal for highlighting
        self.combined_skill_input.textChanged.connect(self.highlight_combined_skill_text)

        # Description of the light cone
        light_cone_desc_layout = QHBoxLayout()
        light_cone_desc_label = QLabel("光锥描述:")
        self.light_cone_desc_input = QTextEdit()
        light_cone_desc_layout.addWidget(light_cone_desc_label)
        light_cone_desc_layout.addWidget(self.light_cone_desc_input)
        layout.addLayout(light_cone_desc_layout)

        # Attributes inputs: Basic
        self.basic_attributes = {}
        basic_attrs_layout = QHBoxLayout()
        for attr in ["生命值", "攻击力", "防御力"]:
            label = QLabel(f"基础{attr}:")
            input_field = QLineEdit()
            self.basic_attributes[attr] = input_field
            basic_attrs_layout.addWidget(label)
            basic_attrs_layout.addWidget(input_field)
        layout.addLayout(basic_attrs_layout)

        # Materials for breakthrough
        self.general_materials = {}
        self.path_materials = {}
        for level in range(1, 4):
            general_mat_layout = QHBoxLayout()
            general_mat_label = QLabel(f"等级 {level} 通用突破材料 ID:")
            general_mat_input = QLineEdit()
            self.general_materials[level] = general_mat_input
            general_mat_layout.addWidget(general_mat_label)
            general_mat_layout.addWidget(general_mat_input)
            layout.addLayout(general_mat_layout)

            path_mat_layout = QHBoxLayout()
            path_mat_label = QLabel(f"等级 {level} 命途突破材料 ID:")
            path_mat_input = QLineEdit()
            self.path_materials[level] = path_mat_input
            path_mat_layout.addWidget(path_mat_label)
            path_mat_layout.addWidget(path_mat_input)
            layout.addLayout(path_mat_layout)

        # Save, load and modify buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        load_button = QPushButton("加载")
        modify_button = QPushButton("修改")

        save_button.clicked.connect(self.save_lightcone)
        load_button.clicked.connect(self.load_lightcone)
        modify_button.clicked.connect(self.modify_lightcone)

        button_layout.addWidget(save_button)
        button_layout.addWidget(load_button)
        button_layout.addWidget(modify_button)
        layout.addLayout(button_layout)

    def highlight_combined_skill_text(self):
        text = self.combined_skill_input.toPlainText()
        cursor = self.combined_skill_input.textCursor()
        original_position = cursor.position()

        # Check for format: [[1, 2, 3, 4, 5]] and highlight
        start_marker = '[['
        end_marker = ']]'

        cursor.movePosition(QTextCursor.Start)
        plain_format = QTextCharFormat()
        cursor.setCharFormat(plain_format)

        self.combined_skill_input.blockSignals(True)

        start = text.find(start_marker)
        while start != -1:
            end = text.find(end_marker, start)
            if end != -1:
                actual_start = start + len(start_marker)
                actual_end = end

                numbers = text[actual_start:actual_end].split(',')
                if len(numbers) == 5 and all(num.strip().isdigit() for num in numbers):
                    # Format the text between the markers
                    cursor.setPosition(actual_start)
                    cursor.setPosition(actual_end, QTextCursor.KeepAnchor)
                    color_format = QTextCharFormat()
                    color_format.setForeground(QColor("orange"))
                    cursor.setCharFormat(color_format)

                start = text.find(start_marker, end + len(end_marker))
            else:
                break

        self.combined_skill_input.blockSignals(False)

        if original_position <= len(text):
            cursor.setPosition(original_position)
        else:
            cursor.setPosition(len(text))
        self.combined_skill_input.setTextCursor(cursor)

    def save_lightcone(self):
        lightcone_data = {
            "light_cone_id": self.id_input.text(),
            "star_level": self.star_level_input.text(),
            "skill_name": self.skill_name_input.text(),
            "combined_skill_description": self.combined_skill_input.toPlainText(),
            "light_cone_description": self.light_cone_desc_input.toPlainText(),
            "general_materials": {level: self.general_materials[level].text() for level in range(1, 4)},
            "path_materials": {level: self.path_materials[level].text() for level in range(1, 4)},
            "basic_attributes": {attr: self.basic_attributes[attr].text() for attr in ["生命值", "攻击力", "防御力"]}
        }

        lightcone_id = self.id_input.text().strip().replace(" ", "_").lower()
        if not lightcone_id:
            return
        file_path = os.path.join("config", "lightcone", f"{lightcone_id}.json")

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(lightcone_data, file, ensure_ascii=False, indent=4)

    def load_lightcone(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Light Cone JSON", os.path.join("config", "lightcone"), "JSON Files (*.json)", options=options)
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                lightcone_data = json.load(file)

            self.id_input.setText(os.path.basename(file_path).replace(".json", ""))
            self.star_level_input.setText(lightcone_data.get("star_level", ""))
            self.skill_name_input.setText(lightcone_data.get("skill_name", ""))
            self.combined_skill_input.setPlainText(lightcone_data.get("combined_skill_description", ""))
            self.highlight_combined_skill_text()
            self.light_cone_desc_input.setPlainText(lightcone_data.get("light_cone_description", ""))
            for level in range(1, 4):
                self.general_materials[level].setText(lightcone_data.get("general_materials", {}).get(level, ""))
                self.path_materials[level].setText(lightcone_data.get("path_materials", {}).get(level, ""))

            # Load attributes
            for attr in ["生命值", "攻击力", "防御力"]:
                self.basic_attributes[attr].setText(lightcone_data.get("basic_attributes", {}).get(attr, ""))

    def modify_lightcone(self):
        # Placeholder: Implement modification logic if desired
        pass

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    editor = LightConeEditor()
    editor.show()
    sys.exit(app.exec_())