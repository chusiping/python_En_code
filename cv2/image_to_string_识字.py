from PIL import Image
import pytesseract
im = Image.open("baodan.jpg")
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
text = pytesseract.image_to_string(im, lang = 'chi_sim+eng')
print(text)

# f = open("result.txt", 'w')
# f.write(text)
# f.close()
# # print(text)

