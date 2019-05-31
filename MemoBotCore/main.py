from dialog_bot_sdk.bot import DialogBot
import grpc
import os


def on_msg(*params):
    bot.messaging.send_message(
        params[0].peer, 'Reply to : ' + str(params[0].message.textMessage.text)
    )


if __name__ == '__main__':
    bot = DialogBot.get_secure_bot(
        'epm.dlg.im:443',  # bot endpoint from environment
        grpc.ssl_channel_credentials(), # SSL credentials (empty by default!)
        'd316f092920d1badf7a3381697419ff89029f9f2'  # bot token from environment
    )

    bot.messaging.on_message(on_msg)