import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import csv
import random
import matplotlib.pyplot as plt
import networkx as nx


class NorthDakotaSpider(scrapy.Spider):
    name = "ND_Spider"
    allowed_domains = ['firststop.sos.nd.gov']
    start_urls = ['https://firststop.sos.nd.gov/search/business']
    crawled_data = []
    header = ['Company', 'Owner', 'Registered Agent', 'Commercial Registered Agent']

    def parse(self, response):
        print(response.xpath('//title/text()').get())
        data = {
            "SEARCH_VALUE": "X",
            "STARTS_WITH_YN": "true",
            "ACTIVE_ONLY_YN": "true",
        }  # data to pass in the url to search with the above values
        return scrapy.http.JsonRequest(url='https://firststop.sos.nd.gov/api/Records/businesssearch', data=data,
                                       callback=self.after_searching)

    def after_searching(self, response):
        json_response = json.loads(response.text)
        for key in json_response["rows"]:
            print(json_response["rows"][key]["TITLE"])
            if json_response["rows"][key]["TITLE"][0][0] == 'X':  # Checking if the Company starts with X or not.
                add_info_request = scrapy.http.JsonRequest("https://firststop.sos.nd.gov/api/FilingDetail/business/" +
                                                           str(key) + "/false", callback=self.get_owners_agents)
                # passing the company name to callback function to store the same in a variable and then in csv
                add_info_request.cb_kwargs['company_name'] = json_response["rows"][key]["TITLE"][0]
                yield add_info_request

    def get_owners_agents(self, response, company_name):
        json_data = json.loads(response.text)  # this contains the data present inside the drawer of every row(company)
        print(company_name)
        registered_agent = ""
        com_registered_agent = ""
        owner_name = ""
        # we clearly have either owner name or Registered agent as a link to each company.
        for i in range(0, len(json_data["DRAWER_DETAIL_LIST"])):
            if json_data["DRAWER_DETAIL_LIST"][i]["LABEL"] == "Registered Agent":
                registered_agent = json_data["DRAWER_DETAIL_LIST"][i]["VALUE"].split('\n')[0]
                print(registered_agent)
            if json_data["DRAWER_DETAIL_LIST"][i]["LABEL"] == "Commercial Registered Agent":
                com_registered_agent = json_data["DRAWER_DETAIL_LIST"][i]["VALUE"].split('\n')[0]
                print(com_registered_agent)
            if json_data["DRAWER_DETAIL_LIST"][i]["LABEL"] == "Owner Name":
                owner_name = json_data["DRAWER_DETAIL_LIST"][i]["VALUE"]
                print(owner_name)
        self.crawled_data.append([company_name, owner_name, registered_agent, com_registered_agent])


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    nds = NorthDakotaSpider
    process.crawl(nds)
    process.start()
    with open('crawled_data.csv', 'w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(nds.header)
        writer.writerows(nds.crawled_data)

    Graph = nx.Graph()
    nodes = set()
    edges = []
    with open('crawled_data.csv') as file:
        reader = csv.reader(file)
        for row in reader:
            nodes.add(row[0])
            if not row[1]:
                if not row[2]:
                    if row[3]:
                        nodes.add(row[3])
                        edges.append((row[0], row[3]))
                else:
                    nodes.add(row[2])
                    edges.append((row[0], row[2]))
            else:
                nodes.add(row[1])
                edges.append((row[0], row[1]))

    Graph.add_nodes_from(nodes)
    Graph.add_edges_from(edges)
    plt.figure(1, figsize=(18, 18))
    # layout graphs with positions using graphviz neato
    pos = nx.nx_agraph.graphviz_layout(Graph, prog="neato")
    # color nodes the same in each connected subgraph
    components = (Graph.subgraph(c) for c in nx.connected_components(Graph))
    for g in components:
        color = [random.random()] * nx.number_of_nodes(g)  # random color...
        nx.draw_networkx(g, pos, node_size=40, node_color=color, vmin=0.0, vmax=1.0, with_labels=True, font_size=3.5)
    plt.savefig('Companies_Graph.png', dpi=1000)  # High quality image so that we can read the labels
