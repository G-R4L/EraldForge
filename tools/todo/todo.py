#!/data/data/com.termux/files/usr/bin/env python3
import json, sys
from pathlib import Path
TFILE = Path.home() / ".eraldforge_todo.json"

def load():
    if TFILE.exists():
        return json.load(TFILE.open())
    return []

def save(data):
    json.dump(data, TFILE.open("w"), indent=2)

def main():
    while True:
        data = load()
        print("\nTodo list:")
        for i, t in enumerate(data):
            print(f"{i}. [{'x' if t.get('done') else ' '}] {t.get('task')}")
        print("a. add, t. toggle, d. delete, q. quit")
        c = input("Choice: ").strip()
        if c == "a":
            task = input("Task: ").strip()
            if task:
                data.append({"task": task, "done": False})
                save(data)
        elif c == "t":
            try:
                idx = int(input("Index: ").strip())
            except Exception:
                print("Invalid index")
                continue
            if idx < 0 or idx >= len(data):
                print("Index out of range")
                continue
            data[idx]['done'] = not data[idx].get('done', False)
            save(data)
        elif c == "d":
            try:
                idx = int(input("Index: ").strip())
            except Exception:
                print("Invalid index")
                continue
            if idx < 0 or idx >= len(data):
                print("Index out of range")
                continue
            data.pop(idx)
            save(data)
        elif c == "q":
            break
        else:
            print("Unknown")

if __name__ == "__main__":
    main()
