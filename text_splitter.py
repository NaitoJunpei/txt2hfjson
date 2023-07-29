### テキストを、指定した文字数ごとに分割して、リストに格納する

def text_spliter(text, max_length=2000):
    # max_lengthを超えない最も近い読点または改行を探す
    splitted_text = []
    while len(text) > max_length:
        temp_text = text[:max_length]
        # 最後の読点または」または改行を探す
        last_delimiter_index = max(temp_text.rfind('。'), temp_text.rfind('」'), temp_text.rfind('\n'))
        if last_delimiter_index == -1:
            # 読点または改行が見つからない場合
            splitted_text.append(text[:max_length])
            text = text[max_length:]
        else :
            splitted_text.append(text[:last_delimiter_index+1])
            text = text[last_delimiter_index+1:]
    splitted_text.append(text)
    return splitted_text

