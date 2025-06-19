from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from busstop.models import BusStop
import time

class Command(BaseCommand):
    help = 'Scrapes bus stop data and saves it to the database'

    def handle(self, *args, **kwargs):
        driver = webdriver.Chrome()  

        for stop_id in range(500, 25000):
            url = f"https://transit.ttc.com.ge/#/board-info/1:{stop_id}/arrival-times"
            driver.get(url)
            time.sleep(0.2)  
            
            try:
                p_tag = driver.find_element(By.CSS_SELECTOR, "p.sc-fsYfdN.cFzFOR")
                arrival_time = p_tag.text
                bus_stop, created = BusStop.objects.get_or_create(stop_id=stop_id)
                bus_stop.arrival_time = arrival_time
                bus_stop.save()
                self.stdout.write(self.style.SUCCESS(f"{stop_id} => {arrival_time}"))
            except NoSuchElementException:
                self.stdout.write(self.style.WARNING(f"{stop_id} => Not found"))
            
        driver.quit()
