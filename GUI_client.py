from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import random as rd
from tkinter import scrolledtext
import tkinter.messagebox
from datetime import datetime
import socket


#global selection
def soc(out):
	
	# Create a socket object 
	s = socket.socket()          
	  
	# Define the port on which you want to connect 
	port =4000             
	  
	# connect to the server on local computer 
	s.connect(('127.0.0.1', port)) 
	  
	# receive data from the server 
	print(s.recv(1024)) 
	

	s.send(str(out).encode('utf-8'))

	print(s.recv(1024)) 
	
	event=s.recv(1024)
	event_m=event.decode('utf-8')
	

	num_of_AC = 3

	event1=['a','b','c']
	event2=['a','b','c']

	log_entry_from_program = 'On the date = {}  \n'.format(out[0])

	txt_scrolled.insert(INSERT,log_entry_from_program)

	for i in range(num_of_AC):
		
		now = datetime.now()
	
		current_time = now.strftime("%H:%M:%S")
	
		AC_ID = i+1

		char1='('
		char2=')'
		event=event_m[event_m.find(char1) : event_m.find(char2)+1]	

		char1='('
		char2=','
		event1[i]=event[event.find(char1)+1 : event.find(char2)]

		char1=':'
		char2=']'
		event2[i]=event[event.find(char1)+1 : event.find(char2)]
	
		message = event1[i]
	
		days = event2[i]
	
		if(days != '-1'):
		
			message = '{} {}'.format(message,days)
		
		log_entry_from_program = '{} :- AC ID = {} {} \n'.format(current_time, AC_ID, message)

		txt_scrolled.insert(INSERT,log_entry_from_program)
		
		event_m=event_m.replace(event,'',1)
	

	s.close() 

	
d1=0
d2=0
d3=0
def clicked():
 
    lbl.configure(text="Values entered",font = 'Comic 10 italic')
    out = []
    d1=rd.randrange(0,100,1)
    d3=rd.randrange(0,100,1)
    d2=rd.randrange(0,100,1)
   
    txt_FE1 = ttk.Label(window, text = d1)
       
    txt_FE1.grid(column=3, row=1)
   
    txt_FE2 = ttk.Label(window, text = d2)

    txt_FE2.grid(column=3, row=2)

    txt_FE3 = ttk.Label(window, text = d3)

    txt_FE3.grid(column=3, row=3)

	
    out.append(str(txt_date.get()))
	
    out.append('1')
    out.append(str(d1))
    out.append('2')
    out.append(str(d2))
    out.append('3')
    out.append(str(d3))

    soc(out)

   
def clicked1():    
    window.destroy()

#global selection
def set_value1(val):
    eff=float(val)
   
    selection=str(int(eff))

    lbl_FE11 = ttk.Label(window, text = selection ,font = 'Comic 10 normal')
   
    lbl_FE11.grid(column=4, row=1)
    return eff


def set_value2(val):
    eff=float(val)
   
    selection=str(int(eff))

    lbl_FE11 = ttk.Label(window, text = selection ,font = 'Comic 10 normal')
   
    lbl_FE11.grid(column=4, row=2)
    return eff


def set_value3(val):
    eff=float(val)
   
    selection=str(int(eff))

    lbl_FE11 = ttk.Label(window, text = selection ,font = 'Comic 10 normal')
   
    lbl_FE11.grid(column=4, row=3)
    return eff


###Name a function here
window = Tk()
 
window.title("AC info")

window.iconbitmap(r'UI/AC.ico')

window.geometry('1000x750')


lbl_date = ttk.Label(window, text = "Date: ")

lbl_date.grid(column=0, row=0)

txt_date = ttk.Entry(window,width=20)

txt_date.grid(column=1, row=0)

lbl_AC1 = ttk.Label(window, text = "AC ID: ")

lbl_AC1.grid(column=0, row=1)

txt_AC1 = ttk.Label(window, text = 1)

#txt_AC1 = ttk.Entry(window,width=20)

txt_AC1.grid(column=1, row=1)

lbl_FE1 = ttk.Label(window, text = "Filter Efficiency ",font = 'Comic 10 normal')

lbl_FE1.grid(column=2, row=1)

lbl_AC2 = ttk.Label(window, text = "AC ID: ")

lbl_AC2.grid(column=0, row=2)

txt_AC2 = ttk.Label(window, text = 2)

#txt_AC2 = ttk.Entry(window,width=20)

txt_AC2.grid(column=1, row=2)

lbl_FE2 = ttk.Label(window, text = "Filter Efficiency ",font = 'Comic 10 normal')

lbl_FE2.grid(column=2, row=2)


lbl_AC3 = ttk.Label(window, text = "AC ID: ")

lbl_AC3.grid(column=0, row=3)

txt_AC3 = ttk.Label(window, text = 3)

#txt_AC3 = ttk.Entry(window,width=20)

txt_AC3.grid(column=1, row=3)

lbl_FE3 = ttk.Label(window, text = "Filter Efficiency ",font = 'Comic 10 normal')

lbl_FE3.grid(column=2, row=3)

lbl = ttk.Label(window, text = "No Values entered yet",font = 'Comic 10 italic')

lbl.grid(column=0, row=4)


   
   
photo = PhotoImage(file='login.png')
btn = ttk.Button(window, text=' Enter', image=photo, command=clicked,compound= LEFT)

btn.grid(column=0, row=6)

photo1 = PhotoImage(file='logout.png')
btn1 = ttk.Button(window, text=' Exit',image=photo1, command=clicked1,compound= LEFT)

btn1.grid(column=1, row=6)

# Create the menubar
menubar = Menu(window)
window.config(menu=menubar)

# Create the submenu

def about_us():
    tkinter.messagebox.showinfo('AC_Client','Enter the relevant data values to add to the blockchain.')


subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Save")
subMenu.add_command(label="Exit",command = clicked1)

subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=subMenu)
subMenu.add_command(label="About Us",command = about_us)



 
txt_scrolled = scrolledtext.ScrolledText(window,width=100,height=50)

txt_scrolled.grid(column=1,row=5)


   

window.mainloop()
