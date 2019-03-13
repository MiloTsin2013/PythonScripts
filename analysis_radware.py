#! /usr/bin python
# -*-encoding: utf-8 -*-

import os
import re
import collections
import linecache

file_path = input('Please input path of tartget file:')
print('Tartget file is:{0}'.format(file_path))
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
#     print('\nVS_ID:\t', key, 
#         '\nVS_IP+PORT:', vs_info[key]['vs_ip'] + ':' + vs_info[key]['vs_port'], 
#         '\nVS_NAME:', vs_info[key]['vs_name'])
#     for key1 in vs_info[key]['vs_rs'].keys():
#         vs_k = vs_info[key]['vs_rs'][key1]
#         print('\t'*3, 
#             'VS_RS_ID:', key1, 
#             '\tVS_RS_IP+PORT:', vs_k['vs_rs_ip'] + ':' + vs_k['vs_rs_port'], 
#             '\tVS_RS_STATUS:', vs_k['vs_rs_status'])
for key in vs_info.keys():
    print('\n', key, vs_info[key]['vs_ip'] + ':' + vs_info[key]['vs_port'], vs_info[key]['vs_name'])
    for key1 in vs_info[key]['vs_rs'].keys():
        vs_k = vs_info[key]['vs_rs'][key1]
        print('\t'*3, key1, vs_k['vs_rs_ip'] + ':' + vs_k['vs_rs_port'], vs_k['vs_rs_status'])
