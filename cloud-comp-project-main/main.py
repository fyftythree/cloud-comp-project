from models import *

def main():
    while True:
        chord = get_chord_note(input("Enter chord name: "),input("Enter chord type: "))
        print(chord)
main()