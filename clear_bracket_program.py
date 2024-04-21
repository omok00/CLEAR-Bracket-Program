import gspread
from collections import defaultdict
import os
#sheet_account = gspread.service_account(r"./tidy-chimera-397007-d29def730f1c.json")
sheet_account = gspread.service_account(r"./clearprogram-b1c611039675.json")
sh = sheet_account.open("clear_rating")
sheet_rating = sh.worksheet("Sheet1")
sa = sheet_account.open("clear_attendance")
sheet_attendance = sa.worksheet("Sheet1")
sb = sheet_account.open("clear_bracket")

student_bracket = []
student_bracket.append(sb.worksheet("Court A"))
student_bracket.append(sb.worksheet("Court B"))
student_bracket.append(sb.worksheet("Court C"))
student_bracket.append(sb.worksheet("Court D"))
student_bracket.append(sb.worksheet("Court E"))
student_bracket.append(sb.worksheet("Court F"))
bracket_main = sb.worksheet("Main")

student_attendance = sheet_attendance.get('A2:B500')
student_attendance_dict = defaultdict(int)
for x in student_attendance:
    student_attendance_dict[x[0]] = int(x[1])
student_rating= sheet_rating.get('A2:B500')
student_rating_dict = defaultdict(int)
for x in student_rating:
    student_rating_dict[x[0]] = int(x[1])
bracket_sequence = [None, None, None, None, [[0,1,2,3], [0,2,1,3], [0,3,1,2], [0,1,2,3], [0,2,1,3], [0,3,1,2]] , 
[[0,2,1,3], [4,0,1,2], [0,3,1,4], [0,3,2,4], [1,4,2,3], [0, 3, 1, 2] , [0, 4, 1, 3]] , 
[[0,3,1,2], [0,5,1,4], [2,5,3,4], [0,4,1,3], [1,5,2,3], [0, 5, 2, 4] , [2, 4, 5, 3], [0, 2, 1, 4]], 
[[0,3,2,1], [4, 5, 6, 0], [1, 4, 2, 3], [1, 6, 0 ,5], [2, 5, 3, 4], [6, 0, 1, 4], [2, 6, 5, 3], [0, 4, 1, 3], [2, 6, 5, 1]],
[[0,3,1,2], [4, 7, 5, 6], [0, 4, 1, 5], [2, 7, 3, 6], [0, 6, 2, 4], [1, 7, 3, 5], [0, 7, 2, 5], [1, 6, 3, 4]],
[[0, 3, 1, 2], [4, 7, 5, 6], [0, 8, 1, 2], [3, 6, 5, 4], [7, 1, 0, 8], [2, 5, 4, 3], [0, 7, 6, 8], [1, 5, 2, 6], [3, 8, 7, 4]]
]

def list_onesheet(L):
    if len(L) < 4 or len(L) > 9:
        print("You should change the number of teams")
        return []
    X = []
    bracket_sequence_ = bracket_sequence[len(L)]
    for i in range(len(bracket_sequence_)):
        X.append([i + 1, L[bracket_sequence_[i][0]] ,"-", L[bracket_sequence_[i][1]] , " ", ":", " ", L[bracket_sequence_[i][2]], "-", L[bracket_sequence_[i][3]]])
    return X

alpha = 400 # Please do not change
beta = 70 
gamma = 0
def rating_change(rating_diff, game_diff):
    return int((1 + gamma * min(25,game_diff)) * (beta) / (1 + 10 ** (-rating_diff / alpha)))

print("input number of 1 to 3 \n1: make bracket, 2: change rating and check attendance, 3: reset attendance list")
mode = int(input())
if mode == 1:
    #make all bracket
    print("input number of student that playing game")
    student_number = int(input())
    print("input number of court that playing game")
    court_num = int(input())
    print("input the court that where you playing game. you should input uppercase letter. (ex: A, B)")
    court_where = []
    for i in range(court_num):
        s = str(input())
        um = ord(s[0]) - 65
        court_where.append(um)
    courtperstudent = [0 for i in range(court_num)]
    for i in range(student_number):
        courtperstudent[i % court_num] += 1
    courtperstudent.reverse()
    X = []
    d = dict()
    print("Input the name of students.")
    count = 0
    while (count < student_number):
        print("student" + str(count + 1) + " name", end = " ")
        s = str(input())
        if (s not in student_rating_dict):
            print("There is no student in our document")
            continue
        if s in d:
            print("already in the student list")
            continue
        if s in student_rating_dict and s not in d:
            X.append([s, student_rating_dict[s]])
            d[s] = 1
            count += 1
    X.sort(key = lambda x: -x[1])
    L = []
    index = 0 
    for i in range(court_num):
        Z = []
        for j in range(courtperstudent[i]):
            Z.append(X[index][0])
            index += 1
        L.append(Z)
    for i in range(court_num):
        X = []
        for x in L[i]:
            X.append([x])
        aa = chr(court_where[i] + 66)
        s = aa + "2:" + aa + "20"
        bracket_main.batch_clear([s])
        bracket_main.update(range_name = s , values = X)
        student_bracket[court_where[i]].batch_clear(['A2:N20'])
        student_bracket[court_where[i]].update(range_name = 'A2:N20' , values = list_onesheet(L[i]))
if mode == 2:
    # result -> change rating
    # result -> attendance
    rating_delta = defaultdict(int)
    for eachsheet in student_bracket:
        L = eachsheet.get('B2:N20')
        eachsheet.batch_clear(['A2:N20'])
        for x in L:
            if len(x) < 9:
                continue
            if x[0] == "" or x[2] == "" or x[3] == "" or x[5] == "" or x[6] == "" or x[8] == "":
                continue
            if x[3].isdigit() == False or x[5].isdigit() == False:
                continue
            if int(x[3]) == int(x[5]):
                rating_delta[x[0]] += 0
                rating_delta[x[2]] += 0
                rating_delta[x[6]] -= 0
                rating_delta[x[8]] -= 0
            if int(x[3]) > int(x[5]):
                ratingdiff = (-student_rating_dict[x[0]] - student_rating_dict[x[2]] + student_rating_dict[x[6]] + student_rating_dict[x[8]]) / 2
                rc = rating_change(ratingdiff, int(x[3]) - int(x[5]))
                rating_delta[x[0]] += rc
                rating_delta[x[2]] += rc
                rating_delta[x[6]] -= rc
                rating_delta[x[8]] -= rc
            if int(x[3]) < int(x[5]):
                ratingdiff = -(-student_rating_dict[x[0]] - student_rating_dict[x[2]] + student_rating_dict[x[6]] + student_rating_dict[x[8]]) / 2
                rc = -rating_change(ratingdiff, int(x[5]) - int(x[3]))
                rating_delta[x[0]] += rc
                rating_delta[x[2]] += rc
                rating_delta[x[6]] -= rc
                rating_delta[x[8]] -= rc
    for x in rating_delta:
        if x in student_rating_dict:
            student_rating_dict[x] += rating_delta[x]
        if x in student_attendance_dict:
            student_attendance_dict[x] += 1
    X = []
    for x in student_rating_dict:
        X.append([x , int(student_rating_dict[x])])
    X.sort(key = lambda x: -x[1])
    sheet_rating.update(range_name = 'A2:B500' , values = X)
    Y = []
    for x in student_attendance_dict:
        Y.append([x , student_attendance_dict[x]])
    Y.sort(key = lambda x: -x[1])
    sheet_attendance.update(range_name = 'A2:B500' , values = Y)    
    bracket_main.batch_clear(['B2:N20'])
if mode == 3:
    print("Warning! if you really want reset attendance list, type Yes")
    s = str(input())
    if s == "Yes":
        X = []
        for x in student_attendance_dict:
            X.append([x , 0])
        X.sort(key = lambda x: -x[1])
        sheet_attendance.update('A2:B500' , X)
