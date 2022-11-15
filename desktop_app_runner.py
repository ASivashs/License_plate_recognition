import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap

from pyqt.design import design
from recognition.main import response, graph_usage
from help_func.help_func import is_not_blank

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.browse_folder)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)

    def browse_folder(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open File', './', "Image (*.png *.jpg *jpeg)")
        if file:
            print(file)
        pixmap = QPixmap(file)
        'pixmap.scaled(width=self.label.width(), height=self.label.height())'

        self.label.setPixmap(pixmap)

        self.label.setScaledContents(True)

        self.add_info(file)
        self.add_photo_to_db(file)

    def add_info(self, path):
        _, recog_num = response(path)
        if is_not_blank(recog_num):
            self.label_2.setText("Не удалось распознать")
        else:
            self.label_2.setText(recog_num)
        if graph_usage.find_and_choose(recog_num):
            dict_driver = graph_usage.find_and_choose(recog_num)
            self.label_3.setText(dict_driver["FIRST_NAME"])
            self.label_4.setText(dict_driver["LAST_NAME"])
        else:
            self.label_3.setText("Нет информации")
            self.label_4.setText("Нет информации")

    @staticmethod
    def add_photo_to_db(path):
        _, recog_num = response(path)
        graph_usage.add_new_node_photo(path, response)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
