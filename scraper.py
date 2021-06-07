import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from selenium.webdriver.firefox.options import Options

# Disables JS, making the pages load, like, a million times faster. Also prevents some ads.
op = Options()
op.set_preference('javascript.enabled', False)

# Sets the display environment variable, not sure if this is even needed for windows or even if it's just my computer that's stupid with this but it's there now.
os.environ['DISPLAY'] = ":0"

# Make the data directory to save the csv in
currentdir = os.listdir()
if "data" not in currentdir:
    os.mkdir("data")

# Select the webdriver, firefox requires geckodriver to work, make sure it's in your PATH
driver = webdriver.Firefox(options=op)

# List of categories for mediabiasfactcheck, their inconsistent on the website, it's not a typo on my end I swear.
cats = {"left", "leftcenter", "center", "right-center",
        "right", "conspiracy", "fake-news", "pro-science", "satire"}
# Do a loop for each category
for category in cats:
    # Connect to the webpage
    driver.get(f'https://mediabiasfactcheck.com/{category}/')

    # Prebuild these dictionaries
    group = []
    href = []
    links = []

    # Pull the HTML of the page
    content = driver.page_source

    # Make soup from the aforementioned HTML
    soup = BeautifulSoup(content, features="html.parser")

    # Find the table and then rows of the news groups
    table = soup.find(lambda tag: tag.name == 'table' and tag.has_attr(
        'id') and tag['id'] == "mbfc-table")
    rows = table.findAll(lambda tag: tag.name == 'tr')

    # Append each group name and the href link to the respective prebuilt dictionaries
    for row in rows:
        group.append(row.text)
        # What in the sweet mother of god happened here, this causes me physical pain but it works so I'm not touching it anymore
        try:
            # Don't even want to attempt trying to explain what hell has occurred here, maybe someone with literally any experience using BeautifulSoup could make this work in a normal way.
            href.append(row.contents[0].contents[0].contents[0].attrs["href"])
        except:
            try:
                href.append(row.contents[0].contents[0].attrs["href"])
            except:  # This means that it's an advert row in the table so we'll remove it.
                href.append(" ")

    for url in href:
        links.append("https://mediabiasfactcheck.com" + str(url))

    # Frame the dictionaries and save them to csv using Pandas
    df = pd.DataFrame({'Group': group, 'Link': links, "Type": category},)
    noadvert = df[~(df["Group"] == " ")]
    noadvert.to_csv(f'data/{category}.csv', index=False, encoding='utf-8')

driver.quit()
files = os.listdir("data")
try:
    files.remove("all.csv")
except:
    pass
if not os.path.exists("./data/all.csv"):
    open("./data/all.csv", 'w').close()
# Consolidate all CSV files into one object
allcsv = pd.concat([pd.read_csv("./data/"+file) for file in files])
# Convert the above object into a csv file and export
allcsv.to_csv("./data/all.csv", index=False, encoding="utf-8")
