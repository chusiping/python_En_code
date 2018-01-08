from PIL import Image
from pytesser import *
text = image_file_to_string('fonts_test.png', graceful_errors=True)
print(text)