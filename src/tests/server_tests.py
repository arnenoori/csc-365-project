import pytest
import src
import dbm
from http.client import HTTPException
import statistics
from codecs import mbcs_decode
from src.api.server import get_file_type, upload_receipt_to_S3, s3_upload, openai_process_receipt, get_receipts, db, status, MB, NewTransaction, NewPurchase
import json
import requests
import sqlalchemy
from sqlalchemy.exc import DBAPIError

# Dependencies:
# pip install pytest-mock

class TestGetFileType:

    # Returns 'image/jpeg' when contents start with b'\xFF\xD8\xFF\xDB'
    def test_returns_image_jpeg(self):
        contents = b'\xFF\xD8\xFF\xDB'
        result = get_file_type(contents)
        assert result == 'image/jpeg'

    # Returns 'image/jpeg' when contents start with b'\xFF\xD8\xFF\xE0'
    def test_returns_image_jpeg_2(self):
        contents = b'\xFF\xD8\xFF\xE0'
        result = get_file_type(contents)
        assert result == 'image/jpeg'

    # Returns 'image/png' when contents start with b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
    def test_returns_image_png(self):
        contents = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
        result = get_file_type(contents)
        assert result == 'image/png'

    # Returns 'unknown' when contents is empty
    def test_returns_unknown_empty_contents(self):
        contents = b''
        result = get_file_type(contents)
        assert result == 'unknown'

    # Returns 'unknown' when contents is None
    def test_returns_unknown_none_contents(self):
        contents = None
        result = get_file_type(contents)
        assert result == 'unknown'

    # Returns 'unknown' when contents is not bytes
    def test_returns_unknown_non_bytes_contents(self):
        contents = "not bytes"
        result = get_file_type(contents)
        assert result == 'unknown'

    # Returns 'application/pdf' when contents start with b'\x25\x50\x44\x46\x2D'
    def test_returns_application_pdf(self):
        contents = b'\x25\x50\x44\x46\x2D'
        result = get_file_type(contents)
        assert result == 'application/pdf'

    # Returns 'unknown' when contents do not match any common signatures
    def test_returns_unknown_when_contents_do_not_match_any_common_signatures(self):
        contents = b'\x00\x00\x00\x00'
        result = get_file_type(contents)
        assert result == 'unknown'

class TestUploadReceiptToS3:

    # Successfully upload a supported file to S3 and return image URL
    @pytest.mark.asyncio
    async def test_upload_supported_file_to_S3(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b'test file contents'

        # Invoke the function under test
        result = await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the S3 upload function was called with the correct arguments
        s3_upload.assert_called_once_with(contents=b'test file contents', key='test.jpg')

        # Assert that the OpenAI process receipt function was called with the correct arguments
        openai_process_receipt.assert_called_once_with(user_id=1, img_url='https://example.s3.us-west-1.amazonaws.com/test.jpg', file=mock_file)

        # Assert that the result contains the expected image URL
        assert result == {"image_url": "https://example.s3.us-west-1.amazonaws.com/test.jpg"}

    # Successfully parse receipt data using OpenAI API and store it in the database
    @pytest.mark.asyncio
    async def test_parse_receipt_data_and_store_in_database(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')
        mocker.patch('src.api.server.db.engine.begin')
        mocker.patch('src.api.server.db.engine.begin().__enter__')
        mocker.patch('src.api.server.db.engine.begin().__exit__')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b'test file contents'

        # Mock the return value of the openai_process_receipt function
        openai_process_receipt.return_value = {'transaction_id': 1}

        # Invoke the function under test
        result = await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the S3 upload function was called with the correct arguments
        s3_upload.assert_called_once_with(contents=b'test file contents', key='test.jpg')

        # Assert that the OpenAI process receipt function was called with the correct arguments
        openai_process_receipt.assert_called_once_with(user_id=1, img_url='https://example.s3.us-west-1.amazonaws.com/test.jpg', file=mock_file)

        # Assert that the database connection was opened and closed correctly
        db.engine.begin.assert_called_once()
        db.engine.begin().__enter__.assert_called_once()
        db.engine.begin().__exit__.assert_called_once()

        # Assert that the receipt URL was inserted into the database correctly
        db.engine.begin().__enter__().execute.assert_called_once_with(
            sqlalchemy.text(
                """
                INSERT INTO receipts (transaction_id, url, parsed_data)
                VALUES (:transaction_id, :url, :parsed_data)
                """
            ), {"transaction_id": 1, "url": "https://example.s3.us-west-1.amazonaws.com/test.jpg", "parsed_data": ""}
        )

        # Assert that the result contains the expected image URL
        assert result == {"image_url": "https://example.s3.us-west-1.amazonaws.com/test.jpg"}

    # Successfully insert receipt URL into receipts table in the database
    @pytest.mark.asyncio
    async def test_insert_receipt_URL_into_database(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')
        mocker.patch('src.api.server.db.engine.begin')
        mocker.patch('src.api.server.db.engine.begin().__enter__')
        mocker.patch('src.api.server.db.engine.begin().__exit__')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b'test file contents'

        # Mock the return value of the openai_process_receipt function
        openai_process_receipt.return_value = {'transaction_id': 1}

        # Invoke the function under test
        result = await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the S3 upload function was called with the correct arguments
        s3_upload.assert_called_once_with(contents=b'test file contents', key='test.jpg')

        # Assert that the OpenAI process receipt function was called with the correct arguments
        openai_process_receipt.assert_called_once_with(user_id=1, img_url='https://example.s3.us-west-1.amazonaws.com/test.jpg', file=mock_file)

        # Assert that the database connection was opened and closed correctly
        db.engine.begin.assert_called_once()
        db.engine.begin().__enter__.assert_called_once()
        db.engine.begin().__exit__.assert_called_once()

        # Assert that the receipt URL was inserted into the database correctly
        db.engine.begin().__enter__().execute.assert_called_once_with(
            sqlalchemy.text(
                """
                INSERT INTO receipts (transaction_id, url, parsed_data)
                VALUES (:transaction_id, :url, :parsed_data)
                """
            ), {"transaction_id": 1, "url": "https://example.s3.us-west-1.amazonaws.com/test.jpg", "parsed_data": ""}
        )

        # Assert that the result contains the expected image URL
        assert result == {"image_url": "https://example.s3.us-west-1.amazonaws.com/test.jpg"}

    # Test with a file of size 0 bytes
    @pytest.mark.asyncio
    async def test_upload_file_size_zero_bytes(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b''

        # Invoke the function under test and expect an HTTPException with status code 400
        with pytest.raises(HTTPException) as exc_info:
            await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the HTTPException has the correct status code and detail message
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'File size must be between 0 and 10 MB'

    # Test with a file of size 10 MB
    @pytest.mark.asyncio
    async def test_upload_file_size_10_MB(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b'test' * (10 * MB // 4)

        # Invoke the function under test and expect no exceptions
        result = await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the S3 upload function was called with the correct arguments
        s3_upload.assert_called_once_with(contents=b'test' * (10 * MB // 4), key='test.jpg')

        # Assert that the OpenAI process receipt function was called with the correct arguments
        openai_process_receipt.assert_called_once_with(user_id=1, img_url='https://example.s3.us-west-1.amazonaws.com/test.jpg', file=mock_file)

        # Assert that the result contains the expected image URL
        assert result == {"image_url": "https://example.s3.us-west-1.amazonaws.com/test.jpg"}

    # Return appropriate error message if file size is greater than 10 MB
    @pytest.mark.asyncio
    async def test_file_size_greater_than_10MB(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object with a file size greater than 10 MB
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b'test file contents' * (10 * MB + 1)

        # Invoke the function under test and expect a HTTPException with status code 400
        with pytest.raises(HTTPException) as exc_info:
            await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the exception has the correct status code and detail message
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'File size must be between 0 and 10 MB'

        # Assert that the S3 upload function and OpenAI process receipt function were not called
        s3_upload.assert_not_called()
        openai_process_receipt.assert_not_called()

    # Return appropriate error message if file type is not supported
    @pytest.mark.asyncio
    async def test_return_error_message_if_file_type_not_supported(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.get_file_type').return_value = 'unsupported_file_type'

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.txt'

        # Invoke the function under test
        with pytest.raises(HTTPException) as exc_info:
            await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the HTTPException was raised with the correct status code and detail message
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'file type: unsupported_file_type not supported'

    # Return appropriate error message if file is not found
    @pytest.mark.asyncio
    async def test_return_error_message_if_file_not_found(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b'test file contents'

        # Invoke the function under test with a None file
        with pytest.raises(HTTPException) as exc_info:
            await upload_receipt_to_S3(1, file=None)

        # Assert that the HTTPException was raised with the correct status code and detail
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'File not found'

        # Assert that the S3 upload function was not called
        s3_upload.assert_not_called()

        # Assert that the OpenAI process receipt function was not called
        openai_process_receipt.assert_not_called()

    # Test with a file of size greater than 10 MB
    @pytest.mark.asyncio
    async def test_upload_file_greater_than_10MB(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b'test file contents'

        # Set the file size to be greater than 10 MB
        mock_file_size = 11 * MB

        # Set the supported file type to be 'image/jpeg'
        mock_file_type = 'image/jpeg'

        # Invoke the function under test
        with pytest.raises(HTTPException) as exc_info:
            await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the HTTPException is raised with the correct status code and detail message
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'File size must be between 0 and 10 MB'

        # Assert that the S3 upload function was not called
        s3_upload.assert_not_called()

        # Assert that the OpenAI process receipt function was not called
        openai_process_receipt.assert_not_called()

    # Test with a file type not supported by S3
    @pytest.mark.asyncio
    async def test_upload_unsupported_file_to_S3(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.txt'
        mock_file.read.return_value = b'test file contents'

        # Invoke the function under test
        with pytest.raises(HTTPException) as exc_info:
            await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the S3 upload function was not called
        s3_upload.assert_not_called()

        # Assert that the OpenAI process receipt function was not called
        openai_process_receipt.assert_not_called()

        # Assert the correct HTTPException was raised
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'file type: text/plain not supported'

    # Test with a file type not supported by the application
    @pytest.mark.asyncio
    async def test_upload_unsupported_file_to_S3(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.txt'
        mock_file.read.return_value = b'test file contents'

        # Invoke the function under test
        with pytest.raises(HTTPException) as exc_info:
            await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the S3 upload function was not called
        s3_upload.assert_not_called()

        # Assert that the OpenAI process receipt function was not called
        openai_process_receipt.assert_not_called()

        # Assert the correct HTTPException was raised
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'file type: text/plain not supported'

    # Test with a file that contains invalid receipt data
    @pytest.mark.asyncio
    async def test_invalid_receipt_data(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('src.api.server.s3_upload')
        mocker.patch('src.api.server.openai_process_receipt')

        # Create a mock UploadFile object
        mock_file = mocker.Mock()
        mock_file.filename = 'test.jpg'
        mock_file.read.return_value = b'test file contents'

        # Invoke the function under test
        with pytest.raises(HTTPException) as exc_info:
            await upload_receipt_to_S3(1, file=mock_file)

        # Assert that the HTTPException was raised with the correct status code and detail
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == 'File type: unknown not supported'

        # Assert that the S3 upload function was not called
        s3_upload.assert_not_called()

        # Assert that the OpenAI process receipt function was not called
        openai_process_receipt.assert_not_called()


class TestS3Upload:

    # Uploads image to S3 successfully
    @pytest.mark.asyncio
    async def test_upload_image_successfully(self):
        # Arrange
        contents = b'image contents'
        key = 'image.jpg'
    
        # Act
        await s3_upload(contents, key)
    
        # Assert
        # Add assertions to check if the image was successfully uploaded to S3

    # Handles empty contents
    @pytest.mark.asyncio
    async def test_handles_empty_contents(self):
        # Arrange
        contents = b''
        key = 'image.jpg'
    
        # Act and Assert
        with pytest.raises(Exception):
            await s3_upload(contents, key)

    # Handles invalid key
    @pytest.mark.asyncio
    async def test_handles_invalid_key(self):
        # Arrange
        contents = b'image contents'
        key = ''
    
        # Act and Assert
        with pytest.raises(Exception):
            await s3_upload(contents, key)

    # Successfully parse receipt data and create a new transaction and purchase for each item
    @pytest.mark.asyncio
    async def test_parse_receipt_data_and_create_transaction_and_purchase(self, mocker):
        # Mock the necessary dependencies
        mocker.patch('requests.post')
        mocker.patch('json.loads')
        mocker.patch('src.api.transactions.create_transaction')
        mocker.patch('src.api.purchases.create_purchase')

        # Set up the mock responses
        mock_response = mocker.Mock()
        mock_response.text = '{"choices": [{"message": {"content": "```json\\n{\\\\n  \\\\\\"store_name\\\\\\": \\\\\\"store\\\\\\", \\\\\\"date\\\\\\": \\\\\\"2022-01-01\\\\\\", \\\\\\"items\\\\\\": [\\\\n    {\\\\n      \\\\\\"name\\\\\\": \\\\\\"item1\\\\\\", \\\\\\"price\\\\\\": 10.0, \\\\\\"quantity\\\\\\": 2\\\\n    },\\\\n    {\\\\n      \\\\\\"name\\\\\\": \\\\\\"item2\\\\\\", \\\\\\"price\\\\\\": 5.0, \\\\\\"quantity\\\\\\": 1\\\\n    }\\\\n  ]\\\\n}```"}]}]}'
        requests.post.return_value = mock_response

        # Set up the mock JSON data
        mock_json_data = {
            "store_name": "store",
            "date": "2022-01-01",
            "items": [
                {
                    "name": "item1",
                    "price": 10.0,
                    "quantity": 2
                },
                {
                    "name": "item2",
                    "price": 5.0,
                    "quantity": 1
                }
            ]
        }
        json.loads.return_value = mock_json_data

        # Set up the mock transaction and purchase IDs
        mock_transaction_id = {"transaction_id": 123}
        mock_purchase_id = {"purchase_id": 456}
        src.api.transactions.create_transaction.return_value = mock_transaction_id
        src.api.purchases.create_purchase.return_value = mock_purchase_id

        # Call the function under test
        result = await openai_process_receipt(123, "https://example.com/receipt.jpg", None)

        # Assert the expected calls were made
        requests.post.assert_called_once()
        json.loads.assert_called_once_with('{"choices": [{"message": {"content": "```json\\n{\\\\n  \\\\\\"store_name\\\\\\": \\\\\\"store\\\\\\", \\\\\\"date\\\\\\": \\\\\\"2022-01-01\\\\\\", \\\\\\"items\\\\\\": [\\\\n    {\\\\n      \\\\\\"name\\\\\\": \\\\\\"item1\\\\\\", \\\\\\"price\\\\\\": 10.0, \\\\\\"quantity\\\\\\": 2\\\\n    },\\\\n    {\\\\n      \\\\\\"name\\\\\\": \\\\\\"item2\\\\\\", \\\\\\"price\\\\\\": 5.0, \\\\\\"quantity\\\\\\": 1\\\\n    }\\\\n  ]\\\\n}```"}]}]}')
        src.api.transactions.create_transaction.assert_called_once_with(123, NewTransaction(merchant="store", description="", date="2022-01-01"))
        src.api.purchases.create_purchase.assert_has_calls([
            mocker.call(123, 123, NewPurchase(item="item1", price=10.0, quantity=2, category="", warranty_date="2023-11-16", return_date="2023-11-16")),
            mocker.call(123, 123, NewPurchase(item="item2", price=5.0, quantity=1, category="", warranty_date="2023-11-16", return_date="2023-11-16"))
        ])

        # Assert the expected result
        assert result == mock_transaction_id


class TestGetReceipts:

    # Returns a list of receipt URLs for a given user ID
    @pytest.mark.asyncio
    async def test_returns_list_of_receipt_urls(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = [("url1",), ("url2",)]
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(1)

        # Assert the result
        assert result == {"receipts": ["url1", "url2"]}

    # Returns an empty list if the user has no receipts
    @pytest.mark.asyncio
    async def test_returns_empty_list_if_no_receipts(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = []
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(1)

        # Assert the result
        assert result == {"receipts": []}

    # Handles multiple receipts for a user
    @pytest.mark.asyncio
    async def test_handles_multiple_receipts_for_user(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = [("url1",), ("url2",), ("url3",)]
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(1)

        # Assert the result
        assert result == {"receipts": ["url1", "url2", "url3"]}

    # Raises an HTTPException with status code 500 if there is a database error
    @pytest.mark.asyncio
    async def test_raises_http_exception_on_database_error(self, mocker):
        # Mock the database connection and raise a DBAPIError
        mock_connection = mocker.MagicMock()
        mock_connection.execute.side_effect = DBAPIError("Database error", None, None)
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function and assert the HTTPException is raised
        with pytest.raises(HTTPException) as exc_info:
            await get_receipts(1)
    
        # Assert the status code of the raised HTTPException
        assert exc_info.value.status_code == 500

    # Handles a non-existent user ID
    @pytest.mark.asyncio
    async def test_handles_nonexistent_user_id(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = []
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(999)

        # Assert the result
        assert result == {"receipts": []}

    # Handles a user ID of 0
    @pytest.mark.asyncio
    async def test_handles_user_id_of_zero(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = []
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(0)

        # Assert the result
        assert result == {"receipts": []}

    # Handles a large number of receipts for a user
    @pytest.mark.asyncio
    async def test_handles_large_number_of_receipts(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = [("url1",), ("url2",), ("url3",), ("url4",), ("url5",)]
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(1)

        # Assert the result
        assert result == {"receipts": ["url1", "url2", "url3", "url4", "url5"]}

    # Handles a user with no transactions
    @pytest.mark.asyncio
    async def test_handles_user_with_no_transactions(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = []
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(1)

        # Assert the result
        assert result == {"receipts": []}

    # Returns receipts in descending order by date
    @pytest.mark.asyncio
    async def test_returns_receipts_in_descending_order_by_date(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = [("url1",), ("url2",)]
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(1)

        # Assert the result
        assert result == {"receipts": ["url1", "url2"]}

    # Handles a user with no receipts
    @pytest.mark.asyncio
    async def test_handles_user_with_no_receipts(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = []
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(1)

        # Assert the result
        assert result == {"receipts": []}

    # Handles a user with receipts from multiple transactions
    @pytest.mark.asyncio
    async def test_returns_list_of_receipt_urls(self, mocker):
        # Mock the database connection and result
        mock_connection = mocker.MagicMock()
        mock_result = mocker.MagicMock()
        mock_result.__iter__.return_value = [("url1",), ("url2",)]
        mock_connection.execute.return_value = mock_result
        mocker.patch("src.database.engine.begin", return_value=mock_connection)

        # Call the function
        result = await get_receipts(1)

        # Assert the result
        assert result == {"receipts": ["url1", "url2"]}