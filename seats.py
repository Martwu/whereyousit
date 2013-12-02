#!/usr/bin/env python
# -*- coding:UTF8 -*-
#抽电影座位票

import random
import sys, os
import re
import json


# 将环境编码强制设定为utf-8
reload(sys)
sys.setdefaultencoding('utf8')


def push_error(str = None):
    if str is not None:
        print "[ERROR] " + str
    exit(1)


def push_info(str):
    print "[INFO] " + str


def push_warm(str):
    print "[WARM] " + str


def push_debug(str = None):
    if str is not None:
        print "[DEBUG] " + str
    exit(1)


def push_help(i = 0):
    if i == 0:
        print '[USAGE] seats.py /path/to/file seatslist'
    print '        seatslist格式："排数:序号-序号 排数-排数:序号-序号 ……"'
    exit(1)


# 自搞一个小异常，主要是在函数 _make_seat_list 中用一下，用以提醒一下
# 可能存在无法实现全部家属坐一起的情况，但是现在的处理还不是很好
class JustError(Exception):
    def __init__(self):
        Exception.__init__(self, 'May not let all pairs sit together.')


# 获取表达式string，返回None或者表达式list，列表元素tuple 
def _get_expr(str = None):
    if str is None:
        # 如果传入为空，返回空，这很公平啊！
        return None
    else:
        # 表达式用正则匹配，形如 8*3+5
        splited_list = []
        regex = re.compile('^\d+(\*\d+)?(\+\d+(\*\d+)?)*$')
        if regex.match(str) is None:
            push_help(1)
        else:
            # 加号分割单位
            splited_list = str.split('+')
            # 逐个单位，转换成 二元tuple，没有乘号的添加乘数1
            lenoflist = len(splited_list)
            for i in range(lenoflist):
                tmpstr = splited_list.pop(0)
                if '*' in tmpstr:
                    tmplist = tmpstr.split('*')
                    splited_list.append((int(tmplist[0]), int(tmplist[1])))
                else:
                    splited_list.append((int(tmpstr), 1))
    # 在这返回就形如[(,),(,),..]的列表
    return splited_list


# 获取表达式string，返回None或者座位分布结构list，列表元素tuple 
def _get_expr_sturct(_str = None):
    if _str is None:
        # 如果传入为空，返回空，这很公平啊！
        splited_list = None
    else:
        # 用正则来匹配表达式，形如 "8-9:1-2 10:3" 
        splited_list = []
        regex = re.compile('^(\d+(-\d+)?:\d+(-\d+)? ?)+$')
        if regex.match(_str) is None:
            push_help(1)
        else:
            # 用空格分割单位
            tmplist = _str.split(' ')
            for i in tmplist:
                # 逐个单位分析，转换成二元tuple
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
                    push_error("序号需要从小到大写。")
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
                push_debug("在函数 make_seat_list")
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
                        push_error("座位数多于人数，请检查。")
                    except:
                        push_debug("在函数 make_seats_list")
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
        push_error("人数多于座位数，请检查。")
    return members_list


#获取 表达式list，返回打印格式模板string
def _get_template(_str = None):
    if _str is not None:
        seat_no = 0
        print_template = ''
        regex = re.compile('^(\d+(-\d+)?:\d+(-\d+)? ?)+$')
        if regex.match(_str) is None:
            push_help()
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
                    line0 = int(tmpi[1])
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


# 从json文件或者__url中获取报名表
def _get_members(FILENAME):
    try:
        JDICT = json.load(open(FILENAME, 'r'))
        CARDLIST = JDICT['actions']
    except IOError:
        push_error('打开文件失败，请检查路径。')
    except ValueError:
        push_error('无法识别的json文件。')
    except KeyError:
        push_debug('json数据格式已改变。')

    memberlist = []
    numberall = 0
    numberpair = 0

    for i in range(len(CARDLIST)):
        try:
            text = CARDLIST[i]['data']['text']
        except KeyError:
            continue
        except:
            push_debug('获取text时程序出错。')

        text = "".join(text.split())

        while text:
            seed = []
            match = re.match(u'([^\d]+)(\d+)', text)
            pushedtext = match.group(0)
            text = text.lstrip(pushedtext)
            numberp = int(match.group(2))
            for i in range(numberp):
                seed.append(match.group(1))
            memberlist.append(seed)
            numberall += numberp
            numberpair += numberp - 1

    return memberlist, numberall, numberpair


if __name__ == '__main__':

    # allseats = "8:5-14 8:19-24 9:4-11 9:18-24 10:5-14 10:17-24"

    try:
        allmembers, numbersall, numberspair  = _get_members(sys.argv[1])
    except IndexError:
        push_help()
    try:
        expr = _get_expr_sturct(sys.argv[2])
        seat = _get_template(sys.argv[2])
        # expr = _get_expr_sturct(allseats)
        # seat = _get_template(allseats)
    except IndexError:
        push_info('总报名人数：' + str(numbersall) + '人，家属人数：'\
                + str(numberspair) +  '人。')
        exit(0)

    RETRYTIMES = 30

    for i in range(RETRYTIMES):
        try:
            namelist = _make_seat_list(allmembers, expr)
        except JustError:
            pass
            if i == RETRYTIMES - 1:
                push_warm("多次重试找不到符合要求的座位分配，现是随机分配。")
                namelist = _make_seat_list(allmembers, None)
        else:
            break
    try:
        print seat.format(*namelist)
    except IndexError:
        push_error("打印排队结果时出错。")
