import requests
import time
import threading

from selenium import webdriver


adidas_host = None

marketDomains = {
    'AT': 'adidas.at',
    'AU': 'adidas.com.au',
    'BE': 'adidas.be',
    'BR': 'adidas.com.br',
    'CA': 'adidas.ca',
    'CF': 'adidas.ca',
    'CH': 'adidas.ch',
    'CL': 'adidas.cl',
    'CN': 'adidas.cn',
    'CO': 'adidas.co',
    'CZ': 'adidas.cz',
    'DE': 'adidas.de',
    'DK': 'adidas.dk',
    'EE': 'baltics.adidas.com',
    'ES': 'adidas.es',
    'FI': 'adidas.fi',
    'FR': 'adidas.fr',
    'GB': 'adidas.co.uk',
    'GR': 'adidas.gr',
    'HK': 'adidas.com.hk',
    'HU': 'adidas.hu',
    'IE': 'adidas.ie',
    'ID': 'adidas.co.id',
    'IN': 'adidas.co.in',
    'IT': 'adidas.it',
    'JP': 'japan.adidas.com',
    'KR': 'adidas.co.kr',
    'KW': 'mena.adidas.com',
    'MX': 'adidas.mx',
    'MY': 'adidas.com.my',
    'NG': 'global.adidas.com',
    'NL': 'adidas.nl',
    'NO': 'adidas.no',
    'NZ': 'adidas.co.nz',
    'OM': 'adidas.com.om',
    'PE': 'adidas.pe',
    'PH': 'adidas.com.ph',
    'PL': 'adidas.pl',
    'PT': 'adidas.pt',
    'QA': 'adidas.com.qa',
    'RU': 'adidas.ru',
    'SE': 'adidas.se',
    'SG': 'adidas.com.sg',
    'SK': 'adidas.sk',
    'TH': 'adidas.co.th',
    'TR': 'adidas.com.tr',
    'TW': 'adidas.com.tw',
    'US': 'adidas.com',
    'VE': 'latin-america.adidas.com',
    'VN': 'adidas.com.vn',
    'ZA': 'adidas.co.za'
}


def main():
    print(
        """
              _ _     _              ____
     /\      | (_)   | |            / __ \
    /  \   __| |_  __| | __ _ ___  | |  | |_   _  ___ _   _  ___ _ __
   / /\ \ / _` | |/ _` |/ _` / __| | |  | | | | |/ _ \ | | |/ _ \ '__|
  / ____ \ (_| | | (_| | (_| \__ \ | |__| | |_| |  __/ |_| |  __/ |
 /_/    \_\__,_|_|\__,_|\__,_|___/  \___\_\\\\__,_|\___|\__,_|\___|_|

                Twitter - https://twitter.com/hunter_bdm
                Github - https://github.com/hunterbdm
        """
    )

    global adidas_host
    country_code = input('Enter country code: ').upper()

    while not (country_code in marketDomains):
        print("Invalid country code. Example: 'US' 'MX' 'AU' 'CA' ect.")
        country_code = input('Enter country code: ').upper()

    adidas_host = 'http://www.' + marketDomains[country_code]
    print('Adidas url: ', adidas_host)

    url = input('Splash page url: ')
    proxies_txt = open('proxies.txt')
    proxies = proxies_txt.readlines()

    if len(proxies) == 0:
        print('No proxies found in proxies.txt, starting without proxies.')
        start(url)
    else:
        print(str(len(proxies)) + ' proxies found.')
        start(url, proxies=proxies)

    while True:
        time.sleep(5)


def start(url, proxies=None):
    """
    :param url: Adidas Queue page url
    :param proxies: Array of proxies
    :return: none
    """
    print('Starting with proxies. Press END to quit.')

    if proxies:
        for proxy in proxies:
            # \n gets left behind and will fuck up the requests later on
            proxy = proxy.replace('\n', '')
            t = threading.Thread(target=_start, args=(url, proxy,))
            t.daemon = True
            t.start()
            time.sleep(1)
    else:
        t = threading.Thread(target=_start, args=(url, None,))
        t.daemon = True
        t.start()


def _start(url, proxy):
    """
    :param url: Adidas Queue page url
    :param proxies: Array of proxies, or None if no proxies
    :return: none
    """
    session = requests.Session()

    # Update User-Agent in session's headers
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }

    time.sleep(1.5)
    session.cookies.clear_session_cookies()

    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy
        }
        print('Entering queue with proxy', proxy)
    else:
        proxies = None
        print('Entering queue without proxy.')

    while True:
        time.sleep(1.5)
        resp = session.get(url, proxies=proxies)
        # If captcha is on page then we got through splash.
        if 'data-sitekey' in resp.text:
            if proxy:
                print('Proxy ' + proxy + ' got through queue. Transferring session.')
            else:
                print('Got through queue. Transferring session.')

            transfer_session(resp.url, session.cookies.get_dict(), resp.text, proxy=proxy)
            return


def transfer_session(url, cookies, page_source, proxy=None):
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1280,720')
    if proxy:
        options.add_argument('--proxy-server=' + proxy)

    browser = webdriver.Chrome(chrome_options=options)

    # Must be on adidas to set cookies for adidas, so just go to a 404 page and set cookies first.
    browser.get(adidas_host + '/settingcookies404')
    browser.delete_all_cookies()
    for cookie in cookies:
        c = {
            'name': cookie,
            'value': cookies[cookie],
            'path': '/'
        }
        browser.add_cookie(c)

    # Go to splash page url so that the referral will show it
    browser.get(url)

    # Setup script to change the HTML to that of the passed splash page.
    script = """
        function setHTML (html) {
            document.body.insertAdjacentHTML('beforeEnd', html);
            var range = document.createRange();
            range.setStartAfter(document.body.lastChild);
            document.documentElement.innerHTML = '';
            var docFrag = range.createContextualFragment(html);
            document.body.appendChild(docFrag);
        }
        html = `{{ html }}`
        setHTML(html)
    """
    script = script.replace("{{ html }}", page_source)

    browser.execute_script(script)


if __name__ == '__main__':
    main()