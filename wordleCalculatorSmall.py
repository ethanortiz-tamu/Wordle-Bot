import csv
import time

# returns the result of a guess answer pair
def wordleResult(guess, answer):
    result = [0,0,0,0,0]
    i = 0
    str = {}
    for letter in guess:
        # case for green letter
        if letter == answer[i]:
            result[i] = 2
        # case for yellow or grey letter
        else:
            str[answer[i]] = str.get(answer[i], 0) + 1
        i += 1
    i = 0
    for letter in guess:
        if result[i] !=2:
            # loop through again and look at non greens
            if str.get(letter, 0) > 0:
                # if the letter is not green and is in the answer subtract from our dictionary of the non green letters
                result[i] = 1
                str[letter] = str[letter] - 1

        i += 1
    return result

# returns true if an answer is possible given a guess and result
def isPossibleAnswer(answer, guess, result):
    return wordleResult(guess, answer) == result

# returns all possible answers
def getPossibleAnswers(answerList, guess, result):
    possible = []
    for answer in answerList:
        if isPossibleAnswer(answer, guess, result):
            possible += [answer]
    return possible

# scores all answers
def scoreAnswers(validGuess, validAnswer):
    guessNumbers = []
    i = 0
    ret = []
    # for every guess assume every answer and see how many answers it would eliminate
    # sum total eliminated answers for score
    for guess in validGuess:
        guessNumbers += [0]
        for answer in validAnswer:
            result = wordleResult(guess, answer)
            for ans in validAnswer:
                if not isPossibleAnswer(ans, guess, result):
                    guessNumbers[i] += 1
        ret += [(guess[0][0] + guess[1][0] + guess[2][0] + guess[3][0] + guess[4][0], guessNumbers[i])]
        i += 1
    return ret

# ranks all scores and returns the best guess
def rankScores(scoredWords):
    scoresDict = {}
    scoresList = []
    for row in scoredWords:
        currScore = float(row[1])
        while currScore in scoresList:
            currScore += 1/len(scoresList)
        scoresList += [currScore]
        scoresDict[currScore] = row[0]
    score = max(scoresList)
    return scoresDict[score]

# eliminates guesses that are deemed bad due to letter frequency
def widdle(validAnswers, validGuesses, results):
    letterFreq = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0,
               'm': 0, 'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0,
               'x': 0, 'y': 0, 'z': 0}
    # creates letter frequency for current valid answers
    for answer in validAnswers:
        for letter in answer:
            letterFreq[letter] += 1

    # if a letter is already know as grey do not guess it again
    grey = []
    for entry in results:
        word = entry[0]
        result = entry[1]
        i = 0
        str = ''
        for number in result:
            if number == 0 and word[i] not in str:
                grey += word[i]
            else:
                str = str + word[i]
            i+=1
    i=0

    # if a letter does not appear in any answers consider it grey
    for letter, val in letterFreq.items():
        if val == 0:
            grey += [letter]
        i+=1
    ret = []

    # remove word if they have a grey
    for word in validGuesses:
        good = True
        for letter in grey:
            if letter in word:
                good = False
                break
        if good:
            ret += [word]
    if len(ret) == 0:
        return validGuesses

    return ret

# eliminates more strictly based on letter frequency in remaining answers
def widdleMore(validAnswers, validGuesses):
    letterFreq = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0,
                  'm': 0, 'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0,
                  'x': 0, 'y': 0, 'z': 0}
    for answer in validAnswers:
        for letter in answer:
            letterFreq[letter] += 1
    least = 13000
    worst = ''


    for letter, val in letterFreq.items():
        if val < least and val != 0:
            least = val
            worst = letter
    ret = []
    for word in validGuesses:
        if worst not in word:
            ret += [word]
    used = [worst]
    while len(ret) > 700:
        least = 13000
        nworst = ''
        for letter, val in letterFreq.items():
            if val < least and val != 0 and letter not in used:
                least = val
                nworst = letter
        ret2 = []
        for word in ret:
            if nworst not in word:
                ret2 += [word]
        used += [nworst]
        if len(ret2) == 0:
            return ret
        ret = ret2
    return ret

def runCalcFromInput(validAnswers, validGuesses):
    guess = 'roate'
    results = []
    ret = 0
    while True:
        ret += 1
        print("Guess:", guess)
        result = []
        while(len(result) != 5):
            result = input("Enter Result: ").split(" ")
            if result == 'STOP':
                return
            try:
                for i in range(5):
                    result[i] = int(result[i])
            except:
                result = []
                print("Invalid!")
                continue
            if ret == 1:
                line = firstResult[result[4] + result[3] * 3+ result[2] * 9 + result[1] * 27 + result[0] * 81]
                guess = line[-5:]
                if(guess == "SIBLE"):
                    result = []
                    print("Invalid!")
                    continue
        
        results += [(guess, result)]
        if result == [2,2,2,2,2]:
            break


        validAnswers = getPossibleAnswers(validAnswers, guess, result)
        print("Number of possible Answers:",len(validAnswers))

        
        if ret == 1:
            continue
        
        optimalGuesses = validGuesses
        if len(validAnswers) > 9:
             optimalGuesses = widdle(validAnswers, validGuesses, results)
             if len(optimalGuesses) > 700:
                 optimalGuesses = widdleMore(validAnswers, validGuesses)

        if (len(validAnswers) > 3):
            scoredAnswers = scoreAnswers(optimalGuesses, validAnswers)
            bestScore = rankScores(scoredAnswers)
        else:
            scoredAnswers = scoreAnswers(validAnswers, validAnswers)
            bestScore = rankScores(scoredAnswers)
        guess = bestScore
    print()
    return ret

# get list of words and format them
# get starting outcomes for roate
validGuessFile = open('validGuess.txt', 'r')
validAnswerFile = open('validAnswer2.txt', 'r')
firstResultFile = open('beginning_roate.txt', 'r')
firstResult = firstResultFile.read().split('\n')
validGuess = validGuessFile.read().split('\n')
validAnswer = validAnswerFile.read().split('\n')
firstResultFile.close()
validAnswerFile.close()
validGuessFile.close()

userInput = 'y'

while userInput != 'n':
    validAnswersTemp = []
    for a in validAnswer:
        validAnswersTemp += [a]
    validGuessesTemp = []
    for g in validGuess:
        validGuessesTemp += [g]
    runCalcFromInput(validAnswersTemp, validGuessesTemp)
    userInput = input('Would you like to continue (y / n): ')