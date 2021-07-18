import os
from src.Harvest import Harvest

def main():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR, 0o777)
    Harvest.crawl()

if __name__ == "__main__":
    main()
    