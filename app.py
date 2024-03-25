from flask import Flask, render_template, Response,redirect,request, url_for, send_file
import fitz
import os
import io
import base64
import json
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import sys 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

pdffile = None
pdffilepath = None

csvfile = None
csvfilepath = None

img_urls = None
textComps = None

bride_groom_Name = None
driver = None 

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)


CHROME_PATH = "/static/public/chromedriver-mac-arm64/chromedriver"
EL_ADDRESS = {
    "new_chat_el" : '//div[@title="Search input textbox"]',
    "attachment_el" : "//div[@title='Attach']",
    "doc_el" : "//input[@accept = '*']",
    "send_el" : '//div[@aria-label="Send"]'
}

def get_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    
    # Specify the remote debugging port
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://web.whatsapp.com")
        el = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, EL_ADDRESS["new_chat_el"]))
        )
    except Exception as err:
        print("Not connected Whatsapp")
    return driver



def savePageImages():
    try:
        global img_urls
        pdf = fitz.open(pdffilepath)
        pageCount = len(pdf)
        img_urls = []
        for i in range(pageCount):
            page = pdf[i]
            pix = page.get_pixmap()
            print("displayed pages' width and height: ", pix.width, pix.height)
            img_bytes = pix.tobytes('png')
            base64_encoded_img = base64.b64encode(img_bytes).decode('utf-8')
            data_url = f"data:image/png;base64,{base64_encoded_img}"
            img_urls.append(data_url)
        return len(img_urls)>0
    except Exception as e:
        print("error while getting images ",e)
        return False
    

def csv_to_json(csv_file_path):
    # Read CSV file and convert it to a list of dictionaries
    data = pd.read_csv(csv_file_path)
    json_str = data.to_json(orient='records')
    json_obj = json.loads(json_str)
    print(data.to_json(orient='values', indent=0))
    return json_obj

@app.route('/')
def index():
    global pdffile
    if(pdffile==None):
        print("Invitation file is not selected")
        return render_template("uploadFile.html")
    else:
        isSaved = savePageImages()
        if(isSaved):
            return render_template('editPdf.html',img_urls=img_urls)
        print("PdfFile not saved")
        pdffile=None
        return render_template("uploadFile.html")

@app.route('/csvUpload')
def csvUpload():
    global csvfile
    if(csvfile==None):
        print("Data file not selected")
        return render_template("uploadCsvFile.html")
    else:
        print("Csv file received", csvfile, csvfilepath)
        data = csv_to_json(csvfilepath)
        print(data)
        data = editPdfs(data)
        return render_template("csvContent.html", data=data)


def editPdfs(data):
    if textComps:
        for i, row in enumerate(data):
            pdf = fitz.open(pdffilepath)
            name = row['Name']
            for (id,textComp) in textComps.items():
                print(f"textComp: {textComp}")
                # print(f"pdf: {pdf}")
                page = pdf.load_page(textComp["page"]-1)
                print("Page size of fitz pdf:", page.rect.width, page.rect.height)
                # appearent x, y -> 500, 800
                # actually x, y -> 446, 697

                # (x1, y1) and (x2, y2) to (x1', y1') and (x2', y2')
                # x' = x1' + (x - x1)(x2' - x1')/(x2 - x1)
                # y' = y1' + (y - y1)(y2' - y1')/(y2 - y1)
                
                # y1 => 0 -> -13     y2 => 802 -> 830
                # x1 => 0 -> 0       x2 => 502 -> 520

                x1, y1 = 0, 0
                x1_new, y1_new = 0, -13

                x2, y2 = 502, 802 
                x2_new, y2_new = 520, 830

                x = int(textComp["x"].replace("px","")) 
                y = int(textComp["y"].replace("px","")) 

                # print("First x and y", x, y)
                
                x = x1_new + (x - x1)*(x2_new - x1_new)/(x2 - x1)
                y = y1_new + (y - y1)*(y2_new - y1_new)/(y2 - y1)
                
                # print("After x and y", x, y)
                textHtml = f"<p style='color: {textComp['color']};font-size:{textComp['fontSize'] + 2}px;'>{name}</p>"
                page.insert_htmlbox(fitz.Rect(x,y,x+1000,y+1000),textHtml)
                print(f"text added : {x} {y}")
                os.makedirs(os.path.join(f'{bride_groom_Name}', 'createdPdfs'), exist_ok=True)
                pdfPath  = os.path.join(f'{bride_groom_Name}/createdPdfs',f'{name}.pdf')
                data[i]['filePath'] = pdfPath
                pdf.save(f"{bride_groom_Name}/createdPdfs/{name}.pdf")
    return data

@app.route('/pdfSubmit', methods=['GET', 'POST'])
def pdfSubmit():
    global pdffile, pdffilepath
    if(request.method=="POST"):
        pdffile = request.files["pdfFile"]
        if(pdffile.filename!=""):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            pdffilepath = os.path.join(app.config['UPLOAD_FOLDER'], pdffile.filename)
            pdffile.save(pdffilepath)
        else:
            pdffile=pdfilepath=None
    print(pdffile, pdffilepath)
    return redirect("/")

@app.route('/csvSubmit', methods=['GET', 'POST'])
def csvSubmit():
    print("Submitting CSV File....")
    global csvfile, csvfilepath
    if(request.method=="POST"):
        print(request)
        csvfile = request.files["csvFile"]
        if(csvfile.filename!=""):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            csvfilepath = os.path.join(app.config['UPLOAD_FOLDER'], csvfile.filename)
            csvfile.save(csvfilepath)
        else:
            csvfile=csvfilepath=None
    print(csvfile, csvfilepath)
    return redirect("/csvUpload")


def generatePdf():
    try:
        pdf = fitz.open(pdffilepath)
        for (id,textComp) in textComps.items():
            # print(f"textComp: {textComp}")
            # print(f"pdf: {pdf}")
            page = pdf.load_page(textComp["page"]-1)
            print("Page size of fitz pdf:", page.rect.width, page.rect.height)
            # appearent x, y -> 500, 800
            # actually x, y -> 446, 697

            # (x1, y1) and (x2, y2) to (x1', y1') and (x2', y2')
            # x' = x1' + (x - x1)(x2' - x1')/(x2 - x1)
            # y' = y1' + (y - y1)(y2' - y1')/(y2 - y1)
            
            # y1 => 0 -> -13     y2 => 802 -> 830
            # x1 => 0 -> 0       x2 => 502 -> 520

            x1, y1 = 0, 0
            x1_new, y1_new = 0, -13

            x2, y2 = 502, 802 
            x2_new, y2_new = 520, 830

            x = int(textComp["x"].replace("px","")) 
            y = int(textComp["y"].replace("px","")) 

            # print("First x and y", x, y)
            
            x = x1_new + (x - x1)*(x2_new - x1_new)/(x2 - x1)
            y = y1_new + (y - y1)*(y2_new - y1_new)/(y2 - y1)
            
            # print("After x and y", x, y)
            textHtml = f"<p style='color: {textComp['color']};font-size:{textComp['fontSize'] + 2}px;'>{textComp['textContent']}</p>"
            page.insert_htmlbox(fitz.Rect(x,y,x+1000,y+1000),textHtml)
            print(f"text added : {x} {y}")
        # os.makedirs(os.path.join(f'{bride_groom_Name}', 'editedSamplePdfs'), exist_ok=True)
        # pdf.save(f"{bride_groom_Name}/editedSamplePdfs/{textComp['textContent']}.pdf")
        return pdf
    except Exception as e:
        print("exception in generatePdf : ",e)
        return None


@app.route('/textSubmit', methods=['GET', 'POST'])
def textSubmit():
    global textComps
    if(request.method=="POST"):
        textComps = request.form["textComps"]
        textComps = json.loads(textComps)
        output = generatePdf()
        if(output!=None):
            outputBuffer = io.BytesIO()
            output.save(outputBuffer)
            return outputBuffer.getvalue()
    return redirect("/")

@app.route('/<path:filepath>', methods = ['GET'])
def download(filepath):
    print(filepath)
    return send_file(filepath, as_attachment=True)


@app.route('/pdfViewer/<path:filepath>', methods = ['GET','POST'])
def viewPdf(filepath):
    print(filepath)
    pdf = fitz.open(filepath)
    if(pdf != None):
        outputBuffer = io.BytesIO()
        pdf.save(outputBuffer)
        return outputBuffer.getvalue()
    
    return render_template("/csvContent")


def open_attachment(name_or_number):
    # driver.find_element_by_xpath(EL_ADDRESS["new_chat_el"]).send_keys(name_or_number,"\n")
    # finding new_chat_el and sending details
    el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, EL_ADDRESS["new_chat_el"]))
    )
    el.send_keys(name_or_number,"\n")
    
    # print("attach finding")
    el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, EL_ADDRESS["attachment_el"]))
    )
    el.click()
    # print("attach clicked")

def send_pdf(saved_name, send_to):
    print('Sending pdf', saved_name, 'to', send_to)
    open_attachment(send_to)
    
    # print("doc finding")
    doc_el = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, EL_ADDRESS["doc_el"]))
    )
    doc_el.send_keys(saved_name)
    # print("doc done")
    
    print("send btn finding")
    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, EL_ADDRESS["send_el"]))
    )
    el.click()
    
    print("send clicked")
    
    sleep(1)

@app.route('/sendFile', methods =   ['GET','POST'])
def sendFile():
    file = request.args.get('file', type=str)
    number = request.args.get('to', type=str)
    send_pdf(current + '/' + file, number)

    return render_template('/csvContent.html')

if __name__ == '__main__':

    # Example usage
    driver = get_chrome_driver()


    os.makedirs('local', exist_ok=True)
    bride_groom_Name = 'local/something'
    os.makedirs(bride_groom_Name, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = os.path.join(bride_groom_Name, "uploads")
    app.run(debug=True) 
    driver.close()
    # generatePdf()