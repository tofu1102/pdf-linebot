import os
import img2pdf
from PIL import Image

def png2pdf(pdfFileName,pngFilePath):
    with open("static/" + pdfFileName + ".pdf","wb") as f:
        f.write(img2pdf.convert([Image.open(pngFilePath).filename]))

    return pdfFileName + ".pdf"
