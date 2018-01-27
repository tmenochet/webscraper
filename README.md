# Webscraper
Scrapy spider for search engines

## Usage
Set up your API keys in settings.py:
```
BING_API_KEY   = '<YOUR_KEY>'
GOOGLE_API_KEY = '<YOUR_KEY>'
GOOGLE_CSE_ID  = '<YOUR_KEY>'
```
Run scrapy:
```
scrapy crawl bing_api -a query='domain:example.com' -a limit=50
scrapy crawl google_api -a query='site:example.com' -a limit=10
```

## Search results
The JsonWriter and ListWriter pipes are enabled by default, search results will be stored as below:
- google_api-items.jl:
  ```
  {"url": "https://example.com/", "title": "Example Domain"}
  {"url": "https://www.example.com/", "title": "Example Subdomain"}
  ```
- google_api-items.lst:
  ```
  https://example.com/
  https://www.example.com/
  ```

## Acquiring API keys
* Bing API key: see [here](https://www.microsoft.com/cognitive-services/en-us/bing-web-search-api)
* Google API key: see [here](https://support.google.com/googleapi/answer/6158841?hl=en&ref_topic=7013279)
* Google CSE ID:
  1. Create a CSE [here](http://www.google.com/cse/all)
  2. Configure the CSE to search the entire web: see [here](https://support.google.com/customsearch/answer/2631040?hl=en)


