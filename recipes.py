import pickle
import sys

sys.setrecursionlimit(20_000)

def make_recipe_book(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    recipe_book = {}
    for tup in recipes:
        #print(tup)
        if tup[0] == "compound":
            if tup[1] not in recipe_book:
                recipe_book[tup[1]] = [tup[2]]
            else:
                recipe_book[tup[1]].append(tup[2])
                
    return recipe_book

def make_atomic_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    atomic_costs = {}
    for tup in recipes:
        #print(tup)
        if tup[0] == "atomic":
            atomic_costs[tup[1]] = tup[2]
                
    return atomic_costs

def lowest_cost(recipes, food_item, forbidden = set()):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    atomic_costs = make_atomic_costs(recipes)
    recipe_book = make_recipe_book(recipes)

    if food_item in forbidden:
        return None
    if food_item in atomic_costs:
        return atomic_costs[food_item]
    if food_item not in atomic_costs and food_item not in recipe_book:
        return None
    else: #recursive step
        min_cost = None
        for recipe in recipe_book[food_item]:
            cost = 0
            for item in recipe:
                if isinstance(lowest_cost(recipes, item[0], forbidden), type(None)):
                    cost = None
                    break
                else:
                    cost += item[1]*lowest_cost(recipes, item[0], forbidden)
            if not isinstance(min_cost, type(None)) and not isinstance(cost, type(None)) and cost < min_cost:
                min_cost = cost
            elif isinstance(min_cost, type(None)) and not isinstance(cost, type(None)):
                min_cost = cost
        return min_cost

def scale_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    scaled = {}
    for item in list(flat_recipe.keys()):
        scaled[item] = flat_recipe[item]*n
    return scaled

def make_grocery_list(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        make_grocery_list([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    grocery_list = {}
    for recipe in flat_recipes:
        for item in list(recipe.keys()):
            if item in grocery_list:
                grocery_list[item] = grocery_list[item] + recipe[item]
            else:
                grocery_list[item] = recipe[item]
    return grocery_list

def cheapest_flat_recipe(recipes, food_item, forbidden = set()):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    atomic_costs = make_atomic_costs(recipes)
    recipe_book = make_recipe_book(recipes)

    if food_item in forbidden:
        return None
    if food_item in atomic_costs:
        return {food_item: 1}
    if food_item not in atomic_costs and food_item not in recipe_book:
        return None
    else: #recursive step
        min_cost = None
        min_items = None
        for recipe in recipe_book[food_item]:
            cost = 0
            items = {}
            for item in recipe:
                if isinstance(lowest_cost(recipes, item[0], forbidden), type(None)):
                    cost = None
                    items = None
                    break
                else:
                    cost += item[1]*lowest_cost(recipes, item[0], forbidden)
                    new_item_dic = scale_recipe(cheapest_flat_recipe(recipes, item[0], forbidden), item[1])
                    for elem in new_item_dic:
                        if elem in items:
                            items[elem] = items[elem] + new_item_dic[elem]
                        else:
                            items[elem] = new_item_dic[elem]
            if not isinstance(min_cost, type(None)) and not isinstance(cost, type(None)) and cost < min_cost:
                min_cost = cost
                min_items = items
            elif isinstance(min_cost, type(None)) and not isinstance(cost, type(None)):
                min_cost = cost
                min_items = items
        return min_items

def ingredient_mixes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes make a certain ingredient as part of a recipe, compute all
    combinations of the flat recipes.
    """
    mixes = flat_recipes[0] 

    for recipe_index, recipe in enumerate(flat_recipes):
        if recipe_index != 0:
            new_mixes = []
            for combo in mixes:
                for ingredients in recipe:
                    new_combo = make_grocery_list([combo, ingredients])
                    new_mixes.append(new_combo)
            mixes = new_mixes 
    return mixes

def all_flat_recipes(recipes, food_item, forbidden = set()):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic_costs = make_atomic_costs(recipes)
    recipe_book = make_recipe_book(recipes)

    flat_recipes = []
    if food_item in forbidden:
        return []
    if food_item not in atomic_costs and food_item not in recipe_book:
        return []
    if food_item in atomic_costs:
        return [{food_item: 1}] #list of dictionaries, each of flat recipes
    else:
        desired_recipes = recipe_book[food_item]
        for recipe in desired_recipes:
            items_flat_recs = []
            for item in recipe:
                item_recs = []
                item_rec = all_flat_recipes(recipes, item[0], forbidden)
                if len(item_rec)==0:
                    items_flat_recs = []
                    break
                for child_item_dic in item_rec: #list of dictionary flat recipes
                    scaled = scale_recipe(child_item_dic, item[1])
                    item_recs.append(scaled) #list of dictionaries flat recipes
                items_flat_recs.append(item_recs)
            if len(items_flat_recs) == 0:
                pass
            else:
                combos = ingredient_mixes(items_flat_recs)
                flat_recipes.extend(combos)
        return flat_recipes

if __name__ == "__main__":
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)


