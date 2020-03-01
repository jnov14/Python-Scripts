import requests as request
import time as time
import datetime as datetime
# import RPi.GPIO as GPIO

# pinLED = 16
teamID = '54'  # Calgary Flames is 20
baseURL = 'https://statsapi.web.nhl.com'
scheduleURL = 'https://statsapi.web.nhl.com/api/v1/schedule'


def checkForGame():

    liveGameURL = ''

    response = request.get(scheduleURL, params={'teamId': teamID})
    scheduleJson = response.json()

    if len(scheduleJson['dates']) > 0:
        liveGameURL = scheduleJson['dates'][0]['games'][0]['link']

    return liveGameURL


def getLiveGameJson(liveURL):

    response = request.get(url=baseURL+liveURL)
    liveJson = response.json()

    return liveJson


def getGameState(liveURL):

    liveJson = getLiveGameJson(liveURL)
    gameState = liveJson['gameData']['status']['abstractGameState']

    return gameState


def checkForGoal(liveJson, previousGoalCount, currentGoalCount):

    if currentGoalCount != previousGoalCount:
        latestGoalID = liveJson['liveData']['plays']['scoringPlays'][currentGoalCount - 1]
        latestGoalTeamID = liveJson['liveData']['plays']['allPlays'][latestGoalID]['team']['id']

        # if currentGoalCount > previousGoalCount and (latestGoalTeamID == 54 or latestGoalTeamID == 22):
        # above if is for when both teams are playing and you want to test any goal

        if currentGoalCount > previousGoalCount and latestGoalTeamID == int(teamID):
            # goalLight()
            print('Goal!')
        else:
            previousGoalCount = currentGoalCount
    else:
        teamScoredNotify = False


# def goalLight():

    # for i in range(10):
        # GPIO.output(pinLED, GPIO.HIGH)
        # time.sleep(0.5)
        # GPIO.output(pinLED, GPIO.LOW)
        # time.sleep(0.3)
        # GPIO.output(pinLED, GPIO.HIGH)
        # time.sleep(0.5)
        # GPIO.output(pinLED, GPIO.LOW)
        # time.sleep(0.3)

def main():

    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(pinLED, GPIO.OUT, initial=GPIO.LOW)

    liveGameURL = checkForGame()

    if liveGameURL == '':
        print('No game today.. closing down..')
        quit()

    gameState = getGameState(liveGameURL)

    if gameState == 'Live':

        print('Game is live')

        liveJson = getLiveGameJson(liveGameURL)
        previousGoalCount = len(liveJson['liveData']['plays']['scoringPlays'])

    else:
        previousGoalCount = 0

    while gameState == 'Preview':

        print('Game has not started yet... checking again in 1 minute')

        time.sleep(60)
        gameState = getGameState(liveGameURL)

        if gameState == 'Live':
            break;

    beginTime = datetime.datetime.utcnow()

    while gameState == 'Live':

        liveJson = getLiveGameJson(liveGameURL)

        currentGoalCount = len(liveJson['liveData']['plays']['scoringPlays'])

        checkForGoal(liveJson, previousGoalCount, currentGoalCount)

        gameState = getGameState(liveGameURL)

        previousGoalCount = currentGoalCount

        inIntermission = liveJson['liveData']['linescore']['intermissionInfo']['inIntermission']

        if inIntermission:

            intermissionRemaining = liveJson['liveData']['linescore']['intermissionInfo']['intermissionTimeRemaining']
            time.sleep(intermissionRemaining)

        else:
            time.sleep(2)

    endTime = datetime.datetime.utcnow()

    timeDiff = endTime - beginTime

    totSecs = timeDiff.total_seconds()

    print('This is the number of requests made during ', int(totSecs()/60), 'minutes, requests = ', int(totSecs/2))

    if gameState == 'Final':

        print('Game is now over.. closing down..')
        quit()

    else:
        print('Game state is.. ', gameState, '.. closing down..')


if __name__ == '__main__':

    main()
