from Tkinter import *
import ttk

root= Tk()
tree= ttk.Treeview(root)
tree.pack(fill=BOTH,expand=YES)
def insert(n):
    if tree.exists(n):
        return
    idx= n.rfind("-")
    if idx<0:
        p=""
    else:
        p= n[:idx]
    insert(p)
    tree.insert( p, "end", n, text=n[idx+1:] )
        
with open("tree.csv") as f:
    for line in f.readlines():
        insert(line)

tree.pack()
root.mainloop()
