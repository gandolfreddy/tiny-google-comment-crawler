'''
    Multiprocess version of the main program
'''

import multiprocessing as mp
from review_crawler import (
    get_driver, read_input_file, write_reviews_file, crawl_reviews, quit_driver)
from review_parser import refine_reviews, get_data_from_reviews, write_into_csv


def process_reviews(review_url):
    '''Process reviews for a single URL'''
    driver = get_driver(headless=True)
    title, reviews = crawl_reviews(driver=driver, review_url=review_url)
    quit_driver(driver)

    # Write reviews to JSON
    write_reviews_file(f'./reviews_jsons/{title}_reviews.json', {
        'title': title,
        'reviews': reviews
    })

    # Process and write to CSV
    title, reviews_soup = refine_reviews(
        f'./reviews_jsons/{title}_reviews.json')
    pre_csv_data = get_data_from_reviews(reviews_soup)
    write_into_csv(f'./reviews_csvs/{title}_reviews.csv', pre_csv_data)

    return title, len(reviews)


def main():
    '''
    Main function using multiprocessing to parallelize review crawling
    '''
    # Read input URLs
    urls = read_input_file('./input/input.txt')

    print('--- Start parallel review crawling ---')

    # Create process pool
    with mp.Pool(processes=min(mp.cpu_count(), len(urls))) as pool:
        # Map URLs to processes
        results = pool.map(process_reviews, urls)

    # Print results
    print('\n--- Results ---')
    for title, review_count in results:
        print(f'{title} - Processed Reviews: {review_count}')

    print('--- Completed parallel processing ---')


if __name__ == '__main__':
    mp.freeze_support()  # Required for Windows
    main()
