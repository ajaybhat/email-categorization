import io

import win32com.client


class OutlookLib:
    def __init__(self, settings=None):
        if not settings:
            settings = {}
        self.settings = settings

    def get_messages(self, user, folder="Inbox", match_field="all", match="all"):
        outlook = win32com.client.Dispatch("Outlook.Application")
        myfolder = outlook.GetNamespace("MAPI").Folders[user]
        inbox = myfolder.Folders[folder]  # Inbox
        if match_field == "all" and match == "all":
            return inbox.Items
        else:
            messages = []
            for msg in inbox.Items:
                try:
                    if match_field == "Sender":
                        if msg.SenderName.find(match) >= 0:
                            messages.append(msg)
                    elif match_field == "Subject":
                        if msg.Subject.find(match) >= 0:
                            messages.append(msg)
                    elif match_field == "Body":
                        if msg.Body.find(match) >= 0:
                            messages.append(msg)

                except:
                    pass
            return messages

    def get_body(self, msg):
        return msg.Body

    def get_subject(self, msg):
        return msg.Subject

    def get_sender(self, msg):
        return msg.SenderName

    def get_recipient(self, msg):
        return msg.To

    def get_attachments(self, msg):
        return msg.Attachments


outlook = OutlookLib()
messages = outlook.get_messages('x@y.com')
count = 0
messages = [message for message in messages if hasattr(message, 'To')]
print 'Got {} messages'.format(len(messages))
for message in messages:
    if count >= 45:
        break
    count += 1
    sender, receiver, subject, body = message.SenderName, message.To, message.Subject, message.Body.replace(
        '(From:).+(\r\n|\n|\\s)(Sent:).+(\r\n|\\s|\n)(To:).+(\r\n|\\s|\n)', '')
    with io.open('../email_dataset/{}.txt'.format(count), 'w', encoding='utf-8', newline='\n') as email_file:
        email_file.write(u'{}\n{}\n{}\n{}\n'.format(sender, receiver, subject, body))
print 'Wrote {} messages'.format(count)

