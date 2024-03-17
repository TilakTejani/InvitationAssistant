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
        return render_template("uploadFile.html")
    else:
        isSaved = savePageImages()
        if(isSaved):
            return render_template('editPdf.html',img_urls=img_urls)
        print(isSaved)
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
        page = pdf.load_page(textComp["page"]-1)
        textHtml = f"<p style='color: {textComp['color']};font-size:{textComp['fontSize']}px;'>{textComp['textContent']}</p>"
        x = int(textComp["x"].replace("px","")) * 1.3585
        y = int(textComp["y"].replace("px","")) * 1.888
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