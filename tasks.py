from robocorp.tasks import task
from robocorp import browser
import pandas as pd
import datetime
import shutil
from RPA.PDF import PDF

@task
def minimal_task():
    
    df = pd.read_csv("input/orders.csv")

    access_page()

    for row in df.iterrows():
        order_robot(row)

    createZip()

def access_page():
    browser.configure(browser_engine="chrome")
    page = browser.page()
    page.goto("https://robotsparebinindustries.com/#/robot-order")
    page.click("button:text('Yep')")

def order_robot(row):

    pdf = PDF()
    nameOfPDF = "robotHTML.pdf"
    nameOfScreenshot = "screenshot.png"

    page = browser.page()
    page.select_option("//*[@id=\"head\"]",f'{row[1]["Head"]}')
    page.click(f'//*[@id="id-body-{row[1]["Body"]}"]')
    page.fill("//*[@placeholder=\"Enter the part number for the legs\"]",f'{row[1]["Legs"]}')
    page.fill("//*[@id=\"address\"]", f'{row[1]["Address"]}')
    page.click("//*[@id=\"order\"]")
    error = 1
    while(error == 1):
        try:
            error = 0
            page.wait_for_selector("//*[@id=\"receipt\"]", timeout=5000)
        except:
            error = 1
            print("Selector not found, trying again to order bot.")
            page.click("//*[@id=\"order\"]")
    robotData = page.locator("//*[@id=\"receipt\"]").inner_html()
    robotLocator = page.locator("//*[@id=\"robot-preview-image\"]")
    robotLocator.screenshot(type='png',path=f'output/temp/{nameOfScreenshot}')
    pdf.html_to_pdf(robotData, f'output/temp/{nameOfPDF}')
    secondsOfNow = datetime.datetime.now().strftime("%y%m%d%H%M%S")
    pdf.add_files_to_pdf(files=[f'output/temp/{nameOfPDF}','output/temp/screenshot.png'],target_document=f'output/robots_data/Robot{row[1]["Address"]}_{secondsOfNow}.pdf')
    page.click("//*[@id=\"order-another\"]")
    page.click("button:text('Yep')")

def createZip():
    name = "output/Robots"
    dir_name = 'output/robots_data'
    shutil.make_archive(name, 'zip', dir_name)