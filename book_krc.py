#!/usr/bin/env python

import sys
import os
import re
import time
import threading
import signal
from datetime import datetime, timedelta
from selenium import webdriver
import pdb

class KrcBook:
    krc_url = "https://reservation.frontdesksuite.ca/rcfs/richcraftkanata"
    prefered_hours = [8, 7, 1, 1, 1, 11, 10]
    tel_txt = u'6134152975'
    email_txt = u'r25hao@uwaterloo.ca'
    name_txt = u'Ray Hao'
    stop = False
    def __init__(self):
        self.thread = None
        book_day = datetime.today() + timedelta(days=2)
        self.weekday = book_day.strftime('%A')
        self.prefered_hour = self.prefered_hours[book_day.weekday()]
        # self.browser = webdriver.Firefox()
        self.browser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
        self.browser.implicitly_wait(30)

    def open_page(self):
        self.browser.get(self.krc_url)
        self.browser.find_element_by_partial_link_text('Lane swim').click()
        self.browser.find_element_by_id('submit').click()

    def get_date_entry(self):
        refresh = False
        while True:
            if KrcBook.stop:
                return None
            try:
                elm = self.browser.find_elements_by_xpath(".//div[@class='date one-queue']")[-1]
                text = elm.text.encode()
                if text.startswith(self.weekday):
                    return elm
            except:
                time.sleep(0.05)
                continue
            if refresh:
                try:
                    # check if the page is reloaded
                    tm_lst = elm.find_element_by_xpath("./ul[@class='times-list']")
                    if not tm_lst.get_attribute('style'):
                        time.sleep(0.05)
                        continue
                except:
                    continue
            refresh = True
            elm.click() # make times-list style='display: none;'
            self.browser.refresh()
            try:
                self.browser.switch_to_alert().accept()
            except:
                pass
            time.sleep(0.1)

    def select_slot(self, element):
        ################################### test with saved page ########################################
        # self.browser.get("file:///home/hcsh/Downloads/Richcraft%20Recreation%20Complex-Kanata4.html")
        # element = self.browser.find_elements_by_xpath("//div[@class='date one-queue']")[-1]
        # element.click()
        #################################################################################################
        slot_elm = []
        for ts in element.find_elements_by_xpath("./ul/li[@class='time']/a"):
            m = re.match(r"(\d+):\d+\s*([AP])M", ts.text.encode())
            if not m:
                continue
            hour = int(m.group(1))
            if hour == self.prefered_hour:
                return ts
            slot_elm.append(ts)
        if not slot_elm:
            print("No slot available.")
            return None
        return slot_elm[-1]

    def send_keys(self, element, input_text):
        elm_txt = element.get_attribute('value')
        if elm_txt == input_text:
            return
        if elm_txt:
            element.clear()
        element.send_keys(input_text)

    def book(self):
        ######################################## test with saved page ##################################
        # self.browser.get("file:///auto/tftpboot-ottawa/chuanhao/RC/Richcraft_Recreation_Complex-Kanata3.html")
        ################################################################################################
        while True:
            if KrcBook.stop:
                break
            try:
                for inp_elm in self.browser.find_elements_by_xpath("//input[not(@type='hidden')]"):
                    if inp_elm.get_attribute('type') == u'tel':
                        self.send_keys(inp_elm, self.tel_txt)
                    elif inp_elm.get_attribute('type') == u'email':
                        self.send_keys(inp_elm, self.email_txt)
                    elif inp_elm.get_attribute('type') == u'text':
                        self.send_keys(inp_elm, self.name_txt)
                self.browser.find_element_by_id('submit').click()
                time.sleep(0.2)
            except:
                break
    
    def run(self):
        self.open_page()
        elm = self.get_date_entry()
        if not elm:
            return
        
        elm.click()
        elm = self.select_slot(elm)
        if elm is None:
            return
        elm.click()
        self.book()

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def join(self):
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def close(self):
        self.browser.close()

if len(sys.argv) == 1:
    web_no = 1
else:
    web_no = int(sys.argv[1])

# wait until hour:minute
hour = 17
minute = 59
now = datetime.now()
until_time = datetime(now.year, now.month, now.day, hour=hour, minute=minute)
if now > until_time:
    until_time += timedelta(days=1)
print("Waiting until {}:{}...".format(hour, minute))
while True:
    time.sleep(1)
    total_seconds = int((until_time - datetime.now()).total_seconds())
    sys.stdout.write("\rTime left: {}         ".format(str(timedelta(seconds=total_seconds))))
    sys.stdout.flush()
    if total_seconds <= 2:
        time.sleep(1)
        break
print("\nStart...")

kbs = []
for i in range(web_no):
    kb = KrcBook()
    kbs.append(kb)
    kb.start()
    time.sleep(1)
while raw_input("Type EXIT to exit: ") != 'EXIT':
    pass

KrcBook.stop = True
for kb in kbs:
    kb.join()
    kb.close()
