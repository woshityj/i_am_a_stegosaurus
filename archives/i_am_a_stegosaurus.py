import os
import tkinter as tk
import wave
from tkinter import Label, Text, Button, messagebox, Frame, Scrollbar, IntVar, Checkbutton, Spinbox

import cv2
from tkinterdnd2 import DND_FILES, Tk
from tkinter.filedialog import asksaveasfilename, askopenfilename
import image_steganography as ims

import math

supported_types = {
    '.png': None,
    '.gif': None,
    '.bmp': None,
    '.wav': None,
    '.mp3': None,
    '.mp4': None,
    '.txt': None,
    '.xls': None,
    '.doc': None
}


def get_path(filetype):
    file_path = askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetype
    )
    if file_path:
        return file_path


def get_drop(event, filetype):
    file_path = event.data
    if os.path.isfile(file_path):
        _, ext = os.path.splitext(file_path)
    else:
        messagebox.showerror("Error", f"Cannot open file from {file_path}")
        return

    if ext.lower() not in list(filetype):
        messagebox.showerror("Error", f"File type {ext} not supported.")
        return
    return file_path


def get_text_content(path):
    with open(path, 'r') as file:
        return file.read()


def show(path):
    os.startfile(path)


class app:
    def __init__(self):
        # UI
        self.root = Tk()
        self.root.title("i_am_a_stegosaurus")
        # self.root.geometry('685x500')
        self.root.resizable(0, 0)

        # frame
        self.rootFrame = Frame(self.root)
        self.settingFrame = Frame(self.rootFrame)
        self.settingSubFrame1 = Frame(self.settingFrame)
        self.settingSubFrame2 = Frame(self.settingFrame)
        self.payloadFrame = Frame(self.rootFrame)
        self.coverFrame = Frame(self.rootFrame)
        self.actionFrame = Frame(self.rootFrame)

        self.payloadFrame.drop_target_register(DND_FILES)
        self.payloadFrame.dnd_bind('<<Drop>>', self.payload_on_drop)

        self.coverFrame.drop_target_register(DND_FILES)
        self.coverFrame.dnd_bind('<<Drop>>', self.cover_on_drop)

        self.rootFrame.pack(padx=10, pady=10)
        self.settingFrame.pack(anchor='w', padx=(0, 10), pady=(0, 10))
        self.settingSubFrame1.grid(row=1, column=0, sticky='w', pady=(0, 10))
        self.settingSubFrame2.grid(row=2, column=0, sticky='w', pady=(0, 10))
        self.payloadFrame.pack(anchor='w', padx=(0, 10), pady=(0, 10))
        self.coverFrame.pack(anchor='w', padx=(0, 10), pady=(0, 10))
        self.actionFrame.pack(padx=(0, 10), pady=(0, 10))

        # variables
        self.payloadPath = None
        self.coverPath = None
        self.payloadText = None
        self.encoded = None

        # setting frame
        Label(self.settingFrame, text="Settings", font=('Aria', 10)).grid(row=0, column=0, sticky='w')
        self.ckbSaveOptionVar = IntVar()
        Checkbutton(self.settingSubFrame1, text="Save decoded text",
                    variable=self.ckbSaveOptionVar).grid(row=0, column=0, sticky='w')
        self.sbNumBit = Spinbox(self.settingSubFrame1, from_=1, to=5)
        Label(self.settingSubFrame1, text="Number of bits:").grid(row=0, column=1, padx=(20, 0))
        self.sbNumBit.grid(row=0, column=2)
        Label(self.settingSubFrame2, text="Password:").grid(row=0, column=0, sticky='w')
        txt_password = Text(self.settingSubFrame2, height=1, width=72)
        txt_password.grid(row=0, column=1, sticky='w')

        # payload frame
        Label(self.payloadFrame, text="Payload", font=('Aria', 10)).grid(row=0, column=0, sticky='w')
        Button(self.payloadFrame, text="Upload a payload file or drag and drop here",
               command=self.payload_on_change, width=90).grid(row=1, column=0, pady=(0, 10))
        self.payload_scroll_bar = Scrollbar(self.payloadFrame)
        self.payload_scroll_bar.grid(row=2, column=1, sticky='nse')
        self.payload_text = Text(self.payloadFrame, height=5, yscrollcommand=self.payload_scroll_bar.set)
        self.payload_text.grid(row=2, column=0, sticky='w')

        # cover frame
        Label(self.coverFrame, text="Cover", font=('Aria', 10)).grid(row=0, column=0, sticky='w')
        Button(self.coverFrame, text="Upload a cover file or drag and drop here",
               command=self.cover_on_change, width=90).grid(row=1, column=0, pady=(0, 10))

        # action frame
        Button(self.actionFrame, text="Encode", command=self.encode).grid(row=0, column=0, sticky='e', padx=(0, 10))
        Button(self.actionFrame, text="Decode", command=self.decode).grid(row=0, column=1, sticky='w', padx=(10, 0))

    def payload_on_change(self):
        self.payloadPath = get_path([('Text file', '*.txt')])
        if self.payloadPath is not None:
            self.show_payload()

    def payload_on_drop(self, event):
        self.payloadPath = get_drop(event, {'.txt'})
        if self.payloadPath is not None:
            self.show_payload()

    def show_payload(self):
        self.payload_text.delete('1.0', tk.END)
        self.payloadText = get_text_content(self.payloadPath)
        self.payload_text.insert('1.0', self.payloadText)

    def cover_on_change(self):
        self.coverPath = get_path([('', '*' + key) for key in supported_types.keys()])
        if self.coverPath is not None:
            show(self.coverPath)

    def cover_on_drop(self, event):
        self.coverPath = get_drop(event, supported_types)
        if self.coverPath is not None:
            show(self.coverPath)

    def encode(self):
        if self.coverPath is None:
            messagebox.showerror("Error", "Please select or drop a cover item first!")
            return
        _, ext = os.path.splitext(self.coverPath)
        self.payloadText = self.payload_text.get('1.0', 'end-1c')
        self.encoded = supported_types[ext.lower()][0](self.coverPath, self.payloadText, int(self.sbNumBit.get()))
        self.save_as(ext)

    def decode(self):
        if self.coverPath is None:
            messagebox.showerror("Error", "Please select or drop a cover item first!")
            return
        _, ext = os.path.splitext(self.coverPath)
        text = supported_types[ext.lower()][1](self.coverPath, int(self.sbNumBit.get()))
        self.payload_text.delete('1.0', tk.END)
        self.payload_text.insert('1.0', text)
        if self.ckbSaveOptionVar.get() == 1:
            path = asksaveasfilename(defaultextension='.txt')
            if path:
                with open(path, 'w') as file:
                    file.write(text)

    def save_as(self, ext):
        # save as prompt
        filename = asksaveasfilename(defaultextension=ext, filetypes=[("Same as original", ext), ("All Files", "*.*")])
        if filename:
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                # save image
                cv2.imwrite(filename, self.encoded)
                # show image as per requested in spec
                show(filename)
            elif filename.endswith(('.wav', '.mp3')):
                song = wave.open(self.coverPath, mode = 'rb')
                with wave.open(filename, 'wb') as fd:
                    fd.setparams(song.getparams())
                    fd.writeframes(self.encoded)
                    print("\nEncoded the data successfully in the audio file")

    def run(self):
        self.root.mainloop()

    def encryptText(msg):
        cipher = ""
    
        # track key indices
        k_indx = 0
    
        msg_len = float(len(msg))
        msg_lst = list(msg)
        key_lst = sorted(list(key))
    
        # calculate column of the matrix
        col = len(key)
        
        # calculate maximum row of the matrix
        row = int(math.ceil(msg_len / col))
    
        # add the padding character '_' in empty
        # the empty cell of the matix 
        fill_null = int((row * col) - msg_len)
        msg_lst.extend('_' * fill_null)
    
        # create Matrix and insert Text and 
        # padding characters row-wise 
        matrix = [msg_lst[i: i + col] 
                for i in range(0, len(msg_lst), col)]
    
        # read matrix column-wise using key
        for _ in range(col):
            curr_idx = key.index(key_lst[k_indx])
            cipher += ''.join([row[curr_idx] 
                            for row in matrix])
            k_indx += 1
    
        return cipher

    def decryptText(cipher):
        msg = ""
    
        # track key indices
        k_indx = 0
    
        # track msg indices
        msg_indx = 0
        msg_len = float(len(cipher))
        msg_lst = list(cipher)
    
        # calculate column of the matrix
        col = len(key)
        
        # calculate maximum row of the matrix
        row = int(math.ceil(msg_len / col))
    
        # convert key into list and sort 
        # alphabetically so we can access 
        # each character by its alphabetical position.
        key_lst = sorted(list(key))
    
        # create an empty matrix to 
        # store deciphered Text
        dec_cipher = []
        for _ in range(row):
            dec_cipher += [[None] * col]
    
        # Arrange the matrix column wise according 
        # to permutation order by adding into new matrix
        for _ in range(col):
            curr_idx = key.index(key_lst[k_indx])
    
            for j in range(row):
                dec_cipher[j][curr_idx] = msg_lst[msg_indx]
                msg_indx += 1
            k_indx += 1
    
        # convert decrypted msg matrix into a string
        try:
            msg = ''.join(sum(dec_cipher, []))
        except TypeError:
            raise TypeError("This program cannot",
                            "handle repeating words.")
    
        null_count = msg.count('_')
    
        if null_count > 0:
            return msg[: -null_count]
    
        return msg
  
app().run()
