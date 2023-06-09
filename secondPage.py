from PySide6.QtCore import QDateTime, QDate, QTime
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QDateTimeEdit, QPushButton, QListWidget, QHBoxLayout, \
    QGridLayout, QVBoxLayout, QMessageBox

from measurements_database import *
import matplotlib.pyplot as plt


def plot_histogram(sugar_values, border_value, mode, start_date, end_date):
    """Plots histogram of sugar values, good results are green, very bad red and bad are orange.

    :param sugar_values: values of sugar
    :type list
    :param border_value: border value that says which values should be orange
    :type int
    :param mode: says whether measurement was after meal
    :type int
    :param start_date: the first date of range from which measurements where taken
    :type str
    :param end_date: the last date of range from which measurements where taken
    :type str
    """
    bins = []
    i = 10
    while i <= 400:
        bins.append(i)
        i += 10
    fig = plt.figure()
    n, bin1, patches = plt.hist(sugar_values, bins=bins, color="green", ec="black")
    for i in range(4):
        patches[i].set_fc("red")
    patches[4].set_fc("orange")
    patches[5].set_fc("orange")
    for i in range(19, 39):
        patches[i].set_fc("red")
    for i in range(int(border_value/10)-1, 19):
        patches[i].set_fc("orange")
    plt.xlabel("Sugar mg/dl")
    plt.ylabel("Frequency")
    plt.legend([patches[0], patches[4], patches[6]], ["life at risk", "abnormal blood sugar", "normal blood sugar"])
    fig.canvas.draw()
    fig.canvas.flush_events()
    if mode == 2:
        mode = "fasting"
    else:
        mode = "after eating"
    end_date = end_date[:-6]
    plt.title(f"Blood sugar -  {mode}, period {start_date} - {end_date}")
    plt.savefig('plot.png')


class SecondPage(QWidget):
    """Class SecondPage is used to model view od the second page of the application"""
    def __init__(self, database):
        """
        :param database: database of measurements
        """
        super().__init__()
        self.database = database

        time_period_label = QLabel("Period: ")
        self.combo_box_time = QComboBox(self)
        self.combo_box_time.addItem("Year")
        self.combo_box_time.addItem("Month")
        self.combo_box_time.addItem("Week")
        self.combo_box_time.addItem("Day")

        start_time_label = QLabel("Starts from: ")
        self.dateEdit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dateEdit.setMaximumDate(QDate.currentDate())
        self.dateEdit.setMaximumTime(QTime.currentTime())
        self.dateEdit.setDisplayFormat("dd.MM.yyyy hh:mm")

        mode_label = QLabel("Mode: ")
        self.combo_box_mode = QComboBox(self)
        self.combo_box_mode.addItem("All")
        self.combo_box_mode.addItem("Fasting")
        self.combo_box_mode.addItem("After eating")

        button_analise = QPushButton("Analysis")
        button_analise.clicked.connect(self.analise)

        self.list_widget = QListWidget(self)

        self.avg_label = QLabel("Blood sugar average: ")
        self.min_label = QLabel("Blood sugar min: ")
        self.max_label = QLabel("Blood sugar max: ")

        v_layout_labels = QVBoxLayout()
        v_layout_labels.addWidget(self.avg_label)
        v_layout_labels.addWidget(self.min_label)
        v_layout_labels.addWidget(self.max_label)

        self.image_label = QLabel()

        h_layout = QHBoxLayout()
        h_layout.addWidget(time_period_label)
        h_layout.addWidget(self.combo_box_time)
        h_layout.addWidget(start_time_label)
        h_layout.addWidget(self.dateEdit)
        h_layout.addWidget(mode_label)
        h_layout.addWidget(self.combo_box_mode)
        h_layout.addWidget(button_analise)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.list_widget, 0, 0)
        grid_layout.addLayout(v_layout_labels, 1, 0)
        grid_layout.addWidget(self.image_label, 0, 1, 2, 2)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addLayout(grid_layout)

        self.setLayout(v_layout)

    def analise(self):
        """ Analise's measurements from chosen mode and period

        After analise has been performed displays histogram and average, min and max value of the measurements
        """
        self.image_label.clear()
        period = self.combo_box_time.currentIndex() + 1
        mode = self.combo_box_mode.currentIndex() + 1
        end_date = self.dateEdit.dateTime().toString(self.dateEdit.displayFormat())
        measurements_list = self.database.measurements_list.copy()
        start_date = return_start_date(period, end_date)
        start_date = start_date.strftime("%d.%m.%Y")

        if mode != 1:
            if mode == 3:
                measurements_list = find_measurements_with_specific_mode("after eating", measurements_list)
                border_value = 140
            else:
                measurements_list = find_measurements_with_specific_mode("fasting", measurements_list)
                border_value = 100
        if len(measurements_list) == 0:
            self.show_message_box(" ","There aren't such measurements")
            return

        measurements_from_period = find_measurements_from_period(period, end_date, measurements_list)
        if len(measurements_from_period) == 0:
            self.show_message_box(" ","There aren't such measurements")
            return
        avg_sugar, min_sugar, max_sugar = analise_measurements(measurements_from_period)
        measurements_list_sorted = return_sorted_chronologically(measurements_from_period)
        self.list_widget.clear()
        string_list = string_measurement_list(measurements_list_sorted)
        self.list_widget.addItems(string_list)
        self.list_widget.setMinimumWidth(self.list_widget.sizeHintForColumn(0))

        self.avg_label.setText("Blood sugar average: " + str(avg_sugar))
        self.min_label.setText("Blood sugar min: " + str(min_sugar))
        self.max_label.setText("Blood sugar max: " + str(max_sugar))

        if mode != 1:
            plot_histogram(return_sugar_values(measurements_list_sorted), border_value, mode, start_date, end_date)
            self.image_label.setPixmap(QPixmap("plot.png"))

    def show_message_box(self, title, value):
        """Displays message

        :param title: title of the message
        :param value: text of the message
        :return:
        """
        ret = QMessageBox.information(self, title, value)