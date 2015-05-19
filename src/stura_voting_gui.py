#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# stura_voting_gui.py
#
# Copyright (C) 2015 Fabian Wenzelmann <fabianwenzelmann(at)posteo.de>
#
# This file is part of stura-voting.
#
# stura-voting is free software: you
# can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# stura-voting is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with stura-voting.
#
# If not, see <http://www.gnu.org/licenses/>.
#

import tkinter
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import tkinter.scrolledtext
import datetime

from stura_voting_io import *


stura_voting_copyright = """Copyright (C) 2015 Fabian Wenzelmann <fabianwenzelmann(at)posteo.de>

stura-voting is free software: you
can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation
either version 3 of the License, or (at your option) any later version.

stura-voting is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License
along with stura-voting.

If not, see <http://www.gnu.org/licenses/>.
"""

class SturaMainFrame(tkinter.Frame):
    def __init__(self, master=None):
        # none gui variables
        self.polls = []
        self.voters = []
        
        tkinter.Frame.__init__(self, master)
        self.grid(row=0, column=0, sticky='NSEW')
        master.title('StuRa Abstimmungen')
        votersLabel = tkinter.Label(self, text='Abstimmende')
        votersButton = tkinter.Button(self, text='Datei öffnen', command=self.openVoters)
        scrollbar1 = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        votersDisplay = tkinter.Listbox(self, yscrollcommand=scrollbar1.set)
        self.votersDisplay = votersDisplay
        scrollbar1.config(command=votersDisplay.yview)
        numVoters = self.numVoters = tkinter.StringVar()
        numVoters.set('ges.: 0')
        numVotersLabel = tkinter.Label(self, textvariable=numVoters)
        votersLabel.grid(row=0, column=0, sticky='W')
        votersButton.grid(row=1, column=0, sticky='WE')
        votersDisplay.grid(row=2, column=0, rowspan=4)
        numVotersLabel.grid(row=6, column=0, sticky='W')
        
        pollsLabel = tkinter.Label(self, text='Abstimmungen')
        pollsOpen = tkinter.Button(self, text='Datei öffnen', command=self.openPolls)
        pollsSave = tkinter.Button(self, text='Datei speichern', command=self.savePolls)
        createTableButton = tkinter.Button(self, text='Tabelle erstellen', command=self.createTable)
        evaluateButton = tkinter.Button(self, text='Auswerten', command=self.evaluate)
        pollsDisplay = tkinter.Listbox(self)
        self.pollsDisplay = pollsDisplay
        numPolls = self.numPolls = tkinter.StringVar()
        numPolls.set('ges.: 0')
        numPollsLabel = tkinter.Label(self, textvariable=numPolls)
        addMedianButton = tkinter.Button(self, text='Median zufügen', command=self.addMedian)
        addSchulzeButton = tkinter.Button(self, text='Schulze zufügen', command=self.addSchulze)
        editPollButton = tkinter.Button(self, text='Auswahl bearbeiten', command=self.editPoll)
        removePollButton = tkinter.Button(self, text='Auswahl entfernen', command=self.removePoll)
        pollsLabel.grid(row=0, column=1, columnspan=4, sticky='W')
        pollsOpen.grid(row=1, column=1)
        pollsSave.grid(row=1, column=2)
        createTableButton.grid(row=1, column=3)
        evaluateButton.grid(row=1, column=4)
        pollsDisplay.grid(row=2, column=1, columnspan=4, rowspan=4, sticky='WE')
        numPollsLabel.grid(row=6, column=1, sticky='W')
        addMedianButton.grid(row=2, column=5, sticky='NWE')
        addSchulzeButton.grid(row=3, column=5, sticky='NWE')
        editPollButton.grid(row=4, column=5, sticky='NWE')
        removePollButton.grid(row=5, column=5, sticky='NWE')
        
        menubar = tkinter.Menu(self)
        menubar.add_command(label='Über', command=self.showLicense)
        master.config(menu=menubar)
    
    def showLicense(self):
        messagebox.showinfo('StuRa Abstimmungstool (stura-voting)', 
            stura_voting_copyright)
    
    def openVoters(self):
        file_opt = {}
        file_opt['defaultextension'] = '.csv'
        file_opt['filetypes'] = [('csv files', '.csv'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.askopenfilename(**file_opt)
        if not name:
            return
        voters = None
        try:
            voters = parseVoters(name)
        except VoterParseException as e:
            messagebox.showerror('Datei öffnen fehlgeschlagen', str(e))
            return
        self.votersDisplay.delete(0, tkinter.END)
        self.votersDisplay.insert(0, *['%s: %d' % (v.name, v.weight) for v in voters])
        self.numVoters.set('ges.: %d' % len(voters))
        self.voters = voters

    def openPolls(self):
        file_opt = {}
        file_opt['defaultextension'] = '.xml'
        file_opt['filetypes'] = [('xml files', '.xml'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.askopenfilename(**file_opt)
        if not name:
            return
        polls = None
        try:
            polls = parsePolls(name)
        except PollParseException as e:
            messagebox.showerror('Datei öffnen fehlgeschlagen', str(e))
            return
        self.pollsDisplay.delete(0, tkinter.END)
        self.pollsDisplay.insert(0, *[p.name for p in polls])
        self.polls = polls
        self.updatePollsNum()


    def savePolls(self):
        file_opt = {}
        file_opt['defaultextension'] = '.xml'
        file_opt['filetypes'] = [('xml files', '.xml'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.asksaveasfilename(**file_opt)
        if not name:
            return
        writePollsToXML(name, self.polls)

    def updatePollsNum(self):
        self.numPolls.set('ges.: %d' % len(self.polls))
    
    def createTable(self):
        file_opt = {}
        file_opt['defaultextension'] = '.csv'
        file_opt['filetypes'] = [('csv files', '.csv'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.asksaveasfilename(**file_opt)
        if not name:
            return
        createInputCSV(name, self.polls, self.voters)

    def evaluate(self):
        ask = messagebox.askyesno('Fortfahren?', 'Sind alle aktuellen Dateien geöffnet?')
        if not ask:
            return
        now = datetime.datetime.now()
        init = 'Abstimmungen StuRa vom %02d.%02d.%d' % (now.day, now.month, now.year)
        title = simpledialog.askstring('Titel', 'Titel für Ausgabe eingeben', parent=self, initialvalue=init)
        if title is None:
            return
        file_opt = {}
        file_opt['defaultextension'] = '.csv'
        file_opt['filetypes'] = [('csv files', '.csv'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.askopenfilename(**file_opt)
        if not name:
            return
        polls = readTable(name, self.voters, self.polls)
        results = []
        for poll in polls:
            results.append(poll.evaluate())
        messagebox.showinfo('Auswertung', 'Abstimmungen wurden ausgewertet, Speicherort auswählen.')
        file_opt = {}
        file_opt['defaultextension'] = '.html'
        file_opt['filetypes'] = [('html files', '.html'), ('all files', '.*')]
        file_opt['initialdir'] = '.'
        file_opt['parent'] = self
        name = filedialog.asksaveasfilename(**file_opt)
        if not name:
            messagebox.showwarning('Hinweis', 'Auswertung wurde nicht gespeichert')
            return
        html = str(pollsToHtml(title, zip(polls, results)))
        with open(name, 'w') as f:
            f.write(html)
    
    def editPoll(self):
        sel = self.pollsDisplay.curselection()
        if not sel:
            return
        assert len(sel) == 1
        sel = sel[0]
        p = self.polls[sel]
        if type(p) == MedianSkel:
            d = MedianDialog(self, p.name, p.percentRequired, p.maxValue, p.allVotes)
            if not d.succ:
                return
            try:
                d.checkTypes()
            except ValueError as e:
                messagebox.showerror('Eingabefehler', str(e))
                return
            p = MedianSkel(d.name, d.req, d.count, d.val)
            self.polls[sel] = p
            self.pollsDisplay.delete(sel)
            self.pollsDisplay.insert(sel, p.name)
        elif type(p) == SchulzeSkel:
            d = SchulzeDialog(self, p.name, p.percentRequired, '\n'.join(p.options), p.allVotes)
            if not d.succ:
                return
            try:
                d.checkTypes()
            except ValueError as e:
                messagebox.showerror('Eingabefehler', str(e))
                return
            p = SchulzeSkel(d.name, d.req, d.count, d.options)
            self.polls[sel] = p
            self.pollsDisplay.delete(sel)
            self.pollsDisplay.insert(sel, p.name)
    
    def removePoll(self):
        sel = self.pollsDisplay.curselection()
        if not sel:
            return
        assert len(sel) == 1
        sel = sel[0]
        self.pollsDisplay.delete(sel)
        self.polls.pop(sel)
        self.updatePollsNum()

    def addMedian(self):
        d = MedianDialog(self)
        if not d.succ:
            return
        try:
            d.checkTypes()
        except ValueError as e:
            messagebox.showerror('Eingabefehler', str(e))
            return
        p = MedianSkel(d.name, d.req, d.count, d.val)
        self.polls.append(p)
        self.pollsDisplay.insert(tkinter.END, p.name)
        self.updatePollsNum()
    
    def addSchulze(self):
        d = SchulzeDialog(self)
        if not d.succ:
            return
        try:
            d.checkTypes()
        except ValueError as e:
            messagebox.showerror('Eingabefehler', str(e))
            return
        p = SchulzeSkel(d.name, d.req, d.count, d.options)
        self.polls.append(p)
        self.pollsDisplay.insert(tkinter.END, p.name)
        self.updatePollsNum()

class MedianDialog(simpledialog.Dialog):
    def __init__(self, parent, initName='', initReq='0.5', initVal='0', checked=0):
        self.nameVar = tkinter.StringVar()
        self.nameVar.set(initName)
        
        self.valVar = tkinter.StringVar()
        self.valVar.set(initVal)
        
        self.reqVar = tkinter.StringVar()
        self.reqVar.set(initReq)
        
        self.checked = tkinter.IntVar()
        self.checked.set(checked)
        
        simpledialog.Dialog.__init__(self, parent, 'Median-Abstimmung')

    def checkTypes(self):
        try:
            self.val = float(self.val)
        except ValueError:
            raise ValueError('%s ist keine Zahl' % self.val)
        try:
            self.req = float(self.req)
        except ValueError:
            raise ValueError('%s ist keine Zahl' % self.req)
        if self.req < 0 or self.req > 1:
            raise ValueError('Prozentzahl muss zwischen 0 und 1 liegen')
    
    def body(self, master):
        tkinter.Label(master, text='Name').grid(row=0, column=0, sticky='W')
        tkinter.Label(master, text='Wert').grid(row=1, column=0, sticky='W')
        tkinter.Label(master, text='Benötigte % der Stimmen').grid(row=2, column=0, sticky='W')
        tkinter.Label(master, text='Enthaltungen mitzählen').grid(row=3, column=0, sticky='W')
        
        self.nameEntry = tkinter.Entry(master, textvariable=self.nameVar)
        self.valEntry = tkinter.Entry(master, textvariable=self.valVar)
        self.requiredEntry = tkinter.Entry(master, textvariable=self.reqVar)
        self.countBox = tkinter.Checkbutton(master, variable=self.checked)
        
        self.nameEntry.grid(row=0, column=1, sticky='W')
        self.valEntry.grid(row=1, column=1, sticky='W')
        self.requiredEntry.grid(row=2, column=1, sticky='W')
        self.countBox.grid(row=3, column=1, sticky='W')
        
        self.succ = False
    
    def apply(self):
        self.succ = True
        self.name = self.nameVar.get()
        self.val = self.valVar.get()
        self.req = self.reqVar.get()
        self.count = self.checked.get()

class SchulzeDialog(simpledialog.Dialog):
    def __init__(self, parent, initName='', initReq='0.5', initOptions='\nNein', checked=0):
        self.nameVar = tkinter.StringVar()
        self.nameVar.set(initName)
        
        self.initOptions = initOptions
        
        self.reqVar = tkinter.StringVar()
        self.reqVar.set(initReq)
        
        self.checked = tkinter.IntVar()
        self.checked.set(checked)
        
        simpledialog.Dialog.__init__(self, parent, 'Schulze-Abstimmung')

        
    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = tkinter.Frame(self)

        w = tkinter.Button(box, text="OK", width=10, command=self.ok, default=tkinter.ACTIVE)
        w.pack(side=tkinter.LEFT, padx=5, pady=5)
        w = tkinter.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.bind("<Escape>", self.cancel)

        box.pack()


    def checkTypes(self):
        try:
            self.req = float(self.req)
        except ValueError:
            raise ValueError('%s ist keine Zahl' % self.req)
        if self.req < 0 or self.req > 1:
            raise ValueError('Prozentzahl muss zwischen 0 und 1 liegen')
        options = []
        for s in self.options.split('\n'):
            s = s.strip()
            if s:
                options.append(s)
        self.options = options

    def body(self, master):
        tkinter.Label(master, text='Name').grid(row=0, column=0, sticky='W')
        tkinter.Label(master, text='Optionen').grid(row=1, column=0, sticky='W')
        tkinter.Label(master, text='Benötigte % der Stimmen').grid(row=2, column=0, sticky='W')
        tkinter.Label(master, text='Enthaltungen mitzählen').grid(row=3, column=0, sticky='W')
        
        self.nameEntry = tkinter.Entry(master, textvariable=self.nameVar)
        self.optionsText = tkinter.scrolledtext.ScrolledText(master)
        self.optionsText.insert(tkinter.END, self.initOptions)
        self.requiredEntry = tkinter.Entry(master, textvariable=self.reqVar)
        self.countBox = tkinter.Checkbutton(master, variable=self.checked)
        
        self.nameEntry.grid(row=0, column=1, sticky='W')
        self.optionsText.grid(row=1, column=1, sticky='W')
        self.requiredEntry.grid(row=2, column=1, sticky='W')
        self.countBox.grid(row=3, column=1, sticky='W')
        self.optionsText.focus_set()
        
        self.succ = False


    def apply(self):
        self.succ = True
        self.name = self.nameVar.get()
        self.options = self.optionsText.get('1.0', tkinter.END + '-1c')
        self.req = self.reqVar.get()
        self.count = self.checked.get()

if __name__ == '__main__':
    root = tkinter.Tk()
    frame = SturaMainFrame(master=root)
    frame.mainloop()
