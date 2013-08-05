#!/usr/bin/env python
# -*- coding:UTF8 -*-
#File:			seatchose.py
#Create Date:	2013年05月09日 星期四 14时15分48秒
# 2013年8月1日 改写
#当天抽电影座位票

import random
import sys, os
import re 

# 自搞一个小异常，主要是在函数 _make_seat_list 中用一下，用以提醒一下
# 可能存在无法实现全部家属坐一起的情况，但是现在的处理还不是很好
class JustError(Exception):
    def __init__(self):
        Exception.__init__(self, 'May not let all pairs sit together.')


# 获取表达式string，返回None或者座位分布结构list，列表元素tuple *
def _get_expr_sturct(_str = None):
    if _str is None:
        splited_list = None
    else:
        splited_list = []
        regex = re.compile('^(\d+(-\d+)?:\d+(-\d+)? ?)+$')
        if regex.match(_str) is None:
            print '表达式不符合要求。例子： 行号:序号-序号[空格]行号:……'
            exit(1)
        else:
            tmplist = _str.split(' ')
            for i in tmplist:
                tmpi = i.split(':')
                if '-' in tmpi[0]:
                    tmprow = tmpi[0].split('-')
                    row = int(tmprow[1]) - int(tmprow[0]) + 1
                else:
                    row = 1
                if '-' in tmpi[1]:
                    tmpline = tmpi[1].split('-')
                    line = int(tmpline[1]) - int(tmpline[0]) + 1
                else:
                    line = 1
                try:
                    assert row >= 1 and line >= 1
                except AssertionError:
                    print '序号要从小到大填写'
                    exit(1)
                splited_list.append((line, row))
    return splited_list



# 获取表达式list和成员名单list，返回排序好的座位顺序list
# 由于这里想实现的是同事跟其家属坐在一起。
# 但是会存在情况，使得此愿望无法实现，故得设置阈值。
def _make_seat_list(members, expr):
    members_list = []
    members_copy = members[:]
    if expr is None:
        while True:
            try:
                chosen = random.choice(members_copy)
            except IndexError:
                break
            except:
                print 'Some ERROR in func "_make_seat"(1)'
                exit(1)
            else:
                members_list = members_list + chosen
                members_copy.remove(chosen)
    else:
        expr_copy = expr[:]
        retry = 0
        for i in expr_copy:
            for j in range(i[1]):
                leftseats = i[0]
                while leftseats > 0:
                    try:
                        chosen = random.choice(members_copy)
                    except IndexError:
                        print '座位数多于人数，检查清楚。'
                        exit(1)
                    except:
                        print 'Some ERROR in func "_make_seat"(2)'
                        exit(1)
                    else:
                        if len(chosen) <= leftseats:
                            leftseats = leftseats - len(chosen)
                            members_list = members_list + chosen
                            members_copy.remove(chosen)
                        else: ## 设置阈值 ##
                            retry = retry + 1
                            if retry > 60:
                                raise JustError
    if len(members_copy) != 0:
        print '人数多于座位数，检查清楚。'
        exit(1)
    return members_list


#获取 表达式list，返回打印格式模板string *
def _get_template(_str = None):
    if _str is not None:
        seat_no = 0
        print_template = ''
        regex = re.compile('^(\d+(-\d+)?:\d+(-\d+)? ?)+$')
        if regex.match(_str) is None:
            print '表达式不符合要求。例子： 行号:序号-序号[空格]行号:……'
            exit(1)
        else:
            tmplist = _str.split(' ')
            for i in tmplist:
                tmpi = i.split(':')
                if '-' in tmpi[0]:
                    tmprow = tmpi[0].split('-')
                    row1 = int(tmprow[1]) + 1
                    row0 = int(tmprow[0])
                else:
                    row1 = int(tmpi[0]) + 1
                    row0 = int(tmpi[0])
                if '-' in tmpi[1]:
                    tmpline = tmpi[1].split('-')
                    line1 = int(tmpline[1]) + 1
                    line0 = int(tmpline[0])
                else:
                    line1 = int(tmpi[1]) + 1
                    line0 = int(tmpi[0])
                for row in range(row0, row1):
                    for line in range(line0, line1):
                        print_template = print_template + str(row) + '.' + \
                                str(line) + ' {' + str(seat_no) + '}'
                        seat_no = seat_no + 1
                        if line == line1 - 1:
                            print_template = print_template + '\n'
                        else:
                            print_template = print_template + '\t'
    else:
        print_template = None
    return print_template


# 从json文件中获取报名表 *
def _get_members(filename):
    try:
        file = open(filename)
    except IOError:
        print "打开文件失败，请检查文件路径、名字是否正确。"
        exit(1)
    else:
        thestring = file.readline()
        list = thestring.replace('}','{').replace(',','{').replace('[','{')\
                .replace(']','{').split('{')
        allmember = []
        for i in list:
            if "text" in i:
                tmp = i.lstrip('"text":"').rstrip('"')
                thegroup = tmp.split()
                seed = []
                try:
                    number = int(thegroup[1])
                except ValueError:
                    print '"',tmp,'"填写不符合要求，跳过统计。'
                except IndexError:
                    print '"',tmp,'"填写不符合要求，跳过统计。'
                else:
                    try:
                        int(thegroup[2])
                    except:
                        for j in range(number):
                            seed.append(thegroup[0])
                        allmember.append(seed)
                    else:
                        print '"',tmp,'"填写不符合要求，跳过统计。'
                        
        return allmember




if __name__ == '__main__':
    try:
        allmembers = _get_members(sys.argv[1])
    except IndexError:
        print '运行： seats.py jsonfile expr\nexpr模板： 行座位数*行数+……'
        exit(1)
    try:
        expr = _get_expr_sturct(sys.argv[2])
        seat = _get_template(sys.argv[2])
    except IndexError:
        print '运行： seats.py jsonfile expr\nexpr模板： 行座位数*行数+……'
        exit(1)
    retrytimes = 30
    for i in range(retrytimes):
        try:
            namelist = _make_seat_list(allmembers, expr)
        except JustError:
            pass
            if i == retrytimes - 1:
                print "多次重试找不到符合要求的座位分配，现是随机分配。"
                namelist = _make_seat_list(allmembers, None)
        else:
            break
    try:
        print seat.format(*namelist)
    except IndexError:
        print '程序出错，需要调试。'
