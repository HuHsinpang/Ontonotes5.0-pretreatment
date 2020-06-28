import os, glob, itertools

def generate_collection(data_tag, dir_name, lang):
    folder = './conll-2012/v4/data/'+ data_tag + '/data/'+ lang
    print(folder)
    results = itertools.chain.from_iterable(glob.iglob(os.path.join(root, '*.v4_gold_conll'))
                                            for root, dirs, files in os.walk(folder))

    text, word_count, sent_count = "", 0, 0
    for cur_file in results: 
        print(cur_file)
        with open(cur_file, 'r') as f:
            print(cur_file)
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
    with open(filepath, 'w') as f:
        f.write(text)

    filepath = os.path.join(dir_name, data_tag+'.info.txt')
    with open(filepath, 'w') as f:
        f.write("For file:{}, there are {} sentences, {} tokens.".format(filepath, sent_count, word_count))

def main():
    # os.chdir(os.path.dirname(__file__))
    for language in ('english', 'chinese', 'arabic'):

        # 针对某种语言
        dir_name = os.path.join('./result/', language)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # 对于该语言的训练集、验证集、测试集
        for split in ['train', 'development', 'test']:
            generate_collection(data_tag=split, dir_name=dir_name, lang=language)


if __name__ == "__main__":
    main()

