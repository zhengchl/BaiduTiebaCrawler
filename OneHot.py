#encoding=utf-8

import sys
import itertools
import ChineseTokenize

def getIdMap(words_list):
    '''为每个word分配一个id'''
    all_words = itertools.chain.from_iterable(words_list)
    all_words_set = set(all_words)

    word_to_idx = {}
    idx_to_word = {}
    for idx, word in enumerate(all_words_set):
        word_to_idx[word] = idx
        idx_to_word[idx] = word

    return word_to_idx, idx_to_word

if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print "Usage: %s [filename]" % sys.argv[0]

    # in_filename = sys.argv[1]
    in_filename = "rawdata.txt"
    in_fid = open(in_filename)

    word_to_idx_fid = open("%s.w2i"%in_filename, "w")
    idx_to_word_fid = open("%s.i2w"%in_filename, "w")
    out_fid = open("%s.out"%in_filename, "w")

    words_list = []
    line_num = 0
    for line in in_fid:
        line_num += 1
        try:
            sentence = line.decode('utf8').strip()
        except UnicodeDecodeError:
            print "error at: %d"%line_num
            continue
        words = ChineseTokenize.wordTokenize(sentence, "simple")
        words_list.append(words)

    word_to_idx, idx_to_word = getIdMap(words_list)
    for key in word_to_idx:
        word_to_idx_fid.write("%s:%d\n"%(key.encode('utf8'), word_to_idx[key]))
    for key in idx_to_word:
        idx_to_word_fid.write("%d:%s\n"%(key, idx_to_word[key].encode('utf8')))
    for words in words_list:
        new_line = u" ".join(str(word_to_idx[var]) for var in words)
        out_fid.write("%s\n"%new_line.encode('utf8'))

    in_fid.close()
    out_fid.close()
    word_to_idx_fid.close()
    idx_to_word_fid.close()
