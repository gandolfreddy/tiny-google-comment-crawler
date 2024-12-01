'''
    The main file to run the program
'''

from review_crawler import (
    get_driver, read_input_file, write_reviews_file, crawl_reviews, quit_driver)
from review_parser import refine_reviews, get_data_from_reviews, write_into_csv


def main():
    '''
        The main function to run the program
    '''
    # 讀取 input.txt 中的所有 Google 評論連結
    test_urls = read_input_file('./input/input.txt')

    # 取得一個 WebDriver，如果要不顯示瀏覽器，將 headless 設為 True
    test_driver = get_driver(headless=False)

    # 依照 test_urls 中的連結爬取評論
    print('--- Start to crawl reviews ---')
    test_results = {}
    for test_url in test_urls:
        test_title, test_result = crawl_reviews(
            driver=test_driver,
            review_url=test_url
        )
        test_results[test_title] = test_result

    print('--- Start to write reviews into files ---')
    for test_title, test_reviews in test_results.items():
        # 確認目前取得的評論數量
        print(f'{test_title} - Gotten Reviews: {len(test_reviews)}')

        # 將爬取的評論寫入對應 reviews.json 文件
        first_phase_result = write_reviews_file(f'./reviews_jsons/{test_title}_reviews.json', {
            'title': test_title,
            'reviews': test_reviews
        })
        print(f'    {first_phase_result}')

        test_title, test_reviews_soup = refine_reviews(
            f'./reviews_jsons/{test_title}_reviews.json')
        test_pre_csv_data = get_data_from_reviews(test_reviews_soup)

        second_phase_result = write_into_csv(
            f'./reviews_csvs/{test_title}_reviews.csv', test_pre_csv_data)
        print(f'    {second_phase_result}')

    # 關閉 WebDriver
    print(f'--- {quit_driver(test_driver)} ---')


if __name__ == '__main__':
    main()
