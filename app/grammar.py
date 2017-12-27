#!/usr/bin/env python3
# coding=utf-8
# author: XiGuang Liu<g10guang@foxmail.com>
# 2017/12/18 20:54
# function: 语法分析

from app import TABLE, ID_CODE, DIGIT_CODE, DELIMITER_CODE, ASSIGNMENT_CODE, OPERAND_CODE_SET
from app import lexical


class GrammarError(Exception):
    """
    语法错误异常
    """
    def __init__(self, message='表达式错误，无法分析') -> None:
        super().__init__(message)


class VariableNoDeclareError(Exception):
    """
    引用了没有声明的变量
    """
    def __init__(self, message) -> None:
        super().__init__(message)


class Grammar:
    """
    语法分析
    """

    def __init__(self, lexical_result):
        """
        :param lexical_result: 词法分析得到的二元组list
        """
        self.lexical_list = lexical_result
        # 记录是否通过了语法分析
        self.is_pass = False
        # 正在扫描的词法分析结果 [(种别码, 值)] 的序列的下标
        self.index = 0
        # 用于表达式分析的栈
        self.stack = []
        # 用于保存已经声明的变量，用于语法分析中是否引用了没有经过声明的变量
        # self.variable['a'] = 1 代表该变量可以引用，self.variable['a'] = 0 代表变量不能被引用
        self.variable = {}

    def analyse(self):
        """
        语法分析
        """
        self.index = 0
        if not self.lexical_list[self.index][0] == TABLE['begin']:
            # 如果不是以 begin 开头，则抛出异常
            raise GrammarError()
        self.increment_index()
        while self.index < len(self.lexical_list):
            # 识别句子
            self.statement()
            # ';' 结束符种别码
            if self.lexical_list[self.index][0] == DELIMITER_CODE:
                self.increment_index()
            else:
                # 如果识别句子后没有遇到 ; 则尝试判断是否后面紧接着 end#，如果是则成功接受，否则判断失败
                if self.index == len(self.lexical_list) - 2:
                    # 判断最后是否以 end # 结束
                    self.increment_index()
                    if self.lexical_list[-2][0] == TABLE['end'] and self.lexical_list[-1][0] == TABLE['#']:
                        # 成功分析
                        self.is_pass = True
                        return
                else:
                    raise GrammarError()

    def statement(self):
        """
        分析普通语句
        :return:
        """
        # ID 种别码
        if self.lexical_list[self.index][0] == ID_CODE:
            last_id = self.lexical_list[self.index][1]
            # 添加当前被赋值的变量为已经声明了的变量
            self.add_new_variable(last_id)
            self.increment_index()
            # ':=' 赋值符号种别码
            if self.lexical_list[self.index][0] == ASSIGNMENT_CODE:
                self.increment_index()
                # 识别后面紧跟着是否是表达式 expression
                self.expression()
                # 如果分析完表达式后，栈中剩下的不是 Digit|ID 那么就分析失败
                # 分析完一个表达式后需要清空栈
                if not self.is_stack_satisfy_expression():
                    raise GrammarError()
                # 更新新的变量可以被引用
                self.enable_variable(last_id)

    def expression(self):
        """
        分析表达式
        一般表达式为中序表示，如 1+2*3/7>=10
        但是特殊情况下需要识别左右括号是否匹配 (1+2/3)*3
        此处借助栈分析
        遇到 ID|Digit op ID|Digit 规约为一个 Digit
        (Digit) 规约为一个 Digit
        :return:
        """
        code = self.lexical_list[self.index][0]
        if code == TABLE['(']:
            # 压入左括号
            self.stack.append(code)
        elif code in (DIGIT_CODE, ID_CODE):
            # 判断栈中是否有 ID|Digit op ID|Digit 成立
            if code == ID_CODE:
                # variable_id 未被声明，则抛出异常
                if not self.has_variable_declare(self.lexical_list[self.index][1]):
                    raise VariableNoDeclareError('引用尚未声明变量:{}'.format(self.lexical_list[self.index][1]))
            if len(self.stack) >= 2:
                if self.stack[-1] in OPERAND_CODE_SET and self.stack[-2] in (DIGIT_CODE, ID_CODE):
                    # 规约为一个 DIGIT_CODE
                    self.stack.pop()
                    self.stack[-1] = DIGIT_CODE
                else:
                    # 虽然栈内容 >= 2，但是栈中压入过 '(' 括号
                    self.stack.append(code)
            else:
                # 栈中内容不足以规约
                self.stack.append(code)
        elif code == TABLE[')']:
            # 期待栈中内容为 (Digit)
            if len(self.stack) < 2:
                # 抛出语法错误异常
                raise GrammarError()
            if self.stack[-1] == DIGIT_CODE and self.stack[-2] == TABLE['(']:
                # 将 (Digit) 规约为 Digit
                self.stack.pop()
                self.stack[-1] = DIGIT_CODE
            else:
                # 防止范围太大的括号
                try:
                    # 寻找栈中是否有左括号
                    self.stack.remove(TABLE['('])
                    # 上一部没有抛出异常，证明成功消除了一个括号
                except ValueError:
                    raise GrammarError('括号不匹配')
        elif code in OPERAND_CODE_SET:
            # 压入操作符
            self.stack.append(code)
        else:
            # 遇到无法处理的种别码
            raise GrammarError()
        self.increment_index()
        # 判断下一个种别码是否可能是表达式的一部分，如果有可能递归调用 expression 进行分析
        next_code = self.lexical_list[self.index][0]
        if next_code in (DIGIT_CODE, ID_CODE, TABLE['('], TABLE[')']) or next_code in OPERAND_CODE_SET:
            self.expression()

    def get_result(self):
        """
        获取语法分析结果
        :return:
        """
        return self.is_pass

    def increment_index(self):
        """
        index 索引自增1
        :return:
        """
        self.index += 1
        return self.index

    def empty_stack(self):
        """
        清空栈内容
        :return:
        """
        self.stack.clear()

    def is_stack_satisfy_expression(self):
        """
        判断栈是否满足表达式 expression 要求
        :return:
        """
        if len(self.stack) == 1 and self.stack[0] in (DIGIT_CODE, ID_CODE):
            self.empty_stack()
            return True
        elif len(self.stack) & 1:
            # 因为如果最后是以 ')' 结束，将会造成在 expression() 函数结束后栈中依然有表达式值未出栈
            while len(self.stack) > 1:
                if self.stack[-1] in (DIGIT_CODE, ID_CODE) and self.stack[-2] in OPERAND_CODE_SET and self.stack[-3] in (DIGIT_CODE, ID_CODE):
                    self.stack.pop()
                    self.stack.pop()
                    self.stack[-1] = DIGIT_CODE
                else:
                    return False
            self.empty_stack()
            return True
        return False

    def has_variable_declare(self, variable_id):
        """
        判断变量是否已经被声明过
        :param variable_id:
        :return:
        """
        try:
            if self.variable[variable_id] == 1:
                return True
        except KeyError:
            return False
        return False

    def add_new_variable(self, variable_id):
        """
        添加新变量，但是在调用 enable_variable 前 variable_id 都不能被引用
        :param variable_id:
        :return:
        """
        if variable_id not in self.variable:
            self.variable[variable_id] = 0

    def enable_variable(self, variable_id):
        """
        让变量可以被调用
        :param variable_id:
        :return:
        """
        self.variable[variable_id] = 1


def main():
    # 获取词法分析结果
    lexical_result = lexical.main()
    grammar = Grammar(lexical_result)
    grammar.analyse()
    is_pass = grammar.get_result()
    if is_pass:
        print('success')
    else:
        print('error')


if __name__ == '__main__':
    main()