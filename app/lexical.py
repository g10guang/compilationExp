#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/12/18 18:30
# function: 词法分析

import os
import re
from app import TABLE, ID_CODE, DIGIT_CODE

# /* .. */ 多行注释
# // 单行注释


class KeywordError(Exception):
    """
    关键字出错
    """

    def __init__(self, message) -> None:
        super().__init__(message)


class CommentMismatchError(Exception):
    """
    Cannot match the comment
    """

    def __init__(self, message='注释书写错误'):
        super().__init__(message)


class Lexical:
    """
    词法分析
    """
    # 匹配 ID 正则表达式
    IS_ID_RGX = re.compile('^[A-Za-z]+[A-Za-z0-9]*$')

    # 匹配数字的正则表达式
    IS_DIGIT_RGX = re.compile('^\d+$')

    # 需要添加空格分隔的字符集
    ADD_BLANK_LIST = [
        ':=',
        '>=',
        '<>',
        '<=',
        '+',
        '-',
        '*',
        '/',
        ':',
        '<',
        '>',
        '=',
        ';',
        '(',
        ')',
        '#',
    ]

    def __init__(self, program_file):
        """
        :param program_file: 程序文件所在位置
        """
        self.result = []
        self.program_file = program_file

    def scanner(self, content):
        """
        扫描字符串
        :param context: 需要分析的程序内容
        :return: 对应的种别码
        """
        # 判断content是否对应词法分析表
        if content in TABLE:
            return TABLE[content]
        if self.is_id(content):
            return ID_CODE
        if self.is_digit(content):
            return DIGIT_CODE
        raise KeywordError('{} 无法匹配'.format(content))

    def analyse(self):
        """
        词法分析
        :return:
        """
        with open(self.program_file, encoding='utf-8') as f:
            self.result = []
            # 读入程序内容
            content = f.read()
            # 去除注释，包括单行注释和多行注释
            content = self.remove_comment(content)
            # 通过 \t \n \r ' ' 来分隔
            content_list = content.split()
            # 可以词法分析 x:=x+1; 可以不适用空格进行分隔
            self.split_by_operand_or_delimiter(content_list)
            # 生成 (种别码, 值) 序列
            for letters in content_list:
                # 防止空字符串异常
                if letters:
                    code = self.scanner(letters)
                    self.result.append((code, letters))
        return self.result

    def is_id(self, letters):
        """
        判断是否为 id
        :param letters:
        :return:
        """
        return True if self.IS_ID_RGX.match(letters) else False

    def is_digit(self, letters):
        """
        判断是否是数字
        :param letters:
        :return:
        """
        return True if self.IS_DIGIT_RGX.match(letters) else False

    def get_result(self):
        """
        获取词法分析结果
        :return:
        """
        return self.result

    def split_by_operand_or_delimiter(self, content_list):
        """
        在运算符和分隔符 ';' 前后加上一个空格
        :param content_list:
        :return:
        """
        # 使用 index 进行一个一个扫描，index记录扫描的字符串的下标
        index = 0
        while index < len(content_list):
            seq = content_list[index]
            # 通过 := + - 运算符 和 终结符 ; 分隔
            for item in self.ADD_BLANK_LIST:
                find_index = seq.find(item)
                if find_index != -1:
                    if len(seq) == len(item):
                        index += 1
                        break
                    # 需要对 seq 进行切分
                    item_len = len(item)
                    content_list[index] = seq[:find_index]
                    content_list.insert(index + 1, item)
                    content_list.insert(index + 2, seq[find_index + item_len:])
                    break
            else:
                index += 1
        if not content_list[-1]:
            content_list.pop()

    def remove_comment(self, content):
        """
        去除注释
        :return:
        """
        # 多行注释开头
        multi_row_comment_index = content.find('/*')
        # 单行注释开头
        one_row_comment_index = content.find('//')
        if multi_row_comment_index != -1:
            if one_row_comment_index != -1:
                if multi_row_comment_index < one_row_comment_index:
                    content = self.remove_multi_row_comment(content)
                else:
                    content = self.remove_row_comment(content)
            else:
                content = self.remove_multi_row_comment(content)
        elif one_row_comment_index != -1:
            content = self.remove_row_comment(content)
        else:
            return content
        return self.remove_comment(content)

    def remove_multi_row_comment(self, content):
        """
        去除多行注释
        :return:
        """
        # the start index of comment
        comment_start_index = content.find('/*')
        if comment_start_index != -1:
            comment_end_index = content.find('*/', comment_start_index)
            if comment_end_index == -1:
                # Cannot find the end match character of comment */
                raise CommentMismatchError('/* 不存在 */ 对应的注释结束符')
            elif comment_end_index <= comment_start_index:
                raise CommentMismatchError('*/ 先于 /* 注释书写错误错误')
            # 找到注释内容，并把注释去除
            content = content[:comment_start_index] + content[comment_end_index + 2:]
            # comment_start_index = content.find('/*')
        return content

    def remove_row_comment(self, content):
        """
        去除行注释
        :param content:
        :return:
        """
        comment_index = content.find('//')
        if comment_index != -1:
            # 针对文件的两种结束符 \n \r\n
            linesep_index_n = content.find('\n', comment_index)
            linesep_index_rn = content.find('\r\n', comment_index)
            if linesep_index_n != -1:
                if linesep_index_rn != -1:
                    linesep_index = linesep_index_rn if linesep_index_rn < linesep_index_n else linesep_index_n
                else:
                    # 不存在 \r\n
                    linesep_index = linesep_index_n
            else:
                linesep_index = linesep_index_rn
            linesep_len = 1 if linesep_index == linesep_index_n else 2
            if linesep_index != -1:
                # 更新 content 的值
                content = content[:comment_index] + content[linesep_index+linesep_len:]
            else:
                # 程序中最后一行程序为注释
                content = content[:comment_index]
            # comment_index = content.find('//')
        return content


def main():
    while True:
        program_file = input('请输入程序所在文件：')
        if not os.path.isfile(program_file):
            print('文件不存在')
        else:
            break
    lexical = Lexical(program_file)
    lexical.analyse()
    print(lexical.get_result())
    return lexical.get_result()


if __name__ == '__main__':
    main()