import subprocess

def run_spider():
    subprocess.run(['scrapy', 'crawl', 'SearchEngine'], check=True)

if __name__ == "__main__":
    run_spider()
