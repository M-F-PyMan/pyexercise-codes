
from PIL import Image
from rembg import remove
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
import sys
import traceback

class BackgroundRemoverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setGeometry(400, 150, 600, 400)
        self.setWindowTitle("Background Remover")
        # Load Image Button
        self.btn_load = QPushButton("Load Image", self)
        self.btn_load.setGeometry(130, 280, 100, 30)
        self.btn_load.clicked.connect(self.load_image)
        # Save Output Button
        self.btn_save = QPushButton("Save Output", self)
        self.btn_save.setGeometry(410, 280, 100, 30)
        self.btn_save.clicked.connect(self.save_output)
        # Disable the save output button until an image is loaded
        self.btn_save.setEnabled(False)
        # Image Preview Labels
        self.lbl_original = QLabel(self)
        self.lbl_original.setGeometry(150, 20, 200, 200)
        self.lbl_original.setText("Original Image")
        self.lbl_removed = QLabel(self)
        self.lbl_removed.setGeometry(400, 20, 200, 200)
        self.lbl_removed.setText("Background Removed")
        # Initialize image paths
        self.input_path = ""
        self.output_path = ""
        # Show the window
        self.show()
    def remove_background(self):
        if self.input_path:
            try:
                # Open the input image
                input_image = Image.open(self.input_path)
                # Remove the background using the rembg module
                output_image = remove(input_image)
                # Generate the output path if it is not set
                self.output_path = self.output_path or self.input_path.replace(".png", "_no_bg.png")
                # Save the output image as a PNG file
                output_image.save(self.output_path)
                # Print a success message
                print(f"Background removed. Saved as {self.output_path}")
                # Update the image preview
                self.update_image_preview()
                # Enable the save output button
                self.btn_save.setEnabled(True)
            except Exception as e:
                # Catch any exception that may occur
                # Print the error details
                traceback.print_exc()
                # Print an error message
                print(f"An error occurred: {e}")
                # Disable the save output button
                self.btn_save.setEnabled(False)
        else:
            # Print a message if no image is loaded
            print("Please load an image first.")
    def update_image_preview(self):
        if self.input_path:
            # Show the original image in the label
            pixmap_original = QPixmap(self.input_path)
            self.lbl_original.setPixmap(pixmap_original.scaled(200, 200, aspectRatioMode=1))
        if self.output_path:
            # Show the output image in the label
            pixmap_removed = QPixmap(self.output_path)
            self.lbl_removed.setPixmap(pixmap_removed.scaled(200, 200, aspectRatioMode=1))
    def load_image(self):
        # Get the file path from the user
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options)
        if file_path:
            # Set the input path
            self.input_path = file_path
            # Remove the background of the image
            self.remove_background()
    def save_output(self):
        if self.output_path:
            # Get the output path from the user
            options = QFileDialog.Options()
            output_path, _ = QFileDialog.getSaveFileName(self, "Save Output Image", "", "Images (*.png);;All Files (*)", options=options)
            if output_path:
                # Check if the output path ends with ".png"
                if not output_path.endswith(".png"):
                    # Add ".png" if it is missing
                    output_path += ".png"
                # Set the output path
                self.output_path = output_path
                # Save the output image
                self.remove_background()
        else:
            # Print a message if no image is loaded
            print("Please load an image first.")
if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)
    # Create the window
    window = BackgroundRemoverApp()
    # Show the window
    window.show()
    # Exit the application
    sys.exit(app.exec_())
