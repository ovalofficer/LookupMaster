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


class MenuTab:

    def __init__(self, root):
        self.main_frame = root
        self.module_data = None

        self.refresh_module_data()

    def refresh_module_data(self):
        self.module_data = MenuTab.load_module_file()

    @staticmethod
    def load_module_file() -> dict[str, dict[str]]:
        with open('modules.json') as f:
            return json.loads(f.read())


class ModuleEditorTab(MenuTab):

    def __init__(self, root):
        super().__init__(root)

        self.main_frame.grid_columnconfigure(2, weight=2)

        self.main_listbox_var = tk.StringVar()
        self.main_listbox = tk.Listbox(self.main_frame, height=16, width=67,
                                       selectbackground='lightgray', selectforeground='black', exportselection=False)
        self.main_listbox.grid(sticky='nsw', columnspan=4)
        self.main_listbox_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL,
                                                    command=self.main_listbox.yview)
        self.main_listbox_scrollbar.grid(column=3, row=0, sticky='nse')

        self.main_listbox['yscrollcommand'] = self.main_listbox_scrollbar.set

        self.main_listbox.bind('<<ListboxSelect>>', lambda x: [self.listbox_item_selected()])

        ttk.Label(self.main_frame, text='URL: ', justify='right').grid(column=0, row=1)
        ttk.Label(self.main_frame, text='Mask: ', justify='right').grid(column=0, row=2)
        ttk.Label(self.main_frame, text='API Key: ', justify='right').grid(column=0, row=3)
        ttk.Label(self.main_frame, text='Captcha: ', justify='right').grid(column=0, row=4)

        self.url_var = tk.StringVar()
        ttk.Entry(self.main_frame, width=32, textvariable=self.url_var).grid(column=1, row=1, pady=2, padx=10,
                                                                             columnspan=3, sticky='we')

        self.mask_var = tk.StringVar()
        ttk.Entry(self.main_frame, width=32, textvariable=self.mask_var).grid(column=1, row=2, pady=2, padx=10,
                                                                              columnspan=3, sticky='we')

        self.api_key_var = tk.StringVar()
        ttk.Entry(self.main_frame, width=32, textvariable=self.api_key_var).grid(column=1, row=3, pady=2, padx=10,
                                                                                 columnspan=3, sticky='we')

        self.captcha_var = tk.StringVar()
        tk.Checkbutton(self.main_frame, variable=self.captcha_var, onvalue='True', offvalue='False').grid(
            column=1, row=4, sticky='w', pady=2, padx=10)

        ttk.Button(self.main_frame, text='Save Current Module').grid(column=2, row=4, sticky='w')
        ttk.Button(self.main_frame, text='Create New Module').grid(column=2, row=4, sticky='e')

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


class PhoneLookupTab(MenuTab):
    def __init__(self, root):
        super().__init__(root)

        self.main_frame.grid_columnconfigure(1, weight=2)

        self.phone_entry_label = ttk.Label(self.main_frame, text='Enter a Phone Number (0-9, A-Z)')
        self.phone_entry_label.grid(pady=5, columnspan=2, sticky='n')

        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(self.main_frame, textvariable=self.phone_var, width=18, justify=tk.CENTER,
                                     font=('Helvetica', 12, 'bold'))
        self.phone_entry.grid(pady=5, padx=10, columnspan=2, sticky='we')

        # For best practice, this should eventually use a StringVar and refresh dynamically
        self.phone_entry_msg = ttk.Label(self.main_frame, text='Phone number must be 10 characters.', foreground='red')
        self.phone_entry_msg.grid(columnspan=2, sticky='n')

        self.phone_entry.bind('<Any-KeyRelease>', lambda x: [self.phone_input_validation()])

        self.buttons = {}

        self.create_buttons()

    def phone_input_validation(self):

        self.phone_var.set(helpers.remove_special_characters(self.phone_var.get().strip()))
        pi = self.get_sanitized_number()

        while len(pi) > 10:
            self.phone_entry.delete(10, END)
            pi = self.get_sanitized_number()

        if len(pi) != 10:
            self.phone_entry_msg.config(text='Phone number must be 10 characters.', foreground='red')
        else:
            self.phone_entry_msg.config(text='Valid Number', foreground='green')

    def get_sanitized_number(self):
        return helpers.clean_phone_number(self.phone_var.get())

    def create_buttons(self):
        button_counter = 0

        for n, d in self.module_data['phone'].items():
            # print(n, d)

            # Have to create an on-click function for the button to use.
            def on_click(target=d):
                # print('Button Clicked')
                if not self.phone_entry_msg.cget('text') == 'Valid Number':
                    return

                # Desired click operation goes here.
                # TODO: implement webbrowser to open a chrome tab. alternatively, implement scraping. add some way to
                #  configure scraped information in modules.json, then then offer option to save data to file or
                #  open in a TopLevel with a textbox
                print(target['url'] + helpers.translate_mask(target['mask'], self.get_sanitized_number()))

            # ugly one-liner but does what I want it to -- find better solution for dynamic button placement
            column = 0 if button_counter < 10 else 1
            button_counter += 1

            # Have to add to grid after, otherwise .grid operation returns None
            self.buttons[n.lower()] = ttk.Button(self.main_frame, text=n, command=on_click)
            self.buttons[n.lower()].grid(sticky='ew', column=column, row=button_counter + 3, padx=10, pady=2)

            # Adds CAPTCHA text next to button when applicable
            if d['captcha'] == 'True':
                ttk.Label(self.main_frame, text='CAPTCHA', foreground='red', font=('Helvetica', 12, 'bold')).grid(
                    column=column + 1, sticky='nsew', row=button_counter + 3)


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

        self.main_notebook.add(self.phone_lookup_frame, text='Phone')
        self.main_notebook.add(self.name_lookup_frame, text='Name')
        self.main_notebook.add(self.username_lookup_frame, text='Username')
        self.main_notebook.add(self.module_editor_frame, text='Module Editor')

        self.module_editor = ModuleEditorTab(self.module_editor_frame)

        self.phone_lookup = PhoneLookupTab(self.phone_lookup_frame)


def main():
    root = tk.Tk()
    instance = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
