from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


class LeadGeneratorApp(App):
    def build(self):
        self.title = "Laplead.com - X Automated Lead Generator"

        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=12)

        # Header
        header_label = Label(
            text="X Automated Lead Generator",
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.1),
        )
        main_layout.add_widget(header_label)

        # Status Label
        self.status_label = Label(
            text="Status: Off",
            font_size='14sp',
            size_hint=(1, 0.1)
        )
        main_layout.add_widget(self.status_label)

        # Power Button
        self.power_button = Button(
            text="Power On",
            size_hint=(1, 0.1),
            on_press=self.toggle_on
        )
        main_layout.add_widget(self.power_button)

        # DM Template
        dm_template_label = Label(
            text="DM Message Template (Use {name} to personalize):",
            size_hint=(1, 0.05),
            halign='left',
            text_size=(None, None), # Allow the label to expand horizontally
            padding=(20, 0, 0, 0)  # Increase top margin by 20 pixels
        )
        main_layout.add_widget(dm_template_label)

        self.dm_template_input = TextInput(
            multiline=True,
            size_hint=(1, 0.2),
            text="Default DM Template"
        )
        main_layout.add_widget(self.dm_template_input)

        save_dm_button = Button(
            text="Save Template",
            size_hint=(1, 0.1),
            on_press=self.save_dm_template
        )
        main_layout.add_widget(save_dm_button)

        # Keywords
        keyword_label = Label(
            text="Enter Keywords (comma-separated):",
            font_size='14sp',
            size_hint=(1, 0.05)
        )
        main_layout.add_widget(keyword_label)

        self.keyword_input = TextInput(
            size_hint=(1, 0.1),
            text=""
        )
        main_layout.add_widget(self.keyword_input)

        save_keywords_button = Button(
            text="Save Keywords",
            size_hint=(1, 0.1),
            on_press=self.save_keywords
        )
        main_layout.add_widget(save_keywords_button)

        # Usernames
        username_label = Label(
            text="Enter Usernames (comma-separated):",
            font_size='14sp',
            size_hint=(1, 0.05)
        )
        main_layout.add_widget(username_label)

        self.username_input = TextInput(
            size_hint=(1, 0.1),
            text=""
        )
        main_layout.add_widget(self.username_input)

        save_usernames_button = Button(
            text="Update Usernames in Queue",
            size_hint=(1, 0.1),
            on_press=self.save_usernames
        )
        main_layout.add_widget(save_usernames_button)

        # Analytics Table (Mocked with TreeView for simplicity)
        analytics_label = Label(
            text="Total Daily DMs Sent:",
            font_size='14sp',
            size_hint=(1, 0.05)
        )
        main_layout.add_widget(analytics_label)

        analytics_view = ScrollView(size_hint=(1, 0.2))
        self.analytics_tree = TreeView()

        # Add sample analytics data
        for date, count in [("2024-06-01", "50"), ("2024-06-02", "65"), ("2024-06-03", "70")]:
            node = self.analytics_tree.add_node(TreeViewLabel(text=f"{date}: {count} DMs Sent"))

        analytics_view.add_widget(self.analytics_tree)
        main_layout.add_widget(analytics_view)

        return main_layout

    def toggle_on(self, instance):
        if self.status_label.text == "Status: Off":
            self.status_label.text = "Status: On"
            self.power_button.text = "Power Off"
        else:
            self.status_label.text = "Status: Off"
            self.power_button.text = "Power On"

    def save_dm_template(self, instance):
        template = self.dm_template_input.text
        popup = Popup(title='Template Saved',
                      content=Label(text=f"DM Template saved:\n{template}"),
                      size_hint=(0.6, 0.4))
        popup.open()

    def save_keywords(self, instance):
        keywords = self.keyword_input.text
        popup = Popup(title='Keywords Saved',
                      content=Label(text=f"Keywords saved:\n{keywords}"),
                      size_hint=(0.6, 0.4))
        popup.open()

    def save_usernames(self, instance):
        usernames = self.username_input.text
        popup = Popup(title='Usernames Saved',
                      content=Label(text=f"Usernames saved:\n{usernames}"),
                      size_hint=(0.6, 0.4))
        popup.open()


if __name__ == '__main__':
    LeadGeneratorApp().run()
