from flask import Flask, render_template, Response,redirect,request, url_for
import fitz
import os
import base64
import json
import pandas as pd
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

pdffile = None
pdffilepath = None

csvfile = None
csvfilepath = None

img_urls = None
textComps = None

bride_groom_Name = None

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
    pdf = fitz.open(pdffilepath)
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
        textHtml = f"<p style='color: {textComp['color']};font-size:{textComp['fontSize'] + 2}px;'>{textComp['textContent']}</p>"
        page.insert_htmlbox(fitz.Rect(x,y,x+1000,y+1000),textHtml)
        print(f"text added : {x} {y}")
        os.makedirs(os.path.join(f'{bride_groom_Name}', 'editedSamplePdfs'), exist_ok=True)
        pdf.save(f"{bride_groom_Name}/editedSamplePdfs/{textComp['textContent']}.pdf")

@app.route('/textSubmit', methods=['GET', 'POST'])
def textSubmit():
    global textComps
    if(request.method=="POST"):
        textComps = request.form["textComps"]
        textComps = json.loads(textComps)
        generatePdf()
    return redirect("/")

if __name__ == '__main__':
    bride_groom_Name = 'ઈશિતા_તિલક'
    os.makedirs(bride_groom_Name, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = os.path.join(bride_groom_Name, "uploads")
    app.run(debug=True) 
    # generatePdf()