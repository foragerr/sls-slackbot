from slack import WebClient
from FastrackStatus import FastrackStatus

class CommandProcessor:

    def __init__(self, slack_key, request_body):
        ''' get bot's user_id '''
        self.slack_key = slack_key
        self.slack_client = WebClient(slack_key)
        self.bot_name = "botty"
        self.bot_id = self.get_bot_id()

        ''' grab event information '''
        self.request_body = request_body
        self.sender = request_body['event']['user']
        self.channel = request_body['event']['channel']
        self.command = request_body['event']['text'].split( '<@' + self.bot_id + '>' )[1].strip().lower()
        
        ''' grab slack thread information '''
        if 'thread_ts' in request_body['event']:
            self.ts = request_body['event']['thread_ts']
        else:
            self.ts = request_body['event']['ts']

        ''' post a message back to slack'''
        message = f"yo <@{self.sender}>, wassup, command is {self.command}"
        self.slack_client.chat_postMessage(
            channel = self.channel,
            text = message,
            thread_ts = self.ts
        )

        if self.command == 'status':
            message = FastrackStatus('foozone').get_message_payload()
            print(message)
            self.slack_client.chat_postMessage(
                channel = self.channel,
                **message,
                thread_ts = self.ts
            )

    def get_bot_id(self):

        api_call = self.slack_client.api_call('auth.test')

        if api_call.get('ok'):
            return api_call.get('user_id')
        return None
