import json
import sqs

class FastrackStatus:
    """Constructs a fastrack status message"""

    HEADER_BLOCK = {
			"type": "context",
			"elements": [
				{
					"text": "*─=≡Fastrack*  | lmb2 | :large_blue_circle: Active | Next deployment at <12:00PM>",
					"type": "mrkdwn"
				}
			]
		}
    
    QUEUE_HEADER_BLOCK = {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": " *Deploy Queue*"
			}
		}

    DIVIDER_BLOCK = {"type": "divider"}

    FOOTER_BLOCK = {
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": ":pushpin: Tag @bre-goalie for help"
				}
			]
		}

    def __init__(self, zone):
        self.zone = zone
        self.username = "botty"
        self.icon_emoji = ":robot_face:"

    def get_message_payload(self):
        return {
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                *self._get_header_block(),
                self.DIVIDER_BLOCK,
                self.QUEUE_HEADER_BLOCK,
                *self._get_queue_items_block(),
                self.DIVIDER_BLOCK,
                self.FOOTER_BLOCK
            ],
        }
    
    @staticmethod
    def _get_fastrack_status_icon(enabled: bool) -> str:
        if enabled:
            return ":large_blue_circle:"
        return ":x:"

    @staticmethod
    def _get_fastrack_status(zone :str) -> str:
        return f"{FastrackStatus._get_fastrack_status_icon(True)} Active"

    @staticmethod
    def _get_next_fastrack_deploy_timestamp(zone :str) -> str:
        return '12:00PM'

    def _get_header_block(self):
        fastrack_status = self._get_fastrack_status(self.zone)
        fastrack_time = self._get_next_fastrack_deploy_timestamp(self.zone)
        
        text = (
            f"*─=≡Fastrack*  | lmb2 | {fastrack_status} | Next deployment at {fastrack_time}"
        )

        return [
            {"type": "context", "elements": [{"type": "mrkdwn", "text": text}]},
        ]

    @staticmethod
    def _get_fastrack_queue_items(zone :str):
        return sqs.peek_messages()

    def _get_queue_items_block(self):
        queue_items = self._get_fastrack_queue_items(self.zone)
        queue_items_block = []

        for item in queue_items:
            queue_items_block.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"> *{item['name']}* | {item['versionfrom']}  *->*  {item['versionto']} | <http://www.foo.com | Changelog> | {item['requestor']}"
                    }
                }
            )

        return queue_items_block



# test
# fs = FastrackStatus('zoneasdf')
# print(json.dumps(fs.get_message_payload(), indent=2))
