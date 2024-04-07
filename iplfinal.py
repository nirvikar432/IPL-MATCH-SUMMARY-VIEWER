import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import webbrowser


# urlnew = ["https://www.cricbuzz.com/live-cricket-scorecard/89763/mi-vs-dc-20th-match-indian-premier-league-2024"]
urlnew = [input("Paste a crickbuz score card link : ")]

def toss(url):
    webpage = requests.get(url)
    if webpage.status_code == 200:
        soup = BeautifulSoup(webpage.content, 'html.parser')
        for m in soup.find_all('div', class_='cb-col cb-col-73'):
            n = m.text
            if "opt" in n:
                return m.text.strip()
    else:
        print("Failed to retrieve toss information from the URL.")
        return None

def matchWin(url):
    webpage = requests.get(url)
    if webpage.status_code == 200:
        soup = BeautifulSoup(webpage.content, 'html.parser')
        for x in soup.find_all('div', class_='cb-col cb-col-100 cb-bg-white'):
            for y in x.find_all('div', class_='cb-col cb-scrcrd-status cb-col-100 cb-text-complete'):
                return y.text.strip()
    else:
        print("Failed to retrieve winner information from the URL.")
        return None

def score(url):
    webpage = requests.get(url)
    if webpage.status_code == 200:
        soup = BeautifulSoup(webpage.content, 'html.parser')
        scores_list = []
        for m in soup.find_all('div', class_='cb-col cb-col-100 cb-scrd-hdr-rw'):
            for span in m.find_all("span", class_='pull-right'):
                scores_list.append(f"Score for {m.text.strip()}")
        return scores_list
    else:
        print("Failed to retrieve score information from the URL.")
        return None

def scrape_batsman_runs(url):
    webpage = requests.get(url)
    if webpage.status_code == 200:
        soup = BeautifulSoup(webpage.content, 'html.parser')
        batsman_data = {}
        innings_data = soup.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')
        for inning in innings_data:
            inning_title_element = inning.find('div', class_='cb-col cb-col-100 cb-scrd-hdr-rw')
            if inning_title_element:
                inning_title = inning_title_element.text.strip()
                batsman_data[inning_title] = {}
                batsmen = inning.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
                for batsman in batsmen:
                    batsman_name_element = batsman.find('a', class_='cb-text-link')
                    runs_element = batsman.find('div', class_='cb-col cb-col-8 text-right text-bold')
                    if batsman_name_element and runs_element:
                        batsman_name = batsman_name_element.text.strip()
                        runs = runs_element.text.strip()
                        if batsman_name not in batsman_data[inning_title]:
                            batsman_data[inning_title][batsman_name] = int(runs)
                        else:
                            batsman_data[inning_title][batsman_name] += int(runs)
        return batsman_data
    else:
        print("Failed to retrieve batsman runs information from the URL.")
        return None

def plot_batsman_runs(batsman_data):
    for inning, batsmen in batsman_data.items():
        plt.figure(figsize=(10, 6))
        plt.barh(list(batsmen.keys()), list(batsmen.values()), height=0.6)
        plt.xlabel('Runs')
        plt.ylabel('Batsmen')
        plt.title(f'Runs scored by each batsman - {inning}')
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        batsman_data[inning] = img_str
        plt.close()


def save_to_html(all_data):
    with open("cricket_stats.html", "w") as f:
        f.write("<html><head><title>Cricket Stats</title></head><body><h1><center>IPL MATCH SUMMARY</center><h1>")
        if 'Toss' in all_data:
            f.write(f"<h2>Toss</h2>")
            f.write(f"<p>{all_data['Toss']}</p>")
        if 'Match Winner' in all_data:
            f.write(f"<h2>Match Winner</h2>")
            f.write(f"<p>{all_data['Match Winner']}</p>")
        if 'Scores' in all_data:
            f.write(f"<h2>Scores</h2>")
            f.write("<ul>")
            for item in all_data['Scores']:
                f.write(f"<li>{item}</li>")
            f.write("</ul>")
        for data_type, data in all_data.items():
            if isinstance(data, pd.DataFrame):
                f.write(f"<h2>{data_type}</h2>")
                f.write(data.to_html(index=False))
            elif isinstance(data, str) and data.startswith('data:image/png;base64,'):
                f.write(f"<h2>{data_type}</h2>")
                f.write(f"<img src='{data}'><br>")
        f.write("</body></html>")

    webbrowser.open(r'cricket_stats.html')

def scrape_and_store(url):
    all_data = {}
    all_data['Toss'] = toss(url)
    all_data['Match Winner'] = matchWin(url)
    all_data['Scores'] = score(url)
    batsman_data = scrape_batsman_runs(url)
    if batsman_data:
        plot_batsman_runs(batsman_data)
        for inning, img_data in batsman_data.items():
            all_data[inning] = f'data:image/png;base64,{img_data}'
    save_to_html(all_data)

for url in urlnew:
    scrape_and_store(url)
