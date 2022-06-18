import json
import pygame
import utils
import glob
import pandas as pd
import numpy as np

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (105, 105, 105)
DARK_GRAY = (65, 65, 65)
BG_COLOR = (10, 10, 12)

VERSION = "Annotator v2.3"
pygame.display.set_caption(VERSION)
icon = pygame.image.load("../res/label-icon.png")
pygame.display.set_icon(icon)


SCREEN_WIDTH, SCREEN_HEIGHT = 1800, 1000
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.init()

with open("../res/label-classes.json") as all_classes:
    classes_dict = json.load(all_classes)

max_group_len = 0
for group in classes_dict.keys():
    group_len = len(classes_dict[group])
    if group_len > max_group_len:
        max_group_len = group_len

class MainWindow:
    def __init__(self, size=(1300, 910)):
        self.size = size
        self.limits = ((10, 10), size)
        self.body = None

    def draw(self, screen, img_folder="", img_filename=" NO FILES FOUND"):
        pygame.draw.rect(screen, BLACK, self.limits)
        try:
            image = pygame.image.load(img_folder+"/"+img_filename)
            image = resize_fit(image, self.limits)
            screen.blit(image, (((self.limits[1][0]/2)+10)-(image.get_size()[0]/2), ((self.limits[1][1]/2)+10)-(image.get_size()[1]/2)))          # centralizar a imagem

        except FileNotFoundError:
            pass

        utils.screen_print(screen, img_filename, (20, 10), color=RED)
        self.body = pygame.draw.rect(screen, WHITE, self.limits, 2)


class ButtonInformation:
    def __init__(self, pos: tuple, size: tuple, color=YELLOW, shape="rect", issue_name=""):
        self.pos = pos
        self.size = size
        self.shape = shape
        self.color = color
        self.state = False
        self.body = pygame.Rect(0, 0, 0, 0)
        self.issue_name = issue_name

    def draw(self, screen):
        if self.shape == "rect":
            if self.state:
                pygame.draw.rect(screen, self.color, (self.pos, self.size), width=0, border_radius=2)
            else:
                pygame.draw.rect(
                    screen, BLACK, (self.pos, self.size), width=0, border_radius=2)
            self.body = pygame.draw.rect(screen, WHITE, (self.pos, self.size), 2, 2)
        else:
            if self.state:
                pygame.draw.circle(screen, self.color, self.pos, self.size[0]/2)
            else:
                pygame.draw.circle(screen, BLACK, self.pos, self.size[0]/2)
            self.body = pygame.draw.circle(screen, WHITE, self.pos, self.size[0]/2, 1)


class Button():
    def __init__(self, pos: tuple, size=(100, 50), name='', font_size=20, info: ButtonInformation = None):
        self.color = DARK_GRAY
        self.x, self.y = pos
        self.width, self.height = size
        self.name = name
        self.font_size = font_size
        self.info = info

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0, border_radius=4)

        self.color = GRAY if self.isOver(pygame.mouse.get_pos()) else DARK_GRAY
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.name != '':
            font = pygame.font.SysFont('Segoe UI Symbol', self.font_size)
            text = font.render(self.name, 1, (230, 230, 230))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos: tuple):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False

def resize_fit(img:pygame.Surface, win_rect:tuple, redo=False):
    im_size = img.get_size()
    im_biggest_axis = np.argmax(im_size)
    im_biggest_axis = not im_biggest_axis if redo else im_biggest_axis
    resize_factor = (win_rect[1][im_biggest_axis])/im_size[im_biggest_axis]
    img = pygame.transform.rotozoom(img, 0, resize_factor)
    im_size = img.get_size()
    if (im_size[0] > win_rect[1][0]) or (im_size[1] > win_rect[1][1]):
        return resize_fit(img, win_rect, redo=True)    
    else:
        return img


def deep_save(df:pd.DataFrame, labels_csv_path, labels_json_path):
    try:
        df.to_csv(labels_csv_path, index=False)
        df.to_json(labels_json_path, orient='records')
        df.to_csv(labels_json_path[:-4]+"csv", index=False)
    except AttributeError:
        print("NO CHANGES MADE - ERROR OCURRED")

def recover_status(df: pd.DataFrame, act_file: int, buttons: list):
    if type(df) != type(None):
        info = dict(df.iloc[act_file][2:])
        for label_issue in info.keys():
            for button in buttons:
                if button.info.issue_name == label_issue and button.name in info[label_issue]:
                    button.info.state = True
    else:
        return "?"
    return "OK"


all_buttons = [
    Button((65, SCREEN_HEIGHT-60), size=(SCREEN_WIDTH//18,
           SCREEN_HEIGHT//20), name="🢀", font_size=40),  # b0 previous
    Button((170, SCREEN_HEIGHT-60), size=(SCREEN_WIDTH//18,
           SCREEN_HEIGHT//20), name="🢂", font_size=40),  # b1 next
    Button((275, SCREEN_HEIGHT-60), size=(50, 50),
           name="⭲", font_size=50),  # b2 last
    Button((10, SCREEN_HEIGHT-60), size=(50, 50),
           name="⭰", font_size=50),  # b3 first
    Button((SCREEN_WIDTH*0.585, SCREEN_HEIGHT-60),
           name="clean labels"),  # b4 reset
    Button((SCREEN_WIDTH*0.666, SCREEN_HEIGHT-60), name="save"),  # b5 save
    Button((SCREEN_WIDTH-40, SCREEN_HEIGHT-35), size=(35, 30),
           name="📂", font_size=25),  # b6 Settings
    Button((SCREEN_WIDTH*0.520, SCREEN_HEIGHT-60), name="NO CAT")]  # b7 NONE label
fixed_buttons = len(all_buttons)

SCREEN.fill(BG_COLOR)

offset_h = (max_group_len+1)*45
collumn_h = -offset_h
for p_num, problem_name in enumerate(classes_dict.keys()):
    p_num %= 3
    collumn_h += offset_h if not p_num else 0
    utils.screen_print(SCREEN, f"{problem_name}", ((
        150*p_num + SCREEN_WIDTH/1.3), collumn_h+20), color=WHITE, size=22)
    for b_num, _class in enumerate(classes_dict[problem_name]):
        #print(b_num, _class)
        all_buttons.append(Button(pos=((150*p_num + SCREEN_WIDTH/1.3), (45*b_num + collumn_h + 60)), size=(80, 35), name=f"{_class}", font_size=18,
                                  info=ButtonInformation(pos=((150*p_num + SCREEN_WIDTH/1.3 - 15), (45*b_num + collumn_h + 78)), size=(10, 10), shape="o", issue_name=f"{problem_name}")))
auto_save_handler = ButtonInformation((340, 958), (14, 14), shape="rect")


view = MainWindow()
run = True
auto_deep_save = 5
setup = True
while run:

    if setup:
        main_folder_path = utils.select_path()
        labels_csv, recover_json = utils.handle_csv(main_folder_path)
        images_path = main_folder_path + "/images"
        all_images = [img_name[len(images_path)+1:]
                      for img_name in glob.glob(images_path + "/*.jpg")]
        try:
            labeling_dataframe = pd.DataFrame(data=pd.read_csv(labels_csv))
            labeling_dataframe["filename"] = all_images
            labeling_dataframe["is_rotulated"].fillna(False, inplace=True)
            labeling_dataframe.fillna("[]", inplace=True)
            last_rotulation = labeling_dataframe.is_rotulated.ne(
                True).idxmax() - 1
        except:
            labeling_dataframe = None
            last_rotulation = 0
        act_file = 0
        recover_status(labeling_dataframe, act_file,
                       all_buttons[fixed_buttons:])
        max_image = len(all_images)-1
        setup = False

    selected_classes = [((but.name, but.info.issue_name) if but.info.state else ("","")) for but in all_buttons[fixed_buttons:]]
    # print(selected_classes)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            window_title = "exiting..."
            pygame.display.set_caption(window_title)
        elif event.type == pygame.KEYDOWN:
            window_title = VERSION+""
            if event.key == pygame.K_ESCAPE:
                run = False
                window_title = "exiting..."
            elif event.key == pygame.K_s:  # auto-save when change images
                auto_save_handler.state = not auto_save_handler.state
            elif event.key == pygame.K_RIGHT:
                if auto_save_handler.state:
                    utils.save_changes(labeling_dataframe, classes_dict, selected_classes, act_file)
                    last_rotulation = act_file if act_file > last_rotulation else last_rotulation
                recover_status(labeling_dataframe, act_file, all_buttons[fixed_buttons:])
                window_title = VERSION+": last image reached!" if act_file == max_image else VERSION + f": labeling image nº {act_file+1}..."
                act_file += 1 if (act_file < max_image) else 0
                if act_file % auto_deep_save == 0: # deep save changes automaticaly
                    deep_save(labeling_dataframe, labels_csv, recover_json)
            elif event.key == pygame.K_LEFT:
                act_file -= 1 if (act_file > 0) else 0
                window_title = VERSION+": first image reached!" if act_file == 0 else VERSION + f": labeling image nº {act_file+1}..."
                recover_status(labeling_dataframe, act_file, all_buttons[fixed_buttons:])
            elif event.key == pygame.K_END:
                act_file = last_rotulation
                window_title = VERSION+": jumped to last rotuladed image"
            elif event.key == pygame.K_HOME:
                act_file = 0
                window_title = VERSION+": jumped to start of images"
            elif event.key == pygame.K_BACKSPACE:
                for but in all_buttons[fixed_buttons:]:
                    but.info.state = False
                window_title = VERSION+": cleaned label selection"
            elif event.key == pygame.K_RETURN:
                utils.save_changes(labeling_dataframe, classes_dict, selected_classes, act_file)
                last_rotulation = act_file if act_file > last_rotulation else last_rotulation
                window_title = VERSION+": saved changes..."
                print(labeling_dataframe)
            elif event.key == pygame.K_LCTRL:
                utils.save_changes(labeling_dataframe, classes_dict, "NC", act_file)
                act_file += 1 if (act_file < max_image) else 0
                last_rotulation = act_file if act_file > last_rotulation else last_rotulation
                for but in all_buttons[fixed_buttons:]:
                    but.info.state = False
                window_title = VERSION+": no cat there huh? skipped to next frame..."
            pygame.display.set_caption(window_title)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = pygame.mouse.get_pos()
            window_title = VERSION+""
            for but_num, but in enumerate(all_buttons):
                if but.isOver(click_pos):
                    if but_num >= fixed_buttons:
                        but.info.state = not but.info.state
                        #print(f"selected {but.name} of {but.info.issue_name}")
                    elif but_num == 0:
                        act_file -= 1 if (act_file > 0) else 0
                        window_title = VERSION+": first image reached!" if act_file == 0 else VERSION + f": labeling image nº {act_file+1}..."
                    elif but_num == 1:
                        if auto_save_handler.state:
                            utils.save_changes(labeling_dataframe, classes_dict, selected_classes, act_file)
                            last_rotulation = act_file if act_file > last_rotulation else last_rotulation
                        recover_status(labeling_dataframe, act_file, all_buttons[fixed_buttons:])
                        window_title = VERSION+": last image reached!" if act_file == max_image else VERSION + f": labeling image nº {act_file+1}..."
                        act_file += 1 if (act_file < max_image) else 0
                        if act_file % auto_deep_save == 0 or act_file == max_image: # deep save changes automaticaly
                            deep_save(labeling_dataframe, labels_csv, recover_json)
                    elif but_num == 2:
                        act_file = last_rotulation
                        window_title = VERSION+": jumped to last rotuladed image"
                    elif but_num == 3:
                        act_file = 0
                        window_title = VERSION+": jumped to start of images"
                    elif but_num == 4:
                        for but in all_buttons[fixed_buttons:]:
                            but.info.state = False
                        window_title = VERSION+": cleaned label selection"
                    elif but_num == 5:
                        utils.save_changes(labeling_dataframe, classes_dict, selected_classes, act_file)
                        last_rotulation = act_file if act_file > last_rotulation else last_rotulation
                        window_title = VERSION+": saved changes..."
                    elif but_num == 6:
                        setup = True
                    elif but_num == 7:
                        utils.save_changes(labeling_dataframe, classes_dict, "NC", act_file)
                        act_file += 1 if (act_file < max_image) else 0
                        last_rotulation = act_file if act_file > last_rotulation else last_rotulation
                        for but in all_buttons[fixed_buttons:]:
                            but.info.state = False
                        window_title = VERSION+": no cat there huh? skipped to next frame..."

            if auto_save_handler.body.collidepoint(click_pos):
                auto_save_handler.state = not auto_save_handler.state

            pygame.display.set_caption(window_title)

    if act_file < len(all_images):
        view.draw(SCREEN, images_path, all_images[act_file])
    else:
        view.draw(SCREEN, images_path)

    auto_save_handler.draw(SCREEN)
    for but in all_buttons:
        but.draw(SCREEN, GRAY)
        try:
            but.info.draw(SCREEN)
        except AttributeError:
            pass
    utils.screen_print(SCREEN, f"auto-save is {'enabled ' if auto_save_handler.state else 'disabled'}", (358, 953), WHITE, size=16, bg=(BG_COLOR))

    label_info = "$ saving as:"
    iss = ""
    posy = 0
    for sclass, issue in selected_classes:
        if sclass != "":
            if issue != iss:
                label_info += f"$# {issue}: "
                iss = issue
            label_info += f"{sclass}; "
    pygame.draw.rect(SCREEN, BLACK, (SCREEN_WIDTH-480, 830, 470, 130), border_radius=4) #info box 
    pygame.draw.rect(SCREEN, BG_COLOR, (SCREEN_WIDTH-480, SCREEN_HEIGHT-30, 410, 200), border_radius=4) # folder name area clearing
    for lb in label_info.split("$"):
        posy += 15
        utils.screen_print(SCREEN, lb, (SCREEN_WIDTH-480, 800+posy), WHITE, 13)

    utils.screen_print(SCREEN, main_folder_path.split("/")[-1], (SCREEN_WIDTH-50-len(main_folder_path.split("/")[-1])*10, SCREEN_HEIGHT-30), (100,100,100), 17, bg=BG_COLOR)
    pygame.display.update()


deep_save(labeling_dataframe, labels_csv, recover_json)
pygame.quit()


# by wkhadgar
# prms@ic.ufal.br