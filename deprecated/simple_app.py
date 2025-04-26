# simple_app.py - Simplified version to debug issues

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTextEdit,
                             QMessageBox)

from config import GENIUS_API_TOKEN


class SimpleLyricsAnalyzerApp(QMainWindow):
    """Simplified application window for testing"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Genius Lyrics Analyzer (Simple)")
        self.setMinimumSize(600, 400)

        # Initialize variables
        self.token = GENIUS_API_TOKEN

        # Set up the UI
        self.setup_ui()

    def setup_ui(self):
        """Create a simplified user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # API Token section
        token_layout = QHBoxLayout()
        token_label = QLabel("Genius API Token:")
        self.token_input = QLineEdit(self.token)
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        main_layout.addLayout(token_layout)

        # Artist input
        artist_layout = QHBoxLayout()
        artist_label = QLabel("Artist Name:")
        self.artist_input = QLineEdit()
        artist_layout.addWidget(artist_label)
        artist_layout.addWidget(self.artist_input)
        main_layout.addLayout(artist_layout)

        # Run button
        self.run_button = QPushButton("Test Connection")
        self.run_button.clicked.connect(self.test_connection)
        main_layout.addWidget(self.run_button)

        # Status
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        main_layout.addWidget(self.status_text)

    def add_status(self, message):
        """Add a message to the status text area"""
        self.status_text.append(message)
        # Scroll to the bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def test_connection(self):
        """Test the connection to the Genius API"""
        # Get the token
        self.token = self.token_input.text().strip()
        if not self.token:
            QMessageBox.warning(self, "Missing Token",
                                "Please enter your Genius API token")
            return

        # Get the artist name
        artist_name = self.artist_input.text().strip()
        if not artist_name:
            QMessageBox.warning(self, "Missing Input",
                                "Please enter an artist name")
            return

        try:
            # Try to import the LyricsGenius library
            from lyricsgenius import Genius
            self.add_status("Successfully imported LyricsGenius library")

            # Try to create a Genius object
            genius = Genius(self.token)
            genius.verbose = False
            self.add_status("Successfully created Genius object")

            # Try to search for the artist
            self.add_status(f"Searching for artist: {artist_name}")
            artist = genius.search_artist(artist_name, max_songs=1)

            if artist:
                self.add_status(f"Successfully found artist: {artist.name}")
                if artist.songs:
                    self.add_status(f"Found song: {artist.songs[0].title}")
            else:
                self.add_status(f"Could not find artist: {artist_name}")

        except Exception as e:
            self.add_status(f"Error: {str(e)}")
            import traceback
            self.add_status(traceback.format_exc())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleLyricsAnalyzerApp()
    window.show()
    sys.exit(app.exec_())