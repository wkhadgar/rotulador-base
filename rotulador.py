import pandas as pd
import utils
import pygame
import numpy as np
import glob

width, height = 1800, 1000 
lower_layout_px = height-60


images_path = "rotulacao/test_images/"
img_format = "jpg"
labels_path = "rotulacao/test_labels.csv" # formato das labels: filename, [labels]
dest_labels_path = labels_path  #mudar caso não queira sobrescrever

class_names = ["test AAAAAAAAA", "teste B", "test C", "test D", "caso y"]
num_classes = len(class_names) #numero de classes de rotulação


pygame.init()

class Button:
    def __init__(self, start, size=(width//18,height//20), color=(130,130,130), name="", border=1, text_size=height//60, text_y_offset=height/150, font="Segoe UI Symbol") -> None:
        self.rect_value = (start, size)
        self.color = np.array(color)
        self.body = pygame.draw.rect(screen, self.color, self.rect_value)
        self.border = border
        self.on_focus = 0
        if len(name) > 11:
            name = name[:12] + "..."
            self.rect_value = (start, (size[0]+len(name)*2, size[1]))
        self.name = name #max 11 chars
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
    def __init__(self, pos, size=height//140, color=(0,200,0)) -> None:
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
    def __init__(self, start=(10,10), size=(width-((width//10)+20), height-((height//20)+40))) -> None:
        self.limits = (start, size)

    def draw(self, screen, status, data, tgt="file_name"):
        if not tgt == "NO FILES FOUND":
            pygame.display.set_caption(f" 🏷 {data[tgt]} f{list(data.keys()).index(tgt)+1} 🔘 {status}...")
            self.body = pygame.draw.rect(screen, (10,10,10), self.limits)
            info_x_layout = 360
            if tgt != "file_name":
                image = pygame.image.load(images_path+tgt)
                im_size = image.get_size()
                expand_axis = np.argmin(im_size)
                if im_size[0] == im_size[1]:
                    expand_axis = 1
                factor = self.limits[1][expand_axis]/im_size[expand_axis]
                image = pygame.transform.rotozoom(image, 0, factor)
                screen.blit(image, ((self.limits[1][0]//2)-(image.get_size()[0]//2), self.limits[0][1])) #centralizar a imagem
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
        else:
            pygame.display.set_caption(tgt)
            self.body = pygame.draw.rect(screen, (0,0,0), self.limits)
            pygame.draw.rect(screen, (250,250,250), self.limits, 2)
            utils.screen_print(screen, tgt, (250,0,0), self.limits[0][0]+10, self.limits[0][1]+10, size=20, font="Arial")
            
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

#comentar caso de problema
icon = pygame.image.load("res/label-icon.png") 
pygame.display.set_icon(icon)
##

viewing = MainViewWindow()

all_buttons = [
    Button((65, lower_layout_px), name=" "*2 + "🢀", text_size=35, text_y_offset=1), #b0 next
    Button((170, lower_layout_px), name=" "*3 + "🢂", text_size=35, text_y_offset=1), #b1 previous
    Button((275, lower_layout_px), size=(50,50), name="⭲", text_size=45, text_y_offset=-5), #b2 last
    Button((10, lower_layout_px), size=(50,50), name="⭰", text_size=45, text_y_offset=-5), #b3 first
    Button((width*0.777, lower_layout_px), name="reset label", font="Arial", text_y_offset=12, text_size=20), #b4 reset
    Button((width*0.839, lower_layout_px), name=" "*4 + "save", font="Arial", text_y_offset=12, text_size=20)] #b5 save
fixed_buttons = len(all_buttons)

indicators = []
for i in range(30, 60*num_classes, 60):
    indicators.append(Indicator((width-160, i+25)))
    all_buttons.append(Button((width-145, i), name=f"{class_names[i//60]}".rjust(3), border=4, font="Arial", text_y_offset=15))


named_df = pd.read_csv(labels_path) #carregando os dados
for i, info in named_df.iterrows(): #achar a ultima alteração
    if info[1] == "[]":
        last_append = i
        break
    
for image_name in glob.glob(images_path+f"*.{img_format}"):
        image_name = image_name[len(images_path):]
        if image_name not in list(named_df.iterrows()):
            named_df = named_df.append({"filename": image_name, "labels": "[]"}, ignore_index=True)
            named_df.to_csv(labels_path, index=False)
            
            
try:        
    print(f"already labeled {last_append} images")
except NameError:
    last_append = 1
    
# gerando o dict dos dados
data = {}
for i, info in named_df.iterrows():
    data[info[0]] = info[1]
for image_name in glob.glob(images_path+f"*.{img_format}"): #mudar de acordo com a extensão das imagens
    if image_name[len(images_path):] not in data.keys():
        data[image_name[len(images_path):]] = []
try:
    this_file = list(data.keys())[0]
except IndexError:
    print("NO Images found at images path")
    this_file = "NO FILES FOUND"


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

for k in data:
    num_labels = data[k] 
    named_label = []
    if num_labels != "[]":
        for n in num_labels:
            named_label.append(class_names[n])
    data[k] = named_label
final_df = pd.DataFrame.from_dict(dict(enumerate(zip(data.keys(), data.values()))), orient="index", columns=["filename", "labels"])
final_df.to_csv(dest_labels_path, index=False)
print("alterações sobrescritas no arquivo")

pygame.quit()