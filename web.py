
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.log import Log
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import webdriver


driver = webdriver.Chrome()

driver.get("https://mozaikportail.ca/")
driver.find_element(By.XPATH, '//button[@class="btnConnexion btn"]').click()

time.sleep(10)
desired_url = "https://mozaikportail.ca/"
try:
    WebDriverWait(driver, 30).until(EC.url_to_be("https://mozaikportail.ca/"))
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, """a[href='#'][onclick="event.preventDefault(); changerEspaceTravail('eleve');"]""")))
    driver.find_element(By.CSS_SELECTOR, """a[href='#'][onclick="event.preventDefault(); changerEspaceTravail('eleve');"]""").click()
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "monHoraire__navigation")))
    monHoraire_button = driver.find_element(By.CLASS_NAME, "monHoraire__navigation")
    driver.execute_script ("arguments[0].click();",monHoraire_button)
    for request in driver.requests:
        print(request.url)
        if "https://apiaffairesmp.mozaikportail.ca/api/organisationScolaire/calendrierScolaire/" in request.url:
            print(request.headers['Authorization:'])
            print("Trouve")

except TimeoutException:
    print("Desired url was not rendered with in allocated time")
    print(driver.current_url)
print("Finish")
while(True):
    pass
