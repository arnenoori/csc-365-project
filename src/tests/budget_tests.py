import pytest
from http.client import HTTPException
from src.api.budget import NewBudget, create_budget, update_budget

class TestNewBudget:

    # Creating a new budget with valid integer values for all categories.
    def test_valid_integer_values_for_all_categories(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=200, electronics=300, home_and_garden=400, health_and_beauty=500, 
                           entertainment=600, travel=700, automotive=800, services=900, gifts_and_special_occasions=1000, 
                           education=1100, fitness_and_sports=1200, pets=1300, office_supplies=1400, financial_services=1500, 
                           other=1600)
    
        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 200
        assert budget.electronics == 300
        assert budget.home_and_garden == 400
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 600
        assert budget.travel == 700
        assert budget.automotive == 800
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 1000
        assert budget.education == 1100
        assert budget.fitness_and_sports == 1200
        assert budget.pets == 1300
        assert budget.office_supplies == 1400
        assert budget.financial_services == 1500
        assert budget.other == 1600

    # Creating a new budget with valid integer values for some categories and None for others.
    def test_valid_integer_values_some_categories_none(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=None, electronics=300, home_and_garden=None, health_and_beauty=500, 
                           entertainment=None, travel=700, automotive=None, services=900, gifts_and_special_occasions=None, 
                           education=1100, fitness_and_sports=None, pets=1300, office_supplies=None, financial_services=1500, 
                           other=None)
    
        assert budget.groceries == 100
        assert budget.clothing_and_accessories is None
        assert budget.electronics == 300
        assert budget.home_and_garden is None
        assert budget.health_and_beauty == 500
        assert budget.entertainment is None
        assert budget.travel == 700
        assert budget.automotive is None
        assert budget.services == 900
        assert budget.gifts_and_special_occasions is None
        assert budget.education == 1100
        assert budget.fitness_and_sports is None
        assert budget.pets == 1300
        assert budget.office_supplies is None
        assert budget.financial_services == 1500
        assert budget.other is None

    # Creating a new budget with valid integer values for some categories and 0 for others.
    def test_valid_integer_values_some_categories_zero(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=0, electronics=300, home_and_garden=0, health_and_beauty=500, 
                           entertainment=0, travel=700, automotive=0, services=900, gifts_and_special_occasions=0, 
                           education=1100, fitness_and_sports=0, pets=1300, office_supplies=0, financial_services=1500, 
                           other=0)
    
        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 0
        assert budget.electronics == 300
        assert budget.home_and_garden == 0
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 0
        assert budget.travel == 700
        assert budget.automotive == 0
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 0
        assert budget.education == 1100
        assert budget.fitness_and_sports == 0
        assert budget.pets == 1300
        assert budget.office_supplies == 0
        assert budget.financial_services == 1500
        assert budget.other == 0

    # Creating a new budget with None for all categories.
    def test_none_for_all_categories(self):
        budget = NewBudget(groceries=None, clothing_and_accessories=None, electronics=None, home_and_garden=None, health_and_beauty=None, 
                           entertainment=None, travel=None, automotive=None, services=None, gifts_and_special_occasions=None, 
                           education=None, fitness_and_sports=None, pets=None, office_supplies=None, financial_services=None, 
                           other=None)
    
        assert budget.groceries is None
        assert budget.clothing_and_accessories is None
        assert budget.electronics is None
        assert budget.home_and_garden is None
        assert budget.health_and_beauty is None
        assert budget.entertainment is None
        assert budget.travel is None
        assert budget.automotive is None
        assert budget.services is None
        assert budget.gifts_and_special_occasions is None
        assert budget.education is None
        assert budget.fitness_and_sports is None
        assert budget.pets is None
        assert budget.office_supplies is None
        assert budget.financial_services is None
        assert budget.other is None

    # Creating a new budget with 0 for all categories.
    def test_zero_for_all_categories(self):
        budget = NewBudget(groceries=0, clothing_and_accessories=0, electronics=0, home_and_garden=0, health_and_beauty=0, 
                           entertainment=0, travel=0, automotive=0, services=0, gifts_and_special_occasions=0, 
                           education=0, fitness_and_sports=0, pets=0, office_supplies=0, financial_services=0, 
                           other=0)
    
        assert budget.groceries == 0
        assert budget.clothing_and_accessories == 0
        assert budget.electronics == 0
        assert budget.home_and_garden == 0
        assert budget.health_and_beauty == 0
        assert budget.entertainment == 0
        assert budget.travel == 0
        assert budget.automotive == 0
        assert budget.services == 0
        assert budget.gifts_and_special_occasions == 0
        assert budget.education == 0
        assert budget.fitness_and_sports == 0
        assert budget.pets == 0
        assert budget.office_supplies == 0
        assert budget.financial_services == 0
        assert budget.other == 0

    # Creating a new budget with valid integer values for some categories and the minimum allowed integer value for others.
    def test_valid_integer_values_for_all_categories(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=200, electronics=300, home_and_garden=400, health_and_beauty=500, 
                           entertainment=600, travel=700, automotive=800, services=900, gifts_and_special_occasions=1000, 
                           education=1100, fitness_and_sports=1200, pets=1300, office_supplies=1400, financial_services=1500, 
                           other=1600)

        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 200
        assert budget.electronics == 300
        assert budget.home_and_garden == 400
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 600
        assert budget.travel == 700
        assert budget.automotive == 800
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 1000
        assert budget.education == 1100
        assert budget.fitness_and_sports == 1200
        assert budget.pets == 1300
        assert budget.office_supplies == 1400
        assert budget.financial_services == 1500
        assert budget.other == 1600

    # Creating a new budget with valid integer values for some categories and the maximum allowed integer value for others.
    def test_valid_integer_values_for_all_categories(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=200, electronics=300, home_and_garden=400, health_and_beauty=500, 
                           entertainment=600, travel=700, automotive=800, services=900, gifts_and_special_occasions=1000, 
                           education=1100, fitness_and_sports=1200, pets=1300, office_supplies=1400, financial_services=1500, 
                           other=1600)

        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 200
        assert budget.electronics == 300
        assert budget.home_and_garden == 400
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 600
        assert budget.travel == 700
        assert budget.automotive == 800
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 1000
        assert budget.education == 1100
        assert budget.fitness_and_sports == 1200
        assert budget.pets == 1300
        assert budget.office_supplies == 1400
        assert budget.financial_services == 1500
        assert budget.other == 1600

    # Updating an existing budget with valid integer values for all categories.
    def test_valid_integer_values_for_all_categories(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=200, electronics=300, home_and_garden=400, health_and_beauty=500, 
                           entertainment=600, travel=700, automotive=800, services=900, gifts_and_special_occasions=1000, 
                           education=1100, fitness_and_sports=1200, pets=1300, office_supplies=1400, financial_services=1500, 
                           other=1600)

        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 200
        assert budget.electronics == 300
        assert budget.home_and_garden == 400
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 600
        assert budget.travel == 700
        assert budget.automotive == 800
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 1000
        assert budget.education == 1100
        assert budget.fitness_and_sports == 1200
        assert budget.pets == 1300
        assert budget.office_supplies == 1400
        assert budget.financial_services == 1500
        assert budget.other == 1600

    # Updating an existing budget with valid integer values for some categories and None for others.
    def test_update_budget_with_valid_integer_values_and_none(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=None, electronics=300, home_and_garden=None, health_and_beauty=500, 
                           entertainment=None, travel=700, automotive=None, services=900, gifts_and_special_occasions=None, 
                           education=1100, fitness_and_sports=None, pets=1300, office_supplies=None, financial_services=1500, 
                           other=None)
    
        result = update_budget(1, 1, budget)
    
        assert result["budget_id"] == 1
        assert result["groceries"] == 100
        assert result["clothing_and_accessories"] is None
        assert result["electronics"] == 300
        assert result["home_and_garden"] is None
        assert result["health_and_beauty"] == 500
        assert result["entertainment"] is None
        assert result["travel"] == 700
        assert result["automotive"] is None
        assert result["services"] == 900
        assert result["gifts_and_special_occasions"] is None
        assert result["education"] == 1100
        assert result["fitness_and_sports"] is None
        assert result["pets"] == 1300
        assert result["office_supplies"] is None
        assert result["financial_services"] == 1500
        assert result["other"] is None

    # Updating an existing budget with valid integer values for some categories and the maximum allowed integer value for others.
    def test_valid_integer_values_for_all_categories(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=200, electronics=300, home_and_garden=400, health_and_beauty=500, 
                           entertainment=600, travel=700, automotive=800, services=900, gifts_and_special_occasions=1000, 
                           education=1100, fitness_and_sports=1200, pets=1300, office_supplies=1400, financial_services=1500, 
                           other=1600)

        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 200
        assert budget.electronics == 300
        assert budget.home_and_garden == 400
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 600
        assert budget.travel == 700
        assert budget.automotive == 800
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 1000
        assert budget.education == 1100
        assert budget.fitness_and_sports == 1200
        assert budget.pets == 1300
        assert budget.office_supplies == 1400
        assert budget.financial_services == 1500
        assert budget.other == 1600

    # Updating an existing budget with valid integer values for some categories and the minimum allowed integer value for others.
    def test_valid_integer_values_for_some_categories_and_minimum_for_others(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=200, electronics=300, home_and_garden=400, health_and_beauty=500, 
                           entertainment=600, travel=700, automotive=800, services=900, gifts_and_special_occasions=1000, 
                           education=1100, fitness_and_sports=1200, pets=1300, office_supplies=1400, financial_services=1500, 
                           other=1)

        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 200
        assert budget.electronics == 300
        assert budget.home_and_garden == 400
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 600
        assert budget.travel == 700
        assert budget.automotive == 800
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 1000
        assert budget.education == 1100
        assert budget.fitness_and_sports == 1200
        assert budget.pets == 1300
        assert budget.office_supplies == 1400
        assert budget.financial_services == 1500
        assert budget.other == 1

    # Updating an existing budget with valid integer values for some categories and 0 for others.
    def test_valid_integer_values_for_some_categories_and_zero_for_others(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=0, electronics=300, home_and_garden=0, health_and_beauty=500, 
                           entertainment=0, travel=700, automotive=0, services=900, gifts_and_special_occasions=0, 
                           education=1100, fitness_and_sports=0, pets=1300, office_supplies=0, financial_services=1500, 
                           other=0)

        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 0
        assert budget.electronics == 300
        assert budget.home_and_garden == 0
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 0
        assert budget.travel == 700
        assert budget.automotive == 0
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 0
        assert budget.education == 1100
        assert budget.fitness_and_sports == 0
        assert budget.pets == 1300
        assert budget.office_supplies == 0
        assert budget.financial_services == 1500
        assert budget.other == 0

    # Creating a new budget with the maximum allowed integer value for all categories.
    def test_valid_integer_values_for_all_categories(self):
        budget = NewBudget(groceries=2147483647, clothing_and_accessories=2147483647, electronics=2147483647, home_and_garden=2147483647, health_and_beauty=2147483647, 
                           entertainment=2147483647, travel=2147483647, automotive=2147483647, services=2147483647, gifts_and_special_occasions=2147483647, 
                           education=2147483647, fitness_and_sports=2147483647, pets=2147483647, office_supplies=2147483647, financial_services=2147483647, 
                           other=2147483647)

        assert budget.groceries == 2147483647
        assert budget.clothing_and_accessories == 2147483647
        assert budget.electronics == 2147483647
        assert budget.home_and_garden == 2147483647
        assert budget.health_and_beauty == 2147483647
        assert budget.entertainment == 2147483647
        assert budget.travel == 2147483647
        assert budget.automotive == 2147483647
        assert budget.services == 2147483647
        assert budget.gifts_and_special_occasions == 2147483647
        assert budget.education == 2147483647
        assert budget.fitness_and_sports == 2147483647
        assert budget.pets == 2147483647
        assert budget.office_supplies == 2147483647
        assert budget.financial_services == 2147483647
        assert budget.other == 2147483647

    # Creating a new budget with a float value for one category and valid integer values for the rest.
    def test_create_budget_with_float_value(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=200, electronics=300, home_and_garden=400, health_and_beauty=500, 
                           entertainment=600, travel=700, automotive=800, services=900, gifts_and_special_occasions=1000, 
                           education=1100, fitness_and_sports=1200, pets=1300, office_supplies=1400, financial_services=1500, 
                           other=1600.5)

        with pytest.raises(HTTPException) as exc_info:
            create_budget(1, budget)
    
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid budget"

    # Creating a new budget with a negative integer value for one category and valid integer values for the rest.
    def test_negative_integer_value(self):
        budget = NewBudget(groceries=100, clothing_and_accessories=200, electronics=300, home_and_garden=400, health_and_beauty=500, 
                           entertainment=600, travel=700, automotive=800, services=900, gifts_and_special_occasions=1000, 
                           education=1100, fitness_and_sports=1200, pets=1300, office_supplies=1400, financial_services=1500, 
                           other=-1600)

        assert budget.groceries == 100
        assert budget.clothing_and_accessories == 200
        assert budget.electronics == 300
        assert budget.home_and_garden == 400
        assert budget.health_and_beauty == 500
        assert budget.entertainment == 600
        assert budget.travel == 700
        assert budget.automotive == 800
        assert budget.services == 900
        assert budget.gifts_and_special_occasions == 1000
        assert budget.education == 1100
        assert budget.fitness_and_sports == 1200
        assert budget.pets == 1300
        assert budget.office_supplies == 1400
        assert budget.financial_services == 1500
        assert budget.other == -1600