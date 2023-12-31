import requests
import re
import random
import time
import xml.etree.ElementTree as ET
import pandas as pd
import collections
import pandas as pd
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

def get_bvids(keyword, pages):
    bvids = []
    # 获取多少个页面的信息，一个页面有20个，共需要15页
    for page in range(0, pages):
        url = f"https://api.bilibili.com/x/web-interface/wbi/search/type?keyword={keyword}&search_type=video&page={page + 1}"
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            print(f"请求状态码：{response.status_code}")
            response_dict = response.json()
            result_list = response_dict.get('data', {}).get('result', [])
            for result in result_list:
                bvid = result.get('bvid')
                if bvid:
                    bvids.append(bvid)
            time.sleep(round(random.uniform(0, 3), 3))
        else:
            print(f"请求失败，状态码：{response.status_code}")
    return bvids

def get_cids(bvids):
    cids = []
    for index, bvid in enumerate(bvids):
        cid_url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp"
        response = requests.get(cid_url, headers=headers)
        cid_match = re.search(r'"cid":(\d+)', response.text)
        if cid_match:
            cid = cid_match.group(1)
            cids.append(cid)
        print(f"正在获取页面cid，现在已进行到 {index+1}/{len(bvids)}")
        time.sleep(round(random.uniform(0, 2), 3))
    return cids

def get_dms(cids):
    dms = []
    for index, cid in enumerate(cids):
        dm_url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
        response = requests.get(dm_url, headers=headers)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.text)
        
        for d in root.iter('d'):
            dm_text = d.text
            dms.append(dm_text)
        
        print(f"正在解析弹幕，现在已进行到 {index+1}/{len(cids)}")
        time.sleep(round(random.uniform(0, 2), 3))
    return dms

# 其他代码部分

if __name__ == "__main__":
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }

    content = input("请输入你要检索的内容: ")
    keyword = content

    cookies = requests.get('https://www.bilibili.com/', headers=headers).cookies.get_dict()
    
    bvids = get_bvids(keyword, pages=15)
    cids = get_cids(bvids)
    dms = get_dms(cids)
    
    # 其他代码部分（统计弹幕、生成词云等）
    # 统计每个弹幕的出现次数
    word_counts = collections.Counter(dms)

    # 对弹幕出现次数进行排序
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    # 输出弹幕数量排名前20的弹幕
    print("弹幕数量排名前20的弹幕：")
    for i in range(min(20, len(sorted_word_counts))):
        print("{}: {}".format(sorted_word_counts[i][0], sorted_word_counts[i][1]))

    # 创建一个空的 DataFrame
    df = pd.DataFrame(columns=['弹幕内容', '出现次数'])

    # 将弹幕和对应的出现次数添加到 DataFrame 中
    for dm, count in sorted_word_counts:
        df = df.append({'弹幕内容': dm, '出现次数': count}, ignore_index=True)

    # 将 DataFrame 保存为 Excel 文件
    df.to_excel('弹幕统计(1).xlsx', index=False)

    # 读取Excel表格数据
    data = pd.read_excel('弹幕统计(1).xlsx')

    # 将数据转换为字典形式 {词: 出现次数}
    word_freq = dict(zip(data['弹幕内容'], data['出现次数']))
    # 打开图像文件并将其转化为numpy数组
    mask = np.array(Image.open('QQ图片20230907154801.jpg'))
    # 创建WordCloud对象并配置参数
    wordcloud = WordCloud(width=3000, height=2800, background_color='white',
                        font_path='ChillKai_Big5.ttf',max_words=10000,
                        stopwords=set(STOPWORDS),mask=mask)

    # 过滤停用词
    stopwords = set(['的', '是', '在'])  # 自定义停用词列表
    wordcloud.stopwords.update(stopwords)  # 添加停用词
    # 根据出现次数设置字体大小
    min_font_size = 20
    max_font_size = 200
    # 计算字体大小的动态范围
    max_count = max(word_freq.values())
    wordcloud.generate_from_frequencies(word_freq, max_font_size=max_font_size)
    wordcloud.recolor(random_state=1000)

    # 绘制词云图并展示
    plt.figure(figsize=(5, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    # 保存为较清晰的图片
    plt.savefig('1.png', dpi=2200)
    plt.show()
