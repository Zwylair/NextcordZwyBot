import asyncio

import requests
import nextcord.ext.commands


class AutoSender:
    
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot
        self.main_auth_header = {
            'authorization':
                'OTExNzE1NjE3MTE0MDQyMzk4.Gl7YBg.AfgvKBBKuBHsXZDwO6_MjuUDI2HlAeBOSLMKI0',
            'content-type':
                'application/json',
            'cookie':
                '__dcfduid=c9fcb4108b3211ec8f293d10d155e283; __sdcfduid=c9fcb4118b3211ec8f293d10d155e28326a47b852c3975a42c1f726c403c77ac357754da507176501c13e003636cc076; __stripe_mid=5e3cb7c5-d4da-4a4f-aab1-a35423a05c510602cd; __cfruid=235bef1b180450cda6602b78709e8adaf0cac224-1679136889; locale=uk'
        }
        self.seco_auth_header = {
            'authorization':
                'OTE0MTA0OTE4NzQ5NjE0MDkx.GdG_pM.IdnH0UHgu7ZTIWJtOLxhF804FphPT8OlxHe4QA',
            'content-type':
                'application/json',
            'cookie':
                '__dcfduid=c9fcb4108b3211ec8f293d10d155e283; __sdcfduid=c9fcb4118b3211ec8f293d10d155e28326a47b852c3975a42c1f726c403c77ac357754da507176501c13e003636cc076; __stripe_mid=5e3cb7c5-d4da-4a4f-aab1-a35423a05c510602cd; __cfruid=89c64511abb97c729eb5da87509a07b91041f215-1679669357; __stripe_sid=f7c5e2e1-9e03-4494-96c4-f5a8038c1e2c9010f1; locale=ru'
        }
        self.json = {
            'content': "!work",
            'nonce': "1086626548531855390",
            'tts': False,
            'flags': 0
        }
        self.json2 = {
            'content': "!dep all",
            'nonce': "1086626548531855390",
            'tts': False,
            'flags': 0
        }
    
    async def poll(self):
        while True:
            for header in [self.main_auth_header, self.seco_auth_header]:
                for i in range(9999):
                    nonce = int(self.json['nonce']) + i
                    self.json['nonce'] = str(nonce)
                    
                    req = requests.post(
                        'https://discord.com/api/v9/channels/981167385979527174/messages',
                        json=self.json,
                        headers=header)
                    if 'referenced_message' in req.json():
                        self.json['nonce'] = f'{int(req.json()["nonce"]) + 1}'
                        self.json2['nonce'] = f'{int(req.json()["nonce"]) + 2}'
                        
                        await asyncio.sleep(1)
                        
                        requests.post(
                            'https://discord.com/api/v9/channels/981167385979527174/messages',
                            json=self.json2,
                            headers=header)
                        
                        self.json['nonce'] = f'{int(self.json2["nonce"]) + 1}'
                        self.json2['nonce'] = f'{int(self.json2["nonce"]) + 1}'
                        break
            
            await asyncio.sleep(60 * 30)
