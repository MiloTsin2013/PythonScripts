#! /usr/bin/env python

import sys
import chardet

# 二进制方式读取，获取字节数据，返回文件编码类型
def get_encode_type(f_name):
	with open(f_name, 'rb') as f:
		print(chardet.detect(f.read()))
		return chardet.detect(f.read())['encoding']

def main(f_name):
	print("Encoding type of {0}: {1}".format(f_name, get_encode_type(f_name)))
	return get_encode_type(f_name)


if __name__ == '__main__':
	main(sys.argv[1])
