import PySimpleGUI as sg
import csv
import os
import sys
from maggiecoin_functions import *
from datetime import datetime 
from datetime import timedelta  
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pathlib
import hashlib

sg.theme('DarkAmber')


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def upload_file_to_drive(file_id, local_path):
    """Overwrites the existing Google drive file."""
    update_file = drive.CreateFile({'id': file_id})
    update_file.SetContentFile(local_path)
    update_file.Upload()


def download_drive_file(file_id, save_path):
    """Downloads an existing Google drive file."""
    download_file = drive.CreateFile({'id': file_id})
    download_file.GetContentFile(save_path)


# Variables
linecount = 0
messageList = [ ['Enter a custom amount', 'This is not a valid amount.'],
                ['How many times was this action performed?', 'This is not a valid amount'],
                ['How many hours?', 'This is not a valid amount'] ]
errorList = ["Insufficient MaggieCoin balance.", 
             "You have reached the limit for borrowing.", 
             "You don't have that much debt.", 
             "Your loan must not exceed your balance."]

folder_path = str(pathlib.Path().resolve())
transactions_file_id = '1gY1WVI6XroigQkyFUdZVrZ94iud1ZA34'
interest_file_id = '1AJrDjNMzQiY7mXzJaxB8NF0bHhxr28s-'
main_file_id = '1ja23a7H3nPFOi99UCvp4b22TEJL7offg'

optionLow = 1
optionHigh = 6
depositLow = 1
depositHigh = 9999999
multiplierLow = 1
multiplierHigh = 9999999
spendLow = 1
spendHigh = 3

gameWeekday = 20
gameWeekend = 10
vacation = 500
mode = 'Accounts'

try:
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")
    
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
        
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
        
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")
    
    drive = GoogleDrive(gauth)

except Exception:
    error_popup('Error authenticating your Google Drive. Please ensure that maggiecoin.exe is located in the same folder as client_secrets.json, and then try rerunning the program. If this error persists, please contact Ryan or Eugene.')    
    sys.exit()


try:
    download_drive_file(transactions_file_id, folder_path + '\\mg_transactions.txt')
    download_drive_file(interest_file_id, folder_path + '\\mg_interest.txt')
    download_drive_file(main_file_id, folder_path + '\\maggiedata.csv')
    
except Exception:
    error_popup('Error gathering your data. Please try rerunning the program. If this error persists, please contact Ryan or Eugene.')    
    sys.exit()
    
try:
    passwords, names, bals, borrowed, roles = readFile("maggiedata.csv")
    
    # Asks to choose user
    
    while mode == 'Accounts':
        # Accounts Window
        layout = [[sg.Text("Welcome to MaggieCoin!\nPlease select an account to proceed:")]]
        for name in names:
            layout.append([sg.Button("{}".format(name))])
            
        layout.append([sg.Button("New User")])
        layout.append([sg.Button("Delete User")])
                      
        window = sg.Window('MaggieCoin Interface', layout, margins=(100, 100))
        
        while True:
            event, values = window.read()
            
            # Error #1
            if event == sg.WIN_CLOSED:
                sys.exit()
    
                
            elif event == 'New User':
                window.close()
                user, balance, password, borrowAmt, role, mode = addNewUser()
                
                if mode != 'Accounts':
                    bals.append(balance)
                    passwords.append(password)
                    names.append(user)
                    borrowed.append(borrowAmt)
                    roles.append(role)
                    writeFile('maggiedata.csv', names, bals, passwords, borrowed, roles)
                    newUserInterest(names)
                    passwords, names, bals, borrowed, roles = readFile("maggiedata.csv")
                    mode = 'Login'
                break
            
            elif event == 'Delete User':
                window.close()
                deleteUser(names, bals, passwords, borrowed, roles)
                mode = 'Accounts'
                break
                
            else:
                window.close()
                user = event
                mode = 'Login'
                break
        # Password check 
        
        if mode == 'Login':
            userIndex = names.index(user)
            mode = accountPasswordCheck(passwords, bals, names, borrowed, userIndex, roles, ["You do not have a password yet.\nPlease create one.", "Please confirm your password."])
            role = getRole(userIndex)
            
            if role == 'default' or role == 'admin':
                bals[userIndex], borrowed[userIndex] = updateInterest(user, names, bals[userIndex], borrowed[userIndex])
                
            if mode != 'Accounts':
                writeFile('maggiedata.csv', names, bals, passwords, borrowed, roles)

except Exception:
    error_popup("There was an error logging in. Please try rerunning the program. If this error persists, please contact Ryan or Eugene")
    sys.exit()
    
#try:
# Account Actions
while mode != 'Quit' and mode != sg.WIN_CLOSED:

    # Main Menu
    if mode == 'Menu':
        mode = menu(user, userIndex)
        passwords, names, balances, borrowed, roles = readFile("maggiedata.csv")
        

    # Display coins
    if mode == 'm1':
        role = getRole(userIndex)
        parents, admins, defaults = getRoleLists()
        combined = defaults + admins
        temp_container = []
        
        if role == 'parent' or role == 'admin':           
            layout = [  [sg.Button('Back')]  ]
            
            for u in combined:
                pos = names.index(u)
                temp_layout = [ [sg.Text('{} currently has {} MaggieCoins. They are {} MaggieCoins in debt.'.format(u, round(bals[pos], 2), borrowed[pos] ))]]
                temp_container.append(sg.Tab('{}'.format(u), temp_layout ) )
                
            layout.append( [sg.TabGroup([temp_container]) ])   
            window = sg.Window("Balances", layout, size=(500,300), grab_anywhere=False)
            
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Back':
                    mode = 'Menu'
                    break
                
            window.close()     
        
        else:
            sg.Popup("You currently have {} MaggieCoins. You owe {} MaggieCoins.".format(round(bals[userIndex], 2), borrowed[userIndex]), title = "Balance")
            mode = 'Menu'
    
    # Deposit coins
    if mode == 'm2':
        options = ["Walk Maggie for 20+ minutes: 1 MaggieCoin",
                   "Wash dinner dishes: 1 MaggieCoin",
                   "Brush Maggie for 15+ minutes: 1 MaggieCoin",
                   "Do homework for 20 minutes: 1 MaggieCoin",
                   "Workout for 20 minutes: 1 MaggieCoin",
                   "Earned A or 90+: 5 MaggieCoins",
                   "Earned A+ or 95+: 7 MaggieCoins",
                   "Earned E: 10 MaggieCoins",
                   "Deposit a custom amount"]
        
        tempUser = user
        tempUserIndex = userIndex
        noun = 'You'
        noun2 = 'Your'
        
        role = getRole(userIndex)
        parents, admins, defaults = getRoleLists()
        
        if role == 'parent':
            layout = [ [sg.Button('Back')],
                       [sg.Text('Select a user')],
                       [sg.Combo(defaults + admins, size=(40,10), enable_events=False, readonly = True, key='-COMBO-')],
                       [sg.Submit()] ]
            
            window = sg.Window('Select User', layout, margins=(100, 100))
            
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Back':
                    mode = 'Menu'
                    break
                if event == 'Submit':
                    tempUser = values['-COMBO-']
                    tempUserIndex = names.index(tempUser.capitalize())
                    noun = tempUser.capitalize()
                    noun2 = noun + "'s"
                    break
         
            window.close()            
        
        if mode != 'Menu':        
            layout = [ [sg.Button('Back')], 
                       [sg.Text('Select an activity')], 
                       [sg.Combo(options, size=(40,10), enable_events=False, readonly = True, key='-COMBO-')], 
                       [sg.Submit()] ]
            window = sg.Window('MaggieCoin Depositing', layout, margins=(100, 100))
            
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Back':
                    mode = 'Menu'
                    break
                if event == 'Submit':
                    comboChoice = values['-COMBO-']
                    break
         
            window.close()
            
            if mode != 'Menu':
                depositChoice = options.index(comboChoice)
                price, task, win_choice = depositFunction(depositChoice, multiplierLow, multiplierHigh, messageList, tempUser, tempUserIndex)
                
                if win_choice == 'stay':
                    bals[tempUserIndex] += price
                    sg.Popup("{} earned {} MaggieCoin(s) for {} {} balance is now {}.".format(noun, price, task, noun2, round(bals[tempUserIndex], 2)), title = "Deposit")
                    writeFile('maggiedata.csv', names, bals, passwords, borrowed, roles)
                    recordTransaction(tempUser, datetime.now(), price, task)
                    mode = 'Menu'
                else:
                    mode = 'm2'
        
    
    # Spend coins
    if mode == 'm3':
        options = ["Spend 10 MCoins for 1 hr of games (weekend)",
                   "Spend 20 MCoins for 1 hr of games (weekday)",
                   "Spend 500 MaggieCoins for a vacation",
                   "Spend custom amount"]
        layout = [ [sg.Button('Back')], 
                   [sg.Text('Select an activity')], 
                   [sg.Combo(options, size=(40,10), enable_events=False, readonly=True, key='-COMBO-')], 
                   [sg.Submit()] ]
        window = sg.Window('MaggieCoin Spending', layout, margins=(100, 100))
        
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Back':
                mode = 'Menu'
                break
            if event == 'Submit':
                comboChoice = values['-COMBO-']
                break
        
        window.close()
        
        if mode != 'Menu':
            spendChoice = options.index(comboChoice)
            price, task, win_choice = spendFunction(spendChoice, 0, bals[userIndex], messageList, user, userIndex)
            
            if win_choice == 'stay':
                bals[userIndex] -= price
                sg.Popup("You spent {} MaggieCoin(s) for {} Your balance is now {}.".format(price, task, round(bals[userIndex], 2)), title = "Withdrawal")
                writeFile('maggiedata.csv', names, bals, passwords, borrowed, roles)
                recordTransaction(user, datetime.now(), -price, task)
                mode = 'Menu'
            else:
                mode = 'm3'
    
    # Penalize MaggieCoin
    if mode == 'm4':
        options = ["Lose 20 MaggieCoins for lying",
                   "Lose 5 MaggieCoins for fighting",
                   "Lose 2 MaggieCoins for quarreling",
                   "Lose 10 MaggieCoins for missed homework",
                   "Lose 5 MaggieCoins for late homework",
                   "Lose 2 MaggieCoins for games during class",
                   "Lose a custom amount"] 
        
        tempUser = user
        tempUserIndex = userIndex
        noun = 'You'
        noun2 = 'Your'
        
        role = getRole(userIndex)
        parents, admins, defaults = getRoleLists()
        combined = defaults + admins        
      
        if role == 'parent' or role == 'admin':
            
            layout = [ [sg.Button('Back')],
                       [sg.Text('Select a user')],
                       [sg.Combo(defaults + admins, size=(40,10), enable_events=False, readonly = True, key='-COMBO-')],
                       [sg.Submit()] ]
            
            window = sg.Window('Select User', layout, margins=(100, 100))
            
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Back':
                    mode = 'Menu'
                    break
                if event == 'Submit':
                    tempUser = values['-COMBO-']
                    tempUserIndex = names.index(tempUser.capitalize())
                    noun = tempUser.capitalize()
                    noun2 = noun + "'s"
                    break
         
            window.close()                        
        
        if mode != 'Menu':
            layout = [ [sg.Button('Back')], 
                       [sg.Text('Select a consequence')], 
                       [sg.Combo(options, size=(40,10), readonly = True, enable_events=False, key='-COMBO-')], 
                       [sg.Submit()] ]
            window = sg.Window('MaggieCoin Deduction', layout, margins=(100, 100))
            
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Back':
                    mode = 'Menu'
                    break
                if event == 'Submit':
                    comboChoice = values['-COMBO-']
                    break
            
            window.close()        
        
        if mode != 'Menu':
            lossChoice = options.index(comboChoice)
            loss, punishment, win_choice = loseFunction(lossChoice, multiplierLow, multiplierHigh, messageList, tempUser)
            
            if win_choice == 'stay':
                bals[tempUserIndex] -= loss
                sg.Popup("{} lost {} MaggieCoin(s) for {}. Their balance is now {}.".format(tempUser, loss, punishment, round(bals[tempUserIndex], 2)), title = "Loss")
                writeFile('maggiedata.csv', names, bals, passwords, borrowed, roles)
                recordTransaction(tempUser, datetime.now(), -loss, punishment)
                mode = 'Menu'
            else:
                mode = 'm4'
                

    # Borrow coins
    if mode == 'm5':
        options = ["Borrow MaggieCoin",
                   "Repay MaggieCoin"] 
        
        layout = [ [sg.Button('Back')], 
                   [sg.Text('Select an action')], 
                   [sg.Combo(options, size=(40,10), readonly = True, enable_events=False, key='-COMBO-')], 
                   [sg.Submit()] ]
        
        window = sg.Window('MaggieCoin Borrow/Repay', layout, margins=(100, 100))
        
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Back':
                mode = 'Menu'
                break
            
            if event == 'Submit':
                comboChoice = values['-COMBO-']
                break        
            
        window.close() 
        
        if mode != 'Menu':
            borrowChoice = options.index(comboChoice)
            
            if borrowChoice == 0:
                layout = [ [sg.Button('Back')],
                           [sg.Text('You owe {} MaggieCoins.'.format(borrowed[userIndex]))],                           
                           [sg.Text('How much would you like to borrow?')],
                           [sg.InputText(key='-NUM-')],
                           [sg.Submit()], [sg.Button('Borrow All')]]
                           
                window = sg.Window('MaggieCoin Borrow', layout, margins=(100, 100))
                
                while True:
                    event, values = window.read()
                    if event == sg.WIN_CLOSED or event == 'Back':
                        mode = 'm5'
                        break
                    
                    if event == 'Submit':
                        if values['-NUM-'].isdigit() == True:
                            allowed = checkDebt(bals[userIndex], borrowed[userIndex], float(values['-NUM-']))
                            
                            if allowed == True and float(values['-NUM-']) > 0:
                                action = 'borrowed'
                                mode = 'Menu'
                                bals[userIndex] += float(values['-NUM-'])
                                borrowed[userIndex] += float(values['-NUM-']) 
                                break
                            else:
                                window.close()
                                sg.Popup("You can not borrow more than your balance, or less than zero.", title = "Error")
                                break
                        else:
                            window.close()
                            sg.Popup("Please enter a valid number.")
                            mode = 'm5'
                            break
                    
                    if event == 'Borrow All':
                        tempBal = bals[userIndex] - borrowed[userIndex]
                        borrowed[userIndex] = bals[userIndex]
                        bals[userIndex] += tempBal
                        sg.Popup("Borrowed {}. Your balance is now {}.".format(tempBal, bals[userIndex]), title = "Error")
                        break
                    
                window.close()

            elif borrowChoice == 1:
                layout = [ [sg.Button('Back')],
                           [sg.Text('You owe {} MaggieCoins.'.format(borrowed[userIndex]))],
                           [sg.Text('How much would you like to repay?')],
                           [sg.InputText(key='-NUM-')],
                           [sg.Submit()]]
                window = sg.Window('MaggieCoin Repayment', layout, margins=(100, 100))
                
                while True:
                    event, values = window.read()
                    if event == sg.WIN_CLOSED or event == 'Back':
                        mode = 'm5'
                        break    
                    
                    if event == 'Submit':
                        if values['-NUM-'].isdigit() == True:
                            allowed = checkBorrowed(bals[userIndex], borrowed[userIndex], float(values['-NUM-']))
                            
                            if allowed == True and float(values['-NUM-']) > 0:
                                action = 'repaid'
                                bals[userIndex] -= float(values['-NUM-'])
                                borrowed[userIndex] -= float(values['-NUM-'])
                                mode = 'Menu'
                                break
                            else:
                                window.close()
                                sg.Popup("You can not repay more than you owe, or less than zero.", title = "Error")
                                break
                        else:
                            window.close()
                            sg.Popup("Please enter a valid number.")
                            mode = 'm5'
                            break                        
                    
                    if event == 'Repay All':
                        borrowed[userIndex] -= float(values['-NUM-'])
                        bals[userIndex] += float(values['-NUM-'])
                        sg.Popup("Repaid {}. Your balance is now {}.".format(values['-NUM-'], bals[userIndex]), title = "Error")
                        break
                    
                window.close()

            if mode != 'm5':
                sg.Popup("You {} {} MaggieCoin(s). You owe {} to the MaggieCoin Bank.".format(action, round(float(values['-NUM-']), 2), round(borrowed[userIndex], 2)), title = "Borrow/Repay")
                writeFile('maggiedata.csv', names, bals, passwords, borrowed, roles)
                recordTransaction(user, datetime.now(), round(float(values['-NUM-']), 2), action)


    if mode == 'm6':
        tempUser = user
        tempUserIndex = userIndex
        role = getRole(userIndex)
        parents, admins, defaults = getRoleLists()
        combined = defaults + admins
        
        if role == 'parent' or role == 'admin':           
            filename = open('mg_transactions.txt')
            data = []
            header_list = ['TIME', 'AMOUNT', 'EXPLANATION' ]
            reader = csv.reader(filename)
            
            try:
                data = list(reader)
         
            except:
                sg.popup_error('Error reading file')
            
            sg.set_options(element_padding=(0, 0))
            transactions = []
            layout = [  [sg.Button('Back')]  ]
            temp_container = []
            
            for u in combined:
                transactions = []
                
                for entry in data:
                    if u in entry:
                        transactions.append([entry[0], entry[2], entry[3]])                
                
                temp_layout = [ [sg.Table(values=transactions, headings=header_list, auto_size_columns=False, col_widths = [14, 10, 30], justification='left', num_rows=min(len(data), 20))] ]
                temp_container.append(sg.Tab('{}'.format(u), temp_layout ) )
                
            layout.append( [sg.TabGroup([temp_container]) ])   
            window = sg.Window("Transactions History", layout, size=(500,300), grab_anywhere=False)
            
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Back':
                    mode = 'Menu'
                    break
                
            window.close()            
        
        else:     
            mode = getHistory(tempUser)
    
    if mode == 'm8':
        passwords, names, bals, borrowed, roles = readFile("maggiedata.csv")
        action = passwordValidator('Please enter your current password', [passwords[userIndex]])
        
        if action == 'back':
            mode = 'Menu'
        
        else:
            passwords[userIndex] = ''
            mode = accountPasswordCheck(passwords, bals, names, borrowed, userIndex, roles, ['Please enter your new password', 'Please confirm your new password'])
            
            if mode == 'Accounts':
                mode = 'Menu'   
            else:
                sg.Popup('Your password has successfully been changed.', title='Change Password')
                    
#except Exception:
    #error_popup('An unkown error has occured. Please try rerunning the program. If this error persists, please contact Ryan or Eugene.')
    #quit()

try:
    upload_file_to_drive(transactions_file_id, folder_path + '\\mg_transactions.txt')
    upload_file_to_drive(interest_file_id, folder_path + '\\mg_interest.txt')
    upload_file_to_drive(main_file_id, folder_path + '\\maggiedata.csv')

    
except Exception:
    error_popup('There was an error updating your transactions. PLease try rerunning the program. If this error persists, please contact Ryan or Eugene.')
    sys.exit()

