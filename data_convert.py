#!/usr/bin/python
#-*- coding: UTF-8 -*-
# author = 'zhangdebin'
import sys
import re
import math

# load && dup data
def loadData( filename):
    title_seg_dup_set = set()
    data_list = list()
    #读取
    fi = open(filename , 'r')
    for line in fi:
        msgs = re.split('\t\t',line)
        if(msgs.__len__()!=3):
            print "error:len=",msgs.__len__(),"\t",line
            break
        #数据获取，标题消重    
        title = msgs[0]
        title_seg = msgs[1]
        content_seg = msgs[2]
        if(title_seg in title_seg_dup_set):
            continue
        title_seg_dup_set.add(title_seg)
        data = {'title':title,'title_seg':title_seg,'content_seg':content_seg}
        data_list.append(data)
    fi.close()
    return data_list
#get words
def get_words( neg_data,pos_data):
    MinIdf = 3
    title_words = set()
    content_words = set()
    content_words_frequently = set()
    content_words_idf = {}
    for i in range(neg_data.__len__()):
        title_seg = neg_data[i]['title_seg']
        content_seg = neg_data[i]['content_seg']
        t_words = re.split(' ',title_seg)
        c_words = re.split(' ',content_seg)
        for word in t_words:
            if (word in title_words):
                continue
            title_words.add(word)
        c_idf_set = set()
        for word in c_words:
            if word in c_idf_set:
                continue
            c_idf_set.add(word)
        for word in c_words:
            if word in content_words:
                continue
            content_words.add(word)
        for word in c_idf_set:
            if(word in content_words_idf):
                content_words_idf[word] +=1
            else:
                content_words_idf[word] = 1
    count = 0
    rest = 0
    total = 0
    for word in content_words:
        if (content_words_idf[word] >= MinIdf):
            content_words_frequently.add(word)
            count +=1
        else:
            rest +=1
        total +=1
    print "total",total,"\tcount",count,"\trest:",rest
    return title_words,content_words,content_words_frequently

#load dict
def load_dict(idf_file):
    idf_dict = {}
    fi = open(idf_file,'r')
    for line in fi :
        msgs = re.split( '\t',line)
        if(msgs.__len__()!=2):
            continue
        word = msgs[0]
        idf = msgs[1]
        idf_dict[word] = idf
    return idf_dict
#gen dict
def gen_dict( words,idf,index):
    idf_dict = {}
    index_dict = {}
    for word in words:
        if (word in idf):
            idf_dict[word] = idf[word]
            index_dict[word] = index
            index+=1
    return idf_dict,index_dict,index
def gen_all_dict( words,index):
    index_dict = {}
    for word in words:
        word = word.strip()
        if word == "":
            continue
        if (word in index_dict):
            continue
        index_dict[word] = index
        index +=1
    return index_dict,index
#conv2vector
def conv2vector(words,idf_dict,index_dict):
    vector = {}
    word_score = {}
    tf_dict = calculate_tf(words,idf_dict)
    for word in tf_dict:
        if(word in idf_dict):
            word_score[word] = tf_dict[word]*(float(idf_dict[word]))
    for word in word_score :
        if word in index_dict:
            vector[index_dict[word]]= word_score[word]
    return vector
#title2vector
def title2vector(data,t_idf,t_index):
    title_seg = data['title_seg']
    vector = conv2vector(title_seg,t_idf,t_index)
    vector = sortVector(vector)
    return vector
#content2vector
def content2vecotr(data,t_idf,t_index,c_idf,c_index):
    title_seg = data['title_seg']
    t_vector = conv2vector(title_seg,t_idf,t_index)
    content_seg = data['content_seg']
    c_vector = conv2vector(content_seg,c_idf,c_index)
    t_vector.update(c_vector)
    vector = sortVector(t_vector)
    return vector
#vector sort
def sortVector(vector):
    vector= sorted(vector.iteritems(), key=lambda d:d[0])
    return vector
#tf
def calculate_tf(line):
    word_tf = {}
    words = re.split(' ',line)
    for word in words:
        if word in word_tf:
            word_tf[word]+=1
        else:
            word_tf[word]=1
    for word in word_tf:
        tf = word_tf[word]
        word_tf[word] = float(math.log(1+tf))
    return word_tf
#words to onehot tf
def words2Onehot(line,index_dict):
    vector = {}
    word_tf = calculate_tf(line)
    for word in word_tf:
        if word in index_dict:
            index = index_dict[word]
            vector[index] = word_tf[word]
    return vector
#title conv2 onehot tf
def title2Onehot(data,t_index_dict):
    title_seg = data['title_seg']
    vector = words2Onehot(title_seg,t_index_dict)
    vector = sortVector(vector)
    return vector

#content conv2 onehot tf
def content2Onehot(data,t_index_dict,c_index_dict):
    title_seg = data['title_seg']
    content_seg = data['content_seg']
    t_vector = words2Onehot(title_seg,t_index_dict)
    c_vector = words2Onehot(content_seg,c_index_dict)
    t_vector.update(c_vector)
    vector = sortVector(t_vector)
    return vector

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    if len(sys.argv) < 2:
        print ('Usage:<posfilename> <negfilename>')
        exit(0)
    pos_num = len(open(sys.argv[1], 'r').readlines()) 
    neg_num = len(open(sys.argv[2], 'r').readlines()) 
    print "pos_num:",pos_num,"\tneg_num:",neg_num
    pos_data = loadData(sys.argv[1])
    pos_dup_num = pos_data.__len__()
    print "pos_data.len:",pos_dup_num
    neg_data = loadData(sys.argv[2])
    neg_dup_num = neg_data.__len__()
    print "neg_data.len:",neg_dup_num
    #数据解析，消重
    title_words,content_words,content_frequently = get_words(pos_data,neg_data)
    print "title_words.len:",len(title_words)
    print "content_words.len:",len(content_words)
    print "content_frequently.len:",len(content_frequently)
    
    #load dict
    content_idf_file = "./idf.txt"
    title_idf_file = "./title_idf.txt"
    content_idf = load_dict(content_idf_file)
    title_idf = load_dict(title_idf_file)
    print "title_idf.len:",title_idf.__len__()
    print "content_idf.len:",content_idf.__len__()

    #gen dict
    index = 1
    t_idf,t_index,index = gen_dict( title_words,title_idf,index)
    index +=1
    c_idf,c_index,index = gen_dict( content_words,content_idf,index)
    print "t_idf.len:",t_idf.__len__()
    print "c_idf.len:",c_idf.__len__()
        
    #conv2 vector
    '''
    for data in neg_data:
        vector = content2vecotr(data,t_idf,t_index,c_idf,c_index)
        print vector
    '''
    #gen all_index
    index = 1
    all_t_index,index = gen_all_dict( title_words,index)
    all_c_index,index = gen_all_dict( content_words,index)
    #conv2 onehot
    for data in neg_data:
        vector = title2Onehot(data,all_t_index)
        print vector
