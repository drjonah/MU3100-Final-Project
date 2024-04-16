import logging
import os
from datetime import date
from tkinter import filedialog

# this method will go through the process of creating a file
def create_file(log: logging) -> tuple | None:
    print("Let's create a new file!")

    # get file details
    print("What would you like to name the file?")
    file_name = input("> ")

    piece_name = input("\nWhat do you want your piece to be called?\n> ")
    piece_athor = input("\nWhat is the name of the composer?\n> ")

    while True:
        significant_letter = input("\nWhat is your significant letter? [a-z]\n> ")
        if significant_letter.isalpha():
            significant_letter.upper()
            break
        print("Must be between [A-Z/a-z]!")

    while True:
        print("\nWould you like to store the file?")
        directory = filedialog.askdirectory()  
        if directory:
            break
        print("Error fetching path, try again.")


    # create file
    try:
        file_path = os.path.join(directory, f"{file_name}.organum")
        with open(file_path, "w") as file:
            # write ignore
            file.write("\ignore {\n")
            file.write(f"\tcreated {date.today()}")
            file.write("}\n\n")

            # write file instructions
            file.write("\instruct {\n")
            file.write(f"\ttitle = {piece_name}\n")
            file.write(f"\tauthor = {piece_athor}\n")
            file.write(f"\tsignificant_letter = {significant_letter}\n")
            file.write("}\n\n")

            # start music 
            file.write("\music {\n")
            file.write("}\n\n")
        
        print("\nFile created! Editor opening now...")
        return (file_name, file_path)
    
    except Exception as e:
        log.error(f"Unknown error [{e}]")
        return None

# this method will open a file
def open_file(log: logging) -> tuple | None:
    print("Let's find your existing file!")

    # get file details
    print("Where is your file stored? ['.organum' files only]")
    try:
        file_path = filedialog.askopenfilename(
            title="Select .organum file",
            filetypes=[("Organum files", "*.organum")]
        )
    except Exception as e:
        log.error(f"Unknown error [{e}]")

    if file_path and validate_file(file_path):
        file_name = os.path.basename(file_path)
        return (file_path, file_name)
    
    return None

def validate_file(file_path: str) -> bool:
    return True