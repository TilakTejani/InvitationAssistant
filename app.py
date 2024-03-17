from flask import Flask, render_template, Response,redirect,request, url_for
import fitz
import os
import base64
import io
import pdf2image
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

file = None
filepath = None
# filepath = os.path.join(app.config['UPLOAD_FOLDER'],"t1.pdf")
img_urls = None
textComps = None
# textComps = {'text1': {'id': 'text1', 'page': 1, 'fontFamily': 'Gujarati', 'fontSize': 15, 'textContent': 'જય શ્રી રામ', 'color': '#FAFAFA', 'x': '232px', 'y': '212px'}, 'text2': {'id': 'text2', 'page': 2, 'fontFamily': 'Gujarati', 'fontSize': 25, 'textContent': 'જય શ્રી રા', 'color': '#FAAAFA', 'x': '163px', 'y': '162px'}}

def savePageImages():
    try:
        global img_urls
        pdf = fitz.open(filepath)
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
    


@app.route('/')
def index():
    global file
    if(file==None):
        print("no file selected")
        return render_template("uploadFile.html")
    else:
        isSaved = savePageImages()
        if(isSaved):
            return render_template('editPdf.html',img_urls=img_urls)
        print("File not saved")
        file=None
        return render_template("uploadFile.html")


@app.route('/pdfSubmit', methods=['GET', 'POST'])
def pdfSubmit():
    global file,filepath
    if(request.method=="POST"):
        file = request.files["pdfFile"]
        if(file.filename!=""):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
        else:
            file=filepath=None
    return redirect("/")

def generatePdf():
    pdf = fitz.open(filepath)
    for (id,textComp) in textComps.items():
        print(f"textComp: {textComp}")
        # print(f"pdf: {pdf}")
        page = pdf.load_page(textComp["page"]-1)
        print("Page size of fitz pdf:", page.rect.width, page.rect.height)
        textHtml = f"<p style='color: {textComp['color']};font-size:{textComp['fontSize'] + 2}px;'>{textComp['textContent']}</p>"
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

        page.insert_htmlbox(fitz.Rect(x,y,x+1000,y+1000),textHtml)
        print(f"text added : {x} {y}")
    
    pdf.save("output.pdf")


@app.route('/textSubmit', methods=['GET', 'POST'])
def textSubmit():
    global textComps
    if(request.method=="POST"):
        textComps = request.form["textComps"]
        textComps = json.loads(textComps)
        generatePdf()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True) 
    # generatePdf()