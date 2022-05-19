# Data-scrapper

Pre requisites:

1.Python 3.x: https://www.python.org/downloads/

2.Scrapy: https://github.com/scrapy/scrapy and https://docs.scrapy.org/en/latest/

3.Networkx: https://networkx.org/documentation/stable/index.html

4.Website used to crawl: https://firststop.sos.nd.gov/search/business


# Instructions to Run

Download the entire code and then run python3 WebScraping.py on command line, this will start a spider and crawl the 
website, then fetch particular data and save it into a csv file. There are print statements in the code which tells what
data is being saved to the csv files (crawled_data.csv).

Later the csv file is read and a graph using networkx and matplotlib is plotted (Companies_graph.png). The main.py file
is a networkx tutorial, result is inside "graph.png".

Please use Chrome dev tools to understand what urls are needed to send the GET and POST requests.

Also, if using windows to run this project you'll face problems with pygraphviz, Hence I used wsl ubuntu distro.



