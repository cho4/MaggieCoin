import PySimpleGUI as sg
import csv
import os
from datetime import datetime 
from datetime import timedelta  
import pathlib
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import hashlib

def error_popup(msg):
    sg.Popup(msg, title = 'Error')
    
def hash_string(string):
    byte_input = string.encode()
    hash_object = hashlib.sha256(byte_input)
    return hash_object


def upload_file_to_drive(file_id, local_path):
    """Overwrites the existing Google drive file."""
    update_file = drive.CreateFile({'id': file_id})
    update_file.SetContentFile(local_path)
    update_file.Upload()


def download_drive_file(file_id, save_path):
    """Downloads an existing Google drive file."""
    download_file = drive.CreateFile({'id': file_id})
    download_file.GetContentFile(save_path)


def getValidNum( lowVal, highVal, msg):
    pos = 0
    attempts = 0
    validNum = lowVal - 1
    win_action = 'stay'
    
    while validNum != None and ((validNum < lowVal) or (validNum > highVal)):
        if attempts > 1:
            pos = 1
            
        layout = [[sg.Text("{}".format(msg[pos]))], [sg.InputText(key='-NUM-')], [sg.Submit(), sg.Cancel()]]  
        window = sg.Window('MaggieCoin Interface', layout)
        
        while True:
            event, values = window.read()
                
            if event == sg.WIN_CLOSED or event == 'Cancel':
                win_action = 'back'
                validNum = None
                break
              
            else:
                if values['-NUM-'].isdigit():
                    validNum = int(values['-NUM-'])
                break
                
        attempts += 1
        window.close()
        
    return validNum, win_action


def clear(): os.system('cls')


def menu(user, userIndex):
    layout = [ [sg.Text("Good day, {}! Please select an action to proceed:".format(user.capitalize())) ], 
          [sg.Button('Display MaggieCoin balance', key = 'm1')], 
          [sg.Button('Deposit MaggieCoins earned', key = 'm2')], 
          [sg.Button('Transaction History', key = 'm6')],
          #[sg.Button('Tasks', key = 'm7')],
          [sg.Button('Change Password', key = 'm8')],
          [sg.Button('Quit')] ]
    
    role = getRole(userIndex)
    
    if role == 'parent' or role == 'admin':
    #if user == 'QI' or user == 'JIN' or user == 'RYAN':
        layout.insert(4, [sg.Button('Penalize MaggieCoins', key = 'm4')])
    
    if role == 'default' or role == 'admin':
    #if user == 'RICHARD' or user == 'RAINYEE' or user == 'RYAN':
        layout.insert(3, [sg.Button('Spend MaggieCoins and redeem rewards', key = 'm3')])
        layout.insert(5, [sg.Button('Borrow MaggieCoins', key = 'm5')])
        
    window = sg.Window('MaggieCoin Interface', layout, margins=(100, 100))
    event, values = window.read()
    window.close()
    return event


def passwordValidator(message, validPasswords):
    passAttempt = 0
    attempt = 1
    msgs = [message, 'Wrong password.\nReenter password']
    pos = 0
    win_action = 'stay'
    
    while win_action != 'back' and (passAttempt not in validPasswords):
        
        if attempt > 1:
            pos = 1
        
        layout = [[sg.Text("{}".format(msgs[pos]))], [sg.InputText(key='-PW-', password_char='*')], [sg.Submit(), sg.Cancel()]]  
        window = sg.Window('Password Authentication', layout)
        
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel':
                win_action = 'back'
                break
            else:
                passAttempt = hash_string(values['-PW-']).hexdigest()
                break
            
        attempt += 1 
        window.close()
    
    return win_action
    

def accountPasswordCheck(passwordList, balanceList, nameList, borrowList, userIndex, roles, msgs):
    newFile = ""
    win_action = 'stay'
    mode = ''
    
    if passwordList[userIndex] == '':
        # create password
        #msgs = ["You do not have a password yet.\nPlease create one.", "Please confirm your password."]
        newpassword = [0,1]
        
        while newpassword[0] != newpassword[1]:

            newpassword = [0,1]
            win_action = 'stay'
            i = 0

            while i < 2:
                
                layout = [[sg.Text(msgs[i])], [sg.InputText(key='-PW-', password_char='*')], [sg.Submit(), sg.Cancel()]]  
                window = sg.Window('Password Setup', layout)
                
                while True:
                    event, values = window.read()
                    
                    if event == sg.WIN_CLOSED or event == 'Cancel':

                        if i == 0:
                            win_action = 'back'
                            mode = 'Accounts'
                            i = 2
                            break
                        else:
                            win_action = 'back'
                            i = 0
                            break
                    
                    else:
                        newpassword[i] = values['-PW-']
                        i += 1
                        win_action = 'stay'
                        break
                    
                window.close()
                
            if newpassword[0] != newpassword[1] and win_action != 'back':
                sg.Popup("Wrong password.", title = "Password Setup")   
       
            elif win_action != 'back':
                passwordList[userIndex] = hash_string(newpassword[0]).hexdigest()                
                writeFile("maggiedata.csv", nameList, balanceList, passwordList, borrowList, roles)
                mode = 'Menu'
        
            else:
                break       
            
        
    else:
        win_action = passwordValidator('Please enter your password', [passwordList[userIndex]])
        mode = 'Menu'
        if win_action == 'back':
            mode = 'Accounts'
    
    return mode
             

def readFile(file_name):
    f = open("{}".format(file_name))
    passwords = []
    names = []
    balances = []
    borrowed_amt = []
    roles = []
    
    for line in f:
        line = line.strip().split(",")
        passwords.append(line[2])
        names.append(line[0])
        balances.append(float(line[1]))  
        borrowed_amt.append(float(line[3]))
        roles.append(line[4])
    
    f.close()
    return passwords, names, balances, borrowed_amt, roles


def writeFile(file_name, names, balances, passwords, borrowed_amt, roles):
    updatedFile = ""
    for i in range(len(names)):
        updatedFile += "{},{:.2f},{},{:.2f},{}\n".format(names[i], float(balances[i]), passwords[i], float(borrowed_amt[i]), roles[i])    
    
    f = open(file_name, "w")
    f.write(updatedFile) 
    f.close()


def getParentPws():
    passwords, names, balances, borrowed, roles = readFile('maggiedata.csv')
    
    parent_pws = []
    
    for i in range(len(passwords)):
        if roles[i] == 'parent' or roles[i] == 'admin':
            parent_pws.append(passwords[i])
        
    return parent_pws




def getRole(userIndex):
    passwords, names, balances, borrowed_amt, roles = readFile('maggiedata.csv')
    return roles[userIndex]

def getRoleLists():
    parents = []
    admins = []
    defaults = []    
    passwords, names, balances, borrowed_amt, roles = readFile('maggiedata.csv')
    
    for i in range(len(roles)):
        
        if roles[i] == 'default':
            defaults.append(names[i])
            
        elif roles[i] == 'parent':
            parents.append(names[i])
            
        elif roles[i] == 'admin':
            admins.append(names[i])
            
    return parents, admins, defaults


def depositFunction(depChoice, multiplierLow, multiplierHigh, msgList, user, userIndex):
    taskList = ['walking Maggie for 20+ minutes.',
                'washing the dishes at dinner.',
                'brushing Maggie for 15+ minutes.',
                'doing homework.',
                'exercising for 20+ minutes.',
                'getting an A or 90+.',
                'getting an A+ or 95+.',
                'getting an E.',
                'a custom deposit.']
    priceList = [1, 1, 1, 0, 1, 5, 7, 10, 0]
    win_choice = 'stay'
    role = getRole(userIndex)
    
    if depChoice == 3:
        priceList[depChoice], win_choice = getValidNum(multiplierLow, multiplierHigh, msgList[1])
    
    elif depChoice == 8:
        if role == 'default':
            parentPasswords = getParentPws()
            win_choice = passwordValidator('Please enter a parent password', parentPasswords)
            
        if win_choice == 'stay':
            priceList[depChoice], win_choice = getValidNum(multiplierLow, multiplierHigh, msgList[0])

    return priceList[depChoice], taskList[depChoice], win_choice

def spendFunction(speChoice, multiplierLow, multiplierHigh, msgList, user, userIndex):
    spendList = ['one hour of video games (weekend)',
                 'one hour of video games (weekday)',
                 'vacation',
                 'a custom amount']
    priceList = [10, 20, 500, 0]
    win_choice = 'stay'
    tempPrice = 0
    
    if speChoice == 0 or speChoice == 1:
        multiplier, win_choice = getValidNum(multiplierLow, multiplierHigh, msgList[1])
        tempPrice = priceList[speChoice] * multiplier
    
    elif speChoice == 3:
        
        role = getRole(userIndex)
        if role == 'default':
            parentPasswords = getParentPws()
            win_choice = passwordValidator('Please enter a parent password', parentPasswords)
            
        if win_choice == 'stay':
            tempPrice, win_choice = getValidNum(multiplierLow, multiplierHigh, msgList[0])
    
    else:
        tempPrice = priceList[speChoice]
        
    return tempPrice, spendList[speChoice], win_choice

def loseFunction(lossChoice, multiplierLow, multiplierHigh, msgList, user):
    lossList = ['lying',
                'fighting',
                'quarreling',
                'missed homework',
                'late homework',
                'games during class',
                'a custom reason']
    priceList = [20, 5, 2, 10, 5, 2, 0]
    win_choice = 'stay'
    
    if lossChoice == 6:
        tempLoss, win_choice = getValidNum(multiplierLow, multiplierHigh, msgList[0])
        
    else:
        tempLoss = priceList[lossChoice]
        
    return tempLoss, lossList[lossChoice], win_choice
    
def checkDebt(balance, borrowedAmount, wantBorrow):
    total_borrowed = borrowedAmount + wantBorrow
    
    if total_borrowed > balance:
        result = False
    else:
        result = True
        
    return result

def checkBorrowed(balance, borrowedAmount, wantRepay):
    total_repay = borrowedAmount - wantRepay
    
    if total_repay < 0:
        result = False
    else:
        result = True
        
    return result

def redeemableCheck(user, nameList, owed):
    interest_days, claimed_verifications, pos = readInterest(user, nameList)
    
    weeks_in_adv = 52
    date_now = datetime.now()
    i = 0
    b = len(interest_days)
    interest_times = 0
    dates_claimed = []
    
    
    while date_now > interest_days[i]:
                
        if claimed_verifications[i][pos] != 'claimed':
            claimed_verifications[i][pos] = 'claimed'
            interest_times += 1
            dates_claimed.append(interest_days[i])
            dates_claimed.append(interest_days[i])
            if owed > 0:
                dates_claimed.append(interest_days[i])
                       
        i += 1  
    
    while len(interest_days) < weeks_in_adv:
        interest_days.append(interest_days[-1] + timedelta(days=7))
        namerow = []
        for i in range(len(nameList)):
            namerow.append('unclaimed')
        claimed_verifications.append(namerow)
        
    file = open('mg_interest.txt', 'w')
    updatedFile = ""

    for i in range(len(interest_days)):
        updated_collections = ""
        for t in range(len(nameList)):
            updated_collections += ",{}".format(claimed_verifications[i][t])
            
        updatedFile += "{}{}\n".format(interest_days[i].strftime("%x %X"), updated_collections) 
        
    file.write(updatedFile)
    file.close()
    return interest_times, dates_claimed


def updateInterest(user, nameList, bal, owed):
    
    interest_times, dates_claimed = redeemableCheck(user, nameList, owed)
    new_bal = interest_times * 20 # Allowance
    new_bal += bal * (1.05 ** interest_times) 
    borrowed_interest = 0
    
    if owed > 0:
        borrowed_interest = owed * (1.1 ** interest_times)
    
    if interest_times > 0:
        file = open('mg_transactions.txt')
        now_changes = []
        now_causes = []
        dates = []
        names = []
        changes = []
        causes = []
        
        for line in file:
            line = line.strip().split(',')
            dates.append(datetime.strptime(line[0], '%m/%d/%y %H:%M:%S'))
            names.append(line[1])
            changes.append(line[2])
            causes.append(line[3])
    
        for i in range(1, interest_times + 1):
            now_changes.append(bal * (1.05 ** i) - bal * (1.05 ** (i - 1)))
            now_causes.append("Interest gained")
            now_changes.append(20)
            now_causes.append("Allowance")
            
            if borrowed_interest > 0:
                now_changes.append(owed * (1.1 ** i) - owed * (1.05 ** (i - 1)))
                now_causes.append("Loan interest")
            
        file = open('mg_transactions.txt', 'w')
        updatedFile = ""
        
        for b in range(len(dates_claimed)):
            if dates_claimed[b] in dates:
                pos = dates.index(dates_claimed[b])
                dates.insert(pos, dates_claimed[b])
                names.insert(pos, user)
                changes.insert(pos, now_changes[b])
                causes.insert(pos, now_causes[b])
                
            else:
                dates.append(dates_claimed[b])
                names.append(user)
                changes.append(now_changes[b])
                causes.append(now_causes[b])
                
        for i in range(len(dates)):
            updatedFile += "{},{},{:.2f},{}\n".format(dates[i].strftime("%x %X"), names[i], float(changes[i]), causes[i]) 
            
        file.write(updatedFile)
    
    return round(new_bal, 2), round(borrowed_interest, 2)



def accessTransactions():
    file = open('mg_transactions.txt')
    dates = []
    names = []
    changes = []
    causes = []
    
    for line in file:
        line = line.strip().split(',')
        dates.append(datetime.strptime(line[0], '%m/%d/%y %H:%M:%S'))
        names.append(line[1])
        changes.append(line[2])
        causes.append(line[3])
    
    return dates, names, changes, causes    

def recordTransaction(user, date, amount, cause):
    
    dates, names, changes, causes = accessTransactions()
    
    file = open('mg_transactions.txt', 'w')
    updatedFile = ""
    
    if date in dates:
        pos = dates.index(date)
        dates.insert(pos, date)
        names.insert(pos, user)
        changes.insert(pos, amount)
        causes.insert(pos, cause.capitalize())
    else:
        dates.append(date)
        names.append(user)
        changes.append(amount)
        causes.append(cause.capitalize())
            
    for i in range(len(dates)):
        updatedFile += "{},{},{:.2f},{}\n".format(dates[i].strftime("%x %X"), names[i], float(changes[i]), causes[i]) 
        
    file.write(updatedFile)   
    
def getHistory(user):
    filename = open('mg_transactions.txt')
    data = []
    header_list = ['TIME', 'AMOUNT', 'EXPLANATION' ]
    reader = csv.reader(filename)
    
    try:
        data = list(reader)
 
    except:
        sg.popup_error('Error reading file')
        return
    
    sg.set_options(element_padding=(0, 0))
    transactions = []
    
    for entry in data:
        if user in entry:
            transactions.append([entry[0], entry[2], entry[3]])
    
    layout = [[sg.Button('Back')],
                [sg.Table(values=transactions, headings=header_list, auto_size_columns=False, col_widths = [14, 10, 30], justification='left', num_rows=min(len(data), 20))]]

    window = sg.Window("{}'s Transactions History".format(user.capitalize()), layout, size=(500,300), grab_anywhere=False)
        
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Back':
            mode = 'Menu'
            break
        
    window.close()
    
    return mode



def addNewUser():
    
    layout = [[sg.Text("Create a username (alpha-only)")], [sg.InputText(key='-NAME-')], [sg.Submit(), sg.Cancel()]]  
    window = sg.Window('Create User', layout)
    
    while True:
        event, values = window.read()
        name = values['-NAME-'].upper()
        alpha = name.isalpha()
        
        if event == sg.WIN_CLOSED or event == 'Cancel':
            mode = 'Accounts'
            break
        
        elif alpha == False or len(name) == 0:
            layout = [[sg.Text("Create a username (alpha-only)")], [sg.InputText(key = '-NAME-')], [sg.Submit(), sg.Cancel()]]
            window = sg.Window('Create User', layout)
            
        else:
            mode = 'Login'
            break
        
    window.close()
    return name.capitalize(), 0.00, '', 0.00, 'default', mode

def deleteUser(names, bals, passwords, borrowed, roles):
    layout = [[sg.Text("Select a user to delete.")], [sg.Button('Back')]]
    for name in names:
        layout.append([sg.Button("{}".format(name))])
    
    window = sg.Window('Delete User', layout)
    
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Back':
            mode = 'Login'
            break
        
        else:
            userIndex = names.index(event)
            action = passwordValidator("Are you sure you want to delete this account?\nPlease enter this account's password to confirm.", [passwords[userIndex]])
            
            if action != 'back':
                position = names.index(event)
                delUserInterest(names, position)
                bals.pop(position)
                names.pop(position)
                borrowed.pop(position)
                passwords.pop(position)
                roles.pop(position)
                writeFile('maggiedata.csv', names, bals, passwords, borrowed, roles)
                passwords, names, bals, borrowed, roles = readFile("maggiedata.csv")
                mode = 'Login'
            break
        
    window.close()
    
    
def readInterest(user, nameList):
    file = open('mg_interest.txt')
    pos = nameList.index(user)
    interest_days = []
    claimed_verifications = []
    
    for line in file:
        line = line.strip().split(',')
        interest_days.append(datetime.strptime(line[0], '%m/%d/%y %H:%M:%S'))
        claimed_verifications.append(line[1:])
        
    return interest_days, claimed_verifications, pos
    

def newUserInterest(names):
    file = open('mg_interest.txt')
    dates = []
    claims = []
    
    for line in file:
        line = line.strip().split(',')
        dates.append(datetime.strptime(line[0], '%m/%d/%y %H:%M:%S'))
        temp = line[1:]
        temp.append('unclaimed')
        claims.append(temp)   
        
    
    file.close()
    file = open('mg_interest.txt', 'w')
    updatedFile = ""

    for i in range(len(dates)):
        
        updated_collections = ""
        for t in range(len(names)):
            updated_collections += ",{}".format(claims[i][t])
            
        updatedFile += "{}{}\n".format(dates[i].strftime("%x %X"), updated_collections) 
        
    file.write(updatedFile)
    file.close()    
    
def delUserInterest(names, userIndex):
    file = open('mg_interest.txt')
    dates = []
    claims = []
    
    for line in file:
        line = line.strip().split(',')
        dates.append(datetime.strptime(line[0], '%m/%d/%y %H:%M:%S'))
        temp = line[1:]
        temp.pop(userIndex)
        claims.append(temp)   
        
    
    file.close()
    file = open('mg_interest.txt', 'w')
    updatedFile = ""

    for i in range(len(dates)):
        
        updated_collections = ""
        for t in range(len(names) - 1):
            updated_collections += ",{}".format(claims[i][t])
            
        updatedFile += "{}{}\n".format(dates[i].strftime("%x %X"), updated_collections) 
        
    file.write(updatedFile)
    file.close()    


def tasksLayout(user):
    pass
