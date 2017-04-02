from pywinauto.application import Application
import time
import csv
import os
import sys

def generateDataFile(t_interval, interface_name, file_name):
    # start Wireshark
    app = Application(backend='uia').start(r"C:\Program Files (x86)\Wireshark\Wireshark.exe")
    win = app['The Wireshark Network Analyzer']

    if app.software_update.exists(timeout=10):
        app.software_update.skip_this_version.click()
        app.software_update.wait_not('visible')  # just to make sure it's closed
    win.wait('ready', timeout=15)

    # Try to find interface_name in TreeView interfaces list
    tree = win["Interface list Interface list"]
    interface_name = "\\" + interface_name
    try:
        tree.get_item(interface_name).double_click_input()
    except Exception:
        print('No such interface')
        exit()

    win = app['Dialog']

    # Wait while WireShark collect information
    win.wait('ready')
    time.sleep(t_interval)
    win.wait('ready')

    # Stop WireShark
    win = app['Dialog']
    win['Stop'].click()

    # open menu (File -> Export Packet Dissections -> As CSV)
    win['File Alt+F'].select()
    win = app.top_window()
    win['Export Packet Dissections'].select()
    win = app.top_window()
    win['As CSV...'].click_input()

    # Export FileDialog
    win = app['Dialog']
    child = win['Export File Dialog']

    check_file_exist = True
    try:
        open(file_name)
    except IOError as e:
        check_file_exist = False

    # input path to temporary file
    win.type_keys(file_name)
    child.window(best_match = "Save").click()
    # child['Save'].click()

    # if window "confirm Save As" pop up
    if (check_file_exist == True):
        child = win['Confirm Save As']
        child.window(best_match='yes').click()
        # child['yes'].click()

    # Quit
    win['File Alt+F'].select()
    win = app.top_window()
    win['Quit Ctrl+Q'].click_input()

    # if window "Quit without Saving" pop up
    try:
        win = app.top_window()
        win['Quit without Saving Alt+w'].click()
    except:
        pass

def parseFile(file_name):
    # parse csv file
    prot_dict = {}
    with open(file_name) as csvfile:
        text = csv.reader(csvfile)
        # skip first line with header
        next(text, None)
        # initialize dict with list
        for row in text:
            prot_dict[row[4]] = list()
        # return back to beginning
        csvfile.seek(0)
        next(text, None)
        # collect information about protocols
        for row in text:
            prot_dict[row[4]].append(int(row[5]))
    # calculate count packets, mean packer length and traffic size
    for key in prot_dict:
        temp_list = prot_dict[key]
        count_pack = len(temp_list)
        mean_pack_len = int(sum(temp_list)/len(temp_list))
        traffic_size = sum(temp_list)
        prot_dict[key].clear()
        prot_dict[key].append(count_pack)
        prot_dict[key].append(mean_pack_len)
        prot_dict[key].append(traffic_size)
    # delete temporary file
    os.remove(file_name)
    return prot_dict

def printResult(result):
    print_order = list()
    keys = list(result.keys())

    for i in range(0,len(keys)):
        max = 0
        temp_key = ''
        # find max key
        for key in keys:
            if result[key][2] > max:
                max = result[key][2]
                temp_key = key
        print_order.append(temp_key)
        keys.remove(temp_key)

    print("Protocol  count protocols  mean length  traffic size")
    for key in print_order:
        string = key + "  " + str(result[key][0]) + "  "\
                 + str(result[key][1]) + "  " + str(result[key][2])
        print (string)

if (len(sys.argv) < 3):
    print("Expected time and interface_name")
    exit()
else:
    t_interval = int(sys.argv[1])
    interface_name = sys.argv[2]

file_name = os.path.dirname(os.path.abspath(__file__)) + '\\' + r"test.csv"

generateDataFile(t_interval,interface_name,file_name)
result = parseFile(file_name)
printResult(result)
