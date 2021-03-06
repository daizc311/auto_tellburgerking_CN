import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import logging

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from util import LogUtil

BASE_URL: str = "https://tellburgerking.com.cn/"
# TODO 调查码应该在文件中读取或者以参数传递
BASE_CODE: str = "997723220095015AAA9"
log1 = LogUtil.LogHelper()

# 校验调查码的长度、形态是否合法，并且修正格式
if not BASE_CODE.isdigit():
    logging.error("请输入正确的调查码")
    sys.exit()
BASE_CODE = BASE_CODE.strip()
if len(BASE_CODE) != 16:
    logging.error("请输入16位调查码")
    sys.exit()

options = webdriver.ChromeOptions()
# 静默模式 无图模式
prefs = {'profile.managed_default_content_settings.images': 2}
options.add_experimental_option('prefs', prefs)
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


def next_page(): driver.find_element_by_id("NextButton").click()


def waiting_for_loading():
    WebDriverWait(driver, 15).until(EC.title_contains("BK"))
    logging.info("当前页面标题：" + driver.title)
    return "谢谢" in driver.title


try:
    # 第一个页面
    driver.get(BASE_URL)

    waiting_for_loading()
    next_page()

    # 第二个页面
    waiting_for_loading()
    for num in range(0, 6):
        driver.find_element_by_id("CN" + str(num + 1)).send_keys(BASE_CODE[3 * num:3 * num + 3])

    # TODO 此处应该根据页面提示语校验调查码是否有效
    next_page()

    # 调查页面
    while 1:
        if waiting_for_loading():
            break
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "radioSimpleInput")))
            for elem in driver.find_elements_by_class_name("radioSimpleInput")[::-1]: elem.click()
        except TimeoutException as e:
            logging.debug("本页没有单选框")
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "checkboxSimpleInput")))
            driver.find_elements_by_class_name("checkboxSimpleInput")[-1].click()
        except TimeoutException as e:
            logging.debug("本页没有复选框")
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.TAG_NAME, "select")))
            for selectEle in driver.find_elements_by_tag_name("select"):
                select = Select(selectEle)
                answer = select.options[-1].text
                select.select_by_visible_text(answer)
        except TimeoutException as e:
            logging.debug("本页没有选择框")
        next_page()

    # 获取结果
    baseCodeStr = "调查代码：" + BASE_CODE
    valCodeStr = driver.find_element_by_class_name("ValCode").text

    with open('tellburgerking[%s].txt' % BASE_CODE, 'wt', encoding="utf-8") as f:
        f.writelines([baseCodeStr, "\n", valCodeStr])

except TimeoutException as e:
    logging.exception("超时")
except Exception as e:
    logging.exception("异常")

finally:
    driver.close()
