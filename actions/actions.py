# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from typing import Any, Text, Dict, List

from utils.config import (CacheStore,
                          _get_recipe_details,
                          _search_recipes,
                          convert_to_text,
                          _get_ingredient_substitute,
                          _get_response_chatgpt
                          )

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


cache = CacheStore()

class ActionGetRecipe(Action):
    def name(self) -> Text:
        return "action_get_recipe"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = "What recipe would you like to cook? Choose appropriate option A to E."
        buttons = []

        try: 
            recipe_query = tracker.get_slot("recipename").strip()
            intolerances = tracker.get_slot("intolerances").strip()
            dietary_req = tracker.get_slot("dietary_req").strip()
            sort_type = tracker.get_slot("sort_type").strip()
            recipe_names = _search_recipes(recipe_query, intolerances, dietary_req, sort_type)

            cache.add_to_cache("recipe_names_list", recipe_names)

            recipe_display_list = ""
            for k, v in recipe_names.items():
                recipe_display_list += "\n" + (f"{k}: {v[0]} ")
            dispatcher.utter_message(message)
            dispatcher.utter_message(recipe_display_list)
            
        except Exception as e:
            print(f"ActionGetRecipe: Encountered exception in the code: {e}")
            dispatcher.utter_message("Sorry we couldn't find that recipe. Please try again")
        
        return []


class ActionSearchRecipe(Action):
    def name(self) -> Text:
        return "action_search_recipe"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        recipeid = tracker.get_slot("recipe_id")
        print("ActionSearchRecipe: Received Recipe id, ", recipeid)

        recipe_names_list = cache.get_from_cache("recipe_names_list")

        recipe_title, ingredient_list, equipments, instructions = _get_recipe_details(recipe_names_list[recipeid][1])

        if (recipe_title is None) or (len(ingredient_list) == 0) or (len(instructions) == 0):
            dispatcher.utter_message(text = "Sorry we are facing issues to find the details for this recipe\
                                    Please try again with different combination of recipes and preferences ")

        else: 
            dispatcher.utter_message(text = "Today we are making {} \n--------------\n".format(recipe_title))
            dispatcher.utter_message(text = "I'll list down the ingredients, equipments and instructions below as per your choice")

            cache.add_to_cache("recipe_title", recipe_title)
            cache.add_to_cache("ingredients_list", ingredient_list)
            cache.add_to_cache("equipments", equipments)
            cache.add_to_cache("instructions", instructions)
        
        return []
    

class ActionGetIngredients(Action):
    def name(self) -> Text:
        return "action_get_ingredients"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Here's the ingredient list")
        dispatcher.utter_message(text = "Ingredients: \n{} \n--------------\n".format(convert_to_text(cache.get_from_cache("ingredients_list"))))


class ActionGetEquipment(Action):
    def name(self) -> Text:
        return "action_get_equipment"
    print("In ActionGetEquipment")
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("Here's the equipment list")
        dispatcher.utter_message(text = "Equipments: \n{} \n--------------\n".format(convert_to_text(cache.get_from_cache("equipments"))))


class ActionGetAllSteps(Action):
    def name(self) -> Text:
        return "action_get_all_steps"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("ActionGetAllSteps: ")
        dispatcher.utter_message("Here's the step list")
        dispatcher.utter_message(text = "Instructions: \n{}".format(convert_to_text(cache.get_from_cache("instructions"))))


class ActionGetNextStep(Action):
    def name(self) -> Text:
        return "action_get_next_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        current_step = tracker.get_slot("current_step_no")
        print("ActionGetNextStep: Current-step is, ", current_step)

        if current_step == "" or current_step == None:
            dispatcher.utter_message(text = "{}".format(cache.get_from_cache("instructions")[0]))
            return [SlotSet("current_step_no", 0)]
        
        elif (int(current_step) +1) == len(cache.get_from_cache("instructions")):
            dispatcher.utter_message(text = "That's all the steps for this recipe")
            return []
        
        else:
            current_step += 1 
            dispatcher.utter_message(text = "{}".format(cache.get_from_cache("instructions")[int(current_step)]))
            return [SlotSet("current_step_no", current_step)]


class ActionGetPreviousStep(Action):
    def name(self) -> Text:
        return "action_get_previous_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        current_step = tracker.get_slot("current_step_no")
        print("ActionGetPreviousStep: Current-Step is, ", current_step)

        if current_step == "" or current_step == None or current_step == 0:
            dispatcher.utter_message(text = "There are no previous steps")
            return []
        
        else:
            current_step -= 1
            dispatcher.utter_message(text = "{}".format(cache.get_from_cache("instructions")[int(current_step)]))
            return [SlotSet("current_step_no", current_step)]


class ActionGetNStep(Action):
    def name(self) -> Text:
        return "action_get_n_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        current_step = int(tracker.get_slot("current_step_no"))
        print("ActionGetNStep: Current-Step is, ", current_step)

        try:
            if current_step-1 == len(cache.get_from_cache("instructions")):
                dispatcher.utter_message(text = "That's all the steps for this recipe")
                return []
            else: 
                current_step -= 1
                dispatcher.utter_message(text = "{}".format(cache.get_from_cache("instructions")[int(current_step)]))
                return [SlotSet("current_step_no", current_step)]

        except Exception as e:
            print(f"ActionGetNStep: Encountered exception: {e}")


class ActionGetIngredientSubstitute(Action):
    def name(self) -> Text:
        return "action_get_ingredient_substitute"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        ingredient_name = tracker.get_slot("sub_ingredients").strip()
        substitutes = _get_ingredient_substitute(ingredient_name)

        dispatcher.utter_message(text = f"The substitute for {ingredient_name} is: ")
        dispatcher.utter_message(text = substitutes)


        return []


class ActionConfirmRecipeItems(Action):
    def name(self) -> Text:
        return "action_confirm_recipe_items"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        item_name = tracker.get_slot("recipe_item")
        ingredient_list = convert_to_text(cache.get_from_cache("ingredients_list"))
        equipment_list = convert_to_text(cache.get_from_cache("equipments"))

        print(f"ActionConfirmRecipeItems: Item name captured in confirm items: {item_name}")

        try: 
            if len(ingredient_list) <= 0 and len(equipment_list) <= 0: 
                dispatcher.utter_message(text = "No recipe selected yet")
            
            elif item_name in ingredient_list or item_name in equipment_list:
                dispatcher.utter_message(text = "Yes this recipe requires " + item_name)

            else:
                dispatcher.utter_message(text = "No this recipe does not require " + item_name)
        
        except Exception as e:
            print("ActionConfirmRecipeItems: Encountered an exception: ", e)


class ActionGetInfoQuestions(Action):
    def name(self) -> Text:
        return "action_get_info_questions"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("ActionGetInfoQuestions: In action_get_info_questions")
    
        question = tracker.latest_message
        print("ActionGetInfoQuestions: Last message: ", question["text"])
        response = _get_response_chatgpt(question["text"])
        print("ActionGetInfoQuestions: Response is:", response)

        dispatcher.utter_message(text=response)

        return []