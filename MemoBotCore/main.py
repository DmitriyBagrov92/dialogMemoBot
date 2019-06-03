from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk import interactive_media
from bs4 import BeautifulSoup
import grpc
import os
import json
import requests

def sendPossibleActions(*messageParams):
    print('present possible actions for', messageParams)
    bot.messaging.send_message(
        messageParams[0].peer,
        "Possible MemoBot actions:",
        [interactive_media.InteractiveMediaGroup(
            [
                interactive_media.InteractiveMedia(
                    1,
                    interactive_media.InteractiveMediaButton("Send Memo", "Send Memo")
                ),
                interactive_media.InteractiveMedia(
                    1,
                    interactive_media.InteractiveMediaButton("Stop Memo sending", "Stop Memo sending")
                ),
            ]
        )]
    )

def onActionTap(actionParams):
    print('on action tap for', actionParams)
    imageUrl = getRandomMemeRemoteURL()
    print('fetched meme url', imageUrl)
    imagePath = downloadFileWith(imageUrl)
    print('meme saved at', imagePath)
    peer = bot.users.get_user_outpeer_by_id(actionParams.uid)
    print('got peer, send image...', peer)
    bot.messaging.send_image(peer, imagePath)

def getRandomMemeRemoteURL():
    # sourceUrl = 'https://api.memeload.us/v1/random'
    # newMemeResponse = requests.get(sourceUrl)
    # jsonResponse = json.loads(newMemeResponse.content)
    # return jsonResponse['image']
    sourceUrl = 'https://pikabu.ru/tag/Мемы?n=4'
    response = requests.get(sourceUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    firstMemeDiv = soup.findAll("div", {"class": "story-image__content"})[0]

    memeImgAttrsSet = firstMemeDiv.findNext("img")
    return memeImgAttrsSet.attrs['src']

def downloadFileWith(url):
    response = requests.get(url)
    if response.ok:
        filePath = os.getcwd() + '/meme.jpeg'
        file = open(filePath, "wb+")  # write, binary, allow creation
        file.write(response.content)
        file.close()
        return filePath
    else:
        print("Failed to get the file")

if __name__ == '__main__':
    bot = DialogBot.get_secure_bot(
        'epm.dlg.im:443',  # bot endpoint from environment
        grpc.ssl_channel_credentials(), # SSL credentials (empty by default!)
        'd316f092920d1badf7a3381697419ff89029f9f2'  # bot token from environment
    )

    bot.messaging.on_message(sendPossibleActions, onActionTap)