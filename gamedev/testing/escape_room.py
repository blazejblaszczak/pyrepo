class GameObject:

    def __init__(self, name, appearance, feel, smell):
        self.name = name
        self.appearance = appearance
        self.feel = feel
        self.smell = smell


    def look(self):
        return f"You look at the {self.name}. {self.appearance}\n"
    

    def touch(self):
        return f"You touch the {self.name}. {self.feel}\n"


    def sniff(self):
        return f"You sniff the {self.name}. {self.smell}\n"
    

class Room:

    escape_code = 0
    game_objects = []

    def __init__(self, escape_code, game_objects):
        self.escape_code = escape_code
        self.game_objects = game_objects


    def check_code(self, code):
        return self.escape_code == code
    

    def get_game_object_names(self):
        names = []
        for object in self.game_objects:
            names.append(object.name)
        return names
    

class Game:

    def __init__(self):
        self.attempts = 0
        self.objects = self.create_objects()
        self.room = Room(731, self.objects)


    def create_objects(self):
        return[
            GameObject("Sweater",
                          "It's a blue sweater that had the number 12 stitched on it.",
                          "Someone had unstitched the second number, leaving only 1.",
                          "The sweater smells of laundry detergent."),
            GameObject("Chair",
                          "It's a wooden chair with only 3 legs.",
                          "Someone had deliberately snapped off one of the legs.",
                          "It smells like old wood."),
            GameObject("Journal",
                          "The final entry states that time should be hours then minutes then seconds (H-M-S).",
                          "The cover is worn and several pages are missing.",
                          "It smells like musty leather."),
            GameObject("Bowl of soup",
                          "It appears to be tomato soup.",
                          "It has cooled down to room temperature.",
                          "You detect 7 differenct herbs and spices."),
            GameObject("Clock",
                          "The hour hand is pointing towards the soup, the minute hand towards the chair, and the second hand towards the sweater.",
                          "The battery compartment is open and empty.",
                          "It smells of plastic.")
        ]
    

    def take_turn(self):
        prompt = self.get_room_prompt()
        selection = int(input(prompt))
        if selection >= 1 and selection <= 5:
            self.select_object(selection - 1)
            self.take_turn()
        else:
            is_code_correct = self.guess_code(selection)
            if is_code_correct:
                print("Congatulations, you won!")
            else:
                if self.attempts == 3:
                    print("Game over, you ran out of guesses. Better luck next time!")
                else:
                    print(f"Incorrect, you have used {self.attempts}/3 attempts")
                    self.take_turn()


    def get_room_prompt(self):
        prompt = "Enter the 3 digit lock code or choose an item to interact with:\n"
        names = self.room.get_game_object_names()
        index = 1
        for name in names:
            prompt += f"{index}. {name}\n"
            index += 1
        return prompt
    

    def select_object(self, index):
        selected_object = self.room.game_objects[index]
        prompt = self.get_object_interaction_string(selected_object.name)
        interaction = input(prompt)
        clue = self.interact_with_object(selected_object, interaction)
        print(clue)
    

    def get_object_interaction_string(self, name):
        return f"How do you want to interact with {name}?\n1. Look\n2. Touch\n3. Smell\n"
    

    def interact_with_object(self, object, interaction):
        if interaction == "1":
            return object.look()
        elif interaction == "2":
            return object.touch()
        elif interaction == "3":
            return object.sniff()
        return ""
    

    def guess_code(self, code):
        if self.room.check_code(code):
            return True
        else:
            self.attempts += 1
            return False

    
if __name__ == "__main__":
    
    game = Game()
    game.take_turn()


# TESTING

# class RoomTests:

#     def __init__(self):
#         self.room_1 = Room(111, [
#             GameObject("Sweater",
#                           "It's a blue sweater that had the number 12 stitched on it.",
#                           "Someone had unstitched the second number, leaving only 1.",
#                           "The sweater smells of laundry detergent."),
#             GameObject("Chair",
#                           "It's a wooden chair with only 3 legs.",
#                           "Someone had deliberately snapped off one of the legs.",
#                           "It smells like old wood.")
#         ])
#         self.room_2 = Room(222, [])


#     def test_check_code(self):
#         print(self.room_1.check_code(111) == True)
#         print(self.room_1.check_code(222) == False)


#     def test_get_game_object_names(self):
#         print(self.room_1.get_game_object_names() == ["Sweater", "Chair"])
#         print(self.room_2.get_game_object_names() == [])


# tests = RoomTests()
# # tests.test_check_code()
# tests.test_get_game_object_names()
