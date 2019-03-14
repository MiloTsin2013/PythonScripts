#! /usr/bin python
# -*-encoding: utf-8 -*-

import os
import re
import time
import xlrd, xlwt
import collections
import linecache

file_path = '10.7.99.120-radware-cfg-log-2.txt'
# file_path = input('Please input path of tartget file:')
# print('Tartget file is:{0}'.format(file_path))
total_ln = os.popen('wc -l {0}'.format(file_path)).read().split()[0]
split_kw = 'Virtual server state:'
end_kw = 'IDS group state:'
splited_fn = 'radware.txt'

vs_info = {}


def slice_text(fn, kw, kw_1):
    with open(fn, 'r', encoding='utf-8') as f:
        for index, line in enumerate(f):
            match_s = re.search(kw, line)
            if match_s is not None:
                dst_line_num = index
            match_e = re.search(kw_1, line)
            if match_e is not None:
                dst_line_end = index
        dst_lines = linecache.getlines(fn)[int(dst_line_num):int(dst_line_end)]
    return dst_lines


def create_dst_txt(content, file_name):
    with open(file_name, 'w') as f_w:
        for line in content:
            f_w.write(line)


def get_id(f):
    ids = []
    with open(f, 'r', encoding='utf-8') as fd:
        for line in fd:
            if ': IP4' in line:
                t_id = re.findall(r"  (.+?): IP4", line)
                ids.append(t_id[0].strip())
    return ids


def get_vs_info(id_num, p, fn):
    with open(fn, 'r') as fo:
        ip_pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        ip_port_pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):\d+\b"
        result = pattern.findall(fo.read())
        vs_dic = vs_info.setdefault(id_num, {})
        if result:
            for line in result[0].split('\n'):
                if ": IP4" in line:
                    vs_dic.setdefault('vs_ip', re.findall(ip_pattern, line)[0])
                    vs_dic.setdefault('vs_name', re.findall(r' vname (.+?)$', line)[0].split(',')[0])
                if ": rport" in line:
                    vs_port = re.findall(r'(\w{4}): rport', line)[0]
                    if not vs_port.isdigit(): 
                        vs_port = '80'
                    vs_dic.setdefault('vs_port', vs_port)
                if (re.findall(ip_pattern,line) or re.findall(ip_port_pattern,line)) and ", health" in line:
                    vs_rs_id = line.split(":")[0].strip()
                    rs_dic = vs_dic.setdefault('vs_rs', {})
                    chld_rs_dic = rs_dic.setdefault(vs_rs_id, {})
                    chld_rs_dic.setdefault('vs_rs_status', line.split(',')[-1])
                    if re.findall(ip_port_pattern,line):
                        vs_rs_info = re.findall(ip_port_pattern, line)
                        chld_rs_dic.setdefault('vs_rs_ip', vs_rs_info[0].split(':')[0])
                        chld_rs_dic.setdefault('vs_rs_port', vs_rs_info[0].split(':')[1])
                    elif re.findall(ip_pattern,line):
                        chld_rs_dic.setdefault('vs_rs_ip', re.findall(ip_pattern, line)[0])
                        chld_rs_dic.setdefault('vs_rs_port', '8001')


def set_style(name, height, bold=False):
    style = xlwt.XFStyle() # 初始化样式

    font = xlwt.Font() # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height

    alignment = xlwt.Alignment() # Create Alignment
    # alignment.horz = xlwt.Alignment.HORZ_CENTER # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED

    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6

    style.font = font
    # style.borders = borders
    style.alignment = alignment

    return style


def content_style():
    return set_style('Times New Roman', 180)


def save_data(dt_dic):
    cur_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    wb = xlwt.Workbook() #创建工作簿
    sheet = wb.add_sheet(u'Radware_configuration_info', cell_overwrite_ok=True)
    table_title = [u'ID', u'VS IP+Port', u'VS Name', u'Realserver ID', u'Realserver IP+Port', u'Realserver Status']
    sheet.col(0).width = 1100
    sheet.col(1).width = 5000
    sheet.col(2).width = 7000
    sheet.col(3).width = 5000
    sheet.col(4).width = 7000
    sheet.col(5).width = 5000

    for i in range(0, len(table_title)):
        sheet.write(0,i,table_title[i],set_style('Times New Roman', 220, True))


    row = 1
    for k in dt_dic.keys():
        print('\n' + '-'*20)
        print('Handling VS_ID: {0} begin'.format(k))
        print(k, vs_info[k]['vs_ip'] + ':' + vs_info[k]['vs_port'], vs_info[k]['vs_name'])
        merge_rows = len(vs_info[k]['vs_rs'].keys())
        row2 = row + merge_rows -1
        sheet.write_merge(row, row2 , 0, 0, k, content_style())
        sheet.write_merge(row, row2, 1, 1, vs_info[k]['vs_ip'] + ':' + vs_info[k]['vs_port'], content_style())
        sheet.write_merge(row, row2, 2, 2, vs_info[k]['vs_name'], content_style())
        for k1 in vs_info[k]['vs_rs'].keys():
            vs_k1 = vs_info[k]['vs_rs'][k1]
            sheet.write_merge(row, row, 3, 3, k1, content_style())
            sheet.write_merge(row, row, 4, 4, vs_k1['vs_rs_ip'] + ':' + vs_k1['vs_rs_port'], content_style())
            sheet.write_merge(row, row, 5, 5, vs_k1['vs_rs_status'], content_style())
            row += 1
        print('Handling VS_ID: {0} end'.format(k))
        print('-'*20)

    xls_name = 'Radware_configuration_information_' + cur_time + '.xls'
    wb.save(xls_name)
    wk_path = os.getcwd()
    print('\nFinshed!!!')
    print('\nAnalysis result saved in: \n{0}\\{1}'.format(wk_path, xls_name))


dst_content = slice_text(file_path, split_kw, end_kw)
create_dst_txt(dst_content, splited_fn)
vs_ids = get_id(splited_fn)
# print(vs_ids)
for index, value in enumerate(vs_ids):
    start_kw = value
    if index < (len(vs_ids) - 1):
        end_kw = vs_ids[index + 1]
        pattern = re.compile(r'(\s{0}: IP4.*?)\s{1}: IP4'.format(start_kw, end_kw), re.MULTILINE|re.DOTALL)
    if index == (len(vs_ids) - 1):
        end_kw = '^$'
        pattern = re.compile(r'(\s{0}: IP4.*?){1}'.format(start_kw, end_kw), re.MULTILINE|re.DOTALL)
    get_vs_info(value, pattern, splited_fn)
# print(vs_info)
# for key in vs_info.keys():
#     print('\n', key, vs_info[key]['vs_ip'] + ':' + vs_info[key]['vs_port'], vs_info[key]['vs_name'])
#     print(len(vs_info[key]['vs_rs'].keys()))
#     for key1 in vs_info[key]['vs_rs'].keys():
#         vs_k = vs_info[key]['vs_rs'][key1]
#         print('\t'*3, key1, vs_k['vs_rs_ip'] + ':' + vs_k['vs_rs_port'], vs_k['vs_rs_status'])
save_data(vs_info)
