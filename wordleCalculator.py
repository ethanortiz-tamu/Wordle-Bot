import csv
import time
import os
from functools import wraps
from functools import lru_cache
import random
import pickle
import os
from functools import wraps

def cache_function_output(storage_path):
    def decorator(func):
        cache_file = os.path.join(storage_path, f"{func.__name__}_cache.pkl")

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use a tuple of arguments and keyword arguments as the cache key
            key = args[0] if args else None 
            
            # Create the storage directory if it doesn't exist
            os.makedirs(storage_path, exist_ok=True)

            # Check if the cache file exists
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as file:
                    cache = pickle.load(file)
            else:
                cache = {}

            # Check if the result is already in the cache
            if key in cache:
                # print(f"Cache hit for {func.__name__}{key}")
                return cache[key]

            # If not in cache, compute the result and store it
            result = func(*args, **kwargs)
            cache[key] = result
            # print(f"Caching result for {func.__name__}{key}")

            # Save the updated cache to the file
            with open(cache_file, 'wb') as file:
                pickle.dump(cache, file)

            return result
    
        def remove_cache(*args, **kwargs):
            # Remove cache based on specified criteria
            key_to_remove = args[0] if args else None

            if key_to_remove:
                try:
                    with open(cache_file, 'rb') as file:
                        cache = pickle.load(file)
                        if key_to_remove in cache:
                            del cache[key_to_remove]
                            with open(cache_file, 'wb') as file:
                                pickle.dump(cache, file)
                            print(f"Cache for {func.__name__}{key_to_remove} removed.")
                        else:
                            print(f"No cache found for {func.__name__}{key_to_remove}.")
                except FileNotFoundError:
                    print("Cache file not found.")

        wrapper.remove_cache = remove_cache
        return wrapper

    return decorator

def memoize(func):
    """Memoization decorator."""
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper

# returns the result of a guess answer pair
def wordleResult(guess, answer):
    result = [0,0,0,0,0]
    i = 0
    str = ""
    for letter in guess:
        # case for green letter
        if letter == answer[i]:
            result[i] = 2
        # case for yellow or grey letter
        else:
            str += answer[i]
        i += 1
    i = 0
    for letter in guess:
        if result[i] !=2:
            # loop through again and look at non greens
            j = 0
            for l in str:
                if letter == l:
                    result[i] = 1
                    str = str[:j] + str[j+1:]
                j+=1
        i += 1
    return (result[0], result[1], result[2], result[3], result[4])

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
    # print("Number of possible Answers:", len(validAnswer))
    guessNumbers = []
    i = 0
    ret = []
    maxScore = -1
    max = validGuess[0]
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
        if guessNumbers[i] > maxScore:
            maxScore = guessNumbers[i]
            max = guess
        i += 1
    # print(maxScore)
    return max

# scores all answers
def bestAnswer(validGuess, validAnswer):
    i = 0
    maxScore = 0
    max = validGuess[0]
    # for every guess assume every answer and see how many answers it would eliminate
    # sum total eliminated answers for score
    for guess in validGuess:
        currScore = 0
        for answer in validAnswer:
            result = [0,0,0,0,0]
            i = 0
            str = ""
            for letter in guess:
                # case for green letter
                if letter == answer[i]:
                    result[i] = 2
                # case for yellow or grey letter
                else:
                    str += answer[i]
                i += 1
            i = 0
            for letter in guess:
                if result[i] !=2:
                    # loop through again and look at non greens
                    j = 0
                    for l in str:
                        if letter == l:
                            result[i] = 1
                            str = str[:j] + str[j+1:]
                        j+=1
                i += 1
            for ans in validAnswer:
                
                result2 = [0,0,0,0,0]
                i = 0
                str = ""
                for letter in guess:
                    # case for green letter
                    if letter == ans[i]:
                        result2[i] = 2
                    # case for yellow or grey letter
                    else:
                        str += answer[i]
                    i += 1
                i = 0
                for letter in guess:
                    if result2[i] !=2:
                        # loop through again and look at non greens
                        j = 0
                        for l in str:
                            if letter == l:
                                result[i] = 1
                                str = str[:j] + str[j+1:]
                            j+=1
                    i += 1
                if result2 != result:
                    currScore += 1
        if(currScore > maxScore):
            max = guess
            maxScore = currScore
    return max

# scores all answers and saves to a csv to determine best starting word
def scoreAnswersAndSave():
    inFile = open('newScored.csv', 'r')
    scored = inFile.read().split('\n')
    scored.pop()
    inFile.close()
    guessNumbers = []
    i = 0
    for s in scored:
        scored[i] = s.split(',')[0]
        guessNumbers += [int(s.split(',')[1])]
        i+=1
    outFile = open('newScored.csv', 'a', newline='')
    outCSV = csv.writer(outFile)
    best = validGuess[0]
    max = 0
    i = 0
    for guess in validGuess:
        guessNumbers += [0]
        if guess in scored:
            if guessNumbers[i] > max:
                max = guessNumbers[i]
                best = guess
                print('MAX:', guess, max)
            i += 1
            continue
        for answer in validAnswer:
            result = wordleResult(guess, answer)
            for ans in validAnswer:
                if not isPossibleAnswer(ans, guess, result):
                    guessNumbers[i] += 1
        outCSV.writerow([guess[0][0] + guess[1][0] + guess[2][0] + guess[3][0] + guess[4][0], guessNumbers[i]])
        if guessNumbers[i] > max:
            max = guessNumbers[i]
            best = guess
            print('MAX:', guess, max)
        i += 1
    outFile.close()

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
    for answer in validAnswers:
        for letter in answer:
            letterFreq[letter] += 1
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
    for letter, val in letterFreq.items():
        if val == 0:
            grey += [letter]
        i+=1
    ret = []
    while(len(grey) > 18):
        grey.remove(grey[len(grey)-1])
    for word in validGuesses:
        bool = True
        for letter in grey:
            if letter in word:
                bool = False
                break
        if bool:
            ret += [word]
    # print("Widdled! Down to", len(ret), "from",len(validGuess))

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
    # print("Widdled More! Down to", len(ret), "from",len(validGuess))
    return ret

def runCalc(validAnswers, validGuesses, secretAnswer):
    guess = 'roate'
    results = []
    ret = 0
    while True:
        ret += 1
        print("Guess:", guess)
        result = wordleResult(guess,secretAnswer)
        results += [(guess, result)]
        if result == (2, 2, 2, 2, 2):
            break

        validAnswers = getPossibleAnswers(validAnswers, guess, result)
        print("Number of possible Answers:", len(validAnswers))
        if ret == 1 and len(validAnswers) > 10:
            firstResultFile = open('beginning_roate.txt', 'r')
            firstResult = firstResultFile.read().split('\n')
            firstResultFile.close()
            line = firstResult[result[4] + result[3] * 3 + result[2] * 9 + result[1] * 27 + result[0] * 81]
            guess = line[-5:]
            print("used save")
            continue

        optimalGuesses = validGuesses
        # optimalGuesses = widdle(validAnswers, validGuesses, results)
        # if len(optimalGuesses) > 700:
            # optimalGuesses = widdleMore(validAnswers, validGuesses)

        if (len(validAnswers) > 3):
            bestScore = scoreAnswers(optimalGuesses, validAnswers)
        else:
            bestScore = scoreAnswers(validAnswers, validAnswers)
        guess = bestScore
    print()
    return ret

def runCalcFromInput(validAnswers, validGuesses, firstResult):
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
        results += [(guess, result)]
        if result == [2,2,2,2,2]:
            break



        if ret == 1:
            line = firstResult[result[4] + result[3] * 3+ result[2] * 9 + result[1] * 27 + result[0] * 81]
            guess = line[-5:]
            while(guess == "SIBLE"):
                print("Invalid!")
                result = input("Enter Result: ").split(" ")
                if result == 'STOP':
                    return
                try:
                    for i in range(5):
                        result[i] = int(result[i])
                    line = firstResult[result[4] + result[3] * 3+ result[2] * 9 + result[1] * 27 + result[0] * 81]
                    guess = line[-5:]
                except:
                    result = []
                    continue
            
            validAnswers = getPossibleAnswers(validAnswers, guess, result)
            print("Number of possible Answers:",len(validAnswers))
            continue
        
        validAnswers = getPossibleAnswers(validAnswers, guess, result)
        print("Number of possible Answers:",len(validAnswers))
        
        optimalGuesses = validGuesses
        if len(validAnswers) > 9:
             optimalGuesses = widdle(validAnswers, validGuesses, results)
             if len(optimalGuesses) > 700:
                 optimalGuesses = widdleMore(validAnswers, validGuesses)

        if (len(validAnswers) > 3):
            bestScore = scoreAnswers(optimalGuesses, validAnswers)
        else:
            bestScore = scoreAnswers(validAnswers, validAnswers)
        guess = bestScore
    print()
    return ret

def writeBeginning(guess, validAnswers, validGuesses):
    for i in range(0, 3*3*3*3*3):
        beginningFile = open('beginning_' + guess + '.txt', 'a')
        results = []
        result = [0,0,0,0,0]

        # write code to increment through all possible results
        temp = i
        result[4] = temp % 3
        temp = temp // 3
        result[3] = temp % 3
        temp = temp // 3
        result[2] = temp % 3
        temp = temp // 3
        result[1] = temp % 3
        temp = temp // 3
        result[0] = temp % 3

        results += [(guess, result)]

        validAnswersTemp = []
        for a in validAnswers:
            validAnswersTemp += [a]
        validGuessesTemp = []
        for g in validGuesses:
            validGuessesTemp += [g]
        validAnswersTemp = getPossibleAnswers(validAnswersTemp, guess, result)
        if len(validAnswersTemp) == 0:
            beginningFile.write(
                str(result[0]) + ' ' + str(result[1]) + ' ' + str(result[2]) + ' ' + str(result[3]) + ' ' + str(
                    result[4]) + ' ' + "NOT_POSSIBLE" + '\n')
            continue
        print("Number of possible Answers:", len(validAnswersTemp))
        optimalGuesses = validGuessesTemp
        if len(validAnswers) > 80:
            optimalGuesses = widdle(validAnswersTemp, validGuessesTemp, results)
            if len(optimalGuesses) > 700:
                optimalGuesses = widdleMore(validAnswersTemp, validGuessesTemp)

        if (len(validAnswers) > 3):
            bestScore = scoreAnswers(optimalGuesses, validAnswers)
        else:
            bestScore = scoreAnswers(validAnswers, validAnswers)
        beginningFile.write(str(result[0]) + ' ' + str(result[1]) + ' ' + str(result[2]) + ' ' + str(result[3]) + ' ' + str(result[4]) + ' ' + bestScore + '\n')
        print('Wrote!')
        print(str(result[0]) + ' ' + str(result[1]) + ' ' + str(result[2]) + ' ' + str(result[3]) + ' ' + str(result[4]) + ' ' + bestScore)
        beginningFile.close()

def runCalcMemoized(validAnswer, validGuesses, secretAnswer, startingWord):
    # print("Guessing:", startingWord)
    resultsArr = [(startingWord, wordleResult(startingWord, secretAnswer))]
    turns = 1

    while resultsArr[-1][1] != (2,2,2,2,2):
        currGuess = getNextWord(tuple(resultsArr), validGuesses, validAnswer)
        # print("Guessing: " + currGuess)
        resultsArr += [(currGuess, wordleResult(currGuess, secretAnswer))]
        turns += 1
    return turns

@cache_function_output(storage_path="/test")
def getNextWord(resultsArr, validGuess, validAnswer):
    validAnswer = list(validAnswer)
    validGuess = list(validGuess)
    key = []
    for info in resultsArr:
        key += [info[1]]
        result = info[1]
        guess = str(info[0]).lower()
        validAnswer = getPossibleAnswers(validAnswer, guess, result)

    optimalGuesses = validGuess
    optimalGuesses = widdle(validAnswer, validGuess, resultsArr)
    # if len(optimalGuesses) > 700:
    #     optimalGuesses = widdleMore(validAnswer, optimalGuesses)
    if (len(validAnswer) > 3):
        bestScore = scoreAnswers(optimalGuesses, validAnswer)
    else:
        bestScore = scoreAnswers(validAnswer, validAnswer)
    guess = bestScore
    return guess


# get list of words and format them
# get starting outcomes for roate
validGuessFile = open('validGuess.txt', 'r')
validAnswerFile = open('validAnswer.txt', 'r')
validGuess = tuple(validGuessFile.read().split('\n'))
validAnswer = validAnswerFile.read().split('\n')
validAnswerFile.close()
validGuessFile.close()

words = []

for word in validGuess:
    s = set()
    for answer in validAnswer:
        s.add(wordleResult(word, answer))
    words += [(word, len(s))]
    
print(sorted(words, key=lambda x: x[1]))

# cached_my_function = cache_function_output(storage_path="/test")(getNextWord)
# cached_my_function.remove_cache((('trace', (0, 0, 2, 1, 0)), ('cable', (2, 1, 0, 1, 0))))

sword = ""
while len(sword) != 5:
    sword = input("Starting Word:")

average = 0
i = 0
start = time.time()
for answer in validAnswer:
    i += 1
    print(f"Word: {answer}")
    last = runCalcMemoized(tuple(validAnswer), validGuess, answer, sword)
    average += last
    print(f"Guesses: {last}")
    print()

end = time.time()

sfile = open("starting_words.txt", "a+")
sfile.write("\n\n")
sfile.write(sword)
sfile.write("\n\n")
sfile.write(f"Total Time: {end - start}\n")
average = average / (i * 1.0)
sfile.write(f'Average Guesses: {average}\n')
sfile.write(f'Average Time: {(end - start) / (i * 1.0)}\n')
sfile.close()