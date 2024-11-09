import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QLineEdit, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QSpinBox

class RelicScoringEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('遗器评分编辑器')
        self.setGeometry(200, 200, 1200, 1000)  # 增加窗口高度

        # 布局
        main_layout = QVBoxLayout()

        # 角色和流派输入
        form_layout = QHBoxLayout()
        self.character_id_input = QLineEdit()
        self.build_name_input = QLineEdit()
        form_layout.addWidget(QLabel('角色ID：'))
        form_layout.addWidget(self.character_id_input)
        form_layout.addWidget(QLabel('流派名称：'))
        form_layout.addWidget(self.build_name_input)
        main_layout.addLayout(form_layout)

        # 套装加成配置
        self.set_bonus_table = QTableWidget(0, 3)
        self.set_bonus_table.setHorizontalHeaderLabels(['套装ID', '件数', '分数'])
        self.set_bonus_table.setMaximumHeight(150)  # 调整高度
        set_bonus_add_button = QPushButton('添加套装加成')
        set_bonus_add_button.clicked.connect(self.add_set_bonus_row)
        
        main_layout.addWidget(QLabel('套装加成配置'))
        main_layout.addWidget(self.set_bonus_table)
        main_layout.addWidget(set_bonus_add_button)

        # 词条权重配置（模块2）
        self.substat_weights_table = QTableWidget(0, 2)
        self.substat_weights_table.setHorizontalHeaderLabels(['词条', '权重'])
        self.substat_weights_table.setMaximumHeight(200)  # 调整高度
        substat_weight_add_button = QPushButton('添加词条权重')
        substat_weight_add_button.clicked.connect(self.add_substat_weight_row)
        
        main_layout.addWidget(QLabel('词条权重配置'))
        main_layout.addWidget(self.substat_weights_table)
        main_layout.addWidget(substat_weight_add_button)

        # 主词条计分配置（模块3）
        self.main_stat_score_table = QTableWidget(0, 3)
        self.main_stat_score_table.setHorizontalHeaderLabels(['遗器类型', '主词条', '分数'])
        self.main_stat_score_table.setMaximumHeight(200)  # 调整高度
        main_stat_add_button = QPushButton('添加主词条计分')
        main_stat_add_button.clicked.connect(self.add_main_stat_score_row)
        
        main_layout.addWidget(QLabel('主词条计分配置'))
        main_layout.addWidget(self.main_stat_score_table)
        main_layout.addWidget(main_stat_add_button)

        # 额外条件配置（模块4）
        self.extra_conditions_table = QTableWidget(0, 4)
        self.extra_conditions_table.setHorizontalHeaderLabels(['词条', '条件', '数值', '调整分数'])
        self.extra_conditions_table.setMaximumHeight(200)  # 调整高度
        extra_condition_add_button = QPushButton('添加条件')
        extra_condition_add_button.clicked.connect(self.add_extra_condition_row)
        
        main_layout.addWidget(QLabel('额外条件配置'))
        main_layout.addWidget(self.extra_conditions_table)
        main_layout.addWidget(extra_condition_add_button)

        # 等级评分标识（模块5，改为 'ACE'）
        self.grade_inputs = {}
        grade_layout = QHBoxLayout()
        grades = ['D', 'C', 'B', 'A', 'A+', 'S', 'SS', 'SSS', 'ACE']
        for grade in grades:
            label = QLabel(grade)
            input_box = QLineEdit()
            input_box.setMaximumWidth(60)
            grade_layout.addWidget(label)
            grade_layout.addWidget(input_box)
            self.grade_inputs[grade] = input_box
        
        main_layout.addWidget(QLabel('等级评分标识'))
        main_layout.addLayout(grade_layout)

        # 生成JSON配置
        generate_button = QPushButton('生成JSON')
        generate_button.clicked.connect(self.generate_json)
        
        # 导入JSON并填充表格
        import_button = QPushButton('导入JSON')
        import_button.clicked.connect(self.import_json)

        # 自然语言描述输出
        describe_button = QPushButton('描述JSON')
        describe_button.clicked.connect(self.describe_json)

        main_layout.addWidget(generate_button)
        main_layout.addWidget(import_button)
        main_layout.addWidget(describe_button)
        
        self.setLayout(main_layout)

    def add_set_bonus_row(self):
        row_position = self.set_bonus_table.rowCount()
        self.set_bonus_table.insertRow(row_position)
        set_id_item = QTableWidgetItem()
        pieces_spinbox = QSpinBox()
        score_spinbox = QSpinBox()
        self.set_bonus_table.setItem(row_position, 0, set_id_item)
        self.set_bonus_table.setCellWidget(row_position, 1, pieces_spinbox)
        self.set_bonus_table.setCellWidget(row_position, 2, score_spinbox)

    def add_substat_weight_row(self):
        row_position = self.substat_weights_table.rowCount()
        self.substat_weights_table.insertRow(row_position)
        substat_combo = QComboBox()
        substat_combo.addItems(self.get_substat_options())
        self.substat_weights_table.setCellWidget(row_position, 0, substat_combo)
        self.substat_weights_table.setItem(row_position, 1, QTableWidgetItem())

    def add_main_stat_score_row(self):
        row_position = self.main_stat_score_table.rowCount()
        self.main_stat_score_table.insertRow(row_position)
        type_combo = QComboBox()
        type_combo.addItems([str(i) for i in range(1, 7)])
        stat_combo = QComboBox()
        stat_combo.addItems(self.get_main_stat_options())
        score_item = QTableWidgetItem()
        self.main_stat_score_table.setCellWidget(row_position, 0, type_combo)
        self.main_stat_score_table.setCellWidget(row_position, 1, stat_combo)
        self.main_stat_score_table.setItem(row_position, 2, score_item)

    def add_extra_condition_row(self):
        row_position = self.extra_conditions_table.rowCount()
        self.extra_conditions_table.insertRow(row_position)
        stat_combo = QComboBox()
        stat_combo.addItems(self.get_substat_options())
        condition_combo = QComboBox()
        condition_combo.addItems(['大于', '小于'])
        self.extra_conditions_table.setCellWidget(row_position, 0, stat_combo)
        self.extra_conditions_table.setCellWidget(row_position, 1, condition_combo)
        self.extra_conditions_table.setItem(row_position, 2, QTableWidgetItem())
        self.extra_conditions_table.setItem(row_position, 3, QTableWidgetItem())

    def get_substat_options(self):
        return [
            '数值生命值', '数值攻击力', '数值防御力',
            '击破特攻', '效果命中', '效果抵抗',
            '暴击率', '暴击伤害', '速度', '能量恢复效率'
        ]

    def get_main_stat_options(self):
        return [
            '生命值', '攻击力', '防御力',
            '击破特攻', '效果命中', '效果抵抗',
            '暴击率', '暴击伤害', '速度', '能量恢复效率',
            '雷属性伤害提高', '冰属性伤害提高',
            '物理属性伤害提高', '虚数属性伤害提高',
            '风属性伤害提高', '量子属性伤害提高', '火属性伤害提高'
        ]

    def generate_json(self):
        character_id = self.character_id_input.text().strip()
        build_name = self.build_name_input.text().strip()
        
        if not character_id or not build_name:
            QMessageBox.warning(self, "输入错误", "角色ID和流派名称是必需的。")
            return

        # 收集套装加分数据
        set_bonus = []
        for row in range(self.set_bonus_table.rowCount()):
            set_id_item = self.set_bonus_table.item(row, 0)
            pieces = self.set_bonus_table.cellWidget(row, 1).value()
            score = self.set_bonus_table.cellWidget(row, 2).value()
            if set_id_item and set_id_item.text():
                set_bonus.append({
                    "套装ID": set_id_item.text().strip(),
                    "件数": pieces,
                    "分数": score
                })
        
        # 收集词条权重数据
        substat_weights = {}
        for row in range(self.substat_weights_table.rowCount()):
            substat_combo = self.substat_weights_table.cellWidget(row, 0)
            weight_item = self.substat_weights_table.item(row, 1)
            if substat_combo and weight_item:
                substat = substat_combo.currentText()
                weight = float(weight_item.text()) if weight_item.text() else 0
                substat_weights[substat] = weight
        
        # 收集主词条计分
        main_stat_score = []
        for row in range(self.main_stat_score_table.rowCount()):
            type_combo = self.main_stat_score_table.cellWidget(row, 0)
            stat_combo = self.main_stat_score_table.cellWidget(row, 1)
            score_item = self.main_stat_score_table.item(row, 2)
            if type_combo and stat_combo and score_item:
                main_stat_score.append({
                    "类型": type_combo.currentText(),
                    "主词条": stat_combo.currentText(),
                    "分数": float(score_item.text()) if score_item.text() else 0
                })

        # 收集额外条件
        extra_conditions = []
        for row in range(self.extra_conditions_table.rowCount()):
            stat_combo = self.extra_conditions_table.cellWidget(row, 0)
            condition_combo = self.extra_conditions_table.cellWidget(row, 1)
            value_item = self.extra_conditions_table.item(row, 2)
            score_adjustment_item = self.extra_conditions_table.item(row, 3)
            if stat_combo and condition_combo and value_item and score_adjustment_item:
                extra_conditions.append({
                    "词条": stat_combo.currentText(),
                    "条件": condition_combo.currentText(),
                    "数值": float(value_item.text()) if value_item.text() else 0,
                    "调整分数": float(score_adjustment_item.text()) if score_adjustment_item.text() else 0
                })

        # 收集等级评分标识
        grade_thresholds = {grade: float(input_box.text()) if input_box.text() else 0 
                            for grade, input_box in self.grade_inputs.items()}

        # 创建JSON结构
        scoring_rules = {
            "套装加成": set_bonus,
            "词条权重": substat_weights,
            "主词条计分": main_stat_score,
            "额外条件": extra_conditions,
            "等级评分标识": grade_thresholds
        }

        # 保存JSON到文件
        directory = os.path.join('config', 'relicrule', character_id)
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f'{build_name}.json')

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(scoring_rules, f, ensure_ascii=False, indent=4)
        
        QMessageBox.information(self, "成功", f"JSON文件已生成: {file_path}")

    def import_json(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, '选择JSON文件', 'config/relicrule', 'JSON文件 (*.json)')

        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                scoring_rules = json.load(f)

            # 填充套装加成配置
            self.set_bonus_table.setRowCount(0)
            for bonus in scoring_rules.get('套装加成', []):
                self.add_set_bonus_row()
                row_pos = self.set_bonus_table.rowCount() - 1
                self.set_bonus_table.setItem(row_pos, 0, QTableWidgetItem(bonus['套装ID']))
                self.set_bonus_table.cellWidget(row_pos, 1).setValue(bonus['件数'])
                self.set_bonus_table.cellWidget(row_pos, 2).setValue(bonus['分数'])

            # 填充词条权重配置
            self.substat_weights_table.setRowCount(0)
            for substat, weight in scoring_rules.get('词条权重', {}).items():
                self.add_substat_weight_row()
                row_pos = self.substat_weights_table.rowCount() - 1
                combo = self.substat_weights_table.cellWidget(row_pos, 0)
                combo.setCurrentText(substat)
                self.substat_weights_table.setItem(row_pos, 1, QTableWidgetItem(str(weight)))

            # 填充主词条计分配置
            self.main_stat_score_table.setRowCount(0)
            for score in scoring_rules.get('主词条计分', []):
                self.add_main_stat_score_row()
                row_pos = self.main_stat_score_table.rowCount() - 1
                type_combo = self.main_stat_score_table.cellWidget(row_pos, 0)
                type_combo.setCurrentText(score['类型'])
                stat_combo = self.main_stat_score_table.cellWidget(row_pos, 1)
                stat_combo.setCurrentText(score['主词条'])
                self.main_stat_score_table.setItem(row_pos, 2, QTableWidgetItem(str(score['分数'])))

            # 填充额外条件配置
            self.extra_conditions_table.setRowCount(0)
            for condition in scoring_rules.get('额外条件', []):
                self.add_extra_condition_row()
                row_pos = self.extra_conditions_table.rowCount() - 1
                stat_combo = self.extra_conditions_table.cellWidget(row_pos, 0)
                stat_combo.setCurrentText(condition['词条'])
                condition_combo = self.extra_conditions_table.cellWidget(row_pos, 1)
                condition_combo.setCurrentText(condition['条件'])
                self.extra_conditions_table.setItem(row_pos, 2, QTableWidgetItem(str(condition['数值'])))
                self.extra_conditions_table.setItem(row_pos, 3, QTableWidgetItem(str(condition['调整分数'])))

            # 填充等级评分标识
            for grade, threshold in scoring_rules.get('等级评分标识', {}).items():
                if grade in self.grade_inputs:
                    self.grade_inputs[grade].setText(str(threshold))

    def describe_json(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, '打开JSON文件', 'config/relicrule', 'JSON文件 (*.json)')

        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                scoring_rules = json.load(f)

            description = self.generate_human_readable_description(scoring_rules)
            QMessageBox.information(self, "JSON描述", description)

    def generate_human_readable_description(self, scoring_rules):
        lines = []
        lines.append("**套装加成配置**")
        for bonus in scoring_rules.get('套装加成', []):
            lines.append(f"- 套装ID: {bonus['套装ID']}, 件数: {bonus['件数']}, 分数: {bonus['分数']}")
        
        lines.append("**词条权重配置**")
        for key, value in scoring_rules.get('词条权重', {}).items():
            lines.append(f"- {key}: {value}")

        lines.append("**主词条计分配置**")
        for item in scoring_rules.get('主词条计分', []):
            lines.append(f"- 类型: {item['类型']}, 主词条: {item['主词条']}, 分数: {item['分数']}")

        lines.append("**额外条件配置**")
        for condition in scoring_rules.get('额外条件', []):
            lines.append(f"- 词条: {condition['词条']} {condition['条件']} {condition['数值']}, 调整分数: {condition['调整分数']}")

        lines.append("**等级评分标识**")
        for grade, threshold in scoring_rules.get('等级评分标识', {}).items():
            lines.append(f"- {grade}: {threshold}")

        return "\n".join(lines)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = RelicScoringEditor()
    editor.show()
    sys.exit(app.exec_())