import requests
import re

BASE_URL = "https://api.spoonacular.com/"
API_KEY = "<spooncular API key>"


class CacheStore:
    def __init__(self):
        self.cache = {}

    def add_to_cache(self, key, value):
        self.cache[key] = value
    
    def get_from_cache(self, key):
        return self.cache[key] 


def _search_recipes(recipename, intolerances, dietary_req, sort_type):
    """
    """
    url = BASE_URL + "recipes/complexSearch"
    recipe_bullets = ["A", "B", "C", "D", "E"]

    if intolerances not in ["Dairy", "Eggs", "Gluten", "Peanut", "Seafood"]:
        intolerances = ""
    
    if dietary_req not in ["Vegan", "Vegetarian", "Gluten Free"]:
        dietary_req = ""

    if sort_type not in ["popularity", "healthiness", "random"]:
        sort_type = "random"


    print(f"Recipe Finder: Recipe_name: {recipename}, intolerences: {intolerances}, dietary_req: {dietary_req}, sort_type: {sort_type}",)

    payload = {
                "query": recipename,
                "titleMatch": recipename,
                "intolerances": intolerances,
                "diet": dietary_req,
                "sort": sort_type,
                "apiKey": API_KEY
              }

    response = requests.get(url, params=payload)
    result = response.json()

    print("Result from recipes: ", result)
    
    no_of_recipes = len(result["results"])

    if no_of_recipes > 5:
        no_of_recipes = 5

    print("Results length: ", no_of_recipes)

    list_of_recipes = {}
    for i in range(no_of_recipes):
        new_recipe = {recipe_bullets[i]: [result["results"][i]["title"], result["results"][i]["id"]]}
        list_of_recipes.update(new_recipe)

    print(list_of_recipes)

    return list_of_recipes


def _get_recipe_details(recipeid):
    """
    """
    url = BASE_URL + "recipes/{}/information".format(recipeid)
    payload = {
                "apiKey": API_KEY
              }

    try: 
        response = requests.get(url, params=payload)
        result = response.json()
    
    except Exception as e:
        print(f"Encountered exception as: {e}")

    ingredients_list = []
    equipments = set()
    instructions = []

    recipe_title = result["title"]

    try: 

        for ingredients in result["extendedIngredients"]:
            ingredients_list.append(f"- {ingredients['original']}")

        for step in result["analyzedInstructions"][0]["steps"]:
            instructions.append("Step-" + str(step["number"]) + ": " + step["step"])
            for equipment in step["equipment"]:
                if len(equipment) > 0:
                    equipments.add(equipment["name"])
    
    except Exception as e:
        print(f"Encountered exception as: {e}")
    
    return recipe_title, ingredients_list, equipments, instructions


def convert_to_text(iter_object):
    """
    """
    text = "\n".join(str(item) for item in iter_object)
    return text


def get_step_number(last_message):
    """
    """
    step_regex = r"Step-(\d+)"
    match = re.search(step_regex, last_message)
    
    return match.group(1)


def _get_ingredient_substitute(item_name):
    """
    """
    url = BASE_URL + "food/ingredients/substitutes"
    payload = {
                "apiKey": API_KEY,
                "ingredientName": item_name,
              }

    try: 
        response = requests.get(url, params=payload)
        result = response.json()

        if result["status"] == "success":
            return convert_to_text(result["substitutes"])
        else:
            chat_gpt_response = _get_response_chatgpt(f"Tell me the substitute ingredient for {item_name}. Just return the ingredient name and quantity proportions.")
            return chat_gpt_response
    
    except Exception as e:
        print(f"Encountered exception as: {e}")
    

def _get_response_chatgpt(prompt):    
    """
    """
    import openai
    openai.api_key = "<openai-API-key>"

    response = openai.Completion.create(
                                            model="text-davinci-001",
                                            prompt=prompt,
                                            temperature=0.2,
                                            max_tokens=50,
                                            n=1,
                                            top_p=0.1
                                        )

    return response["choices"][0]["text"]