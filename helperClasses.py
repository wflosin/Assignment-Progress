import pygame as pg
from datetime import datetime as dt
from colours import BLACK, WHITE, GRAY, D_GRAY, GREEN, RED, YELLOW, \
    COLOR_ACTIVE, COLOR_INACTIVE
from helperFunctions import new_line, string2date, rect2start_pos, \
    rect2end_pos

pg.font.init()
title_font = pg.font.SysFont('Calibri', 28)
header_font = pg.font.SysFont('Calibri', 20)

dates_font = pg.font.SysFont('Calibri', 22)
notes_font = pg.font.SysFont('Calibri', 16)
text_box_font = pg.font.SysFont('Calibri', 14)


class Assignment:
    def __init__(self, title, due_date, section='', start_date='', notes=''):
        #,colour=BLACK, width=298, height=398):
        self.title = title
        self.section = section

        #due date format 2019-06-05T25:53
        self.due_date = string2date(due_date)

        if not start_date:
            self.start_date = str(dt.now())[:-7]
        else:
            self.start_date = start_date

        self.notes = notes

        self.time_left = ''


class DisplayAssignment(pg.sprite.Sprite):
    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self,pos,rect, assignment, background):
        # Call the parent class (Sprite) constructor
        pg.sprite.Sprite.__init__(self)
        self.assignment = assignment
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pg.Surface(pos)
        self.background = background
        self.image.fill(background)

        self.rect = pg.Rect(rect)

        if self.background in [BLACK,RED]:
            self.text_bold = WHITE
            self.text_norm = GRAY
        if self.background in [GREEN,YELLOW,WHITE]:
            self.text_bold = BLACK
            self.text_norm = D_GRAY

    def update(self, surface):
        #background
        pg.draw.rect(surface, self.background, self.rect, 0)
        #title
        title_text = title_font.render(self.assignment.title, True, self.text_bold)
        surface.blit(title_text, (10+self.rect.x, 10+self.rect.y))
        #section
        section_text = header_font.render(self.assignment.section, True, self.text_norm)
        surface.blit(section_text, (10+self.rect.x, 50+self.rect.y))
        #due date
        due_text = header_font.render("Due: {}".format(self.assignment.due_date), True, self.text_bold)
        surface.blit(due_text, (10+self.rect.x, 80+self.rect.y))
        #time left
        time_left_text = header_font.render("Time Left: {}".format(self.assignment.time_left), True, self.text_bold)
        surface.blit(time_left_text, (10+self.rect.x, 110+self.rect.y))
        #start date
        start_text = header_font.render("Start Date: {}".format(self.assignment.start_date), True, self.text_norm)
        surface.blit(start_text, (10+self.rect.x, 140+self.rect.y))
        #notes
        notes_text = notes_font.render("Notes: ", True, self.text_norm)
        surface.blit(notes_text, (10+self.rect.x, 170+self.rect.y))
        #draws the notes onto new lines (40 characters max per line)
        notes_lines = new_line(self.assignment.notes).split('$_$')
        for i in range(len(notes_lines)):
            notes_text = notes_font.render(notes_lines[i], True, self.text_norm)
            surface.blit(notes_text, (10+self.rect.x, 190+self.rect.y+(i*20)))


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = text_box_font.render(text, True, self.color)
        self.active = False
        self.next_tab = False
        self.tab = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONUP or self.tab:
            # If the user clicked on the input_box rect.
            if self.tab or self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            if self.tab:
                self.tab = False
        #typing
        if event.type == pg.KEYDOWN:
            if self.active:
                # if event.key == pg.K_RETURN:
                #     print(self.text)
                #     #self.text = ''
                if event.key == pg.K_TAB:
                    self.next_tab = True
                    self.active = False
                    self.color = COLOR_INACTIVE
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                #if the text is too long
                elif len(self.text) > 45:
                    return 0
                # elif event.unicode in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=~!@#$%^&*()_+[]\\|}{;':\",./<>? ":
                elif event.key == pg.K_RETURN:
                    # self.txt_surface = text_box_font.render(self.text, True, self.color)
                    return 2
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = text_box_font.render(self.text, True, self.color)
                return 1

    def update(self, surface):
        #fill the shape with background colour
        #the extra +2s are for when the text bar is extended and you delete characters
        # to retract the bar
        surface.fill(GRAY, (self.rect.x, self.rect.y, self.rect.w+2, self.rect.h+2))

        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, surface):
        # Blit the text.
        surface.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(surface, self.color, self.rect, 2)

    def clear_text(self):
        self.text = ''


class Popup(pg.sprite.Sprite):
    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self,pos,rect,text_list=['', '', str(dt.now().year)+'-', '', '']):
        # Call the parent class (Sprite) constructor
        pg.sprite.Sprite.__init__(self)

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pg.Surface(pos)
        self.image.fill(GRAY)

        self.rect = rect

        input_box_title = InputBox(30+self.rect.x, 60+self.rect.y, 140, 20, text_list[0])
        input_box_section = InputBox(30+self.rect.x, 150+self.rect.y, 140, 20, text_list[1])
        input_box_due = InputBox(30+self.rect.x, 240+self.rect.y, 140, 20, text_list[2])
        input_box_start = InputBox(30+self.rect.x, 330+self.rect.y, 140, 20, text_list[3])
        input_box_notes = InputBox(30+self.rect.x, 420+self.rect.y, 140, 20, text_list[4])
        self.input_boxes = [input_box_title, input_box_section, input_box_due, input_box_start, input_box_notes]

        self.x1,self.y1 = rect2start_pos(self.rect)
        self.x2,self.y2 = rect2end_pos(self.rect)

        self.exit_win_rect = (self.x2-30,self.y1,30,30)
        self.submit_rect = (self.x2-30,self.y2-30,30,30)

    def update(self, surface):
        #exit window "x" button
        pg.draw.line(surface, RED, (self.x2-26,self.y1+4), (self.x2-4,self.y1+26), 2)
        pg.draw.line(surface, RED, (self.x2-26,self.y1+26), (self.x2-4,self.y1+4), 2)

        #Green cirle to submit the assignment
        pg.draw.circle(surface, GREEN, (self.x2-15,self.y2-15), 11, 2)
        pg.draw.lines(surface, BLACK, False, [(self.x2,self.y2-30),(self.x2-30,self.y2-30),(self.x2-30,self.y2)], 2)

        #add assignment title
        pg.draw.line(surface, BLACK, (self.x2-30,self.y1),(self.x2-30,self.y1+30), 2)
        pg.draw.line(surface, BLACK, (self.x1,self.y1+30),(self.x2,self.y1+30), 2)

        title_text = title_font.render("Assignment", True, BLACK)

        surface.blit(title_text, (10+self.rect.x, self.rect.y+2))

        #box names
        title_text = header_font.render("Title*:", True, BLACK)
        surface.blit(title_text, (30+self.rect.x, 40+self.rect.y))
        section_text = header_font.render("Class:", True, BLACK)
        surface.blit(section_text, (30+self.rect.x, 130+self.rect.y))
        due_text = header_font.render("Due date (YYYY-MM-DDTHH:mm)*:", True, BLACK)
        surface.blit(due_text, (30+self.rect.x, 220+self.rect.y))
        start_text = header_font.render("Start date:", True, BLACK)
        surface.blit(start_text, (30+self.rect.x, 310+self.rect.y))
        notes_text = header_font.render("Notes:", True, BLACK)
        surface.blit(notes_text, (30+self.rect.x, 400+self.rect.y))
        notes_text = text_box_font.render("(THH:mm is optional)", True, BLACK)
        surface.blit(notes_text, (30+self.rect.x, 460+self.rect.y))
