#!/usr/bin/python3
'''
Author: Zhao-Shun Zheng, Cheng Han Yu
Date: 2021/6/19
function: Show datas by connecting MySQL, calculate results and real time video on User Interface 
email: e14051148@gs.ncku.edu.tw, n26094304@gs.ncku.edu.tw
'''
# This is a sample Python script.
# include library
import sys
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QIcon, QPixmap
from UI_Login import *
from UI_Main import *
from UI_DataProfile import *
import pandas as pd
import pymysql
import socket
import cv2
import numpy as np
from datetime import datetime

# global path
global Login, Main, DataProfile, DataProfilePro, SQL

sys.setrecursionlimit(5000)

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
class sql():
    def __init__(self, parent = None):
        db_settings = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "f130073973",
            "db": "IOT",
            "charset": "utf8"
        }
        self.conn = pymysql.connect(**db_settings)

    def GetAllData(self, table="products"):
        command = "SELECT * FROM " + table
        with self.conn.cursor() as cursor:
            cursor.execute(command)
            result = cursor.fetchall()
            res = np.asarray(result)

        return res

    def GetAllColumnName(self, table="products"):
        command = "select * from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '" + table + "' "
        with self.conn.cursor() as cursor:
            cursor.execute(command)
            result = cursor.fetchall()
            res = np.asarray(result)
        return res[:, 3]

    def Insert(self, data, table="products"):
        command = "INSERT INTO " + table + " (id, OrderNumber, name, startDate, defection, image, finishedDate)  VALUES (%s, %s, %s, %s, %s, %s, %s)"
        with self.conn.cursor() as cursor:
            cursor.execute(command, (
            data['OrderNumber'] + "_" + data['name'], data['OrderNumber'], data['name'], data['startDate'],
            data['defection'], data['image'], data['finishedDate']))
        self.conn.commit()

    def Update(self, data, table="products"):
        for d in data:
            if d != 'id' and data[d] != "":
                with self.conn.cursor() as cursor:
                    update_users = "UPDATE " + table + " SET " + d + " = '" + data[d] + "' WHERE id = '" + data[
                        'id'] + "'"
                    cursor.execute(update_users)
                    self.conn.commit()

    def InsertAndUpdate(self, data, table="products"):
        data['id'] = data['OrderNumber'] + "_" + data['name']
        command = "select id from " + table + " where id=%s"
        with self.conn.cursor() as cursor:
            cursor.execute(command, (data['id']))
            # gets the number of rows affected by the command executed
            r = cursor.rowcount
            print(r)
            if r == 0:
                self.Insert(data, table=table)
            else:
                self.Update(data, table=table)
            self.conn.commit()

    def delete(self, id_="", ALL=False, table="products"):
        if ALL:
            r = self.GetAllData()

            for i in range(1, r.shape[0] + 1):
                with self.conn.cursor() as cursor:
                    delete_users = "DELETE FROM " + table + " WHERE id = '" + r[i - 1, 0] + "'"
                    print(delete_users)
                    cursor.execute(delete_users)
                    self.conn.commit()
        else:
            delete_users = "DELETE FROM " + table + " WHERE id = '" + id_ + "'"
            with self.conn.cursor() as cursor:
                cursor.execute(delete_users)
                self.conn.commit()

    def query_id(self, id_, table="products"):
        command = "SELECT * FROM " + table + " WHERE id ='" + id_ + "'"
        with self.conn.cursor() as cursor:
            cursor.execute(command)
            result = cursor.fetchall()
        res = np.asarray(result)
        return res

    def refresh(self):
        db_settings = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "f130073973",
            "db": "IOT",
            "charset": "utf8"
        }
        self.conn = pymysql.connect(**db_settings)


# >>>> 登入畫面
class EnterInterface(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(EnterInterface, self).__init__(parent)
        self.setupUi(self)
        self.Enter.clicked.connect(self.enter_event)  # 綁定 登入函數

    # 登入函数
    def enter_event(self):
        if self.UserName_text.text() == "":
            QMessageBox.about(self, 'Enter', '請輸入姓名')
        elif self.Password_text.text() == "":
            QMessageBox.about(self, 'Enter', '請輸入密碼')
        else:
            boo, limit, photo_path = check(self, self.UserName_text.text(), self.Password_text.text())
            if boo:
                self.close()
                Main.show()
                Main.setting(self.UserName_text.text(), limit, photo_path)
                self.UserName_text.setText("")
                self.Password_text.setText("")


# >>>> 主畫面
class MainInterface(QMainWindow, Ui_Main):
    def __init__(self, parent=None):
        super(MainInterface, self).__init__(parent)
        self.t = "start"
        self.setupUi(self)
        self.StartTime_Calender.clicked.connect(self.set_time)
        self.EndTime_Calender.clicked.connect(self.set_time_2)
        self.Calender.clicked.connect(self.set_date)
        self.Logout.clicked.connect(logout_)
        self.Monitor.clicked.connect(monitor)
        select_day = self.Calender.selectedDate()
        self.StartTime.setText(changeDateFormate(select_day.toString()))
        self.EndTime.setText(changeDateFormate(select_day.toString()))
        self.Query.clicked.connect(self.SHOW)
        self.List.currentIndexChanged.connect(self.query_workorder)

    # 初始設定
    def setting(self, username, limit, photo_path):
        self.UserName.setText(username)
        # print("Data/photo/" + photo_path)
        self.UserPhoto.setPixmap(QtGui.QPixmap("Data\\photo\\" + photo_path))

    # 設定起始時間
    def set_time(self):
        self.t = "start"

    def SHOW(self):
        while(True):
            self.query_date()
            if cv2.waitKey(500) & 0xFF == ord('q'):
                break

    def query_date(self):
        startDate = toDateTime(self.StartTime.text() + " 0:0:0")
        endDate = toDateTime(self.EndTime.text() + " 23:59:59")

        if startDate > endDate:
            QMessageBox.about(Main, 'Enter', 'Please Check Time')
        else:
            if self.List.currentIndex() == -1:
                index = 0
            else:
                index = self.List.currentIndex()

            self.List.clear()

            SQL.refresh()
            if len(SQL.GetAllData()) != 0:
                AllItem = SQL.GetAllData()[:, 8]
                PASS = []
                for i in range(len(AllItem)):
                    D = toDateTime(AllItem[i])
                    if D >= startDate and D <= endDate:
                        PASS.append(i)

                li = np.unique(SQL.GetAllData()[PASS, 1])
                for item in li:
                    self.List.addItem(item)
                self.List.setCurrentIndex(index)

    # 設定終止時間
    def set_time_2(self):
        self.t = "end"

    # 設定日期時間
    def set_date(self):
        select_day = self.Calender.selectedDate()
        if self.t == "start":
            self.StartTime.setText(changeDateFormate(select_day.toString()))
        else:
            self.EndTime.setText(changeDateFormate(select_day.toString()))

    def query_workorder(self):
        workorder = self.List.currentText()
        SQL.refresh()
        ALLData = SQL.GetAllData()
        Items = ALLData[ALLData[:, 1] == workorder]
        self.setitem(Items)
        Defection = Items[:,5]

        if (np.count_nonzero(Defection == 'perfect') + np.count_nonzero(Defection == 'defect')) != 0:
            self.Yield.setText("良率:  " + str(np.count_nonzero(Defection == 'perfect')) +
                   "/" + str(np.count_nonzero(Defection == 'perfect') + np.count_nonzero(Defection == 'defect')) +
                   "  " + "{:.0%}".format(np.count_nonzero(Defection == 'perfect') /
                   (np.count_nonzero(Defection == 'perfect') + np.count_nonzero(Defection == 'defect'))))


    # 設定物件數量
    def setitem(self, items):
        while (self.tableWidget.rowCount() > 0):
                self.tableWidget.removeRow(0)

        lst = SQL.GetAllColumnName()
        columnlist = [0, 3, 4, 5, 7]

        Length = len(columnlist) + 1
        self.tableWidget.setColumnCount(Length)  # set column number

        # import item into Table
        for i in range(len(items)):
            item = items[i]
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            for j in range(len(columnlist)):
                item = QTableWidgetItem(str(items[i][columnlist[j]]))
                self.tableWidget.setItem(row, j, item)

            self.tableWidget.setCellWidget(row, Length - 1, self.button_for_row())  # 在最后一个单元格中加入按钮

        self.tableWidget.setHorizontalHeaderLabels(np.append(lst[columnlist], 'Link'))
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # 使列表自适应宽度
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 设置tablewidget不可编辑
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)  # 设置tablewidget不可选中

    def button_for_row(self):
        widget = QtWidgets.QWidget()
        # Link
        self.deleteBtn = QtWidgets.QPushButton('Link')
        self.deleteBtn.setStyleSheet(''' text-align : center;
                                            background-color : LightCoral;
                                            height : 30px;
                                            border-style: outset;
                                            font : 13px; ''')
        self.deleteBtn.clicked.connect(self.Link_button)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.deleteBtn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    def Link_button(self):
        button = self.sender()
        if button:
            # 确定位置的时候这里是关键
            row = self.tableWidget.indexAt(button.parent().pos()).row()
            id = self.tableWidget.model().data(self.tableWidget.model().index(row, 0))

            Main.close()
            DataProfile.show()
            DataProfile.setitem(id)


class ProfileInterface(QMainWindow, Ui_Profile):
    def __init__(self, parent=None):
        super(ProfileInterface, self).__init__(parent)
        self.t = "start"
        self.setupUi(self)
        self.ReturnButton.clicked.connect(return_)

        self.DataProfile.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # 使列表自适应宽度
        self.DataProfile.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # 使列表自适应宽度
        self.DataProfile.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 设置tablewidget不可编辑
        self.DataProfile.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)  # 设置tablewidget不可选中
        self.DataProfile.setSpan(0, 1, 1, 3)  # 其引數為： 要改變單元格的   1行數  2列數     要合併的  3行數  4列數
        self.DataProfile.setSpan(2, 1, 1, 3)  # 其引數為： 要改變單元格的   1行數  2列數     要合併的  3行數  4列數
        self.DataProfile.setSpan(3, 1, 1, 3)  # 其引數為： 要改變單元格的   1行數  2列數     要合併的  3行數  4列數
        self.DataProfile.setSpan(4, 1, 1, 3)  # 其引數為： 要改變單元格的   1行數  2列數     要合併的  3行數  4列數
        self.DataProfile.setSpan(5, 1, 1, 3)  # 其引數為： 要改變單元格的   1行數  2列數     要合併的  3行數  4列數
        self.DataProfile.setSpan(6, 1, 1, 3)  # 其引數為： 要改變單元格的   1行數  2列數     要合併的  3行數  4列數
        self.DataProfile.setSpan(7, 1, 1, 3)  # 其引數為： 要改變單元格的   1行數  2列數     要合併的  3行數  4列數
        self.DataProfile.setSpan(8, 1, 1, 3)  # 其引數為： 要改變單元格的   1行數  2列數     要合併的  3行數  4列數

    def setitem(self, id_):
        data = SQL.query_id(id_)
        self.DataProfile.setItem(0, 1, QTableWidgetItem(data[0, 0]))
        self.DataProfile.setItem(1, 1, QTableWidgetItem(data[0, 1]))
        self.DataProfile.setItem(1, 3, QTableWidgetItem(data[0, 2]))
        self.DataProfile.setItem(2, 1, QTableWidgetItem(data[0, 8]))
        self.DataProfile.setItem(3, 1, QTableWidgetItem(data[0, 3]))
        self.DataProfile.setItem(4, 1, QTableWidgetItem(data[0, 4]))
        self.DataProfile.setItem(5, 1, QTableWidgetItem(data[0, 5]))
        self.DataProfile.setItem(6, 1, QTableWidgetItem(data[0, 9]))
        self.DataProfile.setItem(7, 1, QTableWidgetItem(data[0, 10]))
        self.DataProfile.setItem(8, 1, QTableWidgetItem(data[0, 7]))
        pixmap = QPixmap(data[0, 6])
        self.Image.setFixedHeight(int(pixmap.height() * self.Image.width() / pixmap.width()))
        self.Image.setPixmap(pixmap)



# >>>>>>>>>>>>>> functions >>>>>>>>>>>>>>
# >>>> 確認帳號密碼有無錯誤
def check(ui, username, password):
    df = pd.read_excel("Data\\User Information.xls")
    if df[df['User'] == username].size > 0:
        if str(df.loc[df['User'] == username, 'Password'].item()) == password:
            QMessageBox.about(ui, 'Enter', username + ' 歡迎登入')

            # return bool, limits, photo path
            print(df.loc[df['User'] == username, 'photo'].item())
            return True, df.loc[df['User'] == username, 'limits'].item(), df.loc[df['User'] == username, 'photo'].item()
        else:
            QMessageBox.about(ui, 'Enter', '密碼錯誤')
            return False, "", ""
    else:
        QMessageBox.about(ui, 'Enter', '查無使用者')
        return False, "", ""


def logout_():
    Main.close()
    Login.show()


# >>>> 詳細資訊畫面
def return_pro():
    DataProfilePro.close()
    Main.show()


def monitor():
    while True:
        length = recvall(sock, 16)
        stringData = recvall(sock, int(length))
        data = np.frombuffer(stringData, dtype='uint8')
        img = cv2.imdecode(data, 1)
        cv2.imshow('client', img)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


# >>>> 資訊畫面
def return_():
    DataProfile.close()
    Main.show()


def changeDateFormate(string):
    x = string.split()
    month = ""
    if x[1] == "一月":
        month = "01"
    elif x[1] == "二月":
        month = "02"
    elif x[1] == "三月":
        month = "03"
    elif x[1] == "四月":
        month = "05"
    elif x[1] == "六月":
        month = "06"
    elif x[1] == "七月":
        month = "07"
    elif x[1] == "八月":
        month = "08"
    elif x[1] == "九月":
        month = "09"
    elif x[1] == "十月":
        month = "10"
    elif x[1] == "十一月":
        month = "11"
    elif x[1] == "十二月":
        month = "12"

    res = x[3] + "/" + month + "/" + x[2]
    return res


def toDateTime(string):
    ISOTIMEFORMAT = '%Y/%m/%d %H:%M:%S'
    return datetime.strptime(string, ISOTIMEFORMAT)


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    TCP_IP = "192.168.0.147"
    TCP_PORT = 8000
    sock = socket.socket()
    sock.connect((TCP_IP, TCP_PORT))

    close = False
    app = QtWidgets.QApplication([])
    SQL = sql()

    # Interface
    Login = EnterInterface()
    Main = MainInterface()
    DataProfile = ProfileInterface()

    Login.show()
    #Main.show()




    sys.exit(app.exec_())
    print("exit")
    socket.close()
