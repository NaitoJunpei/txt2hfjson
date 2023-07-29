# 対象ディレクトリを指定して、サブディレクトリを含めた全てのテキストファイルを取得し、
# tags.jsonに記載のタグを付与したうえで、
# huggingface仕様のjsonファイルに変換する。

# 対象ディレクトリの構成を
# home/
#  tags.json
#  data1/
#   text1.txt
#   text2.txt
#  data2/
#   text3.txt
#   text4.txt
#  data3/
#   sub_data1/
#    text5.txt
#    text6.txt

# とすると、変換後のディレクトリの構成は
# comverted_home/
#  data1_text1.json
#  data1_text2.json
#  data2_text3.json
#  data2_text4.json
#  data3_sub_data1_text5.json
#  data3_sub_data1_text6.json

# となる。

# tags.jsonの記載方法は、
# {
#   "data1": {
#     "tags": ["tag1", "tag2"],
#     "text1": {
#       "tags": ["tag3", "tag4"]
#     },
#     "text2": {
#       "tags": ["tag5", "tag6"]
#     }
#   },
#   "data2": {
#     "tags": ["tag7", "tag8"],
#     "text3": {
#       "tags": ["tag9", "tag10"]
#     },
#     "text4": {
#       "tags": ["tag11", "tag12"]
#     }
#   },
#   "data3": {
#     "tags": ["tag13", "tag14"],
#     "sub_data1": {
#       "tags": ["tag15", "tag16"],
#       "text5": {
#         "tags": ["tag17", "tag18"]
#       },
#       "text6": {
#         "tags": ["tag19", "tag20"]
#       }
#     }
#   }
# }
# である。

# テキストの中身は、text_splitter.pyで分割する。

# jsonファイルの中身は、
# data1_text1.json
# {"tags": ["tag1", "tag2", "tag3", "tag4"], "text": "text1.txtをtext_splitter.pyで分割したテキスト1"}
# {"tags": ["tag1", "tag2", "tag3", "tag4"], "text": "text1.txtをtext_splitter.pyで分割したテキスト2"}
# 以下略
# data1_text2.json
# {"tags": ["tag1", "tag2", "tag5", "tag6"], "text": "text2.txtをtext_splitter.pyで分割したテキスト1"}
# {"tags": ["tag1", "tag2", "tag5", "tag6"], "text": "text2.txtをtext_splitter.pyで分割したテキスト2"}
# 以下略
# ※行末に,はつけない
# とする。


import os
import sys
import json
import glob
import re
import text_splitter

MAX_LENGTH = 700
DELIMITER = "==="

def create_json_dicts(tags, text):
    splitted_text = text_splitter.text_spliter(text, MAX_LENGTH)
    json_dicts = []
    for splitted_text in splitted_text:
        json_dict = {'tags': tags, 'text': splitted_text}
        json_dicts.append(json_dict)
    return json_dicts

def create_json_file(json_dicts, file_name):
    with open(file_name, 'w', encoding="utf-8") as f:
        for json_dict in json_dicts:
            json.dump(json_dict, f, ensure_ascii=False)
            f.write('\n')

def create_savefile_name(target_dir, text_filepath, save_dir):
    # text_filepath, target_dirの絶対パスを取得
    text_filepath = os.path.abspath(text_filepath)
    target_dir = os.path.abspath(target_dir)
    # text_filepathからtarget_dirを除く
    text_filepath = text_filepath.replace(target_dir, '')
    # ディレクトリ区切り文字をDELIMITERに置換
    text_filepath = text_filepath.replace(os.sep, DELIMITER)
    # 拡張子をjsonに置換
    text_filepath = re.sub(r'\.txt$', '.json', text_filepath)
    # 先頭のDELIMITERを削除
    text_filepath = re.sub(r'^' + DELIMITER, '', text_filepath)
    # 保存先ディレクトリを作成
    os.makedirs(os.path.join(save_dir, os.path.dirname(text_filepath)), exist_ok=True)
    # 保存先ファイル名を作成
    savefile_name = os.path.join(save_dir, text_filepath)
    return savefile_name

def get_tags(tags_json, save_filepath):
    # タグは、tags.jsonに記載のタグと、ファイル名から取得する。
    # data1_text1.jsonの場合、
    # tags_json["data1"]["tags"] + tags_json["data1"]["text1"]["tags"]
    # となる。
    # _アンダースコアは任意の回数存在してよい。
    # save_filepathからファイル名を取得
    filename = os.path.basename(save_filepath).replace('.json', '')
    # _で分割
    attributes = filename.split(DELIMITER)

    tags = []
    temp_tags_json = tags_json
    for attribute in attributes:
        if attribute in temp_tags_json:
            temp_tags_json = temp_tags_json[attribute]
            if 'tags' in temp_tags_json:
                tags += temp_tags_json['tags']

    # 重複を削除
    tags = list(set(tags))
    
    return tags

def main():
    target_dir = sys.argv[1]
    save_dir = sys.argv[2]
    print(target_dir, save_dir)
    # tags.jsonが存在しない場合はtags_json = {}とする
    if os.path.exists(os.path.join(target_dir, 'tags.json')):
        tags_json = json.load(open(os.path.join(target_dir, 'tags.json'), 'r', encoding="utf-8"))
    else:
        tags_json = {}
    print(tags_json)
    for text_filepath in glob.glob(os.path.join(target_dir, '**', '*.txt'), recursive=True):
        save_filepath = create_savefile_name(target_dir, text_filepath, save_dir)
        tags = get_tags(tags_json, save_filepath)
        text = open(text_filepath, 'r', encoding="utf-8").read()
        json_dicts = create_json_dicts(tags, text)
        create_json_file(json_dicts, save_filepath)

if __name__ == '__main__':
    main()