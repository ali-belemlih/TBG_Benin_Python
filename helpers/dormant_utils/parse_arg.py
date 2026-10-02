import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process data based on month-year.')
    parser.add_argument('id', type=str, help='id of the table')
    parser.add_argument('bucket_name', type=str, help='bucket name')

    return parser.parse_args()
