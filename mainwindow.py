import sys
from pda import PDA
from graphviz import Digraph
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
import tempfile
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


# Add the PDADialog class before MainWindow class
class PDADialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.states = []
        self.final_states = []
        self.initial_state = None
        self.input_alphabets = []
        self.stack_alphabets = []
        self.stack_tail = None
        self.transitions = []

    def setup_ui(self):
        self.setWindowTitle("Define PDA")
        self.setMinimumSize(600, 400)
        
        self.tabs = QtWidgets.QTabWidget()
        
        # States Tab
        self.states_tab = QtWidgets.QWidget()
        self.setup_states_tab()
        self.tabs.addTab(self.states_tab, "States")
        
        # Alphabets Tab
        self.alphabets_tab = QtWidgets.QWidget()
        self.setup_alphabets_tab()
        self.tabs.addTab(self.alphabets_tab, "Alphabets")
        
        # Transitions Tab
        self.transitions_tab = QtWidgets.QWidget()
        self.setup_transitions_tab()
        self.tabs.addTab(self.transitions_tab, "Transitions")
        
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def setup_states_tab(self):
        layout = QtWidgets.QVBoxLayout()

        # Add State Section
        add_state_layout = QtWidgets.QHBoxLayout()
        self.new_state_input = QtWidgets.QLineEdit()
        self.new_state_input.setPlaceholderText("State name")
        add_state_btn = QtWidgets.QPushButton("Add State")
        add_state_btn.clicked.connect(self.add_state)
        add_state_layout.addWidget(self.new_state_input)
        add_state_layout.addWidget(add_state_btn)

        # States List
        self.states_list = QtWidgets.QListWidget()

        # Initial/Final Selection
        state_controls = QtWidgets.QHBoxLayout()

        # Initialize groups
        self.initial_group = QtWidgets.QGroupBox("Initial State")
        self.final_group = QtWidgets.QGroupBox("Final States")

        # Initialize checkbox list
        self.final_checkboxes = []

        # Initial State
        self.initial_radio_group = QtWidgets.QButtonGroup()
        initial_layout = QtWidgets.QVBoxLayout()
        self.initial_group.setLayout(initial_layout)

        # Final States
        final_layout = QtWidgets.QVBoxLayout()
        self.final_group.setLayout(final_layout)

        state_controls.addWidget(self.initial_group)
        state_controls.addWidget(self.final_group)

        layout.addLayout(add_state_layout)
        layout.addWidget(self.states_list)
        layout.addLayout(state_controls)
        self.states_tab.setLayout(layout)

    def add_state(self):
        state_name = self.new_state_input.text().strip()
        if state_name and state_name not in self.states:
            self.states.append(state_name)
            self.states_list.addItem(state_name)

            # Fix: Create radio button with proper parent
            radio = QtWidgets.QRadioButton(state_name, self.initial_group)
            self.initial_radio_group.addButton(radio)
            self.initial_group.layout().addWidget(radio)

            # Fix: Create checkbox with proper parent
            checkbox = QtWidgets.QCheckBox(state_name, self.final_group)
            self.final_checkboxes.append(checkbox)
            self.final_group.layout().addWidget(checkbox)

            self.new_state_input.clear()

    def setup_alphabets_tab(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Input Alphabets
        input_group = QtWidgets.QGroupBox("Input Alphabets")
        self.input_alpha_layout = QtWidgets.QHBoxLayout()
        self.input_alpha_input = QtWidgets.QLineEdit()
        self.input_alpha_input.setPlaceholderText("Add input symbol")
        input_add_btn = QtWidgets.QPushButton("Add")
        input_add_btn.clicked.connect(lambda: self.add_alphabet('input'))
        self.input_alpha_layout.addWidget(self.input_alpha_input)
        self.input_alpha_layout.addWidget(input_add_btn)
        input_group.setLayout(self.input_alpha_layout)
        
        # Stack Alphabets
        stack_group = QtWidgets.QGroupBox("Stack Alphabets")
        self.stack_alpha_layout = QtWidgets.QVBoxLayout()
        self.stack_alpha_input = QtWidgets.QLineEdit()
        self.stack_alpha_input.setPlaceholderText("Add stack symbol")
        stack_add_btn = QtWidgets.QPushButton("Add")
        stack_add_btn.clicked.connect(lambda: self.add_alphabet('stack'))
        stack_tail_label = QtWidgets.QLabel("Stack Tail Symbol:")
        self.stack_tail_combo = QtWidgets.QComboBox()
        
        stack_controls = QtWidgets.QHBoxLayout()
        stack_controls.addWidget(self.stack_alpha_input)
        stack_controls.addWidget(stack_add_btn)
        self.stack_alpha_layout.addLayout(stack_controls)
        self.stack_alpha_layout.addWidget(stack_tail_label)
        self.stack_alpha_layout.addWidget(self.stack_tail_combo)
        stack_group.setLayout(self.stack_alpha_layout)
        
        layout.addWidget(input_group)
        layout.addWidget(stack_group)
        self.alphabets_tab.setLayout(layout)

    def add_alphabet(self, alpha_type):
        symbol = self.input_alpha_input.text().strip() if alpha_type == 'input' else self.stack_alpha_input.text().strip()
        if symbol:
            if alpha_type == 'input' and symbol not in self.input_alphabets:
                self.input_alphabets.append(symbol)
                self.input_alpha_input.clear()
            elif alpha_type == 'stack' and symbol not in self.stack_alphabets:
                self.stack_alphabets.append(symbol)
                self.stack_tail_combo.addItem(symbol)
                self.stack_alpha_input.clear()

    def setup_transitions_tab(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Transition Table
        self.transition_table = QtWidgets.QTableWidget()
        self.transition_table.setColumnCount(5)
        self.transition_table.setHorizontalHeaderLabels([
            "Source", "Destination", "Input", "Stack Read", "Stack Write"
        ])
        self.transition_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # Transition Controls
        controls = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("Add Transition")
        add_btn.clicked.connect(self.add_transition_row)
        remove_btn = QtWidgets.QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_transition_row)
        controls.addWidget(add_btn)
        controls.addWidget(remove_btn)
        
        layout.addLayout(controls)
        layout.addWidget(self.transition_table)
        self.transitions_tab.setLayout(layout)

    def add_transition_row(self):
        row = self.transition_table.rowCount()
        self.transition_table.insertRow(row)
        
        source_combo = QtWidgets.QComboBox()
        source_combo.addItems(self.states)
        dest_combo = QtWidgets.QComboBox()
        dest_combo.addItems(self.states)
        input_combo = QtWidgets.QComboBox()
        input_combo.addItems(['λ'] + self.input_alphabets)
        stack_read_combo = QtWidgets.QComboBox()
        stack_read_combo.addItems(['λ'] + self.stack_alphabets)
        stack_write_input = QtWidgets.QLineEdit()
        stack_write_input.setPlaceholderText("λ for empty")
        
        self.transition_table.setCellWidget(row, 0, source_combo)
        self.transition_table.setCellWidget(row, 1, dest_combo)
        self.transition_table.setCellWidget(row, 2, input_combo)
        self.transition_table.setCellWidget(row, 3, stack_read_combo)
        self.transition_table.setCellWidget(row, 4, stack_write_input)

    def remove_transition_row(self):
        current_row = self.transition_table.currentRow()
        if current_row >= 0:
            self.transition_table.removeRow(current_row)

    def validate_and_accept(self):
        # Validate states
        self.initial_state = self.initial_radio_group.checkedButton().text() if self.initial_radio_group.checkedButton() else None
        self.final_states = [cb.text() for cb in self.final_checkboxes if cb.isChecked()]
        
        if not self.initial_state:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select an initial state!")
            return
        if not self.final_states:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select at least one final state!")
            return
        
        # Validate stack tail
        self.stack_tail = self.stack_tail_combo.currentText()
        if not self.stack_tail:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select stack tail symbol!")
            return
        
        # Collect transitions
        self.transitions = []
        for row in range(self.transition_table.rowCount()):
            source = self.transition_table.cellWidget(row, 0).currentText()
            dest = self.transition_table.cellWidget(row, 1).currentText()
            _input = self.transition_table.cellWidget(row, 2).currentText().replace('λ', '')
            stack_read = self.transition_table.cellWidget(row, 3).currentText().replace('λ', '')
            stack_write = self.transition_table.cellWidget(row, 4).text().strip() or 'λ'
            
            self.transitions.append({
                'source': source,
                'destination': dest,
                'input': _input,
                'stack_read': stack_read,
                'stack_write': stack_write
            })
        
        if not self.transitions:
            QtWidgets.QMessageBox.warning(self, "Error", "Please add at least one transition!")
            return
        
        # Generate XML
        self.generate_xml()
        self.accept()

    def generate_xml(self):
        root = Element('Automata', type="PDA")
        
        # Alphabets
        alphabets = SubElement(root, 'Alphabets')
        input_alpha = SubElement(alphabets, 'Input_alphabets', numberOfInputAlphabets=str(len(self.input_alphabets)))
        for a in self.input_alphabets:
            SubElement(input_alpha, 'alphabet', letter=a)
        
        stack_alpha = SubElement(alphabets, 'Stack_alphabets', numberOfStackAlphabets=str(len(self.stack_alphabets)))
        for a in self.stack_alphabets:
            SubElement(stack_alpha, 'alphabet', letter=a)
        SubElement(stack_alpha, 'tail', letter=self.stack_tail)
        
        # States
        states = SubElement(root, 'States', numberOfStates=str(len(self.states)))
        for s in self.states:
            SubElement(states, 'state', name=s, positionX="0", positionY="0")
        SubElement(states, 'initialState', name=self.initial_state)
        final_states = SubElement(states, 'FinalStates', numberOfFinalStates=str(len(self.final_states)))
        for s in self.final_states:
            SubElement(final_states, 'finalState', name=s)
        
        # Transitions
        transitions = SubElement(root, 'Transitions', numberOfTrans=str(len(self.transitions)))
        for i, tr in enumerate(self.transitions, 1):
            SubElement(transitions, 'transition',
                       name=f"tr{i}",
                       source=tr['source'],
                       destination=tr['destination'],
                       input=tr['input'],
                       stackRead=tr['stack_read'],
                       stackWrite=tr['stack_write'])
        
        # Create temporary file
        xml_str = minidom.parseString(tostring(root)).toprettyxml()
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xml')
        self.temp_file.write(xml_str.encode())
        self.temp_file.close()

class MainWindow(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(1200, 800)
        
        
        # Application-wide stylesheet
        main_window.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QMenuBar {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #444;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 5px 15px;
            }
            QMenuBar::item:selected {
                background: #505050;
                border-radius: 3px;
            }
            QMenu {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #444;
                padding: 5px;
            }
            QMenu::item:selected {
                background-color: #505050;
                border-radius: 3px;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLineEdit {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #444;
                padding: 7px;
                border-radius: 3px;
            }
            QListWidget {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 3px;
                alternate-background-color: #3d3d3d;
            }
            QTableWidget {
                background-color: #353535;
                color: #ffffff;
                gridline-color: #444;
                border-radius: 3px;
            }
            QHeaderView::section {
                background-color: #404040;
                color: white;
                border: 1px solid #444;
                padding: 5px;
            }
            QGroupBox {
                color: #4CAF50;
                border: 1px solid #444;
                margin-top: 10px;
                padding-top: 15px;
                border-radius: 4px;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #353535;
                color: white;
                padding: 8px 15px;
                border: 1px solid #444;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #505050;
                border-color: #444;
            }
            QScrollBar:vertical {
                background: #353535;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #505050;
                min-height: 20px;
                border-radius: 6px;
            }
        """)

        # Central Widget Setup
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout.setContentsMargins(20, 20, 20, 20)
        self.horizontalLayout.setSpacing(15)
            
        # A stacked widget to switch between views
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.horizontalLayout.addWidget(self.stacked_widget)
        
        # Welcome/Instruction Screen
        self.welcome_widget = QtWidgets.QWidget()
        welcome_layout = QtWidgets.QVBoxLayout()
        
        # Title label
        title_label = QtWidgets.QLabel("PDA to CFG Converter")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            padding: 20px;
        """)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        welcome_layout.addWidget(title_label)
        
        # instructions
        instructions = [
            "1. Click 'New PDA' to define a new Pushdown Automaton",
            "2. Or 'Open PDA' to load an existing PDA from XML",
            "3. Visualize your PDA in the diagram view",
            "4. Click 'Convert to CFG' to generate equivalent Context-Free Grammar",
            "5. Export the diagram in various formats (SVG, PNG, PDF)"
        ]
        
        for instruction in instructions:
            label = QtWidgets.QLabel(instruction)
            label.setStyleSheet("font-size: 14px; padding: 5px;")
            welcome_layout.addWidget(label)
        
        # Example PDA info
        example_label = QtWidgets.QLabel("\nExample PDA for aⁿbⁿ:")
        example_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-top: 15px;")
        welcome_layout.addWidget(example_label)
        
        example_text = QtWidgets.QTextEdit()
        example_text.setReadOnly(True)
        example_text.setPlainText("""States: q0, q1, q2
    Initial: q0
    Final: q2
    Input Alphabets: a, b
    Stack Alphabets: z, 0
    Stack Tail: z
    Transitions:
    - q0 -> q0: a,z → 0z
    - q0 -> q0: a,0 → 00
    - q0 -> q1: b,0 → λ
    - q1 -> q1: b,0 → λ
    - q1 -> q2: λ,z → z""")
        example_text.setStyleSheet("background: #353535; border: 1px solid #444;")
        welcome_layout.addWidget(example_text)
        
        welcome_layout.addStretch()
        self.welcome_widget.setLayout(welcome_layout)

        # SVG Display Area
        self.visualization_widget = QtWidgets.QWidget()
        vis_layout = QtWidgets.QVBoxLayout(self.visualization_widget)  # Create layout and assign to widget
        self.center_image = QtSvg.QSvgWidget()
        self.center_image.setStyleSheet("""
            background-color: #353535;
            border: 2px solid #444;
            border-radius: 5px;
            padding: 10px;
        """)
        vis_layout.addWidget(self.center_image)
        
        self.stacked_widget.addWidget(self.welcome_widget)
        self.stacked_widget.addWidget(self.visualization_widget)
        self.stacked_widget.setCurrentIndex(0)
        main_window.setCentralWidget(self.central_widget)

        # Menu System Setup
        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1200, 24))
        self.menu_bar.setObjectName("menu_bar")

        # Create menus
        self.menu_file = QtWidgets.QMenu(self.menu_bar)
        self.menu_file.setObjectName("menu_file")
        self.menu_export_as = QtWidgets.QMenu(self.menu_file)
        self.menu_export_as.setObjectName("menu_export_as")
        self.menu_help = QtWidgets.QMenu(self.menu_bar)
        self.menu_help.setObjectName("menu_help")
        self.menu_pda = QtWidgets.QMenu(self.menu_bar)
        self.menu_pda.setObjectName("menu_pda")

        # Create actions
        self.action_new_pda = QtWidgets.QAction(main_window)
        self.action_open_pda = QtWidgets.QAction(main_window)
        self.action_exit = QtWidgets.QAction(main_window)
        self.action_about = QtWidgets.QAction(main_window)
        self.action_gv = QtWidgets.QAction(main_window)
        self.action_pdf = QtWidgets.QAction(main_window)
        self.action_png = QtWidgets.QAction(main_window)
        self.action_svg = QtWidgets.QAction(main_window)
        self.action_convert = QtWidgets.QAction(main_window)

        # Font settings
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        main_window.setFont(font)
        self.menu_bar.setFont(font)
###############################
        # Build Menu Structure
        self.menu_export_as.addAction(self.action_gv)
        self.menu_export_as.addAction(self.action_pdf)
        self.menu_export_as.addAction(self.action_png)
        self.menu_export_as.addAction(self.action_svg)
        
        self.menu_file.addAction(self.action_new_pda)
        self.menu_file.addAction(self.action_open_pda)
        self.menu_file.addAction(self.menu_export_as.menuAction())
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        
        self.menu_help.addAction(self.action_about)
        self.menu_pda.addAction(self.action_convert)

        # Add menus to menu bar
        self.menu_bar.addAction(self.menu_file.menuAction())
        self.menu_bar.addAction(self.menu_pda.menuAction())
        self.menu_bar.addAction(self.menu_help.menuAction())
        main_window.setMenuBar(self.menu_bar)

        # Final setup
        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)
        self.set_menu_state(False)
        
        # Add after the retranslateUi() call in setupUi
        self.action_new_pda.triggered.connect(self.new_pda)
        self.action_open_pda.triggered.connect(self.open_pda)
        self.action_exit.triggered.connect(self.app_exit)
        self.action_convert.triggered.connect(self.convert_to_cfg)
        self.action_gv.triggered.connect(lambda: self.export_as('gv'))
        self.action_pdf.triggered.connect(lambda: self.export_as('pdf'))
        self.action_png.triggered.connect(lambda: self.export_as('png'))
        self.action_svg.triggered.connect(lambda: self.export_as('svg'))
        self.action_about.triggered.connect(self.show_about_dialog)

        self.show_welcome_screen()
        
    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "PDA to CFG"))
        self.menu_file.setTitle(_translate("main_window", "File"))
        self.menu_export_as.setTitle(_translate("main_window", "Export as..."))
        self.menu_help.setTitle(_translate("main_window", "Help"))
        self.menu_pda.setTitle(_translate("main_window", "PDA"))
        
        self.action_new_pda.setText(_translate("main_window", "New PDA"))
        self.action_new_pda.setShortcut(_translate("main_window", "Ctrl+N"))
        self.action_open_pda.setText(_translate("main_window", "Open PDA"))
        self.action_open_pda.setShortcut(_translate("main_window", "Ctrl+O"))
        self.action_exit.setText(_translate("main_window", "Exit"))
        self.action_exit.setShortcut(_translate("main_window", "Ctrl+Q"))
        self.action_about.setText(_translate("main_window", "About"))
        self.action_about.setShortcut(_translate("main_window", "Ctrl+H"))
        self.action_gv.setText(_translate("main_window", ".gv"))
        self.action_pdf.setText(_translate("main_window", ".pdf"))
        self.action_png.setText(_translate("main_window", ".png"))
        self.action_svg.setText(_translate("main_window", ".svg"))
        self.action_convert.setText(_translate("main_window", "Convert to CFG"))

    def set_menu_state(self, state):
        self.action_gv.setEnabled(state)
        self.action_pdf.setEnabled(state)
        self.action_png.setEnabled(state)
        self.action_svg.setEnabled(state)
        self.action_convert.setEnabled(state)

    def new_pda(self):
        dialog = PDADialog(self.central_widget)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            try:
                self.open_pda_from_file(dialog.temp_file.name)
            finally:
                import os
                os.unlink(dialog.temp_file.name)  # Cleanup temp file

    def open_pda(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.central_widget, 'Open PDA file...', '.', 'XML Files (*.xml)')
        if file_name:
            self.open_pda_from_file(file_name)

    def open_pda_from_file(self, file_name):
        try:
            self.pda = PDA(file_name)
            self.render_pda()
            self.set_menu_state(True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.central_widget, "Error", str(e))

    def render_pda(self):
        try:
            f = Digraph('pda_machine', filename='pda_tmp.gv', format='svg')
            f.attr(rankdir='LR', size='8,5')
            
            # Initial state
            f.attr('node', shape='plaintext')
            f.node(' ')
            f.attr('node', shape='circle')
            f.node(self.pda.initial_state)
            f.edge(' ', self.pda.initial_state, ' ')
            
            # Final states
            f.attr('node', shape='doublecircle')
            for fs in self.pda.final_states:
                f.node(fs)
            
            # Transitions
            f.attr('node', shape='circle')
            for tr in self.pda.transitions:
                label = f"{PDA.lamb(tr['input'])},{PDA.lamb(tr['stack_read'])},{PDA.lamb(tr['stack_write'])}"
                f.edge(tr['source'], tr['destination'], label)
            
            f.render()
            self.center_image.load('pda_tmp.gv.svg')
            self.graph = f

            # Switch to visualization view
            self.stacked_widget.setCurrentIndex(1)
            self.set_menu_state(True)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.central_widget, "Error", str(e))
            # Stay on welcome screen if error occurs
            self.stacked_widget.setCurrentIndex(0)
            self.show_welcome_screen()
    def export_as(self, file_type):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.central_widget, 
            f'Export as {file_type}', 
            '', 
            f'{file_type.upper()} Files (*.{file_type})'
        )
        if file_name:
            self.graph.format = file_type
            self.graph.render(file_name)

    def convert_to_cfg(self):
        try:
            self.cfg = self.pda.convert_to_cfg()
            messageBox = QtWidgets.QMessageBox()
            messageBox.setText('<font size=16>' + '<br>'.join(self.cfg) + '</font>')
            messageBox.setWindowTitle('Result CFG')
            messageBox.exec_()
        except AttributeError:
            QtWidgets.QMessageBox.warning(self.central_widget, "Error", "No PDA loaded!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.central_widget, "Error", str(e))

    def show_about_dialog(self):
        QtWidgets.QMessageBox.information(
            self.central_widget, 
            'About', 
            'PDA to CFG Converter\nVersion 1.0\nCreated by AliReza Beitari'
        )

    def show_welcome_screen(self):
        self.stacked_widget.setCurrentIndex(0)
        self.set_menu_state(False)

    def app_exit(self):
        QtWidgets.QApplication.quit()