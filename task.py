
from dataclasses import dataclass, field
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox

@dataclass
class Task:
    content: str
    tab: str

    checkbox: CheckBox = field(repr=False)
    label: Label = field(repr=False)
    button: Button = field(repr=False)
