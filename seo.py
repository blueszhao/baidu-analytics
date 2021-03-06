#!/usr/bin/python
# -*- coding:utf-8 -*-
import csv 
import re
import urlparse
import sys
from datetime import datetime

#0 行号
#1 访问时间
#2 地域
#3 访问IP
#4 入口页面
#5 最后停留在
#6 上一次访问时间
#7 访问类型:老访客 新访客
#8 访问频次
#9 操作系统
#10 网络服务商
#11 浏览器
#12 语言环境       X
#13 屏幕分辨率
#14 屏幕颜色       X
#15 Flash版本     X
#16 是否支持Cookie X
#17 是否支持JAVA   X
#18 本次来路
#19 打开时间       newline[20]
#20 停留时长       newline[21]
#21 页面地址       newline[22]

COL_DATE=0
COL_TIME=1
COL_IP =3
COL_SOURCE=14   # 14, 15, 16, 17, 18, 19, 20
                # 来源, 关键词, 搜索词, 计划, 单元, 注册, 手机
COL_REG = 19
COL_BIND=20
COL_OPEN=21
COL_COST=22
COL_ACTIONS=23

def extractInfo(query):

    r = urlparse.parse_qs(query)


def extractSource(s,url):
    """ 来源: 直接访问/百度自然搜索/360搜索/搜狗/外链
        关键词: 关键词/外链地址
        搜索词
        计划
        单元
        注册: 0 未知 1 注册
        手机: 0 未知 1 绑定
    """
    p1 = ['','',''] # 来源 关键词 搜索词
    p2 = ['','']    # 计划 单元
    p3 = ['','']    # 注册, 手机

    if s!='':
        s = s.decode('gbk')
        q = urlparse.urlparse(url).query
        r = urlparse.parse_qs(q)

        if s.startswith('http'):
            r = urlparse.urlparse(s)
            if r.netloc == 'zhidao.baidu.com' and r.query.find('zsyx')>-1:
                # 分析知识营销外链 https://zhidao.baidu.com/question/692380938641169084.html?zsyx=nHnsnHbvrjndrj6kPHRLnHn4P19xPH0s
                p1=[u'百度知识营销',r.netloc,s]
            else:
                p1 = [u'外链',r.netloc, s]

        elif s == u'直接访问':
            p1 = [u'直接访问','','']
            
            if q and r.get('utm_source','') != '':
                    p1 = [u'推广访问','','']
                    p21 = (r.get('utm_campaign',[''])[0]).decode('utf8')
                    p22 = (r.get('utm_content',[''])[0]).decode('utf8')
                    p2 = [p21,p22]
        else:
            rr =  re.match(ur'([\w\u4e00-\u9fa5]+)\(关键词:([\w\s\.\u4e00-\u9fa5]*|--) 搜索词:([\w\s\.\u4e00-\u9fa5]*)',s)
            if rr:
                rr1 = rr.groups()[0]
                rr2 = ''  if rr.groups()[1] == '--' else rr.groups()[1]
                rr3 = rr.groups()[2]

                if q and r.get('utm_source','') != '':
                    rr1 = rr1 + u'推广'
                    p21 = (r.get('utm_campaign',[''])[0]).decode('utf8')
                    p22 = (r.get('utm_content',[''])[0]).decode('utf8')
                    p2 = [p21,p22]

                if rr1 in (u'搜索推广',u'百度自然搜索推广',u'搜索推广推广'):
                    rr1 = u'百度搜索推广'

                p1 = [rr1,rr2,rr3]
        p3[0] = extractRegisted(url)
        p3[1] = extractBinded(url)

    r = p1 + p2 + p3 

    s = []
    try:
        s = [i.encode('gbk') for i in r]
    except:
        print r
        raise

    return s

def extractCost(s):
    cost = 0
    s = s.decode('gbk')
    if s != u'正在访问':
        r = re.match('(\d+)s',s)
        if r:
            cost = int(r.groups()[0])
    return cost

def extractRegisted(url):
    if url.find('thanks')>0:
        return '1'
    return ''

def extractBinded(url):
    if url.find('phone')>0:
        return '1'
    return ''

def extractFiels(files):

    # 从列表写入csv文件: 14, 15, 16, 17, 18, 19, 20
    s11 = [u'来源', u'关键词', u'搜索词', u'计划', u'单元', u'注册', u'手机']
    s12 = [i.encode('gbk') for i in s11]

    files_num = 0
    files_changed = 0
    rows_num = 0
    # files = ['data1.csv', 'data2.csv']
    file_last_time = ''
    file_last_ips = []

    with open("test.csv","w") as csvfile:
        writer = csv.writer(csvfile)

        for f in files:
            csvDataFile = open(f, "r")
            reader = csv.reader(csvDataFile)  # 返回的是迭代类型
            data = [item for item in reader]
            csvDataFile.close()

            i = 0
            newline = []
            m = len(data)
            print 'f=%s,files_num=%d,m=%d' % (f, files_num, m)
            print file_last_time, file_last_ips
            while i<m:
                output = False
                try:
                    if (i==m-1) or (i<(m-1) and data[i+1] and data[i+1][0]!=''):
                        output = True
                except:
                    print f, i, m
                    raise

                line = data[i]
                if line == []: break

                try:
                    action = line[21]
                except:
                    print f, line
                    raise

                if i==0 or re.match('\d+',data[i][0]):

                    source = line[18:19][0]
                    if i == 0:
                        s = line[18:19]+s12
                        newline = line[0:12]+line[13:14]+s+line[19:]
                    else:
                        s = line[18:19]+extractSource(source, action)
                        d, t = (line[1]).split(' ')
                        cost = extractCost(line[20:21][0])
                        newline = [d]+line[1:12]+line[13:14]+s+line[19:20]+[cost]+line[21:]
                else:
                    newline[COL_COST] += extractCost(line[20])
                    newline[COL_ACTIONS] += ',' + line[21]
                    if extractRegisted(action)=='1':
                        newline[COL_REG] = '1'
                    if  extractBinded(action)=='1':
                        newline[COL_BIND] = '1'         

                i = i + 1

                if output:
                    # 后续文件的标题行跳过
                    if i==1 and files_num !=0: 
                        continue
                    if i>1 or files_num>0:
                        # 如果数据重复则跳过
                        newline_time = datetime.strptime(newline[COL_TIME],"%Y/%m/%d %H:%M")
                        if files_changed>0:
                            try:
                                if newline_time>file_last_time: continue
                                if newline_time==file_last_time and newline[COL_IP] in file_last_ips:
                                    file_last_ips = file_last_ips[1:]
                                    print 'repeat', rows_num, newline[COL_TIME], newline[COL_IP-1].decode('gbk'), newline[COL_IP]
                                    continue
                                file_last_time = ''
                                file_last_ips=[]
                                files_changed = 0
                                print 'newfile', rows_num, newline[COL_TIME], newline[COL_IP-1].decode('gbk'), newline[COL_IP]
                            except:
                                print i-1, file_last_time, file_last_ips
                                print newline
                                raise

                        if newline_time == file_last_time:
                            file_last_ips.append(newline[COL_IP])
                        else:
                            file_last_time = newline_time
                            file_last_ips=[newline[COL_IP]]

                    writer.writerow(newline)
                    rows_num = rows_num + 1
                    # print rows_num

            files_num = files_num + 1
            files_changed = 1

        csvfile.close()


if __name__ == '__main__':
    extractFiels( sys.argv[1:])
