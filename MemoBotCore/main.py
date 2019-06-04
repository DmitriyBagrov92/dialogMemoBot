from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk import interactive_media
from bs4 import BeautifulSoup
from threading import Timer,Thread,Event
import time
import grpc
import os
import json
import requests

k_bot_nick = '@memobot'
k_subscribe_here_command = '/start @memobot'
k_pulling_interval = 30
k_subscribe_action_id = "0"
k_unsubscribe_action_id = "1"

meme_subscribers_peers = {}
local_meme_path = os.getcwd() + '/meme.jpeg'

def send_possible_actions(messageParams):
    print('present possible actions for', messageParams)
    # bot.messaging.send_message(
    #     messageParams[0].peer,
    #     "Возможные действия:",
    #     [interactive_media.InteractiveMediaGroup(
    #         [
    #             interactive_media.InteractiveMedia(
    #                 k_subscribe_action_id,
    #                 interactive_media.InteractiveMediaButton("Подписаться на Мемы", "Подписаться на Мемы")
    #             ),
    #             interactive_media.InteractiveMedia(
    #                 k_unsubscribe_action_id,
    #                 interactive_media.InteractiveMediaButton("Отписаться", "Отписаться")
    #             ),
    #         ]
    #     )]
    # )
    bot.messaging.send_message(messageParams[0].peer, "Для подписки на свежие мемы отправьте /start @memobot")

def check_and_present_actions_if_needed(*message):
    textMessage = message[0].message.textMessage.text
    if k_subscribe_here_command in textMessage:
        peer = message[0].peer
        print(dir(peer))
        meme_subscribers_peers[peer.id] = peer
        bot.messaging.send_message(peer, "Подписка оформлена успешно")
        send_last_meme_to(peer)
    elif k_bot_nick in textMessage:
        send_possible_actions(message)

def on_action_tap(actionParams):
    print('on action tap for', actionParams)
    if actionParams.id == k_subscribe_action_id:
        #TODO: send successfuly subscribed message
        # meme_subscribers[actionParams.uid] = True
        send_last_meme_to(actionParams.uid)
    # else:
        #TODO: send successfuly unsubscribed message
        # meme_subscribers[actionParams.uid] = False

def get_freshest_meme_remote_URL():
    sourceUrl = 'https://pikabu.ru/tag/Мемы?n=4'
    response = requests.get(sourceUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    firstMemeDiv = soup.findAll("div", {"class": "story-image__content"})[0]

    memeImgAttrsSet = firstMemeDiv.findNext("img")
    return memeImgAttrsSet.attrs['src']

def download_and_save_meme_with(url):
    response = requests.get(url)
    if response.ok:
        file = open(local_meme_path, "wb+")  # write, binary, allow creation
        file.write(response.content)
        file.close()
    else:
        print("Failed to get the file")

def send_last_meme_to(peer):
    bot.messaging.send_image(peer, local_meme_path)
    print("Meme sent to subscriber", peer)

def send_meme_to_subscribers_if_needed():
    print("Checking for new Meme...")
    while True:
        if is_new_meme_available():
            print("New Meme Available, send to subscribers...")
            #Download Meme and replace on disk
            global lastMemeUrl
            lastMemeUrl = get_freshest_meme_remote_URL()
            download_and_save_meme_with(lastMemeUrl)
            #Calculate subscriber ids
            print(meme_subscribers_peers)
            onlySubscribed = { k:v for k,v in meme_subscribers_peers.items() if v is not None }
            subscribersPeers = onlySubscribed.values()
            for peer in subscribersPeers:
               send_last_meme_to(peer)
        else:
            print("New meme is not available=(")
        time.sleep(k_pulling_interval)

def is_new_meme_available():
    newMemeUrl = get_freshest_meme_remote_URL()
    print("previous = ", lastMemeUrl)
    return newMemeUrl != lastMemeUrl

if __name__ == '__main__':
    bot = DialogBot.get_secure_bot(
        os.environ.get('BOT_ENDPOINT'),  # bot endpoint from environment
        grpc.ssl_channel_credentials(), # SSL credentials (empty by default!)
        os.environ.get('BOT_TOKEN')  # bot token from environment
    )

    memePullingThread = Thread(target=send_meme_to_subscribers_if_needed)
    memePullingThread.start()

    lastMemeUrl = ""

    bot.messaging.on_message(check_and_present_actions_if_needed, on_action_tap)
