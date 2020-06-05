#!/usr/bin/python3
import csv
from selenium import webdriver
import threading , time , datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options

import json

import re

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

ACERTOS=0
FALHAS=0
SEM_RESPOSTAS=0
START_TIME=time.time()
TIMEOUT=5


def lerListaProcessos(nome="lista_processos.txt"):
    procl=[]
    with open(nome,"r") as f:
        for i in f:
            if i=="\n":
                continue
            x=i.replace("\n","")
            procl.append(x)
    return procl

def check_apenso(clean):
    #print(clean)
    match=re.search("COM (\d*) APENSO",clean)
    if match==None:
        return "nenhum",""
    z=match.start()
    evidence=clean[z:z+13]
    return "CONTEM APENSOS",evidence 

def check_volume(clean):
    
    #print(clean)

    match=re.search("VOLUMES [A-Z0-9]",clean)
    if match!=None:

        z=match.start()
        evidence=clean[z:z+40]
        return "CONTEM VOLUMES",evidence

    match=re.search("Vols. [A-Z0-9]",clean)
    if match!=None:
        z=match.start()
        evidence=clean[z:z+40]
        return "CONTEM VOLUMES",evidence

    return "nenhum",""

class writer_manager():
    def __init__(self):
        self.csvfile=open("results-crashed.csv","w",newline='')
        self.fieldnames  = ["num_processo","detalhe","apensos","vulumes","evidencia_apensos","evidencia_columes","size_of_request"]
        self.writer = csv.DictWriter(self.csvfile,fieldnames=self.fieldnames)
        self.writer.writeheader()

    def write_row(self,l):
        self.csvfile=open("results.csv","a",newline='')
        self.writer = csv.DictWriter(self.csvfile,fieldnames=self.fieldnames)
        x=self.fieldnames
        self.writer.writerow({x[0]: l[0],
            x[1]: '',
            x[2]:l[1],
            x[3]:l[2],
            x[4]:l[3],
            x[5]:l[4],
            x[6]:l[5]
            })
        self.csvfile.close()

class Tester:
    def __init__(self):
        self.options = Options()
        self.options.headless =False
        self.firefox_profile = webdriver.FirefoxProfile()
        self.firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
        #self.firefox_profile.set_preference("browser.link.open_newwindow", 1)
    def checar(self,processo):
        #creates a webdriver in anonymous mode and wit gui
        self.driver=webdriver.Firefox(firefox_profile=self.firefox_profile,options=self.options)

        #requests for main page and enters in iframe
        self.driver.get('http://www4.tjrj.jus.br/consprocadm/consultaPorCodProc.aspx/')
        #id form = ContentPlaceHolder1_txtNumProtocolo

        self.driver.find_element_by_id("ContentPlaceHolder1_txtNumProtocolo").send_keys(processo)
        self.driver.find_element_by_id("ContentPlaceHolder1_btnConsultar").click()
        
        try:

            hasSei = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblHtmlDadosProcesso")))
            hasSei=self.driver.find_element_by_id("ContentPlaceHolder1_updatePanelConsultaPorProc")
            sei_html=hasSei.get_attribute('innerHTML')
            #print(sei_html)
            if "Este processo já é eletrônico e está tramitando pelo SEI." in sei_html:
                #print("SEI")
                return "SEI"

            self.driver.find_element_by_id("ContentPlaceHolderBarra_btnTodosMovimentos").click()
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "paginacaoProtocolo")))

            target=self.driver.find_element_by_id("ContentPlaceHolder1_updatePanelConsultaPorProc")
            #element_present = EC.presence_of_element_located((By.class, 'element_id'))
            #content = driver.find_element_by_class_name('content')
        except TimeoutException:
            return None

        #time.sleep(1)

        html=target.get_attribute('innerHTML')
        while len(cleanhtml(html)) <= 851:
            print("SOULDNT HAPPEND")
            print(cleanhtml(html))
            time.sleep(0.5)
            target=self.driver.find_element_by_id("ContentPlaceHolder1_updatePanelConsultaPorProc")
            html=target.get_attribute('innerHTML')
        self.driver.close()
        clean=cleanhtml(html)
        return clean,len(clean)

if __name__=="__main__":
    my_tester=Tester()
    my_csv=writer_manager()
    proc=lerListaProcessos("crashed.txt")
    for num in proc:
        ret=my_tester.checar(num)
        if ret!=None:
            if ret=="SEI":
                print(num,ret)
                my_csv.write_row([num]+["SEI",""]+["","",""])
            else:

                html,size=ret
                x=check_apenso(html)
                y=check_volume(html)
                print(num,x,y,size)
                my_csv.write_row([num]+list(x)+list(y)+[size])

        else:
            print(num,"crashed!")
            my_tester.driver.close()
            my_csv.write_row([num]+["crashed",""]+["","",""])

        #break
