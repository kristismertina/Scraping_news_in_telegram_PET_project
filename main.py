import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


def get_first_news():
    # cписок заголовков
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0"
    }

    # ссылка на ресурс
    url = "https://www.securitylab.ru/news/"  
    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")
    # результат, сво-во текст, парсер
    articles_cards = soup.find_all("a", class_="article-card")

    news_dict = {}
    for article in articles_cards:
        # заголовок, информация
        article_title = article.find("h2", class_="article-card-title").text.strip()
        article_desc = article.find("p").text.strip()
        # домен
        article_url = f'https://www.securitylab.ru{article.get("href")}'

        # date
        article_date_time = article.find("time").get("datetime")
        # допустимый формат исо
        date_from_iso = datetime.fromisoformat(article_date_time)
        #явный формат
        date_time = datetime.strftime(date_from_iso, "%Y-%m-%d %H:%M:%S")
        # unix timestamp формат, кортеж, обращение по индексу
        article_date_timestamp = time.mktime(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timetuple())

        #айди новости, разбиваем по слешу и убираем последние 4 символа
        article_id = article_url.split("/")[-1]
        article_id = article_id[:-4]

        # собираем новости в словарь, к= айди, в=данные
        news_dict[article_id] = {
            "article_date_timestamp": article_date_timestamp,
            "article_title": article_title,
            "article_url": article_url,
            "article_desc": article_desc
        }
    # запись в джейсон
    with open("news_dict.json", "w") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)


# обновления, если появляются свежие новости
def check_news_update():
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0"
    }

    url = "https://www.securitylab.ru/news/"
    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")
    articles_cards = soup.find_all("a", class_="article-card")

    #id
    fresh_news = {}
    for article in articles_cards:
        article_url = f'https://www.securitylab.ru{article.get("href")}'
        article_id = article_url.split("/")[-1]
        article_id = article_id[:-4]

        #проверка на наличие новости в списке, при отсутствии, добавляем
        if article_id in news_dict:
            continue
        else:
            article_title = article.find("h2", class_="article-card-title").text.strip()
            article_desc = article.find("p").text.strip()

            article_date_time = article.find("time").get("datetime")
            date_from_iso = datetime.fromisoformat(article_date_time)
            date_time = datetime.strftime(date_from_iso, "%Y-%m-%d %H:%M:%S")
            article_date_timestamp = time.mktime(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timetuple())


            # новый словарь со свежими новстями
            news_dict[article_id] = {
                "article_date_timestamp": article_date_timestamp,
                "article_title": article_title,
                "article_url": article_url,
                "article_desc": article_desc
            }


             #  только свежие новости
            fresh_news[article_id] = {
                "article_date_timestamp": article_date_timestamp,
                "article_title": article_title,
                "article_url": article_url,
                "article_desc": article_desc
            }


    # добавляем свежие новости в джейсон 
    with open("news_dict.json", "w") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)

    return fresh_news

def main():
#     # get_first_news()
    print(check_news_update())


    


if __name__ == '__main__':
    main()