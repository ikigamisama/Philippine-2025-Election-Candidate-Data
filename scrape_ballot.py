import os
import requests
import asyncio
import random
import nest_asyncio
from playwright.async_api import async_playwright
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
nest_asyncio.apply()

headers = {
    "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    "Cookie": "JSESSIONID=xxxxx; __cf_bm=VqNccgvWkJMsooZPF1G6ehBFtvxk4Zgw7.nTEyWbiNU-1746446483-1.0.1.1-HdjmTE3DuGpuVJDwyXcsV99luJ6zKTHooPNoZC72KnurwdU.kHh_h9CNzLVNJ241b5CVmITYlGIIcuvckOgR1BQJwqjI4rLOj0q.ztQfugQ",
    "User-Agent": UserAgent().random,
    'Priority': "u=0, i",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Ch-Ua": "\"Not(A:Brand\";v=\"99\", \"Opera GX\";v=\"118\", \"Chromium\";v=\"133\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1"
}


async def extract_scrape_content(url, selector):
    soup = None
    browser = None
    try:
        async with async_playwright() as p:
            browser_args = {
                "headless": True,
                "args": ["--disable-blink-features=AutomationControlled"]
            }

            browser = await p.chromium.launch(**browser_args)
            context = await browser.new_context(
                locale="en-US",
                user_agent=UserAgent().random,
                viewport={"width": 1280, "height": 800},
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                screen={"width": 1280, "height": 800},
                permissions=["geolocation"],
                geolocation={"latitude": 14.5995, "longitude": 120.9842},
                timezone_id="Asia/Manila"
            )

            page = await context.new_page()

            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            await page.set_extra_http_headers(headers)
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector(selector, timeout=300000)

            for _ in range(random.randint(3, 6)):
                await page.mouse.wheel(0, random.randint(300, 700))
                await asyncio.sleep(random.uniform(0.5, 1))

            for _ in range(random.randint(5, 10)):
                await page.mouse.move(random.randint(0, 800), random.randint(0, 600))
                await asyncio.sleep(random.uniform(0.5, 1))

            rendered_html = await page.content()
            return BeautifulSoup(rendered_html, "html.parser")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if browser:
            await browser.close()


def download_pdf(path, link, name):
    response = requests.get(link, headers=headers)

    with open(f"{path}{name}", "wb") as f:
        f.write(response.content)


if __name__ == "__main__":

    soup = asyncio.run(extract_scrape_content(
        'https://comelec.gov.ph/html-tpls/2025NLE/2025BallotFace.html', '.body-content'))
    excemption = ['OVERSEAS VOTING', 'LOCAL ABSENTEE VOTING']

    to_replace = "Ã‘"
    replace_with = "Ñ"
    for regional in soup.find_all('a', attrs={'class': ['btn', 'btn-info']}):
        if regional.get_text() not in excemption:
            os.makedirs(
                f"./pdf/{regional.get('href').split('/')[-1]}", exist_ok=True)
            region_site = f'https://comelec.gov.ph/html-tpls/2025NLE/2025BallotFace/{regional.get("href").split("/")[-1]}.html'
            regional_soup = asyncio.run(
                extract_scrape_content(region_site, '.body-content'))
            print(F"Scraping Regional: {region_site.replace('.html', '/')}")
            if regional_soup.find('table'):
                for district in regional_soup.find_all('li', class_="tb"):
                    print(
                        f"Downloading: 'https://comelec.gov.ph/{district.find('a').get('href').replace(to_replace, replace_with)}")
                    download_pdf(f'./pdf/{regional.get("href").split("/")[-1]}/', 'https://comelec.gov.ph/'+district.find('a').get(
                        'href').replace(to_replace, replace_with), district.find('a').get('href').split('/')[-1].replace(to_replace, replace_with))
            else:
                for province in regional_soup.find_all('div', class_="accordion-item"):
                    os.makedirs(
                        f"./pdf/{regional.get('href').split('/')[-1].replace(to_replace, replace_with)}/{province.find('span', class_='tb').getText().replace(to_replace, replace_with)}", exist_ok=True)

                    for prov_district in province.find_all('li'):
                        print(
                            f"Downloading: 'https://comelec.gov.ph/{prov_district.find('a').get('href').replace(to_replace, replace_with)}")
                        download_pdf(f"./pdf/{regional.get('href').split('/')[-1].replace(to_replace, replace_with)}/{province.find('span', class_='tb').getText().replace(to_replace, replace_with)}/",
                                     'https://comelec.gov.ph/'+prov_district.find('a').get('href').replace(to_replace, replace_with), prov_district.find('a').get('href').split('/')[-1].replace(to_replace, replace_with))

        else:
            download_pdf('./pdf/', 'https://comelec.gov.ph/' +
                         regional.get('href'), regional.get('href').split('/')[-1])
