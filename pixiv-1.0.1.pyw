from pathlib import Path
from tkinter import *
from tkinter import filedialog as fd
from ctypes import windll
import tkinter.messagebox as mb
import pixivapi
import sys
import emoji
import os


# Functions
# Login Function
def login():
    try:
        creds = set_username_password()
        client.login(creds[0], creds[1])
        root.withdraw()
        archive_window()
    except:
        mb.showerror(title='ERROR', message='Wrong Username/Password!')


def keyboard_login(event):
    login()


# Assign username and password
def set_username_password():
    username = username_entry.get()
    password = password_entry.get()
    return [username, password]


# Archiving window function
def archive_window():
    def logout():
        username = ''
        password = ''
        username_entry.delete(0, END)
        password_entry.delete(0, END)
        screen.destroy()
        root.deiconify()


    def keyboard_archive(event):
        get_works()

    
    def right_click_menu(event):
        click_menu.tk_popup(event.x_root, event.y_root)


    def get_clipboard():
        artist_url.delete(0, END)
        artist_url.insert(0, screen.clipboard_get())


    # Exit function
    def exit_program():
        screen.destroy()
        sys.exit(0)

    
    # Retrieval function
    def get_works():
        artist_id = artist_url.get().split('users/')[1]
        artist = client.fetch_user(artist_id).name
        for char in artist:
            if char in ('\\', '/', '\"'):
                artist = artist.replace(char, '_%')

        current_artist.config(text='Archiving: ' + artist)

        directory = str(fd.askdirectory()) + '\\' + str(artist)
        directory = Path(directory)

        response = client.fetch_user_illustrations(artist_id)
        while True:
            for ilust in response['illustrations']:
                try:
                    filename = ilust.title.replace(':', '-') + ' by ' + artist
                    counter = 0
                    files_arr = []
                    for (path, dirs, files) in os.walk(directory):
                        if len(files) != 0:
                            files_arr.extend(files)
                            break

                    i = 0
                    while i < len(files_arr):
                        # input(files_arr[i])
                        if filename in files_arr[i]:
                            counter += 1
                            filename = ilust.title.replace(':', '-') + f' ({counter}) by ' + artist
                            i = 0
                            continue
                        i += 1

                    ilust.download(directory=directory, size=pixivapi.Size.ORIGINAL, filename=filename)
                    # ilust.download(directory=directory, size=pixivapi.Size.ORIGINAL, filename=ilust.title.replace(':', '-') + ' by ' + artist)
                except OSError as e:
                    ilust.download(directory=directory, size=pixivapi.Size.ORIGINAL, filename=str(ilust.create_date).split(' ')[0] + ' by ' + artist)

            if not response['next']:
                break
            
            response = client.fetch_user_illustrations(
                artist_id,
                offset=response['next']
            )

        current_artist.config(text='')


    screen = Tk()
    screen.title('Pixiv GUI')
    screen.geometry('400x120')
    banner = Label(screen, text='Pixiv Artist Archiver', font=('Courier', 21))
    banner.grid(row=0, column=0, columnspan=2)

    # Hidden Widgets
    click_menu = Menu(screen, tearoff=0)
    click_menu.add_command(label='Paste', command=get_clipboard)

    # Obtaining the URL
    artist_label = Label(screen, text='Artist\'s URL: ', font=('Courier', 10))
    artist_label.grid(row=1, column=0, sticky=W)
    artist_url = Entry(screen, width=40)
    artist_url.grid(row=1, column=1, sticky=W)

    # Current Artist
    current_artist = Label(screen, text='', font=('Courier', 12))
    current_artist.grid(row=2, column=1, rowspan=2)

    # Execution Buttons
    archive = Button(screen, text='Archive', font=('Courier', 10), command=get_works)
    quit_program = Button(screen, text='Log Out', font=('Courier', 10), command=logout)
    archive.grid(row=2, column=0, sticky=W)
    quit_program.grid(row=3, column=0, sticky=W)
    screen.bind('<Button-3>', right_click_menu)
    screen.bind('<Return>', keyboard_archive)
    screen.mainloop()

# Client Setup
client = pixivapi.Client()
username = ''
password = ''
status = 'signed out'

# Begin Gui
root = Tk()
root.title('Pixiv Login')
root.geometry('300x50')

# Account credentials
username_label = Label(root, text='username: ', font=('Courier', 10))
username_entry = Entry(root, width=20)
username_label.grid(row=0, column=0)
username_entry.grid(row=0, column=1)

password_label = Label(root, text='password: ', font=('Courier', 10))
password_entry = Entry(root, width=20, show='*')
password_label.grid(row=1, column=0)
password_entry.grid(row=1, column=1)

# Execution Buttons
login_button = Button(root, text='Login', font=('Courier', 15), command=login)
login_button.grid(row=0, column=2, rowspan=2, padx=5, sticky=E)
root.bind('<Return>', keyboard_login)

# Instantiating the GUI
root.mainloop()
