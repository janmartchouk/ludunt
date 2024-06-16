import requests
import json
import re
import time
import os
import sys
import bs4 as bs


def get_soup_with_caching(local_filename, url):
    # check if local html exists and is younger than 1 hour, otherwise scrape
    if os.path.exists(local_filename + '.html') and (time.time() - os.path.getmtime(local_filename + '.html')) < (60 * 60):
        with open(local_filename + '.html', 'r') as f:
            return bs.BeautifulSoup(f.read(), 'html.parser')
    else:
        response = requests.get(url)
        with open(local_filename + '.html', 'w') as f:
            f.write(response.text)
        return bs.BeautifulSoup(response.text, 'html.parser')

# for tennis, velo on eurosport
def process_eurosport_entrycombo(entries):
    games = []

    for entry in entries:
        # split at first occurence of a number
        title = re.findall(r'^.*?(?=\d)', entry.text)[0]
        # rest is dates, split at ' - '
        start, end = entry.text[len(title):].split(' - ')
        games += [(title, start, end)]
    return games


def scrape_eurosport_tennis(local_filename, url):
    soup = get_soup_with_caching(local_filename, url)

    # find calendar entries with class flex items-center overflow-hidden
    entries = soup.find_all('div', class_='flex items-center overflow-hidden')

    return process_eurosport_entrycombo(entries)

def scrape_eurosport_velo(local_filename, url):
    soup = get_soup_with_caching(local_filename, url)
    
    races = []

    entries = soup.find_all('a', class_='table-generic__row')

    return process_eurosport_entrycombo(entries)

def scrape_eurosport_football(local_filename, url):
    soup = get_soup_with_caching(local_filename, url)

    games = []

    # one day has class='mt-5 md:mt-10'
    days = soup.find_all('div', class_='mt-5 md:mt-10')
    for day in days:
        date = day.find_all('div', class_='caps-s5-rs font-bold')
        if date == []:
            continue
        else:
            date = '/'.join(date[0].text.split('.')[:2])

        entries = day.find_all('div', class_='flex space-x-[1px]')
        for entry in entries:
            # teams have class='lines-3 text-onLight-02 group-hover:underline group-focus:underline text-right caps-s6-fx font-bold lg:caps-s5-fx'
            team1 = entry.find_all('div', class_='lines-3 text-onLight-02 group-hover:underline group-focus:underline text-right caps-s6-fx font-bold lg:caps-s5-fx')[0].text
            team2 = entry.find_all('div', class_='lines-3 text-onLight-02 group-hover:underline group-focus:underline text-left caps-s6-fx font-bold lg:caps-s5-fx')[0].text
            # if there is a time, it has class='caps-s6-fx flex-center h-10 min-w-[66px] rounded-[2px] font-bold text-onDark-01 lg:caps-s3-fx lg:h-12.5 lg:w-25 bg-fill-09'
            time = entry.find_all('div', attrs={'data-testid': 'team-match-score-atom-container-info-content-box'})
            if time:
                time = time[0].text
                games += [(f"{team1} - {team2}", date, date, None, None, False, time)]
            else:
                # there should be a score
                score1 = entry.find_all('div', attrs={'data-testid': 'team-match-score-atom-container-score-content-box'})[0].text
                score2 = entry.find_all('div', class_='caps-s6-fx flex-center h-10 min-w-[32px] rounded-[2px] font-bold bg-fill-10 text-onDark-03 lg:caps-s3-fx lg:h-12.5 lg:w-12.5')[0].text
                games+= [(f"{team1} - {team2}", date, date, None, None, True, score1, score2)]

    return games

if __name__ == '__main__':
    # set cwd to script location
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # parse args: we can scrape tennis, football and velo. if no args, scrape all
    if len(sys.argv) == 1:
        sports = ['tennis', 'football', 'velo']
    else:
        sports = sys.argv[1:]
        for sport in sports:
            if sport not in ['tennis', 'football', 'velo']:
                raise ValueError('Invalid sport: %s' % sport)
    print(f'scraping {', '.join(sports)}')

    # scrape tennis
    if 'tennis' in sports:
        # men
        with open('tennis_men.json', 'w') as f:
            f.write(json.dumps(scrape_eurosport_tennis(
                'tennis_men', 'https://www.eurosport.de/tennis/atp-race/zeitplan-kalender-ergebnisse.shtml')))
        print('scraped tennis (ATP)')

        with open('tennis_women.json', 'w') as f:
            f.write(json.dumps(scrape_eurosport_tennis(
                'tennis_women', 'https://www.eurosport.de/tennis/wta-race/zeitplan-kalender-ergebnisse.shtml')))
        print('scraped tennis (WTA)')

    # scrape velo
    if 'velo' in sports:
        with open('velo.json', 'w') as f:
            f.write(json.dumps(scrape_eurosport_velo(
                'velo', 'https://www.eurosport.de/radsport/calendar-result.shtml')))
        print('scraped velo')

    # scrape football
    if 'football' in sports:
        # game : ["team1 - team2", date, date, None, None, True/False, score1/time, score2] 
        with open('football_euros.json', 'w') as f:
            f.write(json.dumps(scrape_eurosport_football(
                "football_euros", "https://www.eurosport.de/fussball/euro/zeitplan-kalender-ergebnisse.shtml")))
        with open('football_buli1.json', 'w') as f:
            f.write(json.dumps(scrape_eurosport_football(
                "football_buli1", "https://www.eurosport.de/fussball/bundesliga/zeitplan-kalender-ergebnisse.shtml")))
        with open('football_buli2.json', 'w') as f:
            f.write(json.dumps(scrape_eurosport_football(
                "football_buli2", "https://www.eurosport.de/fussball/2-bundesliga/zeitplan-kalender-ergebnisse.shtml")))
        with open('football_laliga.json', 'w') as f:
            f.write(json.dumps(scrape_eurosport_football(
                "football_laliga", "https://www.eurosport.de/fussball/la-liga/zeitplan-kalender-ergebnisse.shtml")))
        with open('football_premier.json', 'w') as f:
            f.write(json.dumps(scrape_eurosport_football(
                "football_premier", "https://www.eurosport.de/fussball/premier-league/zeitplan-kalender-ergebnisse.shtml")))
        print('scraped football')

