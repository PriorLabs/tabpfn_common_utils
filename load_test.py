import sys
import os.path

sys.path.append("../")
from pathlib import Path
import os
import random
import uuid
import requests
import argparse
from app.main import ENDPOINTS
from enum import Enum
from utils import to_oauth_request_form
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_PATH = Path(__file__).parent.resolve()


class RequestType(Enum):
    DEFAULT = 0
    REGISTER = 1
    LOGIN = 2
    PROTECTED_ROOT = 3
    UPLOAD_TRAIN_SET = 4
    PREDICT = 5


# Fixed User Credentials
user_credentials_template = {
    "password": "Test1@123",
    "password_confirm": "Test1@123",
    "validation_link": "tabpfn",
}


def parse_args():
    """
    Parse command line arguments
        1. Server URL
        2. Number of total users
            - default: 10 users
        3. Number of parallel requests
            - default: 10 users hitting the server at the same time.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_url",
        type=str,
        default="https://tabpfn-server-wjedmz7r5a-ez.a.run.app",
        help="Server URL",
    )
    parser.add_argument("--num_users", type=int, default=10, help="Number of Users")
    parser.add_argument(
        "--num_requests", type=int, default=10, help="Number of parallel requests"
    )
    return parser.parse_args()


def generate_user_email_address():
    """
    Generate a random email address for a user:
    This can generate around 16^32 unique email addresses as of now and
    can be increased by increasing the length of the UUID. So the probability
    of generating the same email address for the second time is very low.
    Approximately, there would be a possibility of
    1 - (16^32! / (16^32^100 * (16^32 - 100)!)) for atleast 1 collision for
    100 generated UUIDs which is significantly low due to increasing combinations
    """
    random_uuid = uuid.uuid4().hex.replace("%", "")
    domain_name = random.choice(["gmail.com", "outlook.org", "yahoo.in", "hotmail.com"])
    random_email = "user" + f"{random_uuid}@{domain_name}"
    return random_email


def api_request(url, data=None, headers=None, type=RequestType.DEFAULT, files=None):
    """
    Make an API request to the server:
    type:
    1. Register API
    2. Login API
    3. Protected Root API
    4. Upload Train Set API
    5. Upload Test Set API / Predict API
    """
    response = None
    if type == RequestType.REGISTER:
        response = requests.post(url, params=data)
    elif type == RequestType.LOGIN:
        response = requests.post(url, data=data)
    elif type == RequestType.PROTECTED_ROOT:
        response = requests.get(url, headers=headers)
    elif type == RequestType.UPLOAD_TRAIN_SET:
        response = requests.post(url, headers=headers, files=files)
    elif type == RequestType.PREDICT:
        response = requests.post(url, headers=headers, params=data, files=files)
    else:
        raise NotImplementedError(f"Response type {type} is not implemented")
    return response.json()


def process_user(user, SERVER_URL):
    """
    Process a user:
       1. Register the user
       2. Login the user
       3. Access the protected root
       4. Upload a train set
       5. Upload a test set
       6. Predict on the test set
    Inputs:
       user: User ID: 1, 2, 3, ...
    """
    email = generate_user_email_address()
    # Combine user data with user_credentials_template and unique email
    user_data = {"email": email, **user_credentials_template, user: user}

    # Register API: Registers a new user
    register_api = SERVER_URL + ENDPOINTS.register.path
    _ = api_request(register_api, user_data, type=RequestType.REGISTER)
    # print(response_register)

    # Login API: Authenticates the user JUST REGISTERED
    request_data = to_oauth_request_form(email, user_credentials_template["password"])
    login_api = SERVER_URL + ENDPOINTS.login.path
    response_login = api_request(login_api, request_data, type=RequestType.LOGIN)
    # print(response_login)

    # Protected Root API: Access the protected root
    user_access_token = response_login["access_token"]
    headers = {"Authorization": f"Bearer {user_access_token}"}
    protected_api = SERVER_URL + ENDPOINTS.protected_root.path
    _ = api_request(
        protected_api, headers=headers, type=RequestType.PROTECTED_ROOT
    )
    # print(response_protected)

    # Upload Train Set API: Upload a train set
    upload_train_set_api = SERVER_URL + ENDPOINTS.upload_train_set.path
    ## Get the path of the train set
    x_train_path = os.path.join(BASE_PATH, "datasets", "X_train.csv")
    y_train_path = os.path.join(BASE_PATH, "datasets", "y_train.csv")
    files = {
        "x_file": ("X_train.csv", open(x_train_path, "rb"), "application/csv"),
        "y_file": ("y_train.csv", open(y_train_path, "rb"), "application/csv"),
    }
    upload_train_set_response = api_request(
        upload_train_set_api,
        headers=headers,
        type=RequestType.UPLOAD_TRAIN_SET,
        files=files,
    )

    # Upload Test Set API: Upload a test set
    ## Get the path of the train set
    x_test_path = os.path.join(BASE_PATH, "datasets", "X_test.csv")
    files_test = {"x_file": ("X_test.csv", open(x_test_path, "rb"), "application/csv")}
    data = {"train_set_uid": upload_train_set_response["train_set_uid"]}
    # THIS IS FOR INTERNAL USE ONLY
    # upload_test_set_api = SERVER_URL + ENDPOINTS.upload_test_set.path
    # upload_test_set_response = api_request(
    #     upload_test_set_api,
    #     data=data,
    #     headers=headers,
    #     type=RequestType.PREDICT,
    #     files=files_test
    # )
    # print(upload_test_set_response)

    # USE ANY OF THE FOLLOWING 2 APIs: PREDCIT OR PREDICT PROBA

    # Predict Proba API: Predict probabilities on the test set
    # predict_proba_api = SERVER_URL + ENDPOINTS.predict_proba.path
    # predict_response = api_request(
    #     predict_proba_api,
    #     data=data,
    #     headers=headers,
    #     type=RequestType.PREDICT,
    #     files=files_test
    # )

    # Predict API: Predict on the test set
    predict_api = SERVER_URL + ENDPOINTS.predict.path
    predict_response = api_request(
        predict_api,
        data=data,
        headers=headers,
        type=RequestType.PREDICT,
        files=files_test,
    )
    # print(predict_response)
    return predict_response


def main():
    """
    Usage:
    `python load_test.py --num_users=100 --num_requests=10 --server_url='http://0.0.0.0/'
    """
    # Generate a list of parsed arguments
    args = parse_args()
    # Set the server URL
    SERVER_URL = args.server_url
    # Number of total users
    num_users = args.num_users
    # Generate a list of users
    users = range(1, num_users + 1)

    # Number of parallel requests
    num_parallel_requests = args.num_requests

    with ThreadPoolExecutor(max_workers=num_parallel_requests) as executor:
        # Submit tasks for each user
        futures = {
            executor.submit(process_user, user, SERVER_URL): user for user in users
        }

        # Wait for all tasks to complete
        for future in as_completed(futures):
            user = futures[future]
            try:
                result = future.result()
                print(f"User {user} processed successfully. Result: {result}")
            except Exception as e:
                print(f"Error processing user {user}: {e}")


if __name__ == "__main__":
    main()
