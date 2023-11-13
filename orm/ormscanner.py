from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2
import numpy as np
import argparse
import random
import os

def parse_answer_key(answer_key):
    result_dict = {}
    for i, val in enumerate(answer_key):
        if isinstance(val, int):
            result_dict[i] = val - 1
        elif isinstance(val, str) and val.lower() in ('a', 'b', 'c', 'd'):
            result_dict[i] = ord(val.lower()) - ord('a')
    return result_dict

# def parse_arguments():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("-i", "--image", required=True, help="path to the input image")
#     args = vars(ap.parse_args())
#     return args

def load_image(image_path):
    return cv2.imread(image_path)

def save_images(images, titles, folder_path="orm/static/outputs"):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for index, image in enumerate(images):
        title = titles[index]
        if not title.endswith(".png"):
            title = f"{title}.png"
        image_path = os.path.join(folder_path, title)
        # Save the image to the folder
        cv2.imwrite(image_path, image)

def show_images(images, titles, kill_later=False):
    for index, image in enumerate(images):
        title = titles[index]
        cv2.imshow(title, image)
    
    if kill_later:
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def edge_detection(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    return edged

def find_contours(image):
    cnts = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    return cnts

def find_document_contour(cnts):
    doc_cnt = None

    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for c in cnts:
            peri = cv2.arcLength(c, closed=True)
            approx = cv2.approxPolyDP(c, epsilon=peri*0.02, closed=True)

            if len(approx) == 4:
                doc_cnt = approx
                break

    return doc_cnt

def perspective_transform(image, doc_cnt):
    paper = four_point_transform(image, doc_cnt.reshape(4, 2))
    warped = four_point_transform(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), doc_cnt.reshape(4, 2))
    return paper, warped

def threshold_document(warped):
    return cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

def find_question_contours(thresh):
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    return cnts

# Modify the min and max midth depends on the size of the bubble
def filter_question_contours(cnts, min_width, min_height, aspect_ratio_range=(0.9, 1.1)):
    filtered_cnts = [
        c for c in cnts
        if is_question_contour(c, min_width, min_height, aspect_ratio_range)
    ]
    return filtered_cnts

def is_question_contour(contour, min_width, min_height, aspect_ratio_range):
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / float(h)
    return w >= min_width and h >= min_height and aspect_ratio_range[0] <= aspect_ratio <= aspect_ratio_range[1]

def sort_question_contours(question_cnts):
    return contours.sort_contours(question_cnts, method="top-to-bottom")[0]

# Modify the number of bubble options, and the question items
def grade_exam(question_cnts, thresh, paper, answer_key, bubble_options):
    question_cnts = contours.sort_contours(question_cnts, method="top-to-bottom")[0]

    correct = 0
    wrong = 0

    for (q, i) in enumerate(np.arange(0, len(question_cnts), bubble_options)):
        cnts = contours.sort_contours(question_cnts[i: i+bubble_options])[0]
        bubbled = None
        invalid = False  # Flag to track if the answer is invalid

        for (j, c) in enumerate(cnts):
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            total = cv2.countNonZero(mask)

            if bubbled is None or total > bubbled[0]:
                bubbled = (total, j)
            elif total == bubbled[0]:
                invalid = True  # Mark the answer as invalid if two or more bubbles are filled

        k = answer_key[q]

        if invalid:
            # Mark the answer as invalid
            color = (225, 255, 0)
        elif k == bubbled[1]:
            correct += 1
            color = (0, 255, 0)
        else:
            wrong += 1
            color = (0, 0, 255)

        cv2.drawContours(paper, [cnts[k]], -1, color, 3)

    return correct, wrong


def show_questions(paper, question_cnts, bubble_options):
    questions_contour_image = paper.copy()
    cv2.drawContours(questions_contour_image, question_cnts, -1, (0, 0, 255), 3)
    show_images([questions_contour_image], ["All questions contours after filtering questions"])

    questions_contour_image = paper.copy()
    for (q, i) in enumerate(np.arange(0, len(question_cnts), bubble_options)):
        cnts = contours.sort_contours(question_cnts[i: i+bubble_options])[0]
        cv2.drawContours(questions_contour_image, cnts, -1, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 2)

    show_images([questions_contour_image], ["All questions contours with different colors"])

def process_image(image):
    # Perform image processing steps (edge detection, contour finding, etc.)
    edged = edge_detection(image)
    cnts = find_contours(edged)
    doc_cnt = find_document_contour(cnts)
    return edged, cnts, doc_cnt


def detect_bubbles(image):
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    # Apply Hough Circle Transform
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=10, maxRadius=30
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            center = (circle[0], circle[1])
            radius = circle[2]

            # Draw the circle on the image
            cv2.circle(image, center, radius, (0, 255, 0), 2)

    return image


# def orm_scanner():

def orm_scanner(image, answer_key, bubble_options):

    ANSWER_KEY = answer_key
    # get a list of the answer either [1, 2, 1, 4, 3] or [a, b, a, d, c]
    # and return with the right format 

    # ANSWER_KEY = parse_answer_key(answer_key):

    BUBBLE_OPTIONS = bubble_options

    BUBBLE_SIZE = 10 # 20 for bigger bubble size

    QUESTIONS_ITEMS = len(ANSWER_KEY)
    print(f"Total number of questions:", QUESTIONS_ITEMS)
    
    # Load the image
    # args = parse_arguments()
    # image = load_image(args["image"])
    image_name = image
    image = load_image(f"images/{image}")

    if image is None:
        print("Error: Unable to load the input image.")
        return None, None, "Unable to load the input image."

    # Process the image
    edged, cnts, doc_cnt = process_image(image)

    print(f"Total contours found after edge detection:", len(cnts))
    all_contour_image = image.copy()
    cv2.drawContours(all_contour_image, cnts, -1, (0, 0, 255), 3)
    show_images([all_contour_image, edged], ["All contours from edge detected image", "Edged"])


    if doc_cnt is not None:

        # Outline the image
        contour_image = image.copy()
        cv2.drawContours(contour_image, [doc_cnt], -1, (0, 0, 255), 2)
        show_images([contour_image], ["Outline"])

        # Process the image to get the bird's eye view
        paper, warped = perspective_transform(image, doc_cnt)
        show_images([paper, warped], ["Paper", "Warped"])

        if paper is not None and warped is not None:

            # bubbles_detected = detect_bubbles(warped)
            
            thresh = threshold_document(warped)
            show_images([thresh], ["Thresh"])

            cnts = find_question_contours(thresh)
            print(f"Total contours found after threshold:", len(cnts))
            
            # Show the contours from the threshold
            all_contour_image = paper.copy()
            cv2.drawContours(all_contour_image, cnts, -1, (0, 0, 255), 1)
            show_images([all_contour_image], ["All contours from threshold image"])

            # Find the bubble contours
            question_cnts = filter_question_contours(cnts, min_height=BUBBLE_SIZE, min_width=BUBBLE_SIZE)
            print(f"Total questions contours found:", len(question_cnts))

            if question_cnts:

                show_questions(paper, question_cnts, BUBBLE_OPTIONS)

                # Modify this for the answer key
                correct, wrong = grade_exam(question_cnts, thresh, paper, ANSWER_KEY, BUBBLE_OPTIONS)

                score = (correct / float(QUESTIONS_ITEMS)) * 100
                print(f"INFO Score: {score:.2f}%, Correct Answers: {correct} / {QUESTIONS_ITEMS}, Wrong Answers: {wrong}")
                cv2.putText(paper, f"{score:.2f}%, {correct} / {QUESTIONS_ITEMS}", (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 2)
                show_images([image, paper], ["Original", f"Result {image_name}"])
                save_images([paper], [f"Result {image_name}"])
                
                # Create a dictionary to store the score information
                score_info = {
                    'score_percent': score,
                    'total_items': QUESTIONS_ITEMS,
                    'correct_answers': correct,
                    'wrong_answers': wrong,
                    'img': f"Result {image_name}"
                }

                # Return the score information and the result image
                return score_info, paper, None

            else:
                print("Error: No question contours found.")
                return None, None, "No question contours found. Make sure your image is clear."

        else:
            print("Error: Unable to apply perspective transform.")
            return None, None, "Unable to apply perspective transform."

    else:
        return None, None, "No outline found."

if __name__ == "__main__":
    orm_scanner()
