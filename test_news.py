import os
import requests

from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("NEWSDATA_API_KEY")


if not API_KEY:

    print("ERROR: NEWSDATA_API_KEY not found in .env")

    exit()


url = "https://newsdata.io/api/1/latest"


params = {
    "apikey": API_KEY,
    "language": "en",
    "country": "in",
    "size": 10
}


try:

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    print("HTTP STATUS:", response.status_code)

    data = response.json()

    print("API STATUS:", data.get("status"))


    if data.get("status") != "success":

        print("API RESPONSE:")
        print(data)

        exit()


    print()
    print("LATEST NEWS")
    print("=" * 50)


    for index, article in enumerate(
        data.get("results", [])[:5],
        start=1
    ):

        title = article.get("title")

        if title:

            print(f"{index}. {title}")


except Exception as error:

    print("ERROR:", error)