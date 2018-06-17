def beautify(file):
    file = input("Input file path\n>>> ")
    bfile = "{}.beautiful".format(file)
    outfile = open(bfile, 'w')
    try:
        with open(file, 'r') as f:
            for line in f:
                if '[' not in line and line != " " and line != "\n":
                    outfile.write(line)
            print("\n[+] Done, outfile is:", bfile)
            outfile.close()
    except FileNotFoundError:
        print("{}: File Not Found. Exiting.".format(file))
