import pandas as pd
import utils
import pygame
import numpy as np
import glob

pygame.init()

width, height = 900, 720
lower_layout_px = height-60

images_path = "images_ar_base/"
labels_path = "rotulacao/labels_ar_by_name_full.csv" # formato das labels: filename, [labels]
dest_labels_path = labels_path  #mudar caso não queira sobrescrever

num_classes = 11 #numero de classes de rotulação

class Button:
    def __init__(self, start, size=(100,50), color=(130,130,130), name="", border=1, text_size=20, text_y_offset = 10, font="Segoe UI Symbol") -> None:
        self.rect_value = (start, size)
        self.color = np.array(color)
        self.body = self.body = pygame.draw.rect(screen, self.color, self.rect_value)
        self.border = border
        self.on_focus = 0
        self.name = name[:12] #max 11 chars
        self.text_size = text_size
        self.tyo = text_y_offset
        self.font = font
    
    def draw(self, screen):
        if self.body.collidepoint(pygame.mouse.get_pos()):
            self.body = pygame.draw.rect(screen, self.color+60, self.rect_value)
            self.on_focus = 1
        else:
            self.body = pygame.draw.rect(screen, self.color, self.rect_value)
            self.on_focus = 0

        utils.screen_print(screen, self.name, (0,0,0), self.rect_value[0][0]+5, self.rect_value[0][1]+self.tyo, size=self.text_size, font=self.font)
        pygame.draw.rect(screen, self.color-80, self.rect_value, self.border) #border

class Indicator:
    def __init__(self, pos, size=9, color=(0,200,0)) -> None:
        self.pos = pos
        self.size = size
        self.color = color
        self.state = 0

    def draw(self, screen):
        if self.state:
            pygame.draw.circle(screen, self.color, self.pos, self.size)
        else:
            pygame.draw.circle(screen, (0,0,0), self.pos, self.size)

        pygame.draw.circle(screen, (220,220,220), self.pos, self.size, 2)

class MainViewWindow:
    def __init__(self, start=(10,10), size=(width-110, height-80)) -> None:
        self.limits = (start, size)

    def draw(self, screen, status, data, tgt="file_name"):
        pygame.display.set_caption(f" 🏷 {data[tgt]} 🔘 {status}...")
        self.body = pygame.draw.rect(screen, (0,0,0), self.limits)
        info_x_layout = 360
        if tgt != "file_name":
            image = pygame.image.load(images_path+tgt)
            image = pygame.transform.scale(image, (self.limits[1]))
            screen.blit(image, self.limits[0])
        pygame.draw.rect(screen, (250,250,250), self.limits, 2)
        utils.screen_print(screen, tgt, (250,0,0), self.limits[0][0]+10, self.limits[0][1]+10, size=20, font="Arial")
        if tgt[:] in data.keys():
            utils.screen_print(screen, f"label: {data[tgt]}", (250,250,250), width//2+60, height-50, size=20)
        if status == "start of labels":
            utils.screen_print(screen, "start of data reached!", (250,250,250), info_x_layout, lower_layout_px+12, size=20)
        elif status == "end of labels":
            utils.screen_print(screen, "end of data reached!", (250,250,250), info_x_layout, lower_layout_px+12, size=20)
        else:
            utils.screen_print(screen, f"labeling file nº {list(data.keys()).index(tgt)+1}", (250,250,250), info_x_layout, lower_layout_px+12, size=20)

def handle_click(buttons):
    counter = 0
    for button in buttons:
        if button.on_focus:
            return counter
        else:
            pass
        counter += 1
    return -1

def data_add(data_dic, indic_list, tgt):
    new_labels = np.argwhere([i.state for i in indic_list])
    new_labels = np.reshape(new_labels, -1)
    data_dic[tgt] = list(new_labels)
    return data_dic


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("rotulador geral")
icon = pygame.image.load("rotulador-base/res/label-icon.png")
pygame.display.set_icon(icon)


viewing = MainViewWindow()

all_buttons = [
    Button((65, lower_layout_px), name=" "*2 + "🢀", text_size=35, text_y_offset=1), #b0 next
    Button((170, lower_layout_px), name=" "*3 + "🢂", text_size=35, text_y_offset=1), #b1 previous
    Button((275, lower_layout_px), size=(50,50), name="⭲", text_size=45, text_y_offset=-5), #b2 last
    Button((10, lower_layout_px), size=(50,50), name="⭰", text_size=45, text_y_offset=-5), #b3 first
    Button((width-310, lower_layout_px), name="reset label", font="Arial", text_y_offset=12), #b4 reset
    Button((width-200, lower_layout_px), name=" "*4 + "save", font="Arial", text_y_offset=12)] #b5 save

fixed_buttons = len(all_buttons)
indicators = []
for i in range(30, 60*num_classes, 60):
    indicators.append(Indicator((width-81, i+25)))
    all_buttons.append(Button((width-65, i), size=(50,50), name=f"{i//60}".rjust(3), border=4, font="Verdana"))


named_df = pd.read_csv(labels_path) #carregando os dados
for i, info in named_df.iterrows(): #achar a ultima alteração
    if info[1] == "[]":
        last_append = i
        break
print(f"already labeled {last_append} images")

# gerando o dict dos dados
data = {}
for i, info in named_df.iterrows():
    data[info[0]] = info[1]
for image_name in glob.glob(images_path+"*.jpg"): #mudar de acordo com a extensão das imagens
    if image_name[len(images_path):] not in data.keys():
        data[image_name[len(images_path):]] = []
this_file = list(data.keys())[0]


run = True
action_trigger = 0
act_file = 0
status = "waiting for action"
while run:
    screen.fill((20,20,20))
    clicked_button = -1
    pressed = None
    
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False
            clicked_button = 4

        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_button = handle_click(all_buttons)
            signal = clicked_button - fixed_buttons
            if signal >= 0: #options indicator
                indicators[signal].state = not indicators[signal].state
            action_trigger = 1

        if event.type == pygame.KEYDOWN:
            pressed = event.key
            signal = None
            for i in range(48, 48+10):
                if pressed == i:
                    signal = i-48 #pressed number
            if pressed == pygame.K_MINUS:
                signal = 10 # (-) pressed -> 10

            if signal is not None:
                indicators[signal].state = not indicators[signal].state
            action_trigger = 1


    if action_trigger:
        
        if clicked_button == 0 or pressed == pygame.K_LEFT:
            if act_file > 0:
                act_file -= 1
                status = "labeling"
            else:
                status = "start of labels"
                print("start of data reached")
        elif clicked_button == 1 or pressed == pygame.K_RIGHT:
            if act_file < len(data.keys())-1:
                act_file += 1
                status = "labeling"
            else:
                status = "end of labels"
                print("end of data reached")
        elif clicked_button == 2 or pressed == pygame.K_END:
            act_file = last_append-1
            status = "jumped to last label"
            print("jumped to last label")
        elif clicked_button == 3 or pressed == pygame.K_HOME:
            act_file = 0
            status = "jumped to first label"
            print("jumped to first label")
        elif clicked_button == 4 or pressed == pygame.K_BACKSPACE: #8 == backspace
            for i in indicators:
                i.state = 0 #reset das labels
        elif clicked_button == 5 or pressed == pygame.K_RETURN:
            status = "label saved"
            print(f"label saved")
            data = data_add(data, indicators, this_file)
            
        #print(act_file)
        this_file = list(data.keys())[act_file]
        action_trigger = 0

    viewing.draw(screen, status, data, tgt=this_file,)
    

    for but in all_buttons:
        but.draw(screen)
    for ind in indicators:
        ind.draw(screen)
    
    
    pygame.display.update()

final_df = pd.DataFrame.from_dict(dict(enumerate(zip(data.keys(), data.values()))), orient="index", columns=["filename", "labels"])
final_df.to_csv(dest_labels_path, index=False)
print("alterações sobrescritas no arquivo")

pygame.quit()