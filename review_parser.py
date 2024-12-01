'''
    使用 BeautifulSoup 解析 reviews.txt 文件
'''
from ast import literal_eval
from csv import writer

from bs4 import BeautifulSoup


def refine_reviews(file_name):
    '''
        將 reviews.txt 文件中的 HTML 元素轉換成 BeautifulSoup 物件
        以便後續的資料處理
    '''
    with open(file_name, 'r', encoding='utf-8') as f:
        reviews_dt = literal_eval(f.read())
    reviews_str = ''.join(reviews_dt['reviews'])
    return (reviews_dt['title'], BeautifulSoup(reviews_str, 'html.parser'))


def write_into_csv(file_name, data):
    '''
        將分析完的結果寫入 CSV 檔案
    '''
    with open(file_name, 'w', encoding='utf-8', newline='') as f:
        csv_writer = writer(f)
        for row in data:
            csv_writer.writerow(row)
    return f'Write to {file_name} successfully'


def get_data_from_reviews(reviews_soup):
    '''
        從 BeautifulSoup 物件中取得評論的資料
    '''
    reviews = reviews_soup.select('.jJc9Ad')
    pre_csv_data = [['Name', 'Experience',
                     'Stars', 'Comment', 'others']]
    for review in reviews:
        name_tag = review.select_one('.d4r55')
        name = name_tag.get_text() if name_tag else '匿名'

        experience_tag = review.select_one('.RfnDt')
        experience = experience_tag.get_text() if experience_tag else '未知'

        stars_tag = review.select_one('.kvMYJc')
        stars = stars_tag.get_attribute_list(
            'aria-label')[0] if stars_tag else '未知'

        comment_tag = review.select_one('.wiI7pd')
        comment = comment_tag.get_text() if comment_tag else '未知'

        others = ''
        other_tag = comment_tag.find_next_sibling() if comment_tag else None
        if other_tag:
            other_sub_tags = other_tag.find_all(recursive=False)
            for sub_tag in other_sub_tags:
                tags = sub_tag.select('.RfDO5c')
                if len(tags) == 1:
                    others += f'{tags[0].get_text()}\n'
                else:
                    title,  content = tags
                    others += f'{title.get_text()}：{content.get_text()}\n'
        others = others if others else '未知'

        pre_csv_data.append([
            name, experience, stars,
            comment, others
        ])

    return pre_csv_data


if __name__ == '__main__':
    test_title, test_reviews_soup = refine_reviews(
        './reviews_jsons/熊翻滾一百八十度暖心鍋物-楠梓人氣鍋物-熱門鍋物-精緻鍋物-特色鍋物-必吃火鍋-聚餐餐廳-在地推薦火鍋-個人火鍋_reviews.json')
    test_pre_csv_data = get_data_from_reviews(test_reviews_soup)

    print(write_into_csv(
        f'./reviews_csvs/{test_title}_reviews.csv', test_pre_csv_data))
