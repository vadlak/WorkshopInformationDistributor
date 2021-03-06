# 1. Install Dependencies

```
pip install google-api-python-client oauth2client apiclient requests
```

# 2. Download and set your google client secret

- Follow the instructions at https://developers.google.com/gmail/api/quickstart/python#step_1_turn_on_the_api_name
- Place the resulting client_secrets.json file in this project folder

# 3. Set configuration values

- sender_email: Set this to the sender's email address
- deployment_id: The deployment id of your RightScale deployment

![Screenshot](images/DeploymentId.png)

- rightscale_refresh_token: Your RightScale API refresh token
    1. Navigate to Settings > API Credentials
    2. Enable the personal token
    3. Copy the resulting refresh token

- ssh_key: The SSH Key you wish to send as an attachment

# 4. Set recipient emails

- Enter a newline separated list of emails into emails.txt

# 5. Customize the email message

- Modify the string on line 55 of rightscaleEmail.py

# 6. Execute the script

```
python rightscaleEmail.py
```