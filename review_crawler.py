'''
    爬取 Google 搜尋結果的評論
'''
from random import randint
from time import sleep
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_driver(headless=True):
    '''
    取得一個 WebDriver
    '''
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    return driver


def quit_driver(driver):
    '''
    關閉 WebDriver
    '''
    driver.quit()
    return 'Quit WebDriver successfully'


def read_input_file(file_name):
    '''
    讀取 input.txt 文件並回傳所有的 Google 評論連結
    '''
    urls = []
    with open(file_name, 'r', encoding='utf-8') as f:
        urls = f.readlines()
    # 去除換行符號、空行
    urls = list(map(lambda url: url.strip(), urls))
    return urls


def write_reviews_file(file_name, reviews_dt):
    '''
    將爬取的評論寫入對應的 reviews.json 文件
    '''
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(str(reviews_dt))
    return f'Write to {file_name} successfully'


def crawl_reviews(driver, review_url):
    '''
    爬取 Google 搜尋結果的評論
    '''

    # 定義需要使用的常數
    CLASS_WITH_REVIEW = '.jJc9Ad'
    CLASS_WITH_TOTAL_REVIEW_AMOUNT = '.fontBodySmall'
    COMMENT_PER_SCROLL = 10
    CLASS_USED_IN_SEPERATE_LINE = '.AyRUI'

    # 打開目標網頁
    driver.get(review_url)

    # 等待元素出現
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, CLASS_WITH_REVIEW)))
    except TimeoutException:
        print("Timeout")

    # 取得總評論數
    potential_total_reviews_tags = driver.find_elements(
        By.CSS_SELECTOR, CLASS_WITH_TOTAL_REVIEW_AMOUNT)
    potential_total_reviews_tag = None
    for tag in potential_total_reviews_tags:
        if '篇評論' in tag.text:
            potential_total_reviews_tag = tag
            break
    total_reviews_amount = 0
    if potential_total_reviews_tag:
        total_reviews_amount = int(
            potential_total_reviews_tag.text.split(' ')[0].replace(',', ''))

    # 取得標題
    title = unquote(driver.current_url
                    .split('place/')[1]
                    .split('/@')[0])
    title = title.replace('+', '-').replace('|', '-')

    # 計算需要滾動的次數，並開始滾動
    scroll_times = total_reviews_amount // COMMENT_PER_SCROLL + 1
    print(f'{title}')
    print(f'    - Need to scroll {scroll_times} times')
    for i in range(scroll_times):
        # 取得所有分隔線的元素
        seperating_line = driver.find_elements(
            By.CSS_SELECTOR, CLASS_USED_IN_SEPERATE_LINE)

        # 聚焦分隔線所在的區域，並向下滾動至最底
        driver.execute_script(
            "arguments[0].scrollIntoView();", seperating_line[-1])

        print(f"    - Scrolling {i + 1} times", end='\r')
        sleep(randint(1, 2))
    print()

    # 再次取得所有評論的元素
    reviews = driver.find_elements(
        By.CSS_SELECTOR, CLASS_WITH_REVIEW)

    # 如果 review 元素中包含「全文」的字樣，則需要點擊展開
    print("    - Clicking 'More' button")
    for review in reviews:
        mores = review.find_elements(By.CSS_SELECTOR, '.w8nwRe.kyuRq')
        for m in mores:
            m.click()

    # 等待 1 秒鐘後，再次取得所有評論的元素
    sleep(1)
    reviews = driver.find_elements(
        By.CSS_SELECTOR, CLASS_WITH_REVIEW)

    # 將所有評論元素轉換成 HTML 字串
    reviews = list(map(
        lambda review: review.get_attribute('outerHTML'),
        reviews
    ))

    # 回傳抓取結果
    return title, reviews


if __name__ == '__main__':
    # 讀取 input.txt 中的所有 Google 評論連結
    test_urls = read_input_file('./input/input.txt')

    # 取得一個 WebDriver
    test_driver = get_driver(headless=False)

    # 依照 test_urls 中的連結爬取評論
    test_results = {}
    for test_url in test_urls:
        test_title, test_result = crawl_reviews(
            driver=test_driver,
            review_url=test_url
        )
        test_results[test_title] = test_result

    # 確認目前取得的評論數量
    for test_title, test_reviews in test_results.items():
        print(f'Title: {test_title}')
        print(f'Reviews: {len(test_reviews)}')

        # 將爬取的評論寫入對應 reviews.json 文件
        print(write_reviews_file(f'./reviews_jsons/{test_title}_reviews.json', {
            'title': test_title,
            'reviews': test_reviews
        }))

    # 關閉 WebDriver
    print(quit_driver(test_driver))
