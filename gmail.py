##################################################
## Project: PTT Goods Trace
## Author: {Chun}
## Version: {190827}
## Status:
##################################################

# Gmail API Requirements
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes, os

# Google API Credentials Requirements
import httplib2
from apiclient import discovery
from oauth2client.file import Storage
from oauth2client import file, client, tools


SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret_gmail.json'
APPLICATION_NAME = 'Gmail API'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials():
    credential_path = os.path.join("./", 'google-api-credential.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Credentials is saved to: ' + credential_path)
    return credentials

def SendMessage(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message).execute())
    print('Message Id: %s' % message['id'])
    return message
  except:
    print('An error occurred: %s' % error)


def CreateMessage(sender, to, data):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    data: The articles of tracing goods.

  Returns:
    An object containing a base64url encoded email object.
  """
  content = ''
  for item in data:
      meta = item['content']['meta']
      good_info = item['content']['good_info']

      content += ('\n').join([meta['title'], '[物品規格]: '+good_info['[物品規格]'], '[交易地點]: '+good_info['[交易地點]'], '[交易方式]: '+good_info['[交易方式]'], '[交易價格]; '+good_info['[交易價格]'], item['url']])
      content +='\n\n'
      content += '------------------------------------------------------------\n'
      content +='\n\n'

  # print(content)
  title = ('').join(['您追蹤的', target_good, '有', str(len(data)), '則新貼文！'])

  message = MIMEText(content)
  message['to'] = to
  message['from'] = sender
  message['subject'] = title
  raw = base64.urlsafe_b64encode(bytes(str(message), "utf-8"))
  return {'raw': raw.decode()}
  # return {'raw': base64.urlsafe_b64encode(message.as_string())}


def CreateMessageWithAttachment(sender, to, subject, message_text, file_dir, filename):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file_dir: The directory containing the file to be attached.
    filename: The name of the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEMultipart()
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  msg = MIMEText(message_text)
  message.attach(msg)

  path = os.path.join(file_dir, filename)
  content_type, encoding = mimetypes.guess_type(path)

  if content_type is None or encoding is not None:
    content_type = 'application/octet-stream'
  main_type, sub_type = content_type.split('/', 1)
  if main_type == 'text':
    fp = open(path, 'rb')
    msg = MIMEText(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'image':
    fp = open(path, 'rb')
    msg = MIMEImage(fp.read(), _subtype=sub_type)
    fp.close()
  elif main_type == 'audio':
    fp = open(path, 'rb')
    msg = MIMEAudio(fp.read(), _subtype=sub_type)
    fp.close()
  else:
    fp = open(path, 'rb')
    msg = MIMEBase(main_type, sub_type)
    msg.set_payload(fp.read())
    fp.close()

  msg.add_header('Content-Disposition', 'attachment', filename=filename)
  message.attach(msg)

  return {'raw': base64.urlsafe_b64encode(message.as_string())}


if __name__ == '__main__':
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    user_profile = service.users().getProfile(userId='me').execute()
    sender_email = user_profile['emailAddress']

    print(user_profile)
    print(sender_email)
    
    mes = CreateMessage(sender_email, sender_email, 'Test', 'test')
    # SendMessage(service, sender_email, mes)
