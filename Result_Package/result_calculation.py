import random

human_scores, app_scores, num_wickets = 0, 0, 0
target_wickets, target = 0, 0
turn_time = 0
choice, toss = 0, 0
is_toss_win = True
is_human_batting = True
is_quit = False


def whoPlay(toss_no, choice_no):
    global is_human_batting, choice, is_toss_win, toss

    choice = choice_no
    toss = toss_no
    print("In Result Calculation: choice no - ", choice_no, " and toss no- ", toss_no)
    rand_toss_int = random.randint(1, 2)
    print("In Result Calculation: random toss - ", rand_toss_int)
    if toss_no != rand_toss_int:
        is_toss_win = False

    if is_toss_win:
        if choice == 2:
            is_human_batting = False
    else:
        if choice == 1:
            is_human_batting = False


def set_numOfWickets(wickets):
    global target_wickets

    target_wickets = wickets
    print("Target Wickets ", target_wickets)


def randomOutputGenerator(fingers):
    global num_wickets, human_scores, app_scores, is_human_batting, target, turn_time

    rand_int = random.randint(1, 5)

    if rand_int == fingers:
        num_wickets += 1

        if num_wickets == target_wickets:
            timeToTurn()
    else:
        if is_human_batting:
            human_scores += fingers
            app_scores = rand_int
        else:
            human_scores = fingers
            app_scores += rand_int

    if turn_time == 1 and (target < human_scores or target < app_scores):
        print("Target is lesser")
        quitGame()


def timeToTurn():
    global is_human_batting, num_wickets, target, human_scores, app_scores, turn_time

    num_wickets = 0
    turn_time += 1

    if turn_time == 1:
        if is_human_batting:
            target = human_scores
            human_scores = 0
        else:
            target = app_scores
            app_scores = 0
        print("Target ", target)
        is_human_batting = not is_human_batting

    print("turn is called")

    if turn_time == 2:
        quitGame()


def quitGame():
    global is_quit

    is_quit = True
    print("Quit Game")


def getMultipleValues():
    global num_wickets, human_scores, app_scores, is_human_batting, is_quit, target, turn_time

    return is_human_batting, human_scores, app_scores, num_wickets, is_quit, target, turn_time


def getTossResult():
    global is_toss_win, is_human_batting, toss

    return is_toss_win, is_human_batting, toss
