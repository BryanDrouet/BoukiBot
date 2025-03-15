import os, sys, ctypes
from PyQt6.QtWidgets import QPlainTextEdit, QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QMessageBox, QHBoxLayout, QFileDialog, QLabel, QSplitter, QInputDialog
from PyQt6.QtCore import Qt, QProcess, QRect, QRegularExpression
from PyQt6.QtGui import QPainter, QColor, QIcon, QSyntaxHighlighter, QTextCharFormat

if os.name == "nt":
    os.system("")

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlighting_rules = []

        # Couleurs personnalisées vives pour différents langages
        self.colors = [
            QColor("#FF6347"),  # JSON : Clés
            QColor("#32CD32"),  # JSON : Valeurs
            QColor("#FFD700"),  # JSON : Délimiteurs
            QColor("#FF4500"),  # Python : Mots-clés
            QColor("#FFFF00"),  # Python : Nombres
            QColor("#9ACD32"),  # Python : Commentaires
            QColor("#00CED1"),  # Python : Chaînes
            QColor("#F08080"),  # Python : Délimiteurs
            QColor("#7B68EE"),  # JavaScript : Mots-clés
            QColor("#FFD700"),  # JavaScript : Nombres
            QColor("#8B4513"),  # JavaScript : Commentaires
            QColor("#32CD32"),  # JavaScript : Chaînes
            QColor("#DC143C"),  # JavaScript : Délimiteurs
            QColor("#FF69B4"),  # HTML : Balises
            QColor("#1E90FF"),  # HTML : Attributs
            QColor("#32CD32"),  # HTML : Valeurs
            QColor("#8B4513"),  # HTML : Commentaires
            QColor("#FF6347"),  # CSS : Propriétés
            QColor("#1E90FF"),  # CSS : Valeurs
            QColor("#8B4513"),  # CSS : Commentaires
            QColor("#FFD700"),  # CSS : Sélecteurs
            QColor("#FF4500"),  # PHP : Mots-clés
            QColor("#32CD32"),  # PHP : Variables
            QColor("#FFFF00"),  # PHP : Nombres
            QColor("#00CED1"),  # PHP : Chaînes
            QColor("#9ACD32"),  # PHP : Commentaires
            QColor("#8A2BE2"),  # Discord : Mots-clés (Commandes Discord)
            QColor("#FF1493"),  # Discord : Événements Discord
            QColor("#00BFFF"),  # Discord : Méthodes et attributs
            QColor("#FFD700"),  # Discord : Réactions
        ]

        # Règles pour Discord (Commandes, événements, etc.)
        discord_command_format = QTextCharFormat()
        discord_command_format.setForeground(self.colors[26])  # Commandes Discord
        self.highlighting_rules.append((QRegularExpression("\\b(/\\w+)\\b"), discord_command_format))

        discord_event_format = QTextCharFormat()
        discord_event_format.setForeground(self.colors[27])  # Événements Discord
        self.highlighting_rules.append((QRegularExpression("\\b(on\\s+\\w+)\\b"), discord_event_format))

        discord_method_format = QTextCharFormat()
        discord_method_format.setForeground(self.colors[28])  # Méthodes et attributs Discord
        self.highlighting_rules.append((QRegularExpression("\\.\\w+\\("), discord_method_format))

        discord_reaction_format = QTextCharFormat()
        discord_reaction_format.setForeground(self.colors[29])  # Réactions Discord
        self.highlighting_rules.append((QRegularExpression("\\b(addReaction|removeReaction|reaction)\\b"), discord_reaction_format))

        # Exemple pour JSON
        json_key_format = QTextCharFormat()
        json_key_format.setForeground(self.colors[0])  # Clés JSON
        self.highlighting_rules.append((QRegularExpression("\"[^\"]+\"(?=:)"), json_key_format))

        json_value_format = QTextCharFormat()
        json_value_format.setForeground(self.colors[1])  # Valeurs JSON
        self.highlighting_rules.append((QRegularExpression("(?<=:)[^,]+"), json_value_format))

        json_delimiters_format = QTextCharFormat()
        json_delimiters_format.setForeground(self.colors[2])  # Délimiteurs JSON
        self.highlighting_rules.append((QRegularExpression("[,:{}]"), json_delimiters_format))

        # Exemple pour Python
        python_keyword_format = QTextCharFormat()
        python_keyword_format.setForeground(self.colors[3])  # Mots-clés Python
        self.highlighting_rules.append((QRegularExpression("\\b(def|class|import|from|return|for|if|else)\\b"), python_keyword_format))

        python_number_format = QTextCharFormat()
        python_number_format.setForeground(self.colors[4])  # Nombres Python
        self.highlighting_rules.append((QRegularExpression("\\b[0-9]+\\b"), python_number_format))

        python_comment_format = QTextCharFormat()
        python_comment_format.setForeground(self.colors[5])  # Commentaires Python
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), python_comment_format))

        python_string_format = QTextCharFormat()
        python_string_format.setForeground(self.colors[6])  # Chaînes Python
        self.highlighting_rules.append((QRegularExpression("\"[^\"]*\""), python_string_format))

        python_delimiters_format = QTextCharFormat()
        python_delimiters_format.setForeground(self.colors[7])  # Délimiteurs Python
        self.highlighting_rules.append((QRegularExpression("[(){}\\[\\]]"), python_delimiters_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match = pattern.match(text)
            while match.hasMatch():
                start_index = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start_index, length, format)  # Utilisation correcte de format
                match = pattern.match(text, match.capturedEnd())

        self.setCurrentBlockState(0)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setStyleSheet("background-color: #333333; color: #aaaaaa;")
        self.editor.blockCountChanged.connect(self.updateAreaWidth)
        self.editor.updateRequest.connect(self.update)
        self.updateAreaWidth()

    def updateAreaWidth(self):
        digits = len(str(self.editor.blockCount()))
        self.setFixedWidth(self.fontMetrics().horizontalAdvance("0") * digits + 10)

    def update(self, rect, scrollBar):
        rect = QRect(rect)
        if rect.intersects(QRect(self.editor.viewport().rect())):
            self.repaint() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#333333"))

        block = self.editor.firstVisibleBlock()
        block_rect = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset())

        line_height = int(self.fontMetrics().height()) 

        while block.isValid():
            block_rect = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset())

            if block_rect.top() > event.rect().bottom():
                break 

            if block_rect.bottom() >= event.rect().top(): 
                line_number = str(block.blockNumber() + 1)
                painter.setPen(QColor("#aaaaaa"))
                painter.drawText(QRect(0, int(block_rect.top()), self.width(), line_height), Qt.AlignmentFlag.AlignRight, line_number)

            block = block.next()

class JSONEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_file = None
        self.original_content = ""
        self.bot_process = None
        self.text_edit.textChanged.connect(self.on_text_changed)

    def initUI(self):
        self.setWindowTitle("Lanceur de Bot Discord")
        self.setWindowIcon(QIcon("assets/off.ico"))
        self.setGeometry(100, 100, 800, 400)

        self.is_modified = False 
        self.current_file = None 
        self.original_content = "" 

        layout = QHBoxLayout()

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_layout = QVBoxLayout()
        self.file_label = QLabel("Éditeur de fichier", self)
        self.file_name_label = QLabel("", self)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_name_label)
        left_layout.addLayout(file_layout)

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setStyleSheet(""" 
            QPlainTextEdit {
                background-color: #444444;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 5px;
                font-family: Consolas, monospace;
                margin: 0;
            }
        """)

        self.line_number_area = LineNumberArea(self.text_edit)
        self.text_edit.setViewportMargins(self.line_number_area.width(), 0, 0, 0)

        editor_layout = QHBoxLayout()
        editor_layout.addWidget(self.line_number_area) 
        editor_layout.addWidget(self.text_edit) 

        left_layout.addLayout(editor_layout)

        save_layout = QHBoxLayout()
        self.save_button = QPushButton("Sauvegarder", self)
        self.save_button.setEnabled(False) 
        self.save_button.clicked.connect(self.save_file)
        save_layout.addWidget(self.save_button)

        self.save_as_button = QPushButton("Enregistrer sous...", self)
        self.save_as_button.setEnabled(False) 
        self.save_as_button.clicked.connect(self.save_as_file)
        save_layout.addWidget(self.save_as_button)

        left_layout.addLayout(save_layout)

        self.load_button = QPushButton("Ouvrir un fichier", self)
        self.load_button.clicked.connect(self.load_file)
        left_layout.addWidget(self.load_button)

        self.close_button = QPushButton("Fermer le fichier", self)
        self.close_button.clicked.connect(self.close_file)
        self.close_button.setEnabled(False) 
        left_layout.addWidget(self.close_button)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        right_layout = QVBoxLayout()
        self.console_label = QLabel("Console du Bot", self)
        right_layout.addWidget(self.console_label)
        self.console_output = QTextEdit(self)
        self.console_output.setReadOnly(True)
        right_layout.addWidget(self.console_output)
        self.status_label = QLabel("État du Bot : Éteint", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.status_label)

        bot_layout = QHBoxLayout()
        self.choose_bot_button = QPushButton("Choisir un bot", self)
        self.choose_bot_button.clicked.connect(self.choose_bot)
        bot_layout.addWidget(self.choose_bot_button)
        self.start_bot_button = QPushButton("Lancer le bot", self)
        self.start_bot_button.setEnabled(False)
        self.start_bot_button.clicked.connect(self.start_bot)
        bot_layout.addWidget(self.start_bot_button)
        self.stop_bot_button = QPushButton("Arrêter le bot", self)
        self.stop_bot_button.setEnabled(False)
        self.stop_bot_button.clicked.connect(self.stop_bot)
        bot_layout.addWidget(self.stop_bot_button)

        right_layout.addLayout(bot_layout)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

        splitter.setSizes([int(self.width() * 0.4), int(self.width() * 0.6)])

        self.syntax_highlighter = SyntaxHighlighter(self.text_edit.document())

        self.apply_dark_mode()
    
    def change_language(self):
        lang, ok = QInputDialog.getItem(self, "Sélectionner la langue", "Choisir une langue :", 
                                        ["json", "python", "html", "js", "css", "java", "c", "cpp", "php"], 
                                        current=0, editable=False)
        if ok:
            self.syntax_highlighter.lang = lang
            self.syntax_highlighter.load_keywords()
            self.text_edit.setPlainText("")
    
    def replace_text(self):
        search_text = self.search_line_edit.text()
        replace_text = self.replace_line_edit.text()

        if not search_text:
            QMessageBox.warning(self, "Avertissement", "Veuillez entrer un texte à rechercher.")
            return

        content = self.text_edit.toPlainText()
        if search_text in content:
            new_content = content.replace(search_text, replace_text)
            self.text_edit.setPlainText(new_content)
            self.on_text_changed() 
        else:
            QMessageBox.information(self, "Information", f"Le texte '{search_text}' n'a pas été trouvé.")

    def apply_colored_output(output_str):
        color_map = {
            "INFO": "\033[1;35m",    # Violet vif + gras
            "ERROR": "\033[1;31m",   # Rouge vif + gras
            "WARNING": "\033[1;33m", # Jaune vif + gras
            "DEBUG": "\033[1;32m",   # Vert vif
        }

        if "Bot démarré" in output_str:
            return f"\033[1;32m{output_str}\033[0m"  # Vert vif

        if "Commande appelée avec les paramètres" in output_str:
            return f"\033[1;34m{output_str}\033[0m"  # Bleu vif

        for level, color in color_map.items():
            if output_str.startswith(level):
                return f"{color}{output_str}\033[0m"

        return output_str  # Pas de couleur spécifique, affichage normal

    def closeEvent(self, event):
        if self.bot_process and self.bot_process.state() == QProcess.ProcessState.Running:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Le bot est en cours d'exécution. Voulez-vous vraiment fermer l'application ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()

    def reset_button_style(self, button):
        """Réinitialise le style du bouton."""
        button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:disabled {
                background-color: #333333;
            }
        """)

    def load_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", "", "Tous les fichiers (*);;Fichiers texte (*.txt);;JSON (*.json);;Markdown (*.md);;Python (*.py)")
        if file:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_edit.setPlainText(content)
                self.current_file = file
                self.original_content = content 
                self.is_modified = False 
                self.update_file_label() 
                self.close_button.setEnabled(True)
                self.save_button.setEnabled(False) 
                self.save_as_button.setEnabled(False) 
                self.reset_button_style(self.close_button) 
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de charger le fichier : {str(e)}")
        else:
            self.reset_after_file_closed() 

    def reset_after_file_closed(self):
        self.current_file = None 
        self.text_edit.clear() 
        self.original_content = "" 
        self.is_modified = False  
        self.update_file_label() 
        self.close_button.setEnabled(False) 
        self.save_button.setEnabled(False) 
        self.save_as_button.setEnabled(False) 
        self.reset_button_style(self.start_bot_button) 

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
                self.original_content = self.text_edit.toPlainText() 
                self.is_modified = False
                self.save_button.setEnabled(False)  
                self.close_button.setEnabled(False)  
                self.update_file_label() 
                self.reset_button_style(self.close_button)
                QMessageBox.information(self, "Succès", "Le fichier a été enregistré.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder le fichier : {str(e)}")

    def save_as_file(self):
        file, _ = QFileDialog.getSaveFileName(self, "Enregistrer sous", "", "Tous les fichiers (*);;Fichiers texte (*.txt);;JSON (*.json);;Markdown (*.md);;Python (*.py)")
        if file:
            try:
                with open(file, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
                self.current_file = file  
                self.original_content = self.text_edit.toPlainText()  
                self.update_file_label()  
                self.close_button.setEnabled(True)  
                self.reset_button_style(self.close_button)  
                self.start_bot_button.setEnabled(False)  
                self.apply_button_style(self.start_bot_button)  
                QMessageBox.information(self, "Succès", "Le fichier a été enregistré.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder le fichier : {str(e)}")
    
    def choose_bot(self):
        bot_file, _ = QFileDialog.getOpenFileName(self, "Choisir un bot", "", "Python files (*.py)")
        if bot_file:
            self.bot_file = bot_file
            self.start_bot_button.setEnabled(True)  
            self.setWindowTitle(f"Lanceur de Bot - {os.path.basename(bot_file)}")  # Mise à jour du titre
            QMessageBox.information(self, "Bot choisi", f"Le bot suivant a été sélectionné : {bot_file}")

    def close_file(self):
        if self.text_edit.toPlainText() != self.original_content:
            reply = QMessageBox.question(self, 'Confirmation', 'Voulez-vous enregistrer les modifications ?',
                                        QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, 
                                        QMessageBox.StandardButton.Save)
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                self.save_as_button.setEnabled(False)
                self.save_button.setEnabled(False)
                self.close_button.setEnabled(False)
                self.reset_after_file_closed()
                self.file_label.setText("Éditeur de fichier")
            elif reply == QMessageBox.StandardButton.Cancel:
                return 
        self.text_edit.clear()
        self.current_file = None
        self.original_content = ""
        self.save_button.setEnabled(False)  
        self.close_button.setEnabled(False)  
        self.reset_button_style(self.close_button)  
        self.file_label.setText("Éditeur de fichier")

    def on_text_changed(self):
        if self.text_edit.toPlainText().strip() != self.original_content.strip():
            if not self.is_modified:
                self.save_button.setEnabled(True)  
                self.save_as_button.setEnabled(True)  
                self.is_modified = True  
        else:
            self.save_button.setEnabled(False)  
            self.save_as_button.setEnabled(False)  
            self.is_modified = False  

    def closeEvent(self, event):
        if self.bot_process:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Voulez-vous vraiment arrêter le bot avant de quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_bot()  
            else:
                event.ignore()  
                return

        
        if self.text_edit.toPlainText() != self.original_content or self.is_modified:
            reply = QMessageBox.question(
                self, 
                'Confirmation', 
                'Voulez-vous enregistrer les modifications ?', 
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, 
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()  
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()  

        event.accept()  

    def update_file_label(self):
        if self.current_file:
            file_name = os.path.basename(self.current_file)
            self.file_label.setText(f"Éditeur de fichier - {file_name}")
        else:
            self.file_label.setText("Éditeur de fichier")

    def start_bot(self):
        if hasattr(self, 'bot_file'):
            self.console_output.clear()

            self.bot_process = QProcess(self)
            self.bot_process.readyReadStandardOutput.connect(self.handle_bot_output)
            self.bot_process.readyReadStandardError.connect(self.handle_bot_error)
            self.bot_process.started.connect(self.handle_bot_started)
            self.bot_process.finished.connect(self.handle_bot_finished)
            self.bot_process.setProgram("python")
            self.bot_process.setArguments([self.bot_file])  
            self.bot_process.start()

            self.status_label.setText("État du Bot : En cours d'exécution")
            self.console_output.append(f"Bot démarré : {self.bot_file}\n\n")

            self.start_bot_button.setEnabled(False)  
            self.stop_bot_button.setEnabled(True)  
            self.choose_bot_button.setEnabled(False)
            self.setWindowIcon(QIcon("assets/on.ico"))
        else:
            QMessageBox.warning(self, "Erreur", "Aucun bot sélectionné.")

    def stop_bot(self):
        if self.bot_process and self.bot_process.state() == QProcess.ProcessState.Running:
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Voulez-vous vraiment arrêter le bot ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.bot_process.kill()  
                self.bot_process = None  
                self.console_output.append("\n\nBot arrêté.")
                self.status_label.setText("État du Bot : Éteint")
                self.stop_bot_button.setEnabled(False)  
                self.start_bot_button.setEnabled(True)  
                self.choose_bot_button.setEnabled(True)

    def handle_bot_output(self):
        if self.bot_process:
            output = self.bot_process.readAllStandardOutput().data().decode("utf-8")
            for line in output.splitlines():  # Assurer une bonne gestion des sauts de ligne
                self.console_output.append(line)

    def handle_bot_error(self):
        if self.bot_process:
            error_output = self.bot_process.readAllStandardError().data().decode("utf-8")
            for line in error_output.splitlines():  # Même traitement pour les erreurs
                self.console_output.append(f"<span style='color: red;'>{line}</span>")

    def handle_bot_started(self):
        self.status_label.setText("État du Bot : En cours d'exécution")

    def handle_bot_finished(self):
        self.status_label.setText("État du Bot : Arrêté")

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: white;
            }
            QLabel, QPushButton {
                color: white;
            }
            QTextEdit {
                background-color: #444444;
                color: white;
                border: 1px solid #666666;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #555555;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:disabled {
                background-color: #333333;
            }
        """)

    def show_error(self, message):
        QMessageBox.critical(self, "Erreur", message)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = JSONEditorApp()
	window.show()
	sys.exit(app.exec())
