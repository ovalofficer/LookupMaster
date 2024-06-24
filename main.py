import tkinter as tk
from tkinter import *
from tkinter import ttk
import json
import webbrowser
import helpers

'''

LookupMaster 

Allows for faster lookup of names, usernames, e-mails, phone numbers, and other info in a simple UI.

'''


class ModuleEditor:

    def __init__(self, root):
        self.main_frame = root
        self.main_frame.grid_columnconfigure(1, weight=2)

        self.module_data = self.load_module_file()

        self.main_listbox_var = tk.StringVar()
        self.main_listbox = tk.Listbox(self.main_frame, height=16, width=67,
                                       selectbackground='lightgray', selectforeground='black', exportselection=False)
        self.main_listbox.grid(sticky='nsw', columnspan=2)
        self.main_listbox_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.main_listbox.yview)
        self.main_listbox_scrollbar.grid(column=1, row=0, sticky='nse')

        self.main_listbox['yscrollcommand'] = self.main_listbox_scrollbar.set

        self.main_listbox.bind('<<ListboxSelect>>', lambda x: [self.listbox_item_selected()])

        ttk.Label(self.main_frame, text='URL: ', justify='right').grid(column=0, row=1)
        ttk.Label(self.main_frame, text='Mask: ', justify='right').grid(column=0, row=2)
        ttk.Label(self.main_frame, text='API Key: ', justify='right').grid(column=0, row=3)
        ttk.Label(self.main_frame, text='Captcha: ', justify='right').grid(column=0, row=4)

        self.url_var = tk.StringVar()
        ttk.Entry(self.main_frame, width=32, textvariable=self.url_var).grid(column=1, row=1, sticky='we', pady=2, padx=10)

        self.mask_var = tk.StringVar()
        ttk.Entry(self.main_frame, width=32, textvariable=self.mask_var).grid(column=1, row=2, sticky='we', pady=2, padx=10)

        self.api_key_var = tk.StringVar()
        ttk.Entry(self.main_frame, width=32, textvariable=self.api_key_var).grid(column=1, row=3, sticky='we', pady=2, padx=10)

        self.captcha_var = tk.StringVar()
        tk.Checkbutton(self.main_frame, variable=self.captcha_var, onvalue='True', offvalue='False').grid(column=1, row=4, sticky='we', pady=2, padx=10)

        for k, v in self.module_data.items():
            for title, att in v.items():
                self.main_listbox.insert(0, k.title() + ' |' + title)

    def listbox_item_selected(self):
        item_values = self.get_current_item_values()

        self.url_var.set(item_values['url'])
        self.mask_var.set(item_values['mask'])
        self.api_key_var.set(item_values['api-key'])
        self.captcha_var.set(item_values['captcha'])

    def get_current_item_values(self):
        if not self.main_listbox.curselection():
            return ''
        else:
            selection = self.main_listbox.get(self.main_listbox.curselection())
            category = selection.split(' ', 1)[0]
            title = selection.split('|', 1)[1]

            return self.module_data[category.lower()][title]

    def load_module_file(self) -> dict[str, dict[str, dict[str, str]]]:
        with open('modules.json') as f:
            return json.loads(f.read())


class App:

    def __init__(self, root):
        self.window = root
        self.window.title('Lookup Master')
        self.window.geometry('450x500')
        self.window.resizable(0, 0)
        self.window.grid_columnconfigure(0, weight=1)

        self.main_notebook = ttk.Notebook(self.window, padding=5)
        self.main_notebook.grid(sticky='nswe', padx=5, pady=5)

        self.username_lookup_frame = ttk.Frame(self.main_notebook)
        self.phone_lookup_frame = ttk.Frame(self.main_notebook)
        self.name_lookup_frame = ttk.Frame(self.main_notebook)
        self.module_editor_frame = ttk.Frame(self.main_notebook)

        self.phone_lookup_frame.grid_columnconfigure(1, weight=2)

        self.main_notebook.add(self.phone_lookup_frame, text='Phone')
        self.main_notebook.add(self.name_lookup_frame, text='Name')
        self.main_notebook.add(self.username_lookup_frame, text='Username')
        self.main_notebook.add(self.module_editor_frame, text='Module Editor')

        self.phone_entry_label = ttk.Label(self.phone_lookup_frame, text='Enter a Phone Number (0-9, A-Z)')
        self.phone_entry_label.grid(pady=5, columnspan=2, sticky='n')

        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(self.phone_lookup_frame, textvariable=self.phone_var, width=18, justify=tk.CENTER,
                                     font=('Helvetica', 12, 'bold'))
        self.phone_entry.grid(pady=5, padx=10, columnspan=2, sticky='we')

        self.phone_entry_msg = ttk.Label(self.phone_lookup_frame,
                                         text='Phone number must be 10 characters.', foreground='red')
        self.phone_entry_msg.grid(columnspan=2, sticky='n')

        self.phone_entry.bind('<Any-KeyRelease>', self.phone_input_validation)

        self.module_editor = ModuleEditor(self.module_editor_frame)

        self.create_buttons()

    def get_sanitized_number(self):
        return helpers.clean_phone_number(self.phone_var.get())

    def phone_input_validation(self, event):

        self.phone_var.set(helpers.remove_special_characters(self.phone_var.get().strip()))
        pi = self.get_sanitized_number()

        while len(pi) > 10:
            self.phone_entry.delete(10, END)
            pi = self.get_sanitized_number()

        if len(pi) != 10:
            self.phone_entry_msg.config(text='Phone number must be 10 characters.', foreground='red')
        else:
            self.phone_entry_msg.config(text='Valid Number', foreground='green')

    def create_buttons(self):
        json_data = self.load_module_file()

        button_counter = 0
        for n, d in json_data['phone'].items():
            # print(n, d)
            def on_click(target=d):
                if not self.phone_entry_msg.cget('text') == 'Valid Number':
                    return
                print(target['url'] + helpers.translate_mask(target['mask'], self.get_sanitized_number()))

            column = 0 if button_counter < 10 else 1
            ttk.Button(self.phone_lookup_frame, text=n, command=on_click).grid(
                sticky='ew', column=column, row=button_counter + 3, padx=10, pady=2)
            if d['captcha'] == 'True':
                ttk.Label(self.phone_lookup_frame, text='CAPTCHA', foreground='red',
                          font=('Helvetica', 12, 'bold')).grid(
                    column=column + 1, sticky='nsew', row=button_counter + 3)
            button_counter += 1

    def load_module_file(self) -> dict[str, dict[str]]:
        with open('modules.json') as f:
            return json.loads(f.read())


def main():
    root = tk.Tk()
    instance = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
