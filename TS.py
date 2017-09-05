# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QMainWindow
from Ui_TS import Ui_MainWindow
from dialog import Dialog
from Thread import *
import requests

import re
import os
class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        self.tableWidget.setColumnHidden(5, True)
        self.tableWidget.setColumnWidth(3, 40)
        self.session=requests.session()
        self.createContextMenu(self.tableWidget)

        if not os.path.exists('ts.ini'):
            f=open('ts.ini','w')
            f.close()
            settings = QtCore.QSettings(r'ts.ini', QtCore.QSettings.IniFormat)
            settings.beginGroup('tmp_wifi')
            settings.setValue('bssid', '')
            settings.setValue('name', '')
            settings.setValue('password', '')
            settings.setValue('wpa_version', '')
            settings.endGroup()
        self.textEdit.append(u'软件如果出现问题，可以删掉ts.ini配置文件然后重启软件进行初始化')
        self.textEdit.append('-------------------------------')
        report=reportThread()
        report.start()
        canuse=canuseThread()
        canuse.canuseButtonSignal.connect(self.canuse)
        canuse.start()
        self.stok=self.login()
    def canuse(self,text):
        if(text[0]=='N'):
            self.textEdit.append('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            self.textEdit.append(u'软件已经过期，请下载新版本，下载链接:')
            self.textEdit.append(text[2:])
            self.textEdit.append('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            self.pushButton.setEnabled(False)
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.setEnabled(False)
            self.pushButton_5.setEnabled(False)
            self.tableWidget.setRowCount(0)
        if(text[0]=='Y'):
            self.textEdit.append('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            self.textEdit.append(u'软件有新公告,链接:')
            self.textEdit.append(text[2:])
            self.textEdit.append('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    def textappend(self, stri):
        self.stri=stri
        self.textEdit.append(self.stri)

    def login(self):
        stok=''
        try:
            #global longin_username,longin_password,session,statue,post_url,post_date,stok,get_url
            post_url = 'http://192.168.5.1/cgi-bin/luci'
            longin_username=unicode(self.lineEdit.text().toUtf8(), 'utf-8', 'ignore')
            longin_password=unicode(self.lineEdit_2.text().toUtf8(), 'utf-8', 'ignore')
            post_date={'username':longin_username,'password':longin_password}
            html=self.session.post(post_url,data=post_date,timeout=3)
            res=re.search(r'stok',html.text)
            if res:
                self.textEdit.append(u'成功进行登录')
                #self.appendSignal.emit(u'成功进行登录')
                #self.appendSignal.emit(u'如果刚刚换完网卡或者插入网卡没有重启路由器,需重启路由器才能上网')
                stok=html.headers['Set-Cookie'].split(';')[2].split('=')[1]
                #get_url='http://192.168.5.1/cgi-bin/luci/;stok='+stok+'/admin/wireless'
            else:
                self.textEdit.append(u'登录失败，用户名或密码错误，复位可重置密码')
                self.textEdit.append(u'按复位键可自动复位')
        except:
            self.textEdit.append(u'页面无法打开，电脑未识别网络，或者网线路由器出了问题')
            self.textEdit.append(u'请重启，按重启键自动重启或拔插电源')
        self.textEdit.append(u'*******************************')
        return stok
    
    def Getradnumb(self, length):#0.21072496053409184   17位
        string=''
        for i in range(0,length):
            string+=str(random.randint(0,9))
        return string
    
    @pyqtSignature("")
    def on_pushButton_clicked(self):#重连
        """ 
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.pushButtonThread=pushButtonThread(self.stok,self.session)
        self.pushButtonThread.appendSignal1.connect(self.textappend)
        self.pushButtonThread.pushButtonSignal.connect(self.pushButtonAble)
        self.pushButtonThread.start()
    def pushButtonAble(self,b):
        self.pushButton.setEnabled(b)


    @pyqtSignature("")
    def on_pushButton_5_clicked(self):#登陆
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.pushButton.setEnabled(False)
        self.stok = self.login()
        self.pushButton.setEnabled(True)

    
    @pyqtSignature("")
    def on_pushButton_2_clicked(self):#搜索
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.searchButtonThread=searchButtonThread(self.stok,self.session)
        self.searchButtonThread.searchButtonSignal.connect(self.searchButtonAble)
        self.searchButtonThread.searchAppendSignal.connect(self.textappend)
        self.searchButtonThread.setDeviceSignal.connect(self.setDevice)
        self.searchButtonThread.data_dicSignal.connect(self.tableWidgetAppend)
        self.searchButtonThread.start()


    def tableWidgetAppend(self,data):
        settings = QtCore.QSettings(r'ts.ini', QtCore.QSettings.IniFormat)
        settings.beginGroup('wifi_password')
        #print settings
        print data
        self.data_dic=data
        self.tableWidget.setRowCount(0)
        i=0
        flag = '0'#WiFi名字含有中文标志
        for key in data:
            self.tableWidget.insertRow(i)
            for j in range(0, 6):
                if(j==0):#wifi名字
                    s=str(data[key]['join'])
                    m = re.search(r'(\\x|\\u)', s)
                    if (m):
                        flag = '1'
                        s = '"' + s + '"'
                        stepItem = QtGui.QTableWidgetItem(unicode(eval(s), 'utf-8', 'ignore'))
                        self.tableWidget.setItem(i, j, stepItem)
                    else:
                        stepItem = QtGui.QTableWidgetItem(data[key]['join'])
                        self.tableWidget.setItem(i, j, stepItem)
                elif(j==1):#密码
                    if(not data[key].has_key('wpa_suites')):#WIFI没有密码
                        stepItem = QtGui.QTableWidgetItem(unicode('无密码，不用输入', 'utf-8', 'ignore'))
                        self.tableWidget.setItem(i, j, stepItem)
                    else:
                        #print str(data[key]['join'])
                        s = str(data[key]['join'])
                        m = re.search(r'(\\x|\\u)', s)
                        #print type(s),s
                        if (m):
                            s = '"' + s + '"'
                            s=unicode(eval(s), 'utf-8', 'ignore')
                            #print type(s),type(s.encode('utf-8'))
                            s=QtCore.QString.fromAscii(s.encode('utf-8'))
                            #print type(s),s.toAscii()
                            #for d in settings.allKeys():
                             #   print d.toAscii()
                              #  print type(d)
                        if(settings.contains(s)):
                            print u'找到密码'
                            #print help(settings.value)
                            pw=settings.value(s).toString()
                            #print pw
                            stepItem = QtGui.QTableWidgetItem(pw)
                            self.tableWidget.setItem(i, j, stepItem)
                            #print self.tableWidget.item(i,j).text()
                        else:
                            stepItem = QtGui.QTableWidgetItem(unicode('请输入密码', 'utf-8', 'ignore'))
                            self.tableWidget.setItem(i, j, stepItem)
                elif (j == 2):
                    stepItem = QtGui.QTableWidgetItem(data[key]['signal'])
                    self.tableWidget.setItem(i, j, stepItem)

                    self.tableWidget.item(i,j).setFlags(QtCore.Qt.ItemIsEnabled)
                elif (j==3):
                    self.button = QtGui.QPushButton(self)
                    self.button.setText(u"连接")
                    self.button.clicked.connect(self.wifi_data_complete)
                    self.tableWidget.setCellWidget(i, j, self.button)
                elif(j==4):
                    if(flag=='1'):
                        stepItem = QtGui.QTableWidgetItem(unicode('WIFI有中文如果显示错误请手动改正', 'utf-8', 'ignore'))
                        self.tableWidget.setItem(i, j, stepItem)
                        flag='0'
                    else:
                        stepItem = QtGui.QTableWidgetItem(unicode('', 'utf-8', 'ignore'))
                        self.tableWidget.setItem(i, j, stepItem)
                    self.tableWidget.item(i, j).setFlags(QtCore.Qt.ItemIsEnabled)
                elif (j == 5):

                    stepItem = QtGui.QTableWidgetItem(key)
                    self.tableWidget.setItem(i, j, stepItem)
            i+=1
            #print key, '---', data[key]
        settings.endGroup()
        #print i
        #print type(key)
        self.tableWidget.sortByColumn(2,QtCore.Qt.DescendingOrder)
        #self.tableWidget.setColumnHidden(3, False)

    def createContextMenu(self, tableWidget):
        tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #tableWidget.currentItem().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tableWidget.contextMenu = QtGui.QMenu(tableWidget)
        tableWidget.action_connect = tableWidget.contextMenu.addAction(u'连接')
        tableWidget.contextMenu.addSeparator()
        tableWidget.action_jq = tableWidget.contextMenu.addAction(u'剪切')

        tableWidget.action_fz = tableWidget.contextMenu.addAction(u'复制')
        tableWidget.action_zt = tableWidget.contextMenu.addAction(u'粘贴')
        tableWidget.action_sc = tableWidget.contextMenu.addAction(u'删除')

        self.clipboard = QtGui.QApplication.clipboard()
        tableWidget.action_connect.triggered.connect(self.wifi_data_complete)
        tableWidget.action_fz.triggered.connect(lambda:self.clipboard.setText(tableWidget.currentItem().text()))
        tableWidget.action_zt.triggered.connect(lambda:tableWidget.currentItem().setText(self.clipboard.text()))
        tableWidget.action_sc.triggered.connect(lambda:tableWidget.currentItem().setText(''))
        tableWidget.action_jq.triggered.connect(self.jianqie)

        tableWidget.customContextMenuRequested.connect(lambda:self.showContextMenu(tableWidget))

    def jianqie(self):
        self.clipboard.setText(self.tableWidget.currentItem().text())
        self.tableWidget.currentItem().setText('')
    def showContextMenu(self, tableWidget):
        # 菜单显示前，将它移动到鼠标点击的位置
        self.pos=QtGui.QCursor.pos()
        try:
            if(self.tableWidget.currentColumn()==2 or self.tableWidget.currentColumn()==4):
                return
            self.tableWidget.currentItem().text().toUtf8()

            tableWidget.contextMenu.exec_(self.pos)  # 在鼠标位置显示
        except:
            pass
    def setDevice(self,s):
        self.device=unicode(s, 'utf-8', 'ignore')
        print u'设备',self.device
    def wifi_data_complete(self):
        #global password_date,device
        if(self.stok==''):
            self.textEdit.append(u'您没有登录，请登录后操作')
            self.textEdit.append(u'*******************************')
            return
        settings=QtCore.QSettings(r'ts.ini',QtCore.QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        password_date = {
            'cbi.cbe.network.1.replace': '1',  #
            'cbi.submit': '1',  #
            'cbid.network.1.replace': '1',  #
            'cbid.network.1._fwzone': 'wan',  #
            'cbid.network.1._fwzone.newzone': '',  #
            'cbid.network.1._netname_new': 'wwan',  #
            'mode': 'Master',  #
            'wep': '0',  #
        }
        try:#按钮点击
            senderObj = self.sender()
            index=self.tableWidget.indexAt(QtCore.QPoint(senderObj.frameGeometry().x(),senderObj.frameGeometry().y()))
            #print index.row()
            ssid=str(self.tableWidget.item(index.row(),5).text().toUtf8())
            password_date['bssid']=self.data_dic[ssid]['bssid']
            password_date['wpa_version']=self.data_dic[ssid]['wpa_version']
            password_date['channel'] = self.data_dic[ssid]['channel']
            text=self.tableWidget.item(index.row(),0).text()
            #b = text.contains(QtCore.QRegExp("[\\x4e00-\\x9fa5]+"))
            #if (b):  # 有中文
            password_date['join'] = unicode(text.toUtf8().data(), 'utf-8','ignore')
            print u'框里的WiFi名字编码',[text.toUtf8().data()]
            password_date['device']=self.device
            #raw_input()
            if(self.data_dic[ssid].has_key('wpa_suites')):
                password_date['wpa_suites'] = self.data_dic[ssid]['wpa_suites']
                b = self.tableWidget.item(index.row(), 1).text().contains(QtCore.QRegExp("[\\x4e00-\\x9fa5]+"))
                if(b):
                    print u'按钮点击'
                    print u'密码有中文！'
                    self.dialog=Dialog()
                    app.beep()
                    self.dialog.exec_()
                    return False
                password_date['cbid.network.1.key'] = unicode(self.tableWidget.item(index.row(), 1).text().toUtf8().data(), 'utf-8', 'ignore')

            #print password_date['join']
            print password_date
            print u'按钮点击'
            print password_date['join']
            settings.beginGroup('tmp_wifi')
            settings.setValue('bssid', str(password_date['bssid']))
            print str([text.toUtf8().data()])[2:-2]
            settings.setValue('name', str([text.toUtf8().data()])[2:-2])
            if (self.data_dic[ssid].has_key('wpa_suites')):
                settings.setValue('password', str(password_date['cbid.network.1.key']))
            else:
                settings.setValue('password','')
            settings.setValue('wpa_version', str(password_date['wpa_version']))
            settings.endGroup()

            try:#将密码写入配置文件
                #print str(text.toUtf8().data())
                #QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName('UTF-8'))
                settings.beginGroup('wifi_password')
                settings.setValue(str(text.toUtf8().data()), password_date['cbid.network.1.key'])
                settings.endGroup()
                #print data[key]['join'].encode('utf-8')
            except:
                print u'无密码无需写入'
            self.apply(password_date)
            self.textEdit.append(u'**************************')
            return True
        except:#菜单点击
            ssid=str(self.tableWidget.item(self.tableWidget.currentRow(), 5).text().toUtf8())
            password_date['bssid']=self.data_dic[ssid]['bssid']
            password_date['wpa_version']=self.data_dic[ssid]['wpa_version']
            password_date['channel'] = self.data_dic[ssid]['channel']
            text=self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
            #b=text.contains(QtCore.QRegExp("[\\x4e00-\\x9fa5]+"))
            #if(b):#有中文
            password_date['join'] = unicode(text.toUtf8().data(), 'utf-8', 'ignore')
            #print type(text)
            password_date['device']=self.device
            if(self.data_dic[ssid].has_key('wpa_suites')):
                password_date['wpa_suites'] = self.data_dic[ssid]['wpa_suites']
                b=self.tableWidget.item(self.tableWidget.currentRow(),1).text().contains(QtCore.QRegExp("[\\x4e00-\\x9fa5]+"))
                if(b):
                    print u'菜单点击'
                    print u'密码有中文！'
                    self.dialog = Dialog()
                    app.beep()
                    self.dialog.exec_()
                    return False
                password_date['cbid.network.1.key']=unicode(self.tableWidget.item(self.tableWidget.currentRow(),1).text().toUtf8().data(), 'utf-8', 'ignore')
            print password_date['join']
            print password_date
            print u'菜单点击'
            try:
                settings.beginGroup('wifi_password')
                settings.setValue(str(text.toUtf8().data()), password_date['cbid.network.1.key'])
                settings.endGroup()
            except:
                print u'无密码无需写入'
            settings.beginGroup('tmp_wifi')
            settings.setValue('bssid', str(password_date['bssid']))
            settings.setValue('name', str([text.toUtf8().data()])[2:-2])
            if (self.data_dic[ssid].has_key('wpa_suites')):
                settings.setValue('password', str(password_date['cbid.network.1.key']))
            else:
                settings.setValue('password','')
            settings.setValue('wpa_version', str(password_date['wpa_version']))
            settings.endGroup()
            self.apply(password_date)
            self.textEdit.append(u'************************')
            return True

    def apply(self, password_Date):
        try:
            self.textEdit.append(password_Date['join'])
            self.textEdit.append(u'正在提交密码')
            connect_url = 'http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/admin/network/wireless_join'
            self.session.post(connect_url, data=password_Date,timeout=3)
            self.textEdit.append(u'提交成功')
            # print html.text.encode('utf-8')#保存与应用的页面
            self.textEdit.append(u'正在保存与应用')
            save_url = 'http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/admin/uci/saveapply?redir='
            self.session.get(save_url)
            fin_save_url = 'http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/servicectl/restart/firewall,wireless?_=0.' + self.Getradnumb(
                17)
            fin = self.session.get(fin_save_url)
            if fin.text.encode('utf-8') == "OK":
                self.textEdit.append(u'OK')
                self.textEdit.append(u'已经成功保存与应用，请等待')
            else:
                self.textEdit.append(u'路由器出现问题，未能连接成功')
                self.textEdit.append(u'按重启键可重启路由器')
            self.textEdit.append(u'如果稍后仍然无法上网，请手动进行设置或者重启路由器，也有可能WiFi密码错误')
            self.textEdit.append(u'如果刚刚插入网卡或者更换网卡，请重新登陆并且搜索WIFI再连接')
        except Exception,e:
            print Exception,e
            self.textappend(u'路由器出现问题，请手动登陆检查,请重启或复位')

    def searchButtonAble(self,b):
        self.pushButton_2.setEnabled(b)
    @pyqtSignature("")
    def on_pushButton_3_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.restartThread=restartThread(self.stok,self.session)
        self.restartThread.start()
        self.restartThread.restartAppendSignal.connect(self.textappend)
        self.stok=''

    
    @pyqtSignature("")
    def on_textEdit_textChanged(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        try:
            self.textEdit.moveCursor(QtGui.QTextCursor.End)
            self.textEdit.ensureCursorVisible()
        except:
            pass

    
    @pyqtSignature("")
    def on_action_14_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.textEdit.append(u'本软件由自由软件作者开发，不作商业用途，免费使用，如需合作或者将软件用作商业用途，请联系作者邮箱wkzj2015@163.com，软件如有错误请反馈邮箱，感谢您的使用!')
        self.textEdit.append(u'(￣▽￣)~*(￣▽￣)~*(￣▽￣)~*(￣▽￣)~*')
    @pyqtSignature("")
    def on_action_15_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.textEdit.append(u'软件写好之后没有规模的测试，有错误请反馈作者邮箱wkzj2015@163.com')
        self.textEdit.append(u'╮(╯﹏╰）╭╮(╯﹏╰）╭╮(╯﹏╰）╭╮(╯﹏╰）╭')
    
    @pyqtSignature("")
    def on_action_16_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.textEdit.append(u'感谢您的联系，作者邮箱wkzj2015@163.com')
        self.textEdit.append(u'(￣▽￣)~*(￣▽￣)~*(￣▽￣)~*(￣▽￣)~*')
if __name__=="__main__":
    import sys
    app = QtGui.QApplication(sys.argv)

    dlg = MainWindow()
    ts=QtCore.QTranslator()
    ts.load(':/new/widgets.qm')
    app.installTranslator(ts)
    ts2=QtCore.QTranslator()
    ts2.load(':/new/qt_zh_CN.qm')
    app.installTranslator(ts2)



    dlg.show()
    sys.exit(app.exec_())
    
    @pyqtSignature("")
    def on_action_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_action_toggled(self, p0):
        """
        Slot documentation goes here.
        
        @param p0 DESCRIPTION
        @type bool
        """
        # TODO: not implemented yet
        raise NotImplementedError
