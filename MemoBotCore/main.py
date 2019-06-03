from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk import interactive_media
from bs4 import BeautifulSoup
from threading import Timer,Thread,Event
import grpc
import os
import json
import requests

kBotNick = '@memobot'
kPullingTimeInterval = 10
kSubscribeActionId = "0"
kUnsubscribeActionId = "1"

memeSubscribers = {}
lastMemeUrl = ''
localMemePath = os.getcwd() + '/meme.jpeg'

def sendPossibleActions(messageParams):
    print('present possible actions for', messageParams)
    bot.messaging.send_message(
        messageParams[0].peer,
        "Возможные действия:",
        [interactive_media.InteractiveMediaGroup(
            [
                interactive_media.InteractiveMedia(
                    kSubscribeActionId,
                    interactive_media.InteractiveMediaButton("Подписаться на Мемы", "Подписаться на Мемы")
                ),
                interactive_media.InteractiveMedia(
                    kUnsubscribeActionId,
                    interactive_media.InteractiveMediaButton("Отписаться", "Отписаться")
                ),
            ]
        )]
    )

def checkAndPresentActionsIfNeeded(*message):
    textMessage = message[0].message.textMessage.text
    if kBotNick in textMessage:
        sendPossibleActions(message)

def onActionTap(actionParams):
    print('on action tap for', actionParams)
    if actionParams.id == kSubscribeActionId:
        #TODO: send successfuly subscribed message
        memeSubscribers[actionParams.uid] = True
        sendLastMemeTo(actionParams.uid)
    else:
        #TODO: send successfuly unsubscribed message
        memeSubscribers[actionParams.uid] = False

def getFreshestMemeRemoteURL():
    sourceUrl = 'https://pikabu.ru/tag/Мемы?n=4'
    response = requests.get(sourceUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    firstMemeDiv = soup.findAll("div", {"class": "story-image__content"})[0]

    memeImgAttrsSet = firstMemeDiv.findNext("img")
    return memeImgAttrsSet.attrs['src']

def downloadAndSaveMemeWith(url):
    response = requests.get(url)
    if response.ok:
        file = open(localMemePath, "wb+")  # write, binary, allow creation
        file.write(response.content)
        file.close()
    else:
        print("Failed to get the file")

def sendLastMemeTo(uid):
    peer = bot.users.get_user_outpeer_by_id(uid)
    bot.messaging.send_image(peer, localMemePath)

def sendMemeToSubscribersIfNeeded():
    if isNewMemeAvailable():
        #Download Meme and replace on disk
        lastMemeUrl = getFreshestMemeRemoteURL()
        downloadAndSaveMemeWith(lastMemeUrl)
        #Calculate subscriber ids
        print(memeSubscribers)
        onlySubscribed = { k:v for k,v in memeSubscribers.items() if v }
        subscribersUids = onlySubscribed.keys()
        for uid in subscribersUids:
            sendLastMemeTo(uid)

def isNewMemeAvailable():
    return getFreshestMemeRemoteURL() != lastMemeUrl

if __name__ == '__main__':
    bot = DialogBot.get_secure_bot(
        'epm.dlg.im:443',  # bot endpoint from environment
        grpc.ssl_channel_credentials(), # SSL credentials (empty by default!)
        'd316f092920d1badf7a3381697419ff89029f9f2'  # bot token from environment
    )

    memePullingTimer = Timer(kPullingTimeInterval, sendMemeToSubscribersIfNeeded)
    memePullingTimer.start()

    bot.messaging.on_message(checkAndPresentActionsIfNeeded, onActionTap)
