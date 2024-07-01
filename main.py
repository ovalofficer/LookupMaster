import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText

import json
import webbrowser
import helpers
import os

'''

LookupMaster 

OSINT tool for looking up names, usernames, phone numbers, e-mails, and more with a simple and user-friendly GUI.

'''


class MenuTab:

    def __init__(self, root, module_name=None):
        self.main_frame = root
        self.module_data = None
        self.module_name = module_name

        self.refresh_module_data()

    def refresh_module_data(self):
        self.module_data = self.load_module_file()

    def load_module_file(self) -> dict[str, dict[str, str]]:

        # This is currently for the module editor tab but may be used in the future. Wish to remove the os dependency
        if self.module_name is None:
            return_dict = {}
            for root, dirs, files in os.walk('modules'):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    with open(file_path) as f:
                        # split at the . and lower() to get just a plain filename
                        return_dict[filename.split('.')[0].lower()] = json.loads(f.read())

            # Remove mutator dict -- it isn't formatted like the others and can't be viewed yet with module editor
            return_dict.pop('mutator')

            # print(return_dict)

            return return_dict

        with open(f'modules/{self.module_name}.json') as f:
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
        ttk.Entry(self.main_frame, width=32, textvariable=self.url_var).grid(column=1, row=1, pady=5, padx=10,
                                                                             columnspan=3, sticky='we')

        self.mask_var = tk.StringVar()
        ttk.Entry(self.main_frame, width=32, textvariable=self.mask_var).grid(column=1, row=2, pady=5, padx=10,
                                                                              columnspan=3, sticky='we')

        self.api_key_var = tk.StringVar()
        ttk.Entry(self.main_frame, width=32, textvariable=self.api_key_var).grid(column=1, row=3, pady=5, padx=10,
                                                                                 columnspan=3, sticky='we')

        self.captcha_var = tk.StringVar()
        ttk.Checkbutton(self.main_frame, variable=self.captcha_var, onvalue='True', offvalue='False').grid(
            column=1, row=4, sticky='w', pady=2, padx=10)

        ttk.Button(self.main_frame, text='Save Module File', command=self.save_module_file).grid(column=2, row=4,
                                                                                                 sticky='w')
        ttk.Button(self.main_frame, text='Add New Module').grid(column=2, row=4, sticky='e')

        self.update_main_listbox()

    def update_main_listbox(self):
        self.main_listbox.delete(0, END)
        for k, v in self.module_data.items():
            for title in v.keys():
                self.main_listbox.insert(END, k + '.json | ' + title)

    def verify_overwrite(self) -> bool:
        return mb.askokcancel(title='Confirm Overwrite',
                              message='Doing this will overwrite current module file. Continue?',
                              icon='warning')

    def save_module_file(self):
        # with open(self.get_current_item_category() + '.json', 'w') as f:
        self.set_current_selection_attribute('url', self.url_var.get())
        self.set_current_selection_attribute('mask', self.mask_var.get())
        self.set_current_selection_attribute('api-key', self.api_key_var.get())
        self.set_current_selection_attribute('captcha', self.captcha_var.get())

        if self.verify_overwrite():
            # with open(self.get_current_item_category(), 'w') as f:
            #     f.write(json.dumps(self.module_data, indent=2))
            print(json.dumps(self.module_data, indent=2))
            self.refresh_module_data()
            self.update_main_listbox()

    def set_current_selection_attribute(self, attr: str, value: str):
        self.module_data[self.get_current_item_category()][self.get_current_item_title()][attr] = value

    def listbox_item_selected(self):
        item_values = self.get_current_item_values()

        self.url_var.set(item_values['url'])
        self.mask_var.set(item_values['mask'])
        self.api_key_var.set(item_values['api-key'])
        self.captcha_var.set(item_values['captcha'])

    def get_current_selection(self):
        if not self.main_listbox.curselection():
            return ''
        else:
            return self.main_listbox.get(self.main_listbox.curselection())

    def get_current_item_category(self):
        return self.get_current_selection().split('.', 1)[0].lower()

    def get_current_item_title(self):
        return self.get_current_selection().split(' ')[2]

    def get_current_item_values(self):
        return self.module_data[self.get_current_item_category()][self.get_current_item_title()]


class PermutationTab(MenuTab):

    def __init__(self, root):
        super().__init__(root, 'mutator')

        self.main_frame.grid_columnconfigure(2, weight=2)

        # First name entry
        ttk.Label(self.main_frame, text='First Name:').grid(column=0, row=1, pady=2)

        self.first_name_var = tk.StringVar()
        self.first_name_entry = ttk.Entry(self.main_frame, textvariable=self.first_name_var)
        self.first_name_entry.grid(column=1, row=1, sticky='we', columnspan=2)

        # Middle name entry
        ttk.Label(self.main_frame, text='Middle Name:').grid(column=0, row=2, pady=2)

        self.middle_name_var = tk.StringVar()
        self.middle_name_entry = ttk.Entry(self.main_frame, textvariable=self.middle_name_var)
        self.middle_name_entry.grid(column=1, row=2, sticky='we', columnspan=2)

        # Last name entry
        ttk.Label(self.main_frame, text='Last Name:').grid(column=0, row=3, pady=2)

        self.last_name_var = tk.StringVar()
        self.last_name_entry = ttk.Entry(self.main_frame, textvariable=self.last_name_var)
        self.last_name_entry.grid(column=1, row=3, sticky='we', columnspan=2)

        ttk.Label(self.main_frame, text='Domain:').grid(column=0, row=4, pady=2)

        self.domain_var = tk.StringVar()
        self.domain_entry = ttk.Entry(self.main_frame, textvariable=self.domain_var)
        self.domain_entry.grid(column=1, row=4, sticky='we', columnspan=2)

        self.mode_var = tk.StringVar(value='email')

        self.email_radiobutton = ttk.Radiobutton(self.main_frame, text='E-Mail', variable=self.mode_var, value='email')
        self.email_radiobutton.grid(column=1, row=0, sticky='w')

        self.extended_email_radiobutton = ttk.Radiobutton(self.main_frame, text='Extended E-Mail',
                                                          variable=self.mode_var, value='email-extended')
        self.extended_email_radiobutton.grid(column=1, row=0, sticky='n', columnspan=2)

        self.username_radiobutton = ttk.Radiobutton(self.main_frame, text='Username', variable=self.mode_var,
                                                    value='username')
        self.username_radiobutton.grid(column=1, row=5, sticky='w')

        ttk.Label(self.main_frame, text='Username:').grid(column=0, row=6, pady=2)

        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var)
        self.username_entry.grid(column=1, row=6, sticky='we', columnspan=2)

        ttk.Separator(self.main_frame, orient='horizontal').grid(sticky='we', pady=10, columnspan=3, row=7)

        ttk.Label(self.main_frame, text='Numbers of Interest:\n'
                                        '( - ) denotes range\n'
                                        'e.g. "1-4" = 1, 2, 3, 4').grid(column=0, row=8, pady=2)

        self.noi_textbox = ScrolledText(self.main_frame, height=10, width=32, font=('Helvetica', 10))
        self.noi_textbox.grid(column=1, row=8)

        # optional textbox entry for numbers of interest
        # optional email domain entry

        # checkboxes for allowed characters in permutation ( ., -, _ )
        # box for numbers specifically to go onto end
        # option to generate incremental numbers on end or as numbers of interest within specified range

        ttk.Button(self.main_frame, text='Generate Permutations', command=self.create_results_popup).grid(
            column=0, columnspan=3, pady=10, sticky='we')

        self.first_name_var.set(value='John')
        self.last_name_var.set(value='Smith')
        self.domain_var.set(value='gmail.com')

    def get_noi(self) -> list[str]:
        # print(list(x for x in self.noi_textbox.get('1.0', END).strip().split('\n') if x != ''))
        # generator for textbox to remove lines that are only whitespace and trailing spaces
        return list(x for x in self.noi_textbox.get('1.0', END).strip().split('\n') if x != '')

    def create_results_popup(self):

        t = tk.Toplevel()
        t.geometry('250x325')
        t.title('Generated Permutations')
        t.columnconfigure(0, weight=1)
        t.resizable(False, False)
        t.grid()

        frame = ttk.Frame(t, borderwidth=5, relief='solid', padding=5)
        frame.grid(sticky='nswe')

        perms = self.generate_permutations()

        ttk.Label(frame, text=f'{len(perms)} permutations').grid()
        results_box = ScrolledText(frame, height=16, width=30, font=('Helvetica', 10))
        results_box.grid()

        for p in perms:
            results_box.insert(END, p + '\n')

        ttk.Button(frame, text='Save to File',
                   command=lambda: self.save_permutations_to_file(results_box.get('1.0', END))).grid(pady=5,
                                                                                                     sticky='we')

    def save_permutations_to_file(self, results: str):

        file_types = (('Text files', '*.txt'),
                      ('All files', '*.*'))

        # Starts save as dialog
        f = fd.asksaveasfile(mode='w', defaultextension='.txt', filetypes=file_types)

        # Returns none if dialog is cancelled
        if f is None:
            return

        # Write result data to the file
        f.write(results.strip())

        # Close file
        f.close()

    def generate_permutations(self):
        if self.mode_var.get() == 'username':
            return self.generate_username_permutations()
        elif self.mode_var.get() == 'email' or self.mode_var.get() == 'email-extended':
            return self.generate_email_permutations()

    def generate_email_permutations(self) -> list[str]:
        noi = helpers.interpret_noi(self.get_noi())
        masks = self.module_data[self.mode_var.get()]
        return helpers.generate_email_permutations(self.first_name_var.get(), self.middle_name_var.get(),
                                                   self.last_name_var.get(), self.domain_var.get(), noi, masks)

    def generate_username_permutations(self) -> list[str]:
        noi = helpers.interpret_noi(self.get_noi())
        masks = self.module_data[self.mode_var.get()]
        return helpers.generate_username_permutations(self.username_var.get(), noi, masks)


class PhoneLookupTab(MenuTab):
    def __init__(self, root):
        super().__init__(root, 'phone')

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

        for n, d in self.module_data.items():
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
                print(target['url'] + helpers.translate_phone_mask(target['mask'][0], target['mask'][1],
                                                                   self.get_sanitized_number()))

            # ugly one-liner but does what I want it to -- find better solution for dynamic button placement
            column = 0 if button_counter < 10 else 1
            button_counter += 1

            # Have to add to grid after, otherwise .grid operation returns None
            self.buttons[n.lower()] = ttk.Button(self.main_frame, text=n + '*' if d['captcha'] == 'True' else n,
                                                 command=on_click)
            self.buttons[n.lower()].grid(sticky='ew', column=column, row=button_counter + 4, padx=10, pady=2)

            # Adds CAPTCHA text next to button when applicable
            # if d['captcha'] == 'True':
            #     ttk.Label(self.main_frame, text='CAPTCHA', foreground='red', font=('Helvetica', 12, 'bold')).grid(
            #         column=column + 1, sticky='nsew', row=button_counter + 3)


class UsernameLookupTab(MenuTab):
    def __init__(self, root):
        super().__init__(root, 'username')

        self.main_frame.grid_columnconfigure(1, weight=2)

        self.username_entry_label = ttk.Label(self.main_frame, text='Enter a Username (A-Z, 0-9, -, _)')
        self.username_entry_label.grid(pady=5, columnspan=2, sticky='n')

        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var, width=18, justify=tk.CENTER,
                                        font=('Helvetica', 12, 'bold'))
        self.username_entry.grid(pady=5, padx=10, columnspan=2, sticky='we')

        self.username_entry.bind('<Any-KeyRelease>', lambda x: [])

        self.buttons = {}

        self.create_buttons()

    def clear_buttons(self):
        for button in self.buttons.values():
            button.destroy()

    def create_buttons(self):
        self.clear_buttons()
        button_counter = 0

        for n, d in self.module_data.items():
            # print(n, d)

            # Have to create an on-click function for the button to use.
            def on_click(target=d):
                # print('Button Clicked')

                # Desired click operation goes here.
                # TODO: implement webbrowser to open a chrome tab. alternatively, implement scraping. add some way to
                #  configure scraped information in modules.json, then then offer option to save data to file or
                #  open in a TopLevel with a textbox
                print(target['url'] + target['mask'].replace('X', self.username_var.get()))

            # TODO: find better solution for dynamic button placement
            if button_counter > 20:
                column = 2
            elif button_counter > 10:
                column = 1
            else:
                column = 0

            button_counter += 1

            # Have to add to grid after, otherwise .grid operation returns None
            self.buttons[n.lower()] = ttk.Button(self.main_frame, text=n + '*' if d['captcha'] == 'True' else n,
                                                 command=on_click)
            self.buttons[n.lower()].grid(sticky='ew', column=column, row=button_counter + 3, padx=10, pady=2)


class App:

    def __init__(self, root):
        self.window = root
        self.window.title('Lookup Master')
        self.window.geometry('380x450')
        self.window.resizable(0, 0)
        self.window.grid_columnconfigure(0, weight=1)

        self.main_notebook = ttk.Notebook(self.window, padding=5)
        self.main_notebook.grid(sticky='nswe')

        self.username_lookup_frame = ttk.Frame(self.main_notebook)
        self.phone_lookup_frame = ttk.Frame(self.main_notebook)
        self.name_lookup_frame = ttk.Frame(self.main_notebook)
        self.module_editor_frame = ttk.Frame(self.main_notebook)
        self.permutation_frame = ttk.Frame(self.main_notebook)

        self.main_notebook.add(self.phone_lookup_frame, text='Phone')
        self.main_notebook.add(self.name_lookup_frame, text='Name')
        self.main_notebook.add(self.username_lookup_frame, text='Username')
        self.main_notebook.add(self.module_editor_frame, text='Module Editor')
        self.main_notebook.add(self.permutation_frame, text='Permutator')

        self.module_editor = ModuleEditorTab(self.module_editor_frame)

        self.phone_lookup = PhoneLookupTab(self.phone_lookup_frame)

        self.username_lookup = UsernameLookupTab(self.username_lookup_frame)

        self.permutator = PermutationTab(self.permutation_frame)


def main():
    root = tk.Tk()
    instance = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
