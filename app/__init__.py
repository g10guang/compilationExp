#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/12/19 16:13
# function:

# 定义公用数据

# 词法分析中单词符号与种别码的对应
TABLE = {
    'begin': 1,
    'if': 2,
    'then': 3,
    'while': 4,
    'do': 5,
    'end': 6,
    # 此处省略 id, digit
    '+': 13,
    '-': 14,
    '*': 15,
    '/': 16,
    ':': 17,
    ':=': 18,
    '<': 20,
    '<>': 21,
    '<=': 22,
    '>': 23,
    '>=': 24,
    '=': 25,
    ';': 26,
    '(': 27,
    ')': 28,
    '#': 0,
}

# ID 种别码
ID_CODE = 10

# 数字种别码
DIGIT_CODE = 11

# 结束符 ';' 种别码
DELIMITER_CODE = TABLE[';']

# ':=' 赋值号种别码
ASSIGNMENT_CODE = TABLE[':=']

# 运算符种别码集合
OPERAND_CODE_SET = {
    TABLE['+'], TABLE['-'], TABLE['*'], TABLE['/'], TABLE[':'], TABLE['<'], TABLE['<>'], TABLE['<='], TABLE['>'],
    TABLE['>='], TABLE['=']
}

