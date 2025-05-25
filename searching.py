from time import sleep
from bs4 import BeautifulSoup
from requests import get
from urllib.parse import unquote
import random
import re

def get_useragent():
    lynx_version = f"Lynx/{random.randint(2, 3)}.{random.randint(8, 9)}.{random.randint(0, 2)}"
    libwww_version = f"libwww-FM/{random.randint(2, 3)}.{random.randint(13, 15)}"
    ssl_mm_version = f"SSL-MM/{random.randint(1, 2)}.{random.randint(3, 5)}"
    openssl_version = f"OpenSSL/{random.randint(1, 3)}.{random.randint(0, 4)}.{random.randint(0, 9)}"
    return f"{lynx_version} {libwww_version} {ssl_mm_version} {openssl_version}"

def _req(term, results, lang, start, proxies, timeout, safe, ssl_verify, region, tbs=None):
    params = {
        "q": term,
        "num": results + 2,  # Prevents multiple requests
        "hl": lang,
        "start": start,
        "safe": safe,
        "gl": region,
    }
    if tbs:
        params["tbs"] = tbs
    resp = get(
        url="https://www.google.com/search",
        headers={
            "User-Agent": get_useragent(),
            "Accept": "*/*"
        },
        params=params,
        proxies=proxies,
        timeout=timeout,
        verify=ssl_verify,
        cookies = {
            'CONSENT': 'PENDING+987', # Bypasses the consent page
            'SOCS': 'CAESHAgBEhIaAB',
        }
    )
    resp.raise_for_status()
    return resp


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def search(term, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=2, timeout=5, safe="active", ssl_verify=None, region=None, start_num=0, unique=False, timeframe=None):
    """Search the Google search engine
    
    Args:
        term: The search query string
        num_results: Number of results to return (default: 10)
        lang: Language code (default: 'en' for English)
        proxy: Proxy server URL (default: None)
        advanced: Return SearchResult objects instead of just URLs (default: False)
        sleep_interval: Time to sleep between requests (default: 2)
        timeout: Request timeout in seconds (default: 5)
        safe: Safe search setting ('active', 'moderate', or 'off') (default: 'active')
        ssl_verify: Verify SSL certificates (default: None)
        region: Region code for search results (default: None)
        start_num: Starting index for results (default: 0)
        unique: Only return unique results (default: False)
        timeframe: Time restriction for results. Options:
            - 'h' or 'hour': Past hour
            - 'd' or 'day': Past 24 hours
            - 'w' or 'week': Past week
            - 'm' or 'month': Past month
            - 'y' or 'year': Past year
            - '3h': Past 3 hours (similarly: '6h', '12h', etc.)
            - '3d': Past 3 days (similarly: '2d', '10d', etc.)
            - '2w': Past 2 weeks (similarly: '3w', '4w', etc.)
            - '2m': Past 2 months (similarly: '6m', '9m', etc.)
            - '2y': Past 2 years (similarly: '3y', '5y', etc.)
            - '2 years', '3 months', '4 weeks', '5 days', '6 hours': Human-readable formats
    
    Returns:
        Generator yielding results (URLs or SearchResult objects)
    """

    # Proxy setup
    proxies = {"https": proxy, "http": proxy} if proxy and (proxy.startswith("https") or proxy.startswith("http")) else None

    start = start_num
    fetched_results = 0  # Keep track of the total fetched results
    fetched_links = set() # to keep track of links that are already seen previously

    # Time-based search (TBS) parameter
    tbs = None
    if timeframe:
        # Handle single-character time periods
        if timeframe == 'h' or timeframe == 'hour':
            tbs = "qdr:h"
        elif timeframe == 'd' or timeframe == 'day':
            tbs = "qdr:d"
        elif timeframe == 'w' or timeframe == 'week':
            tbs = "qdr:w"
        elif timeframe == 'm' or timeframe == 'month':
            tbs = "qdr:m"
        elif timeframe == 'y' or timeframe == 'year':
            tbs = "qdr:y"
        # Handle numeric time periods (e.g., '3h', '2d', '4w')
        elif len(timeframe) >= 2:
            try:
                # Check for formats like "3h", "2d"
                amount = timeframe[:-1]  # Get everything except last character
                unit = timeframe[-1]     # Get last character
                
                if amount.isdigit() and unit in ['h', 'd', 'w', 'm', 'y']:
                    tbs = f"qdr:{unit}{amount}"
            except:
                pass

            # Check for formats like "2 years", "3 months", etc.
            try:
                # Define a pattern to match formats like "2 years", "3 months", etc.
                pattern = r'(\d+)\s+(hour|hours|day|days|week|weeks|month|months|year|years)'
                match = re.match(pattern, timeframe, re.IGNORECASE)
                
                if match:
                    amount = match.group(1)  # Extract the number
                    unit_text = match.group(2).lower()  # Extract the unit text
                    
                    # Convert unit text to Google's single-letter code
                    if 'hour' in unit_text:
                        unit = 'h'
                    elif 'day' in unit_text:
                        unit = 'd'
                    elif 'week' in unit_text:
                        unit = 'w'
                    elif 'month' in unit_text:
                        unit = 'm'
                    elif 'year' in unit_text:
                        unit = 'y'
                    
                    tbs = f"qdr:{unit}{amount}"
            except:
                # Invalid timeframe format, ignore it
                pass

    while fetched_results < num_results:
        # Send request
        resp = _req(term, num_results - start,
                    lang, start, proxies, timeout, safe, ssl_verify, region, tbs)
        
        # put in file - comment for debugging purpose
        # with open('google.html', 'w') as f:
        #     f.write(resp.text)
        
        # Parse
        soup = BeautifulSoup(resp.text, "html.parser")
        result_block = soup.find_all("div", class_="ezO2md")
        new_results = 0  # Keep track of new results in this iteration

        for result in result_block:
            # Find the link tag within the result block
            link_tag = result.find("a", href=True)
            # Find the title tag within the link tag
            title_tag = link_tag.find("span", class_="CVA68e") if link_tag else None
            # Find the description tag within the result block
            description_tag = result.find("span", class_="FrIlee")

            # Check if all necessary tags are found
            if link_tag and title_tag and description_tag:
                # Extract and decode the link URL
                link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", "")) if link_tag else ""
            # Extract and decode the link URL
            link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", "")) if link_tag else ""
            # Check if the link has already been fetched and if unique results are required
            if link in fetched_links and unique:
                continue  # Skip this result if the link is not unique
            # Add the link to the set of fetched links
            fetched_links.add(link)
            # Extract the title text
            title = title_tag.text if title_tag else ""
            # Extract the description text
            description = description_tag.text if description_tag else ""
            # Increment the count of fetched results
            fetched_results += 1
            # Increment the count of new results in this iteration
            new_results += 1
            # Yield the result based on the advanced flag
            if advanced:
                yield SearchResult(link, title, description)  # Yield a SearchResult object
            else:
                yield link  # Yield only the link

            if fetched_results >= num_results:
                break  # Stop if we have fetched the desired number of results

        if new_results == 0:
            #If you want to have printed to your screen that the desired amount of queries can not been fulfilled, uncomment the line below:
            #print(f"Only {fetched_results} results found for query requiring {num_results} results. Moving on to the next query.")
            break  # Break the loop if no new results were found in this iteration

        start += 10  # Prepare for the next set of results
        sleep(sleep_interval)

if __name__ == "__main__":
    for i in search("best camping site in free fire bermuda map", num_results=5,advanced=True,timeframe="1 month"):
        print(i)