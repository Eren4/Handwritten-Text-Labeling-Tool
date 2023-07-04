import cv2
import numpy as np
import time
import tkinter as tk
import os
import sys
from PIL import ImageTk, Image

def destroy_word_root():
    try:
        word_root.destroy()
    except:
        print("Please do not close the window")

def destroy_line_root():
    try:
        line_root.destroy()
    except:
        print("Please do not close the window")

def check_digits(counter):
    if(counter < 10):
        modified_counter = "0" + str(counter)
    else:
        modified_counter = str(counter)

    return modified_counter

def exit_system():
    print("Labeling successfully completed. Please check turkish-words.txt and turkish-lines.txt")
    time.sleep(7)
    sys.exit()

form_list = os.listdir("words/")

root = tk.Tk()
root.title("Main window")
root.withdraw()

while(True):
    with open("turkish-words.txt", "r", encoding="UTF-8") as file:
        lines = file.readlines()

    labeled_form_list = []
    for line in lines:
        if(line.startswith('#')):
            continue
        labeled_form_list.append(line.split('/')[1])

    labeled_form_list = list(dict.fromkeys(labeled_form_list))

    remaining_forms = 0
    for form in form_list:
        if(form in labeled_form_list):
            continue
        else:
            remaining_forms += 1

    print("Remaining forms: " + str(remaining_forms))

    for form in form_list:
        if(form in labeled_form_list):
            continue
        else:
            current_form = form
            break

    print("Labeling form: " + current_form)

    input_filename = current_form

    words_folder = "words/" + input_filename
    word_lines_folder = "word-lines/" + input_filename

    words_list = os.listdir(words_folder)
    word_lines_list = os.listdir(word_lines_folder)

    with open("turkish-words.txt", 'a', encoding="UTF-8") as file:
        for word in words_list:
            line_number = int(word.split('-')[3])
            line_index = line_number - 1

            line_path = word_lines_folder + '/' + word_lines_list[line_index]
            line_picture = cv2.imread(line_path)
            line_picture = cv2.cvtColor(line_picture, cv2.COLOR_BGR2RGB)
            line_picture = cv2.resize(line_picture, (1000, 100))

            line_root = tk.Toplevel(root)
            line_root.title(word_lines_list[line_index])
            line_root.geometry("1000x100+100+50")

            frame = tk.Frame(line_root, width=1000, height=100)
            frame.grid(row=0, column=0, sticky="NW")

            tk_line_label = ImageTk.PhotoImage(Image.fromarray(line_picture))
            tk_my_line_label = tk.Label(line_root, image=tk_line_label)
            tk_my_line_label.place(relx=0.5, rely=0.5, anchor="center")

            word_path = words_folder + '/' + word
            word_picture = cv2.imread(word_path)
            word_picture = cv2.cvtColor(word_picture, cv2.COLOR_BGR2RGB)

            word_root = tk.Toplevel(root)
            word_root.title(word)
            word_root.geometry("600x150+100+250")

            frame = tk.Frame(word_root, width=600, height=150)
            frame.grid(row=0, column=0, sticky="NW")

            tk_word_label = ImageTk.PhotoImage(Image.fromarray(word_picture))
            tk_my_label = tk.Label(word_root, image=tk_word_label)
            tk_my_label.place(relx=0.5, rely=0.5, anchor="center")

            word_status_input = input("Is the word correctly segmented? [y/n]: ")
            while(word_status_input != 'y' and word_status_input != 'n' and word_status_input != ''):
                print("Please provide a valid answer")
                word_status_input = input("Is the word correctly segmented? [y/n]: ")

            if(word_status_input == 'y' or word_status_input == ''):
                word_label = input("Enter the label of " + word + ": ")
                word_label = word_label.replace(" ", "")
                word_status = "ok"

                row = [word_path, word_status, word_label]
                row_string = " ".join(row)
                file.write(row_string + "\n")
            else:
                word_status = "err"
                row = [word_path, word_status]
                row_string = " ".join(row)
                file.write(row_string + "\n")

                destroy_word_root()
                destroy_line_root()
                continue
            
            destroy_word_root()
            destroy_line_root()

    # automatically labeling the lines from the words txt file
    words = open("turkish-words.txt", "r", encoding="UTF-8").readlines()
    line_and_label = []
    filename_list = []

    for line in words:
        if(line.startswith("#")):
            continue

        if(line.split(' ')[1].rstrip("\n") == "err"):
            continue

        line_split = line.split(" ")
        
        if(line_split[0].startswith(("words/" + input_filename))):
            file_location = line_split[0]
            label = line_split[-1].rstrip('\n')
            filename = file_location.split("/")[2]
            filename_list.append(filename)
            line_number = filename.split("-")[3]
            line_and_label.append([line_number, label])

    # create a list to determine how many lines are there
    number_of_lines = []
    for i in range(len(line_and_label)):
        number_of_lines.append(line_and_label[i][0])

    number_of_lines = list(dict.fromkeys(number_of_lines)) # remove duplicates

    # generating the line by adding the words together
    full_sentence = ''
    prev_line = 1
    sentence_list = []
    element_counter = 0
    for element in line_and_label:
        line_number = int(element[0])
        label = element[-1]

        if(line_number != prev_line):
            full_sentence = full_sentence.rstrip(" ")
            sentence_list.append(full_sentence)
            full_sentence = ''
        
        full_sentence += label + " "
        prev_line = line_number
        element_counter += 1

        if(element_counter == len(line_and_label)):
            full_sentence = full_sentence.rstrip(" ")
            sentence_list.append(full_sentence)
            break

    # clean the empty elements
    for element in sentence_list:
        if element == "":
            sentence_list.remove(element)

    # create a list of file locations
    file_location_list = []
    for element in filename_list:
        line_name = element[0:14] + ".png"
        line_location = "lines/" + input_filename + "/" + line_name
        file_location_list.append(line_location)

    file_location_list = list(dict.fromkeys(file_location_list)) # remove duplicates

    # concatenate line path, status and label together for appending to the lines txt file
    concatenated = []
    for i in range(len(file_location_list)):
        if(len(sentence_list) == 0):
            exit_system()

        sentence = sentence_list[i].replace(" ", "|")
        line_number = file_location_list[i][30:32]

        if(line_number.startswith("0")):
            line_number = line_number.rstrip("0")
        
        index = int(line_number) - 1
        concatenated.append([file_location_list[i], sentence])

    # append the lines to the lines txt file
    with open("turkish-lines.txt", "a", encoding="UTF-8") as file:
        for line in concatenated:
            line = " ".join(line)
            file.write(line + "\n")

    print("Labeling successfully completed. Please check turkish-words.txt and turkish-lines.txt")
    continue_answer = input("Do you wish to continue labeling? [y/n]: ")

    while(continue_answer != 'n' and continue_answer != 'y'):
        print("Please provide a valid answer [y or n]")
        continue_answer = input("Do you wish to continue labeling? [y/n]: ")

    if(continue_answer == 'n'):
        break
