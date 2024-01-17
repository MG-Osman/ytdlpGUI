import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    download_completed = pyqtSignal(str, str)
    download_error = pyqtSignal(str)

    def __init__(self, url, directory, filename, filetype, audio_only):
        super().__init__()
        self.url = url
        self.directory = directory
        self.filename = filename
        self.filetype = filetype
        self.audio_only = audio_only

    def run(self):
        if not self.url.startswith('http'):
            self.url = f"ytsearch:{self.url}"
        
        command = ['yt-dlp', '-o', f"{self.directory}/{self.filename}.%(ext)s", self.url]
        
        if self.audio_only:
            command += ['--extract-audio']
            if self.filetype:
                command += ['--audio-format', self.filetype]
            else:
                command += ['--audio-format', 'best']
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            self.download_completed.emit(self.filename, self.filetype or 'best')
        else:
            self.download_error.emit(stderr.decode('utf-8').strip())

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YouTube Downloader")

        # Layout setup
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Input URL
        input_layout = QHBoxLayout()
        self.url_label = QLabel("URL / search term (yt only):")
        self.url_entry = QLineEdit()
        input_layout.addWidget(self.url_label)
        input_layout.addWidget(self.url_entry)
        main_layout.addLayout(input_layout)

        # Filename
        self.filename_entry = QLineEdit()
        self.filename_entry.setPlaceholderText("File name (optional)")
        main_layout.addWidget(self.filename_entry)

        # Filetype
        self.filetype_entry = QLineEdit()
        self.filetype_entry.setPlaceholderText("File type (e.g., mp3, optional)")
        main_layout.addWidget(self.filetype_entry)

        # Audio Only Checkbox
        self.audio_only_checkbox = QCheckBox("Download Audio Only")
        main_layout.addWidget(self.audio_only_checkbox)

        # Download Button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download)
        main_layout.addWidget(self.download_button)

        # Fonts and styles
        self.setFont(QFont('Comic Sans MS', 10))
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 15px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QCheckBox {
                margin: 4px 2px;
            }
        """)
        self.resize(480, 200)

    def display_message(self, title, message, type='info'):
        msg_box = QMessageBox()
        if type == 'error':
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def download(self):
        url = self.url_entry.text().strip()
        if not url:
            self.display_message("Error", "Please enter a video URL.", 'error')
            return

        dir_ = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not dir_:
            return

        filename = self.filename_entry.text().strip() or "video"
        filetype = self.filetype_entry.text().strip()
        audio_only = self.audio_only_checkbox.isChecked()

        self.download_thread = DownloadThread(url, dir_, filename, filetype, audio_only)
        self.download_thread.download_completed.connect(self.on_download_completed)
        self.download_thread.download_error.connect(self.on_download_error)
        self.download_thread.start()
        self.download_button.setEnabled(False)

    def on_download_completed(self, filename, filetype):
        self.display_message("Success", f"Download completed!\nFilename: {filename}\nFormat: {filetype or 'best'}")
        self.download_button.setEnabled(True)

    def on_download_error(self, error):
        self.display_message("Error", f"An error occurred:\n{error}", 'error')
        self.download_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())