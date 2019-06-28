# 1.收集语料库，获取先验概率
# 2.根据编辑距离确定错误单词对应的正确单词
# -*- coding: utf-8 -*-
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
import os

letter_str = 'abcdefghijklmnopqrstuvwxyz'

def text_content():
    if os.path.exists('D:/数据/words.csv'):
        words_df = pd.read_csv('D:/数据/words.csv')
    else:
        # 读取语义文件，统计词频作为改正的根据
        with open('D:/数据/big.txt') as f:
            text = f.read()
        # 通过正则找出所有单词
        all_words = re.findall('[a-z]+', text.lower())  # 忽略大小写
        # print(len(all_words)) 1091250
        myfile = ' '.join(all_words)  # 将其转化为空格分隔的文件，方便使用sklearn统计
        count_vec = CountVectorizer()
        # 得到单词与对应频数的dataframe(series)
        words_df = pd.DataFrame(count_vec.fit_transform([myfile]).toarray(),
                                columns=count_vec.get_feature_names())
        # 存储语义库，下次直接加载
        words_df.to_csv('D:/数据/words.csv')
    words_dic = words_df.to_dict(orient='record')[0]  # 转化后为每行一个字典组成的列表
    # print(words_dic)
    # value_to_word_dict = {v:k for k,v in words_dic.items()}  # 可能出现多个键对应同一个值
    # print(value_to_word_dict)
    return words_dic

# 输出word编辑距离为1的词库
def word_edit1(word):
    n = len(word)
    # letter_str = 'abcdefghijklmnopqrstuvwxyz'
    possible_word1 = list(set(
        [word[0:i] + word[i + 1:] for i in range(n)] +  # 删除一个字母
        [word[0:i] + word[i + 1] + word[i] + word[i + 2:] for i in range(n - 1)] +  # 改一个字母的顺序
        [word[0:i] + c + word[i + 1:] for i in range(n) for c in letter_str] +  # 改一个字母
        [word[0:i] + c + word[i:] for i in range(n) for c in letter_str]  # 增一个字母
    ))
    return possible_word1

# 输出word编辑距离为2的词库
def word_edit2(word):
    possible_word1 = word_edit1(word)
    possible_word2 = list()
    for w in possible_word1:
        possible_word2 += word_edit1(w)
    return possible_word2

# 输出最有可能结果（若有两个次可能性一样，都是最大的，默认输出前一个词）
def output(check_list, words_dic):
    value_list = [words_dic[key] for key in check_list]
    candidate = check_list[value_list.index(max(value_list))] if len(value_list) else None
    return candidate


# 输入待检查单词，若出现在语言词库中则直接输出，否则逐步检查编辑距离1-2的词库
def correct(word, words_dic):
    if word in words_dic.keys() or len(word) < 2:
        return word
    # 检查编辑距离为1对应的词库
    check_list1 = word_edit1(word)
    # 只需检查词库中存在的词
    check_list1 = [i for i in check_list1 if i in words_dic.keys()]
    candidate = output(check_list1, words_dic)
    if candidate:
        return candidate
    # 检查编辑距离为2的库
    check_list2 = word_edit2(word)
    check_list2 = [i for i in check_list2 if i in words_dic.keys()]
    candidate = output(check_list2, words_dic)
    if candidate:
        return candidate
    else:
        return word

def str_correct(words_str, words_dic):
    word_start = 0
    word_end = 0
    new_str = ''
    while word_end < len(words_str):
        single_word = ''
        while words_str[word_end] in letter_str:
            single_word += words_str[word_end]
            if word_end == len(words_str)-1:
                # 在进行单词校正前，指针应该指向单词后一个位置
                word_end += 1
                break
            word_end += 1
        # 单个单词进行校正
        if word_end >word_start:
            word = correct(single_word, words_dic)
            new_str += word
        # 其余字符直接输出
        else:
            new_str += words_str[word_end]
            word_end += 1
        word_start = word_end
    str_list = new_str.split()
    new_str = ' '.join(str_list)
    return new_str

if __name__ == '__main__':
    words_dic = text_content()
    while True:
        # # 判断单词书写是否正确，并返回正确单词
        # input_word = input("请输入单词：(输入stop结束)")
        # if input_word == 'stop':
        #     break
        # print(correct(input_word, words_dic))

        # 判断一段文本中的错误单词，并返回正确文本
        input_str = input('请输入字符串语句：（输入stop结束）')
        if input_str == 'stop':
            break
        print(str_correct(input_str, words_dic))