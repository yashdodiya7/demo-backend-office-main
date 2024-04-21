import numpy as np
import pytesseract
import cv2
import re
import math
import os


def verify_aadhar(image_path):
    # Specify the path to the Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform thresholding or other preprocessing if necessary

    # Use Tesseract for OCR
    config = r'--oem 3 --psm 6'  # Tesseract configuration for single block of text
    text = pytesseract.image_to_string(gray, config=config)

    return text


def validate_aadhar_text(text, name):
    # Split the text into lines
    lines = text.split('\n')

    name_list = name.split(" ")

    # Initialize variables to track validation results
    name_present = False
    aadhar_number_valid = False

    # Iterate through each line of text
    for line in lines:
        # Check if the name is present in the line
        if all(word in line for word in name_list):
            name_present = True

        # Extract digits from the line
        digits = ''.join(filter(str.isdigit, line))

        # Check if extracted digits have a valid length
        if len(digits) == 12:
            aadhar_number_valid = True

    # Return validation results
    return name_present, aadhar_number_valid
