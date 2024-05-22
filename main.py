
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from task import Task

from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission 
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

#list of Task objects
tasks_list = []
#directory of "tab name": TaskLayout object
tasks_layouts = {}
#list of tabs objects
tabs_list = []

store = JsonStore("todolist_data.json")

class MainApp(App):

    def build(self):
        self.window = MainWindow()
        self.window.load_tabs()
        
        return self.window

                
    
    
class MainWindow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #set up default Daily tab
        tasks_layouts.update({"Daily": GridLayout(cols= 3, size_hint= (1, None), padding= 40, spacing= 10)})
        tasks_layouts["Daily"].bind(minimum_height=tasks_layouts["Daily"].setter("height"))
        self.tabs.default_tab_content = TabLayout()
        #synchronize global task_list with tabs widget (TabbedPanel)
        tabs_list.extend(self.tabs.tab_list)

    def tabs_popup(self):
        manager = Popup(title = "Tabs manager", size_hint = (.8, .8))

        manager_content= GridLayout(cols= 1, padding= (10,10), spacing= (10,10))

        add_button = Button(text= "+", font_size= 90, size_hint= (1, .2), background_normal="", background_color= [.349, .451, .639, 1])
        add_button.bind(on_press= self.add_tab)
        add_button.bind(on_press= manager.dismiss)

        manager_content.add_widget(add_button)
        manager_content.add_widget(Button(text= "Close", font_size= 50, size_hint= (1, .2), background_normal="", background_color= [.349, .451, .639, 1], on_press= manager.dismiss))
        manager_content.add_widget(Label(text= "Click on tab to remove it", font_size= 40, size_hint= (1, .1)))

        #add all tabs other than Daily
        for x in self.tabs.tab_list:
            if x.text != "Daily":
                tab_button = Button(text=x.text, font_size= 50, size_hint= (1, .2))
                tab_button.bind(on_press= self.remove_tab)
                tab_button.bind(on_press= manager.dismiss)               
                manager_content.add_widget(tab_button)
            else:
                pass
        manager.content = manager_content
        manager.open()

    #popup to insert new tab name
    def add_tab(self, instance):
        create = Popup(title= "Insert new tab name", size_hint= (1, .2))
        name = TextInput(multiline= False, font_size= 50)
        name.bind(on_text_validate= self.create_tab)
        name.bind(on_text_validate= create.dismiss)
        create.content= name
        create.open()

        

    def remove_tab(self, instance):
        tab_to_remove = next(x for x in self.tabs.tab_list if x.text == instance.text)
        self.tabs.remove_widget(tab_to_remove)
        tabs_list.remove(tab_to_remove)
        tasks_layouts.pop(tab_to_remove.text)
        for x in tasks_list:
            if x.tab == tab_to_remove.text:
                store.delete(x.content)
            else:
                pass

    def create_tab(self, instance):
        #not empty
        if instance.text.strip() != "":
            #different names
            for x in self.tabs.tab_list:
                if x.text == instance.text:
                    break
                else:
                    pass
            if x.text == instance.text:
                pass
            else:
                tab = TabbedPanelItem(text= instance.text)

                tasks_layouts.update({instance.text: GridLayout(cols= 3, size_hint= (1, None), padding= 40, spacing= 10)})
                tasks_layouts[instance.text].bind(minimum_height=tasks_layouts[instance.text].setter("height"))

                tab.content = (TabLayout())
                self.tabs.add_widget(tab)

                tabs_list.append(tab)
        else:
            pass

    def load_tabs(self):
        keys = store.store_keys()

        for k in keys:
            if store.get(k)["tab"] != "Daily":
                
                tab = TabbedPanelItem(text= store.get(k)["tab"])

                for x in tabs_list:
                    if x.text == tab.text:
                        break
                    else:
                        pass

                if x.text == tab.text:
                    pass
                else:
                    tasks_layouts.update({store.get(k)["tab"]: GridLayout(cols= 3, size_hint= (1, None), padding= 40, spacing= 10)})
                    tasks_layouts[store.get(k)["tab"]].bind(minimum_height=tasks_layouts[store.get(k)["tab"]].setter("height"))

                    tab.content = (TabLayout())
                    self.tabs.add_widget(tab)

                    tabs_list.append(tab)
            else:
                pass
        
        tabs_list[0].content.load_tasks()




class TabLayout(BoxLayout):
    
    def __init__(self):
        super(TabLayout, self).__init__()
        self.scroll.add_widget(tasks_layouts[list(tasks_layouts)[-1]])

    def add_task(self, instance):
        tab = next(x for x in tabs_list if x.content == instance.parent.parent.parent)

        if self.text_in.text.strip() != "":
            checkbox_to_add = CheckBox(size_hint=(.05, None), state="normal")
            checkbox_to_add.bind(active= self.change_task_state)
            tasks_list.append(Task(self.text_in.text,
                                tab.text,
                                checkbox_to_add, 
                                Button(text= self.text_in.text , size_hint= (.85, None), background_normal= "img/btn_normal.png", background_down= "img/btn_down.png", border=(50,50,50,50), background_color = [.8,.8,.8,1], color= [1,1,1,1], font_size= 50, on_press= self.change_task_color), 
                                Button(text="-", font_size= 90, size_hint=(.1, None), background_normal= "img/transparent_btn.png", background_down= "img/transparent_btn.png", border=(10,10,10,10), on_press= self.remove_task))
                                    )
            
            tasks_layouts[tab.text].add_widget(tasks_list[-1].checkbox)
            tasks_layouts[tab.text].add_widget(tasks_list[-1].label)
            tasks_layouts[tab.text].add_widget(tasks_list[-1].button)

            store.put(self.text_in.text, state="notdone", color=[1,1,1,1], tab=tab.text)

            self.text_in.text=""
        else:
            pass

    def remove_task(self, instance):
        tab = next(x for x in tabs_list if x.content == instance.parent.parent.parent.parent.parent)
        task = next(x for x in tasks_list if instance == x.button)

        tasks_layouts[tab.text].remove_widget(task.checkbox)
        tasks_layouts[tab.text].remove_widget(task.label)
        tasks_layouts[tab.text].remove_widget(task.button)
        tasks_list.remove(task)

        store.delete(task.content)

    def change_task_state(self, instance, value):
        task = next(x for x in tasks_list if instance == x.checkbox)
            
        if value:
            task.label.color = [0,1,0,1]
            task.label.background_color = [.4,1,.4,1]
            store.put(task.content, state="done", color= store.get(task.content)["color"], tab= store.get(task.content)["tab"])
        else:
            task.label.color = store.get(task.content)["color"]
            task.label.background_color = [.8,.8,.8,1]
            store.put(task.content, state="notdone", color= store.get(task.content)["color"], tab= store.get(task.content)["tab"])


    def change_task_color(self, instance):
        task = next(x for x in tasks_list if instance == x.label)

        if task.checkbox.state == "normal":
            if task.label.color == [1,1,1,1]:
                task.label.color = [1,0,0,1] #red
                store.put(task.content, state= store.get(task.content)["state"], color= [1,0,0,1], tab= store.get(task.content)["tab"])
            elif task.label.color == [1,0,0,1]:
                task.label.color = [1,.8,0,1] #orange
                store.put(task.content, state= store.get(task.content)["state"], color= [1,.8,0,1], tab= store.get(task.content)["tab"])
            elif task.label.color == [1,.8,0,1]:
                task.label.color = [1,.5,.8,1] #pink
                store.put(task.content, state= store.get(task.content)["state"], color= [1,.5,.8,1], tab= store.get(task.content)["tab"])
            elif task.label.color == [1,.5,.8,1]:
                task.label.color = [0,1,1,1] #blue
                store.put(task.content, state= store.get(task.content)["state"], color= [0,1,1,1], tab= store.get(task.content)["tab"])
            else:
                task.label.color = [1,1,1,1]
                store.put(task.content, state= store.get(task.content)["state"], color= [1,1,1,1], tab= store.get(task.content)["tab"])


    def load_tasks(self):
        keys = store.store_keys()
   
        for k in keys:

            if store.get(k)["state"] == "done":
                checkbox_to_add = CheckBox(size_hint=(.05, None), state="down")
                checkbox_to_add.bind(active= self.change_task_state)
                tasks_list.append(Task(k,
                                    store.get(k)["tab"],
                                    checkbox_to_add, 
                                    Button(text= k , size_hint= (.85, None), background_normal= "img/btn_normal.png", background_down= "img/btn_down.png", border=(50,50,50,50), background_color = [.4,1,.4,1], color= [0,1,0,1], font_size= 50, on_press= self.change_task_color), 
                                    Button(text="-", font_size= 90, size_hint=(.1, None), background_normal= "img/transparent_btn.png", background_down= "img/transparent_btn.png", border=(10,10,10,10), on_press= self.remove_task))
                                        )
                tasks_layouts[store.get(k)["tab"]].add_widget(tasks_list[-1].checkbox)
                tasks_layouts[store.get(k)["tab"]].add_widget(tasks_list[-1].label)
                tasks_layouts[store.get(k)["tab"]].add_widget(tasks_list[-1].button)
            else:
                checkbox_to_add = CheckBox(size_hint=(.05, None))
                checkbox_to_add.bind(active= self.change_task_state)
                tasks_list.append(Task(k,
                                    store.get(k)["tab"],
                                    checkbox_to_add, 
                                    Button(text= k , size_hint= (.85, None), background_normal= "img/btn_normal.png", background_down= "img/btn_down.png", border=(50,50,50,50), background_color = [.8,.8,.8,1], color= store.get(k)["color"], font_size= 50, on_press= self.change_task_color), 
                                    Button(text="-", font_size= 90, size_hint=(.1, None), background_normal= "img/transparent_btn.png", background_down= "img/transparent_btn.png", border=(10,10,10,10), on_press= self.remove_task))
                                        )
                tasks_layouts[store.get(k)["tab"]].add_widget(tasks_list[-1].checkbox)
                tasks_layouts[store.get(k)["tab"]].add_widget(tasks_list[-1].label)
                tasks_layouts[store.get(k)["tab"]].add_widget(tasks_list[-1].button)



       


if __name__ == "__main__":
    app = MainApp()
    app.run()