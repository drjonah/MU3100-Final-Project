import pygame
from modules import generate_voices, map_note, play

class Notator:
    def __init__(self) -> None:
        # initialize notator
        pygame.init()

        # window properties
        self.window_size = (600, 900)  
        self.screen = None 

        # font
        self.letter_font = pygame.font.Font("./assets/OldEnglishFive.ttf", 110)
        self.title_font = pygame.font.SysFont('Times New Roman', 40)
        self.author_font = pygame.font.SysFont('Times New Roman', 20)

        # colors
        self.background_color = (232,216,195)
        self.staff_color = (204, 0, 0)
        self.text_color = (0, 0, 0)
        self.note_color = (0, 0, 0)

        # music
        self.voices = generate_voices()
        self.note_size = 15

        # generate window
        self.set_window()

    def set_window(self) -> None:
        # set screen
        self.screen = pygame.display.set_mode(self.window_size)
        # set window
        pygame.display.set_caption("Organum Notator")
        # set background
        self.screen.fill(self.background_color) 

        pygame.display.flip()

    def draw_staff(self) -> None:
        # draw all the staff by the voice
        for voice in self.voices:
            # all the staffs associated with a voice
            all_staff = voice.staffs
            # each staff group in all staffs
            for staff_group in all_staff:
                # each staff in the staff groups
                for staff_line, staff in enumerate(staff_group):
                    # get correct width
                    width = 2 if staff_line % 5 == 0 or staff_line % 5 == 4 else 1
                    # draw
                    pygame.draw.line(self.screen, self.staff_color, staff[0], staff[1], width)
                    pygame.display.flip()

    def draw_text(self) -> None:
        # Significant letter
        significant_letter = self.letter_font.render("G", True, self.text_color)
        self.screen.blit(significant_letter, (10,100))

        # Title 
        title = self.title_font.render("Gregorian Chant", True, self.text_color)
        title_rect = title.get_rect(center=(600//2, 40))
        self.screen.blit(title, title_rect)
        
        # Author
        title = self.author_font.render("Jonah Lysne", True, self.text_color)
        title_rect = title.get_rect(center=(600//2, 70))
        self.screen.blit(title, title_rect)

    def add_note(self, x: int, y: int) -> None:
        # map note to where the voice and staff it belongs
        voice, staff, y_coord = map_note(self.voices, x, y)
        print(f"voice = {voice}, staff = {staff}")

        # invalid
        if voice is None: return

        # draw a square at the calculated position
        pygame.draw.rect(self.screen, self.note_color, pygame.Rect(x - self.note_size // 2, y_coord - self.note_size // 2, self.note_size, self.note_size))
        pygame.display.flip()

    def run(self) -> None:
        # run notator
        run = True
        while run:
            # draw 
            self.draw_staff()
            self.draw_text()

            # game loop
            for event in pygame.event.get():
                # exit  
                if event.type == pygame.QUIT:
                    run = False
                # key presses
                elif event.type == pygame.KEYDOWN:
                    # escape click
                    if event.key == pygame.K_ESCAPE:
                        run = False
                    # open tool bar
                    elif event.key == pygame.K_p:
                        play(self.voices[0])
                # button click
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.add_note(*event.pos)

        # quit notator
        pygame.quit()