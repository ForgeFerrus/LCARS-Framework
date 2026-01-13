class LCARSConsole:
    def __init__(self):
        print("LCARS Console Initialized")

    def run(self):
        while True:
            command = input("LCARS> ")
            if command.lower() in ["exit", "quit"]:
                print("Exiting LCARS Console...")
                break
            else:
                print(f"Command '{command}' not recognized.")

xj = LCARSConsole()
xj.run()