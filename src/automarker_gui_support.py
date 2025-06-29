#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
#
# Support module generated by PAGE version 8.0
#  in conjunction with Tcl version 8.6
#    Apr 18, 2025 04:46:56 PM BST  platform: Windows NT
#    Apr 19, 2025 04:08:43 AM BST  platform: Windows NT
#    Apr 22, 2025 04:33:58 PM BST  platform: Windows NT
#    Apr 22, 2025 05:04:44 PM BST  platform: Windows NT
#    Apr 23, 2025 03:06:30 AM BST  platform: Windows NT
#    Apr 23, 2025 04:12:26 AM BST  platform: Windows NT
#    Apr 23, 2025 04:16:19 PM BST  platform: Windows NT
#    May 13, 2025 08:38:55 PM BST  platform: Windows NT

import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from tkinter import filedialog
from pathlib import Path
from automarker import *
import tkinter.messagebox as msgbox 

import automarker_gui

_debug = True # False to eliminate debug printing from callback functions.

#
# Entry point of the application; sets up main and help windows and starts the GUI loop
def main(*args):
    '''Main entry point for the application.'''
    global root
    root = tk.Tk()
    root.protocol( 'WM_DELETE_WINDOW' , root.destroy)
    # Creates a toplevel widget.
    global _top4, _w4
    _top4 = root
    _w4 = automarker_gui.Toplevel1(_top4)
    # Start up code
    
    # Creates a toplevel widget.
    global _top5, _w5
    _top5 = tk.Toplevel(root)
    _top5.protocol("WM_DELETE_WINDOW", btn_Close)
    _w5 = automarker_gui.Toplevel2(_top5)
    initialise()
    root.mainloop()

#
# Initialises the GUI by resetting all widget states
def initialise():
    _top5.withdraw()

    _w4.che39.set(0)
    _w4.che40.set(0)
    _w4.che41.set(0)
    _w4.che42.set(0)

    _w4.nonCleanbtn['state'] = DISABLED
    _w4.btnSetVenv['state'] = DISABLED
    _w4.btnCopyOverride['state'] = DISABLED
    _w4.btnRunTest['state'] = DISABLED

#
# Callback for "Run Test" button; collects selected tasks and runs grading
def btnRunTest_lclick(*args):
    if _debug:
        print('automarker_gui_support.btnRunTest_lclick')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()
        global chk1, chk2, chk3, chk4

        chk1 = _w4.che39.get()
        chk2 = _w4.che40.get()
        chk3 = _w4.che41.get()
        chk4 = _w4.che42.get()
        task_dict = {"Task_1": chk1, "Task_2": chk2, "Task_3": chk3, "Task_4":chk4}
        tasks = [ key for key in task_dict.keys() if task_dict[key]]

        if not (chk1 or chk2 or chk3 or chk4):
            msgbox.showerror("Error", "No task was chosen.") 
        else:

            grade_all_submissions(tasks, runPath)
            titl = "Operation Completed"
            msg = f"A collated report for the chosen tasks has been created in {path}."
            msgbox.showinfo(titl, msg)
        
#
# Callback for "Clean Submissions" button; invokes submission cleaning process
def btn_Clean(*args):
    if _debug:
        print('automarker_gui_support.btn_Clean')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        cln = submission_cleaner(nonClean_path, filesPath)
        titl = "Operation Completed"
        msg = f"Cleaned Submissions can be found in {cln}"
        msgbox.showinfo(titl, msg)

#
# Callback for getting non-clean submissions directory from file dialog
def btn_GetNonClean(*args):
    if _debug:
        print('automarker_gui_support.btn_GetNonClean')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        global nonClean_path
        
        nonClean_path = Path(filedialog.askdirectory())
        _w4.vEntry.set(str(nonClean_path))
        _w4.nonCleanbtn['state'] = ACTIVE

#
# Callback for "Copy Override" button; injects test files into student submissions
def btn_CopyOverride(*args):
    if _debug:
        print('automarker_gui_support.btn_CopyOverride')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        preprocess_subs(testPath, path)
        titl = "Operation Completed"
        msg = "Submissions have been successfully copied and overriden."
        msgbox.showinfo(titl, msg)
        

#
# Callback for selecting test path directory; enables override button
def btn_GetTestPath(*args):
    if _debug:
        print('automarker_gui_support.btn_GetTestPath')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        global testPath

        testPath = Path(filedialog.askdirectory())
        _w4.btnCopyOverride['state'] = ACTIVE
        _w4.vEntry3.set(testPath)

#
# Callback for setting up virtual environments for submissions
def btn_SetupVenv(*args):
    if _debug:
        print('automarker_gui_support.btn_SetupVenv')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        setup_virtualenvs(path)
        titl = "Operation Completed"
        msg = f"A collated report has been created in {path}"
        msgbox.showinfo(titl, msg)

#
# Callback for selecting cleaned submissions directory; enables venv setup button
def btn_GetCleanPath(*args):
    if _debug:
        print('automarker_gui_support.btn_GetCleanPath')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()
        global path

        path = Path(filedialog.askdirectory())
        _w4.btnSetVenv['state'] = ACTIVE
        _w4.vEntry2.set(path)

#
# Callback to exit the application cleanly
def btnExit_lclick(*args):
    if _debug:
        print('automarker_gui_support.btnExit_lclick')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()
    root.destroy()

#
# Callback to close the help window
def btn_Close(*args):
    if _debug:
        print('automarker_gui_support.btn_Close')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        _top5.withdraw()

#
# Callback to display the help window
def btn_Help(*args):
    if _debug:
        print('automarker_gui_support.btn_Help')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()
        
        _top5.deiconify()

#
# Opens a dialog to select test files for copying (currently prints selected file)
def btn_CopyTestFiles(*args):
    if _debug:
        print('automarker_gui_support.btn_CopyTestFiles')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        files = filedialog.askopenfiles()
        print(files[0].name)

def btn_GetCopyFiles(*args):
    if _debug:
        print('automarker_gui_support.btn_GetCopyFiles')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

#
# Callback for selecting test files directory
def btn_GetTestFiles(*args):
    if _debug:
        print('automarker_gui_support.btn_GetTestFiles')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        global filesPath

        filesPath = Path(filedialog.askdirectory())

        _w4.vEntry4.set(filesPath)

def btn_Checkboxes(*args):
    if _debug:
        print('automarker_gui_support.btn_Checkboxes')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

def btn_RunTests(*args):
    if _debug:
        print('automarker_gui_support.btn_RunTests')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

#
# Callback for selecting the folder in which to run tests; enables run button
def btn_GetRunfolder(*args):
    if _debug:
        print('automarker_gui_support.btn_GetRunfolder')
        for arg in args:
            print ('    another arg:', arg)
        sys.stdout.flush()

        global runPath

        runPath = Path(filedialog.askdirectory())
        _w4.btnRunTest['state'] = ACTIVE

        _w4.vEntry5.set(runPath)

if __name__ == '__main__':
    automarker_gui.start_up()





