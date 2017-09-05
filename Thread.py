# -*- coding: utf-8 -*-
from PyQt4 import QtCore
import re
import requests
from bs4 import BeautifulSoup
import random
mutex = QtCore.QMutex()
import json
import socket
import uuid
import time

class canuseThread(QtCore.QThread):
    canuseButtonSignal = QtCore.pyqtSignal(str)
    def __init__(self,parent=None):
        super(canuseThread, self).__init__(parent)
    def run(self):
        time.sleep(5)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        while(True):
            try:
                print u'正在连接服务器'
                s.connect(('47.94.10.252', 1002))
                print u'连接更新服务器成功'
                data=s.recv(1024)
                print u'返回信息',data
                s.close()
                if(data[0]=='N' or data[0] == 'Y'):
                    self.canuseButtonSignal.emit(data)
                else:
                    pass
                break
            except Exception,e:
                print Exception,e
                try:
                    s.close()
                except:
                    pass
                time.sleep(60)
                pass

class reportThread(QtCore.QThread):
    def __init__(self,parent=None):
        super(reportThread, self).__init__(parent)
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        settings = QtCore.QSettings(r'ts.ini', QtCore.QSettings.IniFormat)
        settings.setIniCodec('UTF-8')
        settings.beginGroup('state')
        state=unicode(settings.value('state').toString(), 'utf-8', 'ignore')
        print u'发送信息状态',state
        settings.endGroup()
        if(not state==''):
            print u'不用发送信息'
            return
        while(True):
            try:
                session = requests.session()
                page = session.get('http://ip.cn/index.php',timeout=10)
                soup = BeautifulSoup(page.text, 'lxml')
                ip = soup.find_all('code')[0].string
                index = page.text.find('GeoIP')
                # print index
                end_index = page.text.find('</p>', index)
                # print end_index
                location = page.text[index + 7:end_index]
                location_list = location.split(',')
                ip = ip + ' ' + location_list[-1] + ' ' + location_list[-2]+' '+self.get_mac_address()
                print ip
                s.connect(('47.94.10.252', 1001))
                s.send(ip)
                s.close()
                print u'连接成功'
                settings = QtCore.QSettings(r'ts.ini', QtCore.QSettings.IniFormat)
                settings.setIniCodec('UTF-8')
                settings.beginGroup('state')
                settings.setValue('state', 'Y')
                settings.endGroup()
                print u'发送成功'
                break
            except Exception,e:
                print u'连接失败',Exception,e
                time.sleep(60)
                pass

    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
class pushButtonThread(QtCore.QThread):
    '''重连'''
    appendSignal1=QtCore.pyqtSignal(str)
    pushButtonSignal=QtCore.pyqtSignal(bool)
    def __init__(self,stok,session,parent=None):
        super(pushButtonThread,self).__init__(parent)
        self.session=session
        self.stok=stok
        #self.mutex = QtCore.QMutex()
    def Getradnumb(self, length):#0.21072496053409184   17位
        string=''
        for i in range(0,length):
            string+=str(random.randint(0,9))
        return string
    def run(self):
        if(self.stok==''):
            self.appendSignal1.emit(u'您没有登录，请登录后操作')
            self.appendSignal1.emit(u'*******************************')
            return
        bssid = '74:A7:8E:64:D5:8A'
        name = 'ChinaNet-NTXF'
        password = '23546168'
        wpa_version='3'
        try:
            settings = QtCore.QSettings(r'ts.ini', QtCore.QSettings.IniFormat)
            settings.setIniCodec('UTF-8')
            settings.beginGroup('tmp_wifi')
            bssid = unicode(settings.value('bssid').toString(), 'utf-8', 'ignore')
            name = unicode(settings.value('name').toString(), 'utf-8', 'ignore')
            password = unicode(settings.value('password').toString(), 'utf-8', 'ignore')
            wpa_version = unicode(settings.value('wpa_version').toString(), 'utf-8', 'ignore')
            settings.endGroup()
            print [name]
            print bssid,name,password,wpa_version
            if(bssid=='' or name=='' or wpa_version==''):
                self.appendSignal1.emit(u'您上次没有连接WiFi')
                self.appendSignal1.emit(u'*******************************')
                return
        except:
            self.appendSignal1.emit(u'配置文件错误')
            self.appendSignal1.emit(u'*******************************')
            return
        self.pushButtonSignal.emit(False)
        mutex.lock()
        #global statue,name,device,channel,password,wpa_version,password_date
        self.appendSignal1.emit(u'正在重连，请稍候。。。。。')
        get_url = 'http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/admin/wireless'
        try:
            self.html=self.session.get(get_url,timeout=3)
            #print get_url
            #print self.html.text
            try:
                self.pattern=r'var wifidevs = { "(.*?)": "(.*?)", "(.*?)": "(.*?)" };'

                self.res = re.findall(self.pattern,self.html.text)

                #print self.res
                self.ra0=self.res[0][3]
                #print '111'
                if(len(self.ra0)==3):
                    device = self.res[0][1]
                    wifi_url='http://192.168.5.1/cgi-bin/luci/;stok='+self.stok+'/admin/network/wireless_status/'+self.res[0][2]+','+self.res[0][0]+'?_=0.'+self.Getradnumb(17)
                else:
                    device = self.res[0][3]
                    wifi_url='http://192.168.5.1/cgi-bin/luci/;stok='+self.stok+'/admin/network/wireless_status/'+self.res[0][0]+','+self.res[0][2]+'?_=0.'+self.Getradnumb(17)
                #print '222'
                try:
                    self.html = self.session.get(wifi_url)
                    self.pattern = r'"bitrate": (.*?),'
                    self.bitrate_list = re.findall(self.pattern, self.html.text)
                    if (len(self.bitrate_list) == 0):
                        self.appendSignal1.emit(u'路由器信号: 0%-----网卡信号：0%')
                        self.appendSignal1.emit(u'请重启路由器，按重启键自动重启或拔插电源')
                    elif(self.html.text.find('Client')==-1):
                        self.appendSignal1.emit(u'网卡未插入，请重新拔插网卡与路由器电源')
                    elif(len(self.bitrate_list)==1):#需要搜索一次WiFi才能连接
                        self.q_url='http://192.168.5.1/cgi-bin/luci/;stok='+self.stok+'/admin/network/wireless_join?device='+str(device)
                        self.appendSignal1.emit(u'正在搜索WiFi请稍候......')
                        self.html=self.session.get(self.q_url,timeout=30)
                        #print self.html.text
                        if(self.html.text.find(name)==-1):
                            self.appendSignal1.emit(u'无法搜到这个网络')
                        else:
                            self.pattern=r'<big><strong>'+name+'</strong></big><br /><strong>Channel:</strong> (.*?) |'
                            print 'aa'
                            self.res=re.findall(self.pattern,self.html.text)
                            print 'bb'
                            channel = self.res[0]
                            self.appendSignal1.emit(u'已经获取WiFi列表')
                            name = '"' + name + '"'
                            name=unicode(eval(name), 'utf-8', 'ignore')
                            password_date={
                            'bssid':bssid,
                            'cbi.cbe.network.1.replace':'1',
                            'cbi.submit':'1',
                            'cbid.network.1.key':password,
                            'cbid.network.1.replace':'1',
                            'cbid.network.1._fwzone':'wan',
                            'cbid.network.1._fwzone.newzone':'',
                            'cbid.network.1._netname_new':'wwan',
                            'channel':channel,
                            'device':device,
                            'join':name,
                            'mode':'Master',
                            'wep':'0',
                            'wpa_suites':'PSK',
                            'wpa_version':wpa_version
                            }
                            if(password==''):
                                print u'密码为空'
                                del password_date['cbid.network.1.key']
                                del password_date['wpa_suites']
                            self.apply(password_date)
                    elif(len(self.bitrate_list)==2):#之前已经连接好了
                        pattern=r'"channel": (.*?),'
                        self.res = re.findall(pattern,self.html.text)
                        channel=self.res[1]
                        name = '"' + name + '"'
                        name = unicode(eval(name), 'utf-8', 'ignore')
                        #self.textEdit.append(u'已经获取WiFi列表')
                        password_date={
                        'cbi.cbe.network.1.replace':'1',#
                        'cbi.submit':'1',#
                        'cbid.network.1.replace':'1',#
                        'cbid.network.1._fwzone':'wan',#
                        'cbid.network.1._fwzone.newzone':'',#
                        'cbid.network.1._netname_new':'wwan',#
                        'mode': 'Master',  #
                        'wep': '0',  #


                        'bssid': bssid,  #
                        'cbid.network.1.key': password,
                        'channel':channel,#
                        'device':device,#
                        'join':name,#
                        'wpa_suites':'PSK',
                        'wpa_version':wpa_version#
                        }
                        if (password == ''):
                            print u'密码为空'
                            del password_date['cbid.network.1.key']
                            del password_date['wpa_suites']
                        self.apply(password_date)
                except Exception,e:
                    print Exception,e
                    self.appendSignal1.emit(u'页面无法打开，网线或路由器出了问题')
                    self.appendSignal1.emit(u'按重启键重启路由器')
            except Exception,e:
                print Exception,e
                self.appendSignal1.emit(u'网卡未插入，请插入网卡或拔出再插，然后重启')
                self.appendSignal1.emit(u'按重启键可重启')
        except:
            print Exception, e
            self.appendSignal1.emit(u'页面无法打开，电脑未识别网络，或者网线路由器出了问题')
            self.appendSignal1.emit(u'请重启，按重启键自动重启或拔插电源')
        self.appendSignal1.emit(u'*******************************')
        self.pushButtonSignal.emit(True)
        mutex.unlock()
    def apply(self, password_Date):
        print password_Date
        self.appendSignal1.emit(password_Date['join'])
        self.appendSignal1.emit(u'正在提交密码')
        connect_url='http://192.168.5.1/cgi-bin/luci/;stok='+self.stok+'/admin/network/wireless_join'

        self.session.post(connect_url,data=password_Date)
        self.appendSignal1.emit(u'提交成功')
        #print html.text.encode('utf-8')#保存与应用的页面
        self.appendSignal1.emit(u'正在保存与应用')
        save_url='http://192.168.5.1/cgi-bin/luci/;stok='+self.stok+'/admin/uci/saveapply?redir='

        self.session.get(save_url)
        self.fin_save_url='http://192.168.5.1/cgi-bin/luci/;stok='+self.stok+'/servicectl/restart/firewall,wireless?_=0.'+self.Getradnumb(17)
        
        fin=self.session.get(self.fin_save_url)
        
        if fin.text == "OK":
            self.appendSignal1.emit(u'OK')
            self.appendSignal1.emit(u'已经成功保存与应用，请等待')
        else:
            self.appendSignal1.emit(u'路由器出现问题，未能连接成功')
            self.appendSignal1.emit(u'按重启键可重启路由器')
        self.appendSignal1.emit(u'如果稍后仍然无法上网，请手动进行设置或者重启路由器，也有可能WiFi密码错误')

class searchButtonThread(QtCore.QThread):
    searchAppendSignal = QtCore.pyqtSignal(str)
    data_dicSignal = QtCore.pyqtSignal(dict)
    searchButtonSignal=QtCore.pyqtSignal(bool)
    setDeviceSignal=QtCore.pyqtSignal(str)
    def __init__(self,stok,session,parent=None):
        super(searchButtonThread, self).__init__(parent)
        self.stok=stok
        self.session=session
    def Getradnumb(self, length):#0.21072496053409184   17位
        string=''
        for i in range(0,length):
            string+=str(random.randint(0,9))
        return string
    def run(self):
        if (self.stok == ''):
            self.searchAppendSignal.emit(u'您没有登录，请登录后操作')
            self.searchAppendSignal.emit(u'*******************************')
            return
        #print '5555'
        self.searchButtonSignal.emit(False)
        #self.MainWindow.pushButton_2.setEnabled(False)
        #print '777'
        mutex.lock()
        #print '444'
        get_url = 'http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/admin/wireless'
        #global statue, name, device, channel, password, wpa_version,data_dic
        try:
            self.html = self.session.get(get_url,timeout=3)
            try:
                self.pattern = r'var wifidevs = { "(.*?)": "(.*?)", "(.*?)": "(.*?)" };'
                self.res = re.findall(self.pattern, self.html.text)
                self.ra0 = self.res[0][3]
                if (len(self.ra0) == 3):
                    device = self.res[0][1]
                    wifi_url = 'http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/admin/network/wireless_status/' + \
                               self.res[0][2] + ',' + self.res[0][0] + '?_=0.' + self.Getradnumb(17)
                else:
                    device = self.res[0][3]
                    wifi_url = 'http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/admin/network/wireless_status/' + \
                               self.res[0][0] + ',' + self.res[0][2] + '?_=0.' + self.Getradnumb(17)
                self.setDeviceSignal.emit(device)
                try:
                    self.html = self.session.get(wifi_url)
                    self.pattern = r'"bitrate": (.*?),'
                    self.bitrate_list = re.findall(self.pattern, self.html.text)
                    if (len(self.bitrate_list) == 0):
                        self.searchAppendSignal.emit(u'路由器信号: 0%-----网卡信号：0%')
                        self.searchAppendSignal.emit(u'请重启，按重启键自动重启或拔插电源')
                    elif (self.html.text.find('Client') == -1):
                        self.searchAppendSignal.emit(u'网卡未插入，请重新拔插网卡与路由器电源')
                    else:
                        self.q_url = 'http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/admin/network/wireless_join?device=' + str(
                            device)
                        self.searchAppendSignal.emit(u'正在搜索WiFi请稍候......')
                        self.html = self.session.get(self.q_url,timeout=30)
                        self.searchAppendSignal.emit(u'已经获取WiFi列表')
                        #print self.html.text
                        self.soup = BeautifulSoup(self.html.text,"lxml")
                        self.signal_list=[]
                        for a in self.soup.find_all('small'):
                            self.signal_list.append(a.get_text())
                        data_dic={}
                        j = 0
                        for s in self.soup.find_all('form'):
                            self.name = s.find_all('input', attrs={'name': 'join'})
                            self.bssid = s.find_all('input', attrs={'name': 'bssid'})
                            self.channel = s.find_all('input', attrs={'name': 'channel'})
                            self.wpa_version = s.find_all('input', attrs={'name': 'wpa_version'})
                            self.wpa_suites = s.find_all('input', attrs={'name': 'wpa_suites'})
                            #print self.wpa_suites
                            if (len(self.name) == len(self.bssid) == len(self.channel) == len(self.wpa_version)):
                                for i in range(len(self.name)):
                                    if (len(self.wpa_suites) == 1):
                                        data_dic[self.bssid[i].attrs['value']] = {'wpa_suites': 'PSK',
                                                                             'signal': self.signal_list[j],
                                                                             'join': self.name[i].attrs['value'],
                                                                             'bssid': self.bssid[i].attrs['value'],
                                                                             'channel': self.channel[i].attrs['value'],
                                                                             'wpa_version':self.wpa_version[i].attrs['value']
                                                                             }
                                    else:
                                        data_dic[self.bssid[i].attrs['value']] = {
                                            'signal': self.signal_list[j],
                                            'join': self.name[i].attrs['value'],
                                            'bssid': self.bssid[i].attrs['value'],
                                            'channel': self.channel[i].attrs['value'],
                                            'wpa_version': self.wpa_version[i].attrs['value']
                                        }
                                    j += 1
                        self.data_dicSignal.emit(data_dic)
                except Exception,e:
                    print Exception,e
                    self.searchAppendSignal.emit(u'页面无法打开，网线或路由器出了问题')
                    self.searchAppendSignal.emit(u'按重启键重启路由器')

            except Exception,e:
                print Exception,e
                self.searchAppendSignal.emit(u'网卡未插入，请插入网卡或拔出再插，然后重启')
                self.searchAppendSignal.emit(u'按重启键可重启')
        except:
            self.searchAppendSignal.emit(u'页面无法打开，电脑未识别网络，或者网线路由器出了问题')
            self.searchAppendSignal.emit(u'请重启，按重启键自动重启或拔插电源')
        self.searchButtonSignal.emit(True)
        self.searchAppendSignal.emit(u'*******************************')
        mutex.unlock()
class restartThread(QtCore.QThread):
    restartAppendSignal=QtCore.pyqtSignal(str)
    def __init__(self, stok,session,parent=None):
        super(restartThread, self).__init__(parent)
        self.stok=stok
        self.session=session
    def run(self):
        if (self.stok == ''):
            self.restartAppendSignal.emit(u'您没有登录，请登录后操作')
            self.restartAppendSignal.emit(u'*******************************')
            return
        self.restartAppendSignal.emit(u'正在进行重启。。。。')
        try:
            self.session.get('http://192.168.5.1/cgi-bin/luci/;stok=' + self.stok + '/admin/reboot?reboot=1',timeout=3)
            self.restartAppendSignal.emit(u'重启命令已经发出，等路由器重启完成之后再进行其他操作')
            self.restartAppendSignal.emit(u'*******************************')
        except:
            self.restartAppendSignal.emit(u'路由器已经没有反应，需要拔插电源')
            self.restartAppendSignal.emit(u'*******************************')
