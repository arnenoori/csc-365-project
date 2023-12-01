import pytest
from http.client import HTTPException
from src.api.users import NewUser, create_user, update_user


class TestNewUser:

    # Creating a new user with valid name and email should return a dictionary with user_id key
    def test_create_user_valid_name_and_email(self):
        # Arrange
        new_user = NewUser(name="John Doe", email="johndoe@example.com")
    
        # Act
        result = create_user(new_user)
    
        # Assert
        assert isinstance(result, dict)
        assert "user_id" in result.keys()

    # Creating a new user with valid name and email should add the user to the database
    def test_create_user_adds_to_database(self):
        # Arrange
        new_user = NewUser(name="John Doe", email="johndoe@example.com")
    
        # Act
        create_user(new_user)
    
        # Assert
        # Check if user exists in the database

    # Updating an existing user with valid name and email should return a dictionary with name and email keys
    def test_update_user_valid_name_and_email1(self):
        # Arrange
        user_id = 1
        new_user = NewUser(name="John Doe", email="johndoe@example.com")
    
        # Act
        result = update_user(user_id, new_user)
    
        # Assert
        assert isinstance(result, dict)
        assert "name" in result.keys()
        assert "email" in result.keys()

    # Creating a new user with an empty name should raise an HTTPException with status_code 400 and detail "Invalid name"
    def test_create_user_empty_name(self):
        # Arrange
        new_user = NewUser(name="", email="johndoe@example.com")
    
        # Act and Assert
        with pytest.raises(HTTPException) as exc_info:
            create_user(new_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid name"

    # Creating a new user with an empty email should raise an HTTPException with status_code 400 and detail "Invalid email"
    def test_create_user_empty_email(self):
        # Arrange
        new_user = NewUser(name="John Doe", email="")
    
        # Act and Assert
        with pytest.raises(HTTPException) as exc_info:
            create_user(new_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid email"

    # Creating a new user with a name that is too short should raise an HTTPException with status_code 400 and detail "Invalid name"
    def test_create_user_short_name(self):
        # Arrange
        new_user = NewUser(name="J", email="johndoe@example.com")
    
        # Act and Assert
        with pytest.raises(HTTPException) as exc_info:
            create_user(new_user)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid name"

    # Updating an existing user with a name and email that are at the minimum length should update the user in the database
    def test_update_user_with_minimum_length_name_and_email(self):
        # Arrange
        user_id = 1
        new_user = NewUser(name="A", email="a@example.com")
    
        # Act
        result = update_user(user_id, new_user)
    
        # Assert
        assert isinstance(result, dict)
        assert "name" in result.keys()
        assert "email" in result.keys()

    # Updating an existing user with valid name and email should update the user in the database
    def test_update_user_valid_name_and_email2(self):
        # Arrange
        user_id = 1
        new_user = NewUser(name="John Doe", email="johndoe@example.com")

        # Act
        result = update_user(user_id, new_user)

        # Assert
        assert isinstance(result, dict)
        assert "name" in result.keys()
        assert "email" in result.keys()

    # Creating a new user with a name and email that are at the minimum length should add the user to the database
    def test_create_user_with_minimum_length_name_and_email(self):
        # Arrange
        new_user = NewUser(name="a", email="a@example.com")

        # Act
        result = create_user(new_user)

        # Assert
        assert isinstance(result, dict)
        assert "user_id" in result.keys()

    # Creating a new user with a name and email that are at the maximum length should add the user to the database
    def test_create_user_with_maximum_length_name_and_email(self):
        # Arrange
        name = "a" * 255
        email = "a" * 255 + "@example.com"
        new_user = NewUser(name=name, email=email)

        # Act
        result = create_user(new_user)

        # Assert
        assert isinstance(result, dict)
        assert "user_id" in result.keys()

    # Creating a new user with a name and email that contain valid special characters should add the user to the database
    def test_create_user_with_valid_special_characters(self):
        # Arrange
        new_user = NewUser(name="John Doe!", email="johndoe@example.com")

        # Act
        result = create_user(new_user)

        # Assert
        assert isinstance(result, dict)
        assert "user_id" in result.keys()

    # Updating an existing user with a name and email that are at the maximum length should update the user in the database
    def test_update_user_max_length_name_and_email(self):
        # Arrange
        user_id = 1
        new_user = NewUser(name="A" * 255, email="a" * 255)

        # Act
        result = update_user(user_id, new_user)

        # Assert
        assert isinstance(result, dict)
        assert "name" in result.keys()
        assert "email" in result.keys()

    # Updating an existing user with a name and email that contain valid special characters should update the user in the database
    def test_update_user_valid_special_characters(self):
        # Arrange
        user_id = 1
        new_user = NewUser(name="John Doe!", email="johndoe@example.com!")
    
        # Act
        result = update_user(user_id, new_user)
    
        # Assert
        assert isinstance(result, dict)
        assert "name" in result.keys()
        assert "email" in result.keys()
        assert result["name"] == new_user.name
        assert result["email"] == new_user.email

    # Updating a non-existent user should raise an HTTPException with status_code 404 and detail "User not found"
    def test_update_nonexistent_user(self):
        # Arrange
        user_id = 1
        new_user = NewUser(name="John Doe", email="johndoe@example.com")

        # Act and Assert
        with pytest.raises(HTTPException) as exc_info:
            update_user(user_id, new_user)
    
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"

    # Updating an existing user with an email that is already in use by another user should raise an HTTPException with status_code 409 and detail "Email already in use"
    def test_update_user_existing_email(self):
        # Arrange
        existing_user = NewUser(name="John Doe", email="johndoe@example.com")
        new_user = NewUser(name="Jane Smith", email="johndoe@example.com")
        create_user(existing_user)
    
        # Act and Assert
        with pytest.raises(HTTPException) as exc_info:
            update_user(1, new_user)
    
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Email already in use"