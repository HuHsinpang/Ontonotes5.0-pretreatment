import os, glob, itertools


def generate_collection(data_tag, dir_name, lang):
    folder = './conll-2012/v4/data/'+ data_tag + '/data/'+ lang
    results = itertools.chain.from_iterable(glob.iglob(os.path.join(root, '*.v4_gold_conll'))
                                            for root, dirs, files in os.walk(folder))

    text, word_count, sent_count = "", 0, 0
    for cur_file in results: 
        with open(cur_file, 'r') as f:
            flag = None
            for line in f.readlines():
                l = ' '.join(line.strip().split())
                ls = l.split(" ")
                if len(ls) >= 11:
                    word = ls[3]
                    pos = ls[4]
                    cons = ls[5]
                    ori_ner = ls[10]
                    ner = ori_ner
                    # print(word, pos, cons, ner)
                    if ori_ner == "*":
                        if flag==None:
                            ner = "O"
                        else:
                            ner = "I-" + flag
                    elif ori_ner == "*)":
                        ner = "I-" + flag
                        flag = None
                    elif ori_ner.startswith("(") and ori_ner.endswith("*") and len(ori_ner)>2:
                        flag = ori_ner[1:-1]
                        ner = "B-" + flag
                    elif ori_ner.startswith("(") and ori_ner.endswith(")") and len(ori_ner)>2 and flag == None:
                        ner = "B-" + ori_ner[1:-1]

                    text += "\t".join([word, pos, cons, ner]) + '\n'
                    word_count += 1
                else:
                    text += '\n'
                    if not line.startswith('#'):
                        sent_count += 1
            text += '\n'
            # break

    if data_tag == 'development':
        data_tag = 'dev'
    
    filepath = os.path.join(dir_name, data_tag + '.bio')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    filepath = os.path.join(dir_name, data_tag+'.info.txt')
    with open(filepath, 'w') as f:
        f.write("For file:{}, there are {} sentences, {} tokens.".format(filepath, sent_count, word_count))


def nertag_bio2bioes(dir_name):
    for bio_file in glob.glob(dir_name + '/*.bio'):
        with open(bio_file.rsplit('/', 1)[0]+'/ontonotes5.'+bio_file.rsplit('/',1)[1].rstrip('bio')+'bmes', 'w', encoding='utf-8') as fout, open(bio_file, 'r', encoding='utf-8') as fin:
            lines = fin.readlines()
            for idx in range(len(lines)):
                if len(lines[idx])<3:   # 句尾
                    fout.write(' \n')
                    continue

                word, label = lines[idx].split()[0], lines[idx].split()[-1]
                if "-" not in label:        # O
                    for char in word:
                        fout.write(char+' O\n')
                else:
                    label_type=label.split('-')[-1]
                    if 'B-' in label:       # B
                        if (idx<len(lines)-1 and len(lines[idx+1])<3) or \
                            idx==len(lines)-1                         or \
                            (idx<len(lines)-1 and 'I' not in lines[idx+1].split()[-1]): # 位于句尾/文件尾、或下个标记不为I
                            if len(word)==1:    # S
                                fout.write(word+' S-'+label_type+'\n')
                            else:               # 对于BIE在同一个word
                                fout.write(word[0]+' B-'+label_type+'\n')
                                for char_idx in range(1, len(word)-1):
                                    fout.write(word[char_idx]+' M-'+label_type+'\n')
                                fout.write(word[-1]+' E-'+label_type+'\n')
                        else:
                            fout.write(word[0]+'B-'+label_type+'\n')
                            for char_idx in range(1, len(word)-1):
                                fout.write(word[char_idx]+' M-'+label_type+'\n')
                    elif 'I-' in label:     # I
                        if (idx<len(lines)-1 and len(lines[idx+1])<3) or \
                            idx==len(lines)-1                         or \
                            (idx<len(lines)-1 and 'I' not in lines[idx+1].split()[-1]): # 位于句尾/文件尾、或下个标记不为I
                            for char_idx in range(0, len(word)-1):
                                fout.write(word[char_idx]+' M-'+label_type+'\n')
                            fout.write(word[-1]+' E-'+label_type+'\n')
                        else:
                            for char in word:
                                fout.write(char+' M-'+label_type+'\n')


def main():
    for language in ('english', 'chinese', 'arabic'):

        # # 针对某种语言
        dir_name = os.path.join('./result/', language)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # 对于该语言的训练集、验证集、测试集
        for split in ['train', 'development', 'test']:
            generate_collection(data_tag=split, dir_name=dir_name, lang=language)

        if language=='chinese':
            nertag_bio2bioes(dir_name)


if __name__ == "__main__":
    main()

