""" Seleniumアクセス管理 """
import os
import time
import sys
import utils
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


# 結果オブジェクト
RESULTS = None


def login(driver: WebDriver, wait: WebDriverWait):
    """ ログイン """
    url = 'https://s.amebame.com'

    driver.get(url)

    # click login
    link_text = os.environ.get('SOCIAL_VENDOR_NAME')
    wait.until(ec.element_to_be_clickable((By.LINK_TEXT, link_text)))
    target_link = driver.find_element_by_link_text(link_text)
    target_link.click()

    # username
    username = driver.find_element_by_id('username')
    wait.until(ec.visibility_of(username))
    username.send_keys(os.environ.get('SOCIAL_USERNAME'))
    driver.find_element_by_id('btnNext').click()
    time.sleep(2)

    # password
    wait.until(ec.visibility_of_element_located((By.ID, 'passwd')))
    password = driver.find_element_by_id('passwd')
    password.send_keys(os.environ.get('SOCIAL_PASSWORD'))
    time.sleep(2)

    # click
    driver.find_element_by_id('btnSubmit').click()


def get_driver(user_agent=''):
    """ WebDriver生成 """
    opts = Options()
    binary_location = os.environ.get('BINARY_LOCATION')
    if binary_location:
        opts.binary_location = binary_location

    if user_agent:
        opts.add_argument('user-agent=%s' % (user_agent))

    driver = webdriver.Chrome(chrome_options=opts)
    wait = WebDriverWait(driver, 10)
    driver.set_window_size(400, 900)
    driver.implicitly_wait(10)

    return (driver, wait)


def access_to_sp():
    """ SPサイトへアクセス """
    user_agent = 'Mozilla/5.0 (Linux; Android 5.0.2; SH-04G Build/SC010)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Mobile Safari/537.36'
    driver, wait = get_driver(user_agent)

    try:
        login(driver, wait)

        if not RESULTS.slot.get('success'):
            slot(driver)

        if not RESULTS.roulette.get('success'):
            roulette(driver, wait)

        if not RESULTS.scratch.get('success'):
            scratch(driver, wait)

    except:
        utils.LOGGER.error(sys.exc_info()[0])
        raise
    finally:
        driver.quit()


def slot(driver: WebDriver):
    """ スロット """
    url = 'https://aw.mobadme.jp/slot/play?m_id=1528'
    success = False

    driver.get(url)

    # スロットは処理に時間がかかるので長めに設定
    slot_wait = WebDriverWait(driver, 20)

    try:
        current = driver.current_url

        # 開始ボタン（ここは長めに待つ）
        start = driver.find_element_by_xpath(
            '//*[@id=\"enchant-stage\"]/div/div[57]')
        start.click()

        # URLが結果画面になるのを待つ
        slot_wait.until(lambda driver: driver.current_url != current)

        success = True
    except:
        utils.LOGGER.warn("　スロットはプレイ済みでした。")

    # ステータス更新
    RESULTS.slot = {
        'success': success
    }


def roulette(driver: WebDriver, wait: WebDriverWait):
    """ ルーレット """
    url = 'https://s.amebame.com/#gacha/roulette/lp'
    success = True

    # プレイ回数を決める
    count = 1
    loop_count = 1

    driver.get(url)

    # URLが一度リダイレクトするため、それらが終わるのを待つ
    try:
        wait.until(lambda driver: driver.current_url != url)
        wait.until(lambda driver: driver.current_url !=
                   'https://s.amebame.com')
    except:
        # タイムアウトになったのでURL遷移できているものとみなす
        pass

    try:
        # "roulette_img" > img のファイルパスを見て実行回数を決める
        image = driver.find_element_by_css_selector('.roulette_img img')
        src = image.get_attribute("src")
        if src.endswith("-x3.png"):
            utils.LOGGER.info("3回実施")
            count = 3
        elif src.endswith("-x2.png"):
            utils.LOGGER.info("2回実施")
            count = 2

        while loop_count <= count:
            button_locator = '.gacha_button'
            start = driver.find_element_by_css_selector(button_locator)
            wait.until(ec.element_to_be_clickable(
                (By.CSS_SELECTOR, button_locator)))

            # フッターで要素が隠れるため、少し下の要素へ移動してからボタンを押す
            start.click()

            # URLが結果画面になるのを待つ
            wait.until(lambda driver: driver.current_url != url)

            # 結果が出るのを待つ
            # はずれ：// *[@id="gacha"] / div[1] / img
            # あたり：// *[@id=\"gacha\"] / div[1] / div[1] / img
            wait.until(ec.visibility_of_element_located(
                (By.CSS_SELECTOR, '#gacha > div.roulette_result img')))

            loop_count += 1

            if loop_count <= count:
                # 3秒待つ
                time.sleep(3)
                # 戻ってページ再読み込み
                driver.back()
                wait.until(ec.url_to_be(url))
                driver.refresh()
    except:
        utils.LOGGER.exception('ルーレットプレイエラー')
        success = False

    # 最終結果
    RESULTS.roulette = {
        'count': count,
        'success': success,
    }


def scratch(driver: WebDriver, wait: WebDriverWait):
    """ スクラッチ """
    url = 'http://d-moneymall.mobadme.jp/scratch/'
    success = False

    driver.get(url)

    # URLがリダイレクトしていない（結果画面でない）場合、スクラッチを実施
    if driver.current_url == url:
        try:
            # ページをリフレッシュし、URLが結果画面になるのを待つ
            driver.refresh()
            wait.until(lambda driver: driver.current_url != url)
        except:
            utils.LOGGER.exception('スクラッチプレイエラー')

    # ステータス更新
    RESULTS.scratch = {
        'success': success,
    }
