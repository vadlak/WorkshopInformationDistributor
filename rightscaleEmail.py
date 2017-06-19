import requests, json, os, httplib2, oauth2client, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from oauth2client import client, tools, file
from apiclient import errors, discovery

global ssh_key, refresh_token, emails, deployment_id,sender_email

servers = []

authEndpoint = "https://us-4.rightscale.com/api/oauth2"
baseEndpoint = "https://us-4.rightscale.com"

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'KeyDistributor'



def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def sendMessage(sender, to, subject, msg):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    email = createMessage(sender, to, subject, msg)

    try:
        message = (service.users().messages().send(userId=sender_email, body=email).execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        return "Error"


def createMessage(sender, to, subject, body):
    message = MIMEMultipart('mixed')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to
    message.attach(MIMEText(body))

    content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    msg = MIMEText(ssh_key, _subtype=sub_type)

    msg.add_header('Content-Disposition', 'attachment', filename="sshKey")
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def getAccessToken(refreshToken, authEndpoint, apiVersion):
    oauthObject = requests.post(
                                    authEndpoint,
                                    data={'grant_type':'refresh_token', 'refresh_token':refreshToken},
                                    headers = {'X-API-Version': apiVersion}
                                )
    parsedAuthObject = json.loads(oauthObject.text)
    return parsedAuthObject["access_token"]

def rightScaleAPIRequest(accessToken, request, apiVersion):
    request = requests.get(
        baseEndpoint + request,
        headers={"X_API_VERSION": apiVersion, "Authorization": "Bearer " + accessToken},
    )
    return json.loads(request.text)


def sendEmails():
    global emails, servers
    credentials = get_credentials()

    for i in range(0, len(emails)):
        instanceURL = servers[i]["links"][2]["href"]
        instance = rightScaleAPIRequest(accessToken, instanceURL, "1.5")
        sendMessage(sender_email, emails[i],
                    "DataStax Data n' Drinks Workshop - June 14th",
                    "Hello,\n\nWelcome to DataStax's Data N Drinks Workshop on June 14th."
                    " Attached you'll find the necessary information to log into your DSE Node, "
                    "including the SSH Key, Username and Public IP Address.\n\nUsername: ds_user\nPublic IP Address: "
                    + instance["public_ip_addresses"][0] + "\n\nThank You")

def init_email_list():
    global emails
    file = open("emails.txt", "rb")
    emails = file.readlines()
    file.close()

if __name__ == "__main__":

    config = {}
    exec(open("config.conf").read(), config)
    ssh_key = config["ssh_key"]
    refresh_token = config["rightscale_refresh_token"]
    deployment_id = config["deployment_id"]
    sender_email=config["sender_email"]

    init_email_list()

    accessToken = getAccessToken(refresh_token, authEndpoint, "1.5")
    servers = rightScaleAPIRequest(accessToken, "/api/deployments/" + deployment_id + "/servers", "1.5")
    if len(servers) > len(emails):
        print "More servers than emails, proceeding regardless"
        sendEmails()
    elif len(servers) < len(emails):
        print "More emails than servers, not proceeding"
    elif len(servers) == len(emails):
        sendEmails()


