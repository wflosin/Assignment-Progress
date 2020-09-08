#William Losin
#June 6, 2019

import pygame as pg
import sys
import os

from helperClasses import Assignment, DisplayAssignment, Popup
from colours import BLACK, WHITE, RED, YELLOW
from helperFunctions import getDuedateBackground, loadSort, save_object, \
    loadall, delete_assignment, date2string, delete_specific_assignment

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100)

#RECT
# (left,top,width, height)


class Main:
    def __init__(self):
        #width and height of surface
        (self.w, self.h) = (1250,850)

        #surface initialization
        self.surface = pg.display.set_mode((self.w, self.h))  #, pg.RESIZABLE)
        pg.display.set_caption('Assignment Progress')
        self.surface.fill(BLACK)

        #font
        pg.font.init()
        self.message_font = pg.font.SysFont('Calibri', 40)
        self.general_font = pg.font.SysFont('Calibri', 14)

        #set the clock
        self.clock = pg.time.Clock()

        #set key repeat
        pg.key.set_repeat(500, 100)

        #set the current working file (assignments.pkl or readings.pkl)
        self.cw_file = "assignments.pkl"

    def preparation(self):
        #message box
        #the message box does not extend into the main (1200,850) area
        #stretches from y=800 to 804
        pg.draw.line(self.surface, WHITE, (0,802),(self.w,802),5)

        #box areas
        # 0,1,2,3
        # 4,5,6,7
        #Because of the dividing line, each box loses one or two pixels
        boxes_rect = [
            (0  ,0,  299,399),
            (301,0,  298,399),
            (601,0,  298,399),
            (901,0,  298,399),
            (0  ,401,299,398),
            (301,401,298,398),
            (601,401,298,398),
            (901,401,298,398),
        ]

        ########################## INITIAL GRAPHICS ###############################
        #navigation bar (on the right, 45 pixels allocated)
        #stretches from x=1200 to 1204
        #because of the domain, the rects are confined to 46x46
        pg.draw.line(self.surface, WHITE, (1202,0),(1202,self.h),5)
        #next page
        next_page_rect = (1205,0,45,45)
        pg.draw.lines(self.surface, WHITE, True, [(1214,30),(1227,12),(1240,30)], 3)
        pg.draw.lines(self.surface, RED, True, [(1216,29),(1229,11),(1242,29)], 3)
        #previous page
        prev_page_rect = (1205,46,45,45)
        pg.draw.lines(self.surface, WHITE, True, [(1214,58),(1227,76),(1240,58)], 3)
        pg.draw.lines(self.surface, RED, True, [(1216,57),(1229,75),(1242,57)], 3)
        #undo
        undo_rect = (1205,92,45,45)
        pg.draw.arc(self.surface, WHITE, (1216,102,26,26), -3.14159/2, 3.14159, 3) 
        pg.draw.lines(self.surface, WHITE, False, [(1212,110),(1218,117),(1224,110)], 3)
        pg.draw.arc(self.surface, RED, (1218,101,26,26), -3.14159/2, 3.14159, 2) 
        pg.draw.lines(self.surface, RED, False, [(1214,109),(1220,116),(1226,109)], 3)
        #redo
        redo_rect = (1205,138,45,45)
        pg.draw.arc(self.surface, WHITE, (1214,148,26,26), 0, 3/2*3.14159, 3) 
        pg.draw.lines(self.surface, WHITE, False, [(1232,156),(1238,163),(1242,156)], 3)
        pg.draw.arc(self.surface, RED, (1216,147,26,26), 0, 3/2*3.14159, 2) 
        pg.draw.lines(self.surface, RED, False, [(1234,155),(1240,162),(1244,155)], 3)
        #add assignment
        add_rect = (1205,184,45,45)
        pg.draw.line(self.surface, WHITE, (1214,207),(1240,207),3)
        pg.draw.line(self.surface, WHITE, (1227,194),(1227,220),3)
        pg.draw.line(self.surface, RED, (1216,206),(1242,206),3)
        pg.draw.line(self.surface, RED, (1229,193),(1229,219),3)
        #remove assignment
        remove_rect = (1205,230,45,45)
        pg.draw.line(self.surface, WHITE, (1214,253),(1240,253),3)
        pg.draw.line(self.surface, RED, (1216,252),(1242,252),3)
        #edit assignment
        edit_rect = (1205,276,45,45)
        pg.draw.lines(self.surface, WHITE, False, [(1228,285),(1214,285),(1214,312),(1239,312),(1239,299)], 3)
        pg.draw.lines(self.surface, RED  , False, [(1230,283),(1216,283),(1216,310),(1241,310),(1241,297)], 3)
        pg.draw.lines(self.surface, WHITE , True, [(1242,280),(1228,297),(1226,301),(1230,299),(1246,284)], 3)
        pg.draw.lines(self.surface, RED   , True, [(1244,277),(1230,294),(1228,298),(1232,296),(1248,281)], 3)
        #assignments/readings toggle
        readings_rect = (1205,322,45,45)
        pg.draw.lines(self.surface, WHITE, True, [(1242,328),(1214,328),(1214,360),(1242,360)], 3)

        #page number
        page_num_rect = (1205,805,45,45)

        # pg.draw.line(self.surface, RED, (0,400), (0,400), 1)
        # pg.draw.line(self.surface, RED, (1200,100), (1200,100), 1)

        #pg.display.flip()
        #############################################################################

        self.buttons_rect = [next_page_rect,prev_page_rect,undo_rect,redo_rect,
                             add_rect,remove_rect,edit_rect,readings_rect]
        self.visuals_rect = [boxes_rect,page_num_rect]

        #initial page number
        self.page = 0

        #draw the yellow lines and the page number
        self.drawScreen()
        self.drawPageNumber()

        self.message_rect = (0,805,1190,45)

        #the shape of the popup window
        self.popup_rect = pg.Rect(400,150,400,500)
        self.popup = Popup((400,500),self.popup_rect)
        self.popup_sprites = pg.sprite.Group(self.popup)  #this overall was poor sprite management
        #there is only one sprite in this group
        self.popup_buttons = [self.popup.exit_win_rect, self.popup.submit_rect]

        self.current_page_sprites = pg.sprite.Group()

        # all_sprites = pg.sprite.Group()

        self.reload_asn(self.visuals_rect[0])

        pg.display.update()

    def draw_message(self, message):
        text = self.message_font.render(message,0,WHITE)
        #draw over the text that was there before
        self.surface.blit(text, (5,810))
        pg.display.update(self.message_rect)

    def remove_message(self):
        pg.draw.rect(self.surface, BLACK, self.message_rect)
        pg.display.update(self.message_rect)

    def message(self, message, event=True):
        self.draw_message(message)
        if event:
            self.events()
        self.remove_message()

    def removeAssignment(self, click_spots):
        self.draw_message("Single click on an assignment you wish to delete")

        #returns a number from 0 to 7 corresponding to the assignment that was clicked
        asn_num = self.events(click_spots,False)
        sprites = self.current_page_sprites.sprites()

        selected_sprite_title = sprites[asn_num].assignment.title

        self.remove_message()
        self.draw_message("Remove '{}'? Click on it again".format(selected_sprite_title))

        #returns a number from 0 to 7
        asn_num2 = self.events(click_spots)

        #remove the assignment
        if asn_num == asn_num2:
            delete_assignment(asn_num+self.page*8, self.cw_file)  #there are only 8 assignments per page,
            # but this value being passed indexes the entire list of assignments

        self.remove_message()

    def editAssignment(self, click_spots):
        self.draw_message("Click on an assignment you wish to edit")

        #returns a number from 0 to 7 corresponding to the assignment that was clicked
        asn_num = self.events(click_spots,False)

        #get the pkl file state and the assignment
        pkl_assignments = loadSort(self.cw_file)
        assignment = pkl_assignments[asn_num+self.page*8]

        self.remove_message()

        #edit the assignment
        # the pkl data needs to be passed as a state so that the objects don't change
        #  their place in memory before they are done being accessed.
        self.popup_events(assignment, pkl_assignments)  #there are only 8 assignments per page

    def toggle_readings(self, click_spots):
        if self.cw_file == "assignments.pkl":
            # change current working file
            self.cw_file = "readings.pkl"
            # toggle box colour
            pg.draw.lines(self.surface, RED, True, [(1242,328),(1214,328),(1214,360),(1242,360)], 3)

        else:
            # change current working file
            self.cw_file = "assignments.pkl"
            # toggle box colour
            pg.draw.lines(self.surface, WHITE, True, [(1242,328),(1214,328),(1214,360),(1242,360)], 3)

        # load the new file
        self.reload_asn(self.visuals_rect[0])

        # set page to 0
        self.page = 0

    def events(self, clickables=None, timer_on=True):
        if not clickables:
            clickables = [(0,0,self.w,self.h)]

        # ticks = 0
        timer = pg.USEREVENT+1
        pg.time.set_timer(timer, 1000)
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == timer and timer_on:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        sys.exit()
                if event.type == pg.MOUSEBUTTONUP:
                    for i in range(len(clickables)):
                        boundary_rect = pg.Rect(clickables[i])
                        if boundary_rect.collidepoint(event.pos):
                            return i

    def popup_events(self, existing_assignment=None, pkl_state=None):
        #when editing an assignment
        if existing_assignment:
            #removes the previous popup sprite so it can be replaced
            self.popup.kill()
            self.popup = Popup((400,500),self.popup_rect,
                               [
                               existing_assignment.title,
                               existing_assignment.section,
                               date2string(existing_assignment.due_date),
                               existing_assignment.start_date,
                               existing_assignment.notes
                               ])
            self.popup_sprites.add(self.popup)

        # print( self.popup == popup) # TRUE
        #draw the popup box
        self.popup_sprites.draw(self.surface)
        self.popup_sprites.update(self.surface)
        #counter so that the
        # count = 0

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        sys.exit()

                #text box loop
                for i in range(len(self.popup.input_boxes)):
                    if i>0 and self.popup.input_boxes[i-1].next_tab:
                        self.popup.input_boxes[i].tab = True
                    inp = self.popup.input_boxes[i].handle_event(event)
                    if inp == 1:
                        break
                    if inp == 2:  #submit with enter key
                        self.submit(existing_assignment, pkl_state)
                        running = False
                    if i>0 and self.popup.input_boxes[i-1].next_tab:
                        self.popup.input_boxes[i-1].next_tab = False
                        break

                if event.type == pg.MOUSEBUTTONUP:
                    for i in range(len(self.popup_buttons)):
                        boundary_rect = pg.Rect(self.popup_buttons[i])
                        if boundary_rect.collidepoint(event.pos):
                            if i == 0:  #cancel
                                #remove the text in the text boxes
                                for box in self.popup.input_boxes:
                                    box.clear_text()
                                #exit add attachment window
                                running = False

                            if i == 1:  #submit with click
                                self.submit(existing_assignment, pkl_state)
                                running = False

            #only reload the boxes every 30 frames
            # if count > 30:
            for box in self.popup.input_boxes:
                box.update(self.surface)

            for box in self.popup.input_boxes:
                box.draw(self.surface)

            pg.display.flip()
            # count += 1

    def submit(self,existing_assignment,pkl_state):
        #submit the assignment
        add_assignment_data = [self.popup.input_boxes[j].text for j in range(5)]
        #checks if there is a title and a due date
        if add_assignment_data[0] != '' and add_assignment_data[2] != '':
            asn = Assignment(add_assignment_data[0],
                             add_assignment_data[2],
                             add_assignment_data[1],
                             add_assignment_data[3],
                             add_assignment_data[4],
                             )
            #checks if the inputted date was formatted properly
            if asn.due_date is False:
                self.message("Error: improper date fromatting (use YYYY-MM-DDTHH:mm)")
            # elif asn.due_date == 0:
            #     self.message("The due date cannot be sonner than right now")
            else:
                #if editing, delete original
                if existing_assignment:
                    delete_specific_assignment(existing_assignment, pkl_state, self.cw_file)
                #saved to the current working file
                save_object(asn, self.cw_file)
                self.message("Added assignment '{}'".format(add_assignment_data[0]))
                #remove the text in the text boxes
                for box in self.popup.input_boxes:
                    box.clear_text()
        else:
            self.message("The assignement is missing a title or a due date.")

    def reload_asn(self, boxes_rect):
        #returns assignements sorted by due date
        assignments = loadSort(self.cw_file)
        #empties the sprite group
        self.current_page_sprites.empty()
        #display assignments on the screen
        for i in range(self.page*8,len(assignments)):
            if i < 8*(1+self.page):
                #checks if the background colour needs to change
                background = getDuedateBackground(assignments[i])
                asn = DisplayAssignment((boxes_rect[i%8][0],boxes_rect[i%8][0]),boxes_rect[i%8],assignments[i],background)
                self.current_page_sprites.add(asn)

        self.drawScreen()
        self.current_page_sprites.update(self.surface)

    def pageUp(self):
        #only goes up a page if there are assignments on it
        #loads the assignmets
        assignments = [i for i in loadall(self.cw_file)]
        if len(assignments) > (self.page+1)*8:
            self.page += 1
        return self.page

    def pageDown(self):
        if self.page != 0:
            self.page -= 1
        return self.page

    def drawScreen(self):
        #black background
        pg.draw.rect(self.surface, BLACK, (0,0,1200,800), 0)

        #yellow lines
        for i in range(3):
            x_pos = 300*(i+1)
            pg.draw.line(self.surface, YELLOW, (x_pos,0), (x_pos,800), 2)
        pg.draw.line(self.surface, YELLOW, (0,400), (1200,400), 2)

    def drawPageNumber(self):
        #page number
        pg.draw.rect(self.surface, BLACK, (1208,810,42,40),0)
        page_text = self.message_font.render(str(self.page), True, WHITE)
        self.surface.blit(page_text, (1208,810))
        pg.display.update((1208,810,42,40))

    def run(self):
        #main loop
        self.running = True
        while self.running:
            self.dt = self.clock.tick(60) / 1000  # 60 FPS

            button_clicked = self.events(self.buttons_rect)
            # print("button clicked: ", button_clicked)
            if button_clicked == 0:
                #next_page
                self.page = self.pageUp()
            elif button_clicked == 1:
                #prev_page
                self.page = self.pageDown()
            elif button_clicked == 2:
                #undo
                pass
            elif button_clicked == 3:
                #redo
                pass
            elif button_clicked == 4:
                #copy the rect that will be filled
                sub = self.surface.subsurface(self.popup_rect)
                sub = sub.copy()
                #add assignment popup
                self.popup_events()
                #paste the copied rect to return to the main screen
                self.surface.blit(sub, (self.popup_rect.x,self.popup_rect.y))
            elif button_clicked == 5:
                #remove assignment
                self.removeAssignment(self.visuals_rect[0])
            elif button_clicked == 6:
                #edit assignment
                self.editAssignment(self.visuals_rect[0])
            elif button_clicked == 7:
                #toggle_readings
                self.toggle_readings(self.visuals_rect[0])
            else:
                pass
                #print("here")
            #print(self.page)

            #draw and update page number
            self.drawPageNumber()

            self.reload_asn(self.visuals_rect[0])
            pg.display.update()


main = Main()
while True:
    # print("test")
    main.preparation()
    main.run()
