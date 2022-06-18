import json
import os
import pygame
import pandas as pd

def screen_print(screen, text, pos, color=(0,0,0), size=25, font="verdana", bg=None):

    text_font = pygame.font.SysFont(font, size)
    text_body = text_font.render(text, True, color, bg)
    screen.blit(text_body, (pos[0], pos[1]))


def split_video_by_frames(video_path, output_path, leading_zeros="many"):
    import cv2

    capture = cv2.VideoCapture(video_path)

    frameNr = 0
    output_path = output_path+r"\images"
    try:
        os.mkdir(output_path)
    except FileExistsError:
        print("file folder pre-existent!")

    while True:

        success, frame = capture.read()
        
        if success:
            if leading_zeros == "many":
                cv2.imwrite(output_path + f"/frame_{frameNr:06d}.jpg", frame)
            else:
                cv2.imwrite(output_path + f"/frame_{frameNr:04d}.jpg", frame)

        else:
            break

        frameNr = frameNr + 1
        print(f"frame {frameNr} created.")

    capture.release()


def save_changes(DataFrame_:pd.DataFrame, dict_classes:dict, current_selection:list, act_file:int):
    
    """
    save the current changes on the .csv files.

    Args:
        DataFrame_ (pd.DataFrame): DataFrame containing the actual info
        dict_classes (dict): dict of all classes
        current_selection (list): list of all selected classes: list of tuples (class, issue)

    """
    
    old_df = DataFrame_
    
    if old_df is not None:
        new_label = {}
        new_label["is_rotulated"] = True
        for main_issue in dict_classes.keys(): 
            new_label[main_issue] = []
            if current_selection != "NC": 
                for selected_class, issue in current_selection: 
                    if (selected_class in dict_classes[main_issue]) and issue==main_issue:
                        new_label[main_issue].append(selected_class)
            else: 
                new_label[main_issue] = "NC"

        old_df.loc[act_file, new_label.keys()] = new_label.values()
        return new_label
    else:
        print("(__class__ None) df")
        return old_df
    
def handle_csv(folder_path:str):
    """select the .csv files if already exists, otherwise create them.

    Args:
        folder_path (str): path to the main actual rotulation folder

    Returns:
        (str, str): labels.csv path and recover labels.csv path, if found.
    """
    with open("../res/label-classes.json") as all_classes:
        classes_dict = json.load(all_classes)

    if os.path.exists(folder_path+"/images"):
        import csv
        
        header = ["filename", "is_rotulated"]
        for key in classes_dict.keys():
            header.append(key.strip())
        
        backup_path = os.path.join(folder_path, "bkp")
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
            r_l_path = backup_path+"/recover_labels.json"
        else:
            r_l_path = backup_path+"/recover_labels.json"
                
        labels_path = folder_path+"/labels.csv"
        if not os.path.exists(labels_path):
            with open(labels_path, "w") as label:
                csv_writer = csv.writer(label)
                csv_writer.writerow(header)
        
        return labels_path, r_l_path 
    else:
        return None, None
 

def select_path():
    from tkinter import Tk, filedialog

    root = Tk() # pointing root to Tk() to use it as Tk() in program.
    root.withdraw() # Hides small tkinter window.
    root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
    open_folder = filedialog.askdirectory(mustexist=True, title="Select a rotulation folder to work on:") # Returns opened path as str
    
    return open_folder

