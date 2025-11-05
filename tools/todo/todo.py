#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Todo (upgraded)
import json, os
from pathlib import Path
HOME=Path.home()
FILE=HOME/".eraldforge_todo.json"

def load():
    try:
        if FILE.exists(): return json.loads(FILE.read_text())
    except: pass
    return []

def save(data):
    try: FILE.write_text(json.dumps(data,indent=2))
    except: pass

def show(data):
    if not data: print("No todos")
    for i,t in enumerate(data, start=1):
        done="x" if t.get("done") else " "
        pr=t.get("priority","-")
        due=t.get("due","-")
        print(f"{i}. [{done}] ({pr}) {t.get('task')}  due:{due}")

def main():
    print("EraldForge Todo")
    while True:
        data=load()
        show(data)
        print("a: add, t: toggle, e: edit, d: delete, q: quit")
        cmd=input("Choice: ").strip().lower()
        if cmd=="a":
            task=input("Task: ").strip()
            pr=input("Priority (low/med/high): ").strip() or "med"
            due=input("Due (YYYY-MM-DD) or blank: ").strip()
            data.append({"task":task,"priority":pr,"due":due,"done":False})
            save(data)
            continue
        if cmd=="t":
            idx=int(input("Index: ").strip())-1
            if 0<=idx<len(data): data[idx]["done"]=not data[idx].get("done",False); save(data)
            continue
        if cmd=="e":
            idx=int(input("Index: ").strip())-1
            if 0<=idx<len(data):
                data[idx]["task"]=input("Task: ").strip() or data[idx]["task"]
                data[idx]["priority"]=input("Priority: ").strip() or data[idx]["priority"]
                data[idx]["due"]=input("Due: ").strip() or data[idx]["due"]
                save(data)
            continue
        if cmd=="d":
            idx=int(input("Index: ").strip())-1
            if 0<=idx<len(data): data.pop(idx); save(data)
            continue
        if cmd in ("q","quit","exit"): break
        print("Unknown")

if __name__=="__main__":
    main()
