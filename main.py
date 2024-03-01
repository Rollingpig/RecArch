import pygame
import sys
import webbrowser
import tkinter as tk
from tkinter import filedialog

from query import query_from_database

pygame.init()

# UI
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
IMAGE_NUM_PER_ROW = 3
IMAGE_HEIGHT = 150
BASE_PADDING = 50
FONT_SIZE = 32
SMALL_FONT_SIZE = 24
BUTTON_WIDTH = 80
BUTTON_GAP = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

image_width = (WINDOW_WIDTH - BASE_PADDING * 2) / IMAGE_NUM_PER_ROW

# Window setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("RecArch - Project Search")
font = pygame.font.Font(None, FONT_SIZE)
small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
clock = pygame.time.Clock()

# Input box
input_box_width = (WINDOW_WIDTH - BASE_PADDING * 2) - BUTTON_WIDTH*2 - BUTTON_GAP
input_box = pygame.Rect(BASE_PADDING, BASE_PADDING, input_box_width, FONT_SIZE)
color_inactive = GRAY
color_active = BLACK
color = color_inactive
active = False
text = ''

# Find Button
find_button = pygame.Rect(BASE_PADDING + input_box_width, BASE_PADDING, BUTTON_WIDTH, FONT_SIZE)
button_text = font.render('Find', True, WHITE)
button_color = BLACK

# File Button
file_button = pygame.Rect(BASE_PADDING + input_box_width + BUTTON_WIDTH + BUTTON_GAP, BASE_PADDING, BUTTON_WIDTH, FONT_SIZE)
file_button_text = font.render('Open', True, WHITE)
file_button_color = BLACK

# Function to open file dialog and return selected file path
def open_file_dialog():
    file_path = filedialog.askopenfilename()  # Open the file dialog
    return file_path

# Function to be called
def find(input_text, database_folder_path="test_database"):
    similarity_dict = query_from_database(input_text, database_folder_path)

    result_text = f"Result for '{input_text}':\n"

    # print the most similar projects
    for project_name in similarity_dict:
        result_text += f"{project_name}: {similarity_dict[project_name]}\n"

    image_paths = []
    url_paths = []
    for project_name in similarity_dict:
        image_paths.append(similarity_dict[project_name]["image_path"])
        url_paths.append(similarity_dict[project_name]["web_url"])

    return result_text, image_paths, url_paths

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    while words:
        line = ''
        while words and font.size(line + words[0])[0] <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line)
    return lines


def open_webpage(urls, index):
    # webbrowser.open(urls[index])
    pass

# Function to load and scale images
def load_and_scale_images(paths, target_width=image_width):
    images = []
    for i, path in enumerate(paths):
        try:
            # Load the image
            image = pygame.image.load(path)
            # Get the original dimensions
            width, height = image.get_size()
            # Maintain aspect ratio
            aspect_ratio = height / width
            new_height = int(target_width * aspect_ratio)
            # Scale the image
            scaled_image = pygame.transform.scale(image, (target_width, new_height))
            # image position
            position = (BASE_PADDING + (i % IMAGE_NUM_PER_ROW)*image_width, 
                        BASE_PADDING*2 + (i // IMAGE_NUM_PER_ROW)*IMAGE_HEIGHT)
            
            images.append((scaled_image, position))
        except pygame.error as e:
            print(f"Error loading or scaling image: {path} - {e}")
            images.append(None, (0, 0))
    return images

# Image display variables
image_surfaces = []

# Result display
result = ""
result_surf = font.render('', True, BLACK)

def main(database_folder_path):
    global color, text, active, result, result_surf, image_surfaces
    urls = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input box
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

                # Check if click is within any image bounds
                for i, (image, pos) in enumerate(image_surfaces):
                    if image:
                        image_rect = image.get_rect(topleft=pos)
                        if image_rect.collidepoint(event.pos):
                            open_webpage(urls, i)  # Open webpage with the index of the image

                # If the user clicked on the find button
                if find_button.collidepoint(event.pos):
                    result, img_paths, urls = find(text, database_folder_path)
                    result_surf = small_font.render(result, True, BLACK)
                    image_surfaces = load_and_scale_images(img_paths)

                # If the user clicked on the file button
                if file_button.collidepoint(event.pos):
                    file_path = open_file_dialog()
                    if file_path:
                        text = file_path
                
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        text += '\n'
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(WHITE)
        # Render the current text
        txt_surface = font.render(text, True, color)
        # Resize the box if the text is too long
        width = max(input_box_width, txt_surface.get_width()+10)
        input_box.w = width
        # Blit the text
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input box
        pygame.draw.rect(screen, color, input_box, 2)
        
        # Draw button
        pygame.draw.rect(screen, button_color, find_button)
        screen.blit(button_text, (find_button.x + 20, find_button.y + 5))
        # Draw file button
        pygame.draw.rect(screen, file_button_color, file_button)
        screen.blit(file_button_text, (file_button.x + 10, file_button.y + 5))
        
        # Display images
        if len(image_surfaces) > 0:
            for i, (image, pos) in enumerate(image_surfaces):
                if image:  # Check if image was successfully loaded
                    screen.blit(image, pos)

        # # Display result with wrapping
        # wrapped_text = wrap_text(result, small_font, (WINDOW_WIDTH - BASE_PADDING * 2))
        # y_offset = WINDOW_HEIGHT * 0.8
        # for line in wrapped_text:
        #     line_surface = small_font.render(line, True, BLACK)
        #     screen.blit(line_surface, (50, y_offset))
        #     y_offset += small_font.get_height()
        
        
        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main("database")
