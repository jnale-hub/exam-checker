# Exam Checker

An automated optical mark recognition (OMR) system built with Django and OpenCV that scans and grades multiple-choice exam answer sheets.

## Overview

This web application uses computer vision techniques to detect, scan, and automatically grade bubble-sheet exams. It processes uploaded images of answer sheets, identifies marked bubbles, compares them against an answer key, and provides instant scoring results.

## Features

- **Automatic Answer Sheet Detection**: Uses edge detection and contour finding to locate the exam sheet in images
- **Perspective Correction**: Applies four-point transformation for accurate bird's-eye view of the answer sheet
- **Bubble Detection**: Identifies and validates marked answer bubbles using OpenCV
- **Instant Grading**: Compares student answers against answer keys and calculates scores
- **Visual Feedback**: Generates result images with color-coded answers (green for correct, red for incorrect, cyan for invalid)
- **Web Interface**: User-friendly Django web app for uploading images and viewing results

## Technology Stack

- **Backend**: Django 4.2.5
- **Computer Vision**: OpenCV 4.8.1
- **Image Processing**: NumPy, imutils
- **Database**: SQLite3

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the development server:
   ```bash
   python manage.py runserver
   ```
2. Navigate to `http://localhost:8000` in your web browser
3. Upload an answer sheet image, enter your name and exam code
4. View your automatically graded results

## Configuration

- **Answer Keys**: Update the `answer_key` dictionary in `orm/views.py` to match your exam
- **Bubble Options**: Modify `bubble_options` variable for different numbers of choices (e.g., 4 for A-D, 5 for A-E)
- **Bubble Size**: Adjust `BUBBLE_SIZE` in `orm/ormscanner.py` based on your answer sheet format

## Important Notes

- Image quality significantly affects accuracy - use clear, well-lit photos
- Ensure the entire answer sheet is visible and not cropped
- The scanner detects multiple marks on a single question and flags them as invalid
- Main image processing logic is in `orm/ormscanner.py`

## Project Structure

- `orm/` - Main application module with views, forms, and scanner logic
- `orm/ormscanner.py` - Core computer vision and grading algorithms
- `orm/views.py` - Django views and request handling
- `images/` - Uploaded answer sheet images
- `orm/static/outputs/` - Generated result images
