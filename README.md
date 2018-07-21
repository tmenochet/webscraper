# Webscraper
Scrapy spiders for search engines and mirrors.

Implemented spiders:
* baidu_web
* bing_api (API keys required)
* bing_web
* google_api (API keys required)
* google_web
* qwant_api
* waybackmachine

The provided Python script leverage dorks to fetch juicy resources.

## Usage
* Scraping mirrors:
```
python3 ./webscraper.py --spider waybackmachine --domain example.com --from 20160101 --to 20180101
```
* Dorking with search engines:
```
python3 ./webscraper.py --spider bing_api --domain example.com --limit 50 --delay 3
```
* Custom search query:
```
scrapy crawl google_api -a query='site:s3.amazonaws.com inurl:example' -a limit=10 -o google_api-items.jl
```

## Search results
The JsonWriter and ListWriter pipes are enabled by default in the script, search results will be stored as below:
- <spider>-items.jl:
  ```
  {"url": "https://example.com/", "title": "Example Domain", "query": "site:example.com"}
  {"url": "https://www.example.com/", "title": "Example Subdomain", "query": "site:example.com"}
  ```
- <spider>-items.lst:
  ```
  https://example.com/
  https://www.example.com/
  ```

With the scrapy command, only the ListWriter pipe is enabled by default. Use the native command line option to store items in JSON format.

## Install
* It is recommended to set up a Python virtual environment:
  ```
  virtualenv pyenv-webscraper --no-site-packages --python=python3.5
  cd pyenv-webscraper; source bin/activate
  ```
* Pull the Git repository and install the Python dependencies:
  ```
  git clone https://github.com/tmenochet/webscraper.git
  cd webscraper; pip3 install -r requirements.txt
  ```
* Set up your API keys in webscraper/settings.py:
  ```
  BING_API_KEY   = '<YOUR_KEY>'
  GOOGLE_API_KEY = '<YOUR_KEY>'
  GOOGLE_CSE_ID  = '<YOUR_KEY>'
  ```

## Acquiring API keys
* Bing API key: see [here](https://www.microsoft.com/cognitive-services/en-us/bing-web-search-api)
* Google API key: see [here](https://support.google.com/googleapi/answer/6158841?hl=en&ref_topic=7013279)
* Google CSE ID:
  1. Create a CSE [here](http://www.google.com/cse/all)
  2. Configure the CSE to search the entire web: see [here](https://support.google.com/customsearch/answer/2631040?hl=en)

