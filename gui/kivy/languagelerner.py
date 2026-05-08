from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.clock import Clock

from random import randint


Window.clearcolor = (1, 1, 1, 1)
Window.size = (400, 600)


class EndGameScreen(ModalView):
    final_score = NumericProperty(0)
    high_score = NumericProperty(0)


    def update_scores(self, final_score, high_score):
        self.final_score = final_score
        self.high_score = high_score


class ProgressBar(Widget):
    pass


class ImageBox(Widget):
    index = NumericProperty(0)
    image_name = StringProperty("")


    def get_image_path(self, image_name):
        return "images/" + image_name + ".png"


class GameScreen(Widget):
    correct_answer_index = NumericProperty(0)
    display_image_names = ListProperty([
        "bote",
        "diamante",
        "espada",
        "hacha"
    ])
    correct_answer_text = StringProperty("bote")
    bar_width = NumericProperty(0)

    answer_popup = Popup()
    item_names = [
        "bote",
        "diamante",
        "espada",
        "hacha",
        "ladrillos",
        "manzana",
        "pala",
        "pasto",
        "roca",
        "tierra"
    ]
    seconds = 0
    is_game_over = False
    score = 0
    high_score = 0


    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.load_new_question()


    def make_selection(self, index):
        if self.check_if_answer_correct(index):
            print("Correct")
            self.show_answer_popup(True)
        else:
            print("Incorrect")
            self.show_answer_popup(False)


    def check_if_answer_correct(self, index):
        if index == self.correct_answer_index:
            self.score += 1
            return True
        return False


    def get_random_image_names(self):
        temp_item_names = self.item_names.copy()
        items = []
        for _ in range(4):
            rand_index = randint(0,len(temp_item_names)-1)
            items.append(temp_item_names[rand_index])
            del temp_item_names[rand_index]
        return items


    def load_new_question(self, *args):
        self.display_image_names = self.get_random_image_names()
        self.correct_answer_index = randint(0,3)
        self.correct_answer_text = self.display_image_names[self.correct_answer_index]


    def show_end_game_popup(self):
        end_game_screen = EndGameScreen(
            size_hint=(.75,.6),
            auto_dismiss=False)
        end_game_screen.update_scores(self.score, self.high_score)
        end_game_screen.bind(on_dismiss=self.reset)
        end_game_screen.open()


    def show_answer_popup(self, is_correct):
        content = Image(source='images/' + self.correct_answer_text + '.png')

        self.answer_popup = Popup(
            title='Correct' if is_correct else 'Incorrect',
            size_hint=(.5, .4),
            content=content,
            title_align='center',
            title_color=(0,0,0,1),
            background='images/white.png'
        )
        self.answer_popup.bind(on_dismiss=self.load_new_question)
        self.answer_popup.open()


    def increase_bar_width(self, *args):
        if self.is_game_over:
            return
        width_increase = ((800 * .8) - 10) / 60
        self.bar_width += width_increase
        self.seconds += 1
        if self.seconds >= 60:
            self.execute_end_game()


    def execute_end_game(self):
        self.is_game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
        self.show_end_game_popup()
        

    def reset(self, *args):
        self.bar_width = 0
        self.is_game_over = False
        self.seconds = 0
        self.score = 0
        self.answer_popup.dismiss()
        self.load_new_question()


class LanguageLearnerApp(App):
    def build(self):
        game_screen = GameScreen()
        Clock.schedule_interval(game_screen.increase_bar_width, 60.0 / 60.0)
        return game_screen


if __name__ == '__main__':
    LanguageLearnerApp().run()
