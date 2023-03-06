from gptcli.main import main

if "__main__" == __name__:
    try:
        main()
    except KeyboardInterrupt:
        print("Bye")
