# ChessController.py
def startGame():
    from ChessMain import main  # Döngüsel bağımlılığı önlemek için burada import ediyoruz
    main()

def startMenu():
    from ChessMenu import mainMenu  # Döngüsel bağımlılığı önlemek için burada import ediyoruz
    mainMenu()