import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from tkinter.scrolledtext import ScrolledText
from googlesearch import search

class CustomTkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PMT Assistant")
        self.root.geometry("700x400")
        self.root.configure(bg="#f0f0f0")  # Set background color for the root window

        # Custom off-white theme settings
        self.style = ttk.Style()
        self.style.theme_create("offwhite", parent="clam", settings={
            "TLabel": {"configure": {"foreground": "#333333", "background": "#f0f0f0", "font": ('Helvetica', 14)}},
            "TFrame": {"configure": {"background": "#f0f0f0"}},
            "TEntry": {
                "configure": {"foreground": "#333333", "background": "#ffffff", "font": ('Helvetica', 14), "width": 30,
                              "padding": 5}},
            "TButton": {
                "configure": {"foreground": "#ffffff", "background": "#004d99", "font": ('Helvetica', 14, 'bold'),
                              "width": 10, "justify": 'center'},
                "map": {
                    "background": [("active", "#003366")],
                    "foreground": [("active", "#ffffff")]
                }
            },
            "TCheckbutton": {
                "configure": {"foreground": "#333333", "background": "#f0f0f0", "font": ('Helvetica', 14),
                              "indicatoron": False},
                "map": {
                    "background": [("selected", "#333333")],
                    "foreground": [("selected", "#ffffff")]
                }
            },
            "TCombobox": {"configure": {"foreground": "#333333", "background": "#ffffff", "font": ('Helvetica', 14)}},
            "Vertical.TScrollbar": {"configure": {"background": "#ffffff"}},
            "Horizontal.TScrollbar": {"configure": {"background": "#ffffff"}}
        })
        self.style.theme_use("offwhite")

        # Main frame to hold all components
        self.main_frame = ttk.Frame(self.root, padding=(20, 10))
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # First row: Dropdown and Text Input
        self.create_dropdown_and_input()

        # Second row: Action Button
        self.create_action_button()

        # Third row: Output Text Box, Copy Button, and Reset Button
        self.create_output_textbox_with_copy()

    def create_dropdown_and_input(self):
        frame = ttk.Frame(self.main_frame, padding=(0, 10))
        frame.pack(fill=tk.X)

        # Dropdown
        ttk.Label(frame, text="Task ").pack(side=tk.LEFT, padx=(0, 5))
        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(frame, textvariable=self.dropdown_var,
                                     values=["Headings", "Download Images", "SERP"])
        self.dropdown.pack(side=tk.LEFT, ipady=6, ipadx=25)

        # Text Input
        ttk.Label(frame, text="       URL/KW ").pack(side=tk.LEFT)
        self.text_input = ttk.Entry(frame)
        self.text_input.pack(side=tk.LEFT, ipadx=70, ipady=6)  # Increase input box height

    def create_action_button(self):
        frame = ttk.Frame(self.main_frame, padding=(0, 10))
        frame.pack(fill=tk.X)
        self.action_button = ttk.Button(frame, text="     Action", style="CopyButton.TButton", command=self.action)
        self.action_button.pack(side=tk.BOTTOM)

    def create_output_textbox_with_copy(self):
        frame = ttk.Frame(self.main_frame, padding=(0, 10))
        frame.pack(fill=tk.BOTH, expand=True)

        # Output Text Box
        ttk.Label(frame, text="Output:").pack(side=tk.TOP, anchor=tk.W)
        self.output_text = ScrolledText(frame, height=10, width=50, bg="#ffffff", fg="#333333", wrap=tk.WORD,
                                        state='disabled')
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Button Frame for Copy and Reset Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(10, 0))

        # Copy Button with hover effect
        copy_button = ttk.Button(button_frame, text="     Copy", style="CopyButton.TButton", command=self.copy_output)
        copy_button.pack(side=tk.LEFT, padx=(0, 10))

        # Reset Button
        reset_button = ttk.Button(button_frame, text="     Reset", style="ResetButton.TButton",
                                  command=self.reset_output)
        reset_button.pack(side=tk.LEFT, padx=(0, 10))

        # Style configuration for Copy Button
        self.style.configure("CopyButton.TButton", font=('Helvetica', 14, 'bold'), foreground="#ffffff",
                             background="#004d99")
        self.style.map("CopyButton.TButton", foreground=[("active", "#ffffff")], background=[("active", "#003366")])

        # Style configuration for Reset Button
        self.style.configure("ResetButton.TButton", font=('Helvetica', 14, 'bold'), foreground="#ffffff",
                             background="#ff6347")
        self.style.map("ResetButton.TButton", foreground=[("active", "#ffffff")], background=[("active", "#d32f2f")])

    def copy_output(self):
        self.output_text.config(state='normal')
        output_text = self.output_text.get("1.0", tk.END).strip()
        self.output_text.config(state='disabled')
        self.root.clipboard_clear()
        self.root.clipboard_append(output_text)
        messagebox.showinfo("Copied", "Output copied to clipboard!")

    def reset_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state='disabled')

    def download_image(self, img_url, folder_path):
        try:
            img_data = requests.get(img_url).content
            img_name = os.path.basename(img_url)
            img_path = os.path.join(folder_path, img_name)
            with open(img_path, 'wb') as img_file:
                img_file.write(img_data)
            self.output_text.config(state='normal')
            self.output_text.insert(tk.END, f"Downloaded {img_url} to {img_path}\n")
            self.output_text.config(state='disabled')
        except Exception as e:
            self.output_text.config(state='normal')
            self.output_text.insert(tk.END, f"Could not download {img_url}. Error: {e}\n")
            self.output_text.config(state='disabled')

    # Function to find all image URLs from a webpage
    def find_image_urls(self, page_url):
        try:
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            img_urls = [urljoin(page_url, img['src']) for img in img_tags if 'src' in img.attrs]
            return img_urls
        except Exception as e:
            self.output_text.config(state='normal')
            self.output_text.insert(tk.END, f"Could not retrieve image URLs from {page_url}. Error: {e}\n")
            self.output_text.config(state='disabled')
            return []

    def get_headings(self, page_url):
        try:
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            headings = ""
            for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                headings += f"{tag.name.upper()}: {tag.text.strip()}\n"
            return headings
        except Exception as e:
            return f"Could not retrieve headings from {page_url}. Error: {e}"


    def get_serp(self, keyword):
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(keyword)}"
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            serp_links = []
            for link in links:
                href = link['href']
                if "url?q=" in href and not "webcache" in href:
                    serp_links.append(href.split("?q=")[1].split("&sa=U")[0])
            return "\n".join(serp_links[:15])
        except Exception as e:
            return f"Could not retrieve SERP results for {keyword}. Error: {e}"

    # Main function to handle actions based on dropdown selection
    def action(self):
        #action_button_text = self.action_button.cget("text")
        self.action_button.config(text="Processing")
        self.root.update_idletasks()
        task = self.dropdown_var.get()
        input_text = self.text_input.get()

        if task == "Headings":
            self.output_text.config(state='normal')
            self.output_text.delete("1.0", tk.END)
            headings = self.get_headings(input_text)
            self.output_text.insert(tk.END, headings)
            self.output_text.config(state='disabled')
        elif task == "Download Images":
            self.output_text.config(state='normal')
            self.output_text.delete("1.0", tk.END)
            folder_path = os.path.join(os.path.expanduser("~"), "Desktop", "PMT Assistant")
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            img_urls = self.find_image_urls(input_text)
            for img_url in img_urls:
                self.download_image(img_url, folder_path)
            self.output_text.config(state='disabled')
        elif task == "SERP":
            self.output_text.config(state='normal')
            self.output_text.delete("1.0", tk.END)
            serp_result =''
            num_links = 10
            try:
                # Perform a Google search and get the top links
                links = list(search(input_text, num_results=num_links))

                # Print the top links
                print(f"Top {num_links} links for '{input_text}':")
                for index, link in enumerate(links, start=1):
                    serp_result=serp_result+(f"{index}. {link}")+'\n'

            except Exception as e:
                messagebox.showerror(f"Could not retrieve SERP results for {input_text}. Error: {e}")
            #serp_results = self.get_serp(input_text)
            self.output_text.insert(tk.END, serp_result)
            self.output_text.config(state='disabled')
        else:
            messagebox.showerror("Error", "Please select a task from the dropdown.")
        self.action_button.config(text="     Action")
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = CustomTkinterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
