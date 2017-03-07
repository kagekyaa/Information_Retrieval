'''
file name: subdomainCombine.py
Author: Kevin Permana,Cesar Eduardo Tejada,Jason Nghe
UCInet ID: 50259184_79277676_77653453

Description:
this subdomainCombine.py is a file for combining result logs from analytics.txt

# Log Header: (example)
    Start Date and Time          : 2017-02-14 20:21:43
    End   Date and Time          : 2017-02-15 00:16:49
    Downloaded                   : 4001
    Total Number of invalids     : 56499
    Page with most outgoing link : http://www.ics.uci.edu/~minhaenl/MH/MHP2G/MHP2G%20v1.2.files
    Number of outgoing links     : 851

    subdomain : # of unique occurrence

'''


def combine():
    number_of_logs = 0
    number_of_downloaded = 0
    total_number_of_invalids = 0
    page_with_most_outgoing_link = ""
    temp_page = ""
    number_of_outgoing_link = 0
    dict_of_subdomains = dict()
    input_file_name = "analytics.txt"
    output_file_name = "analyticsFinal.txt"

    for line in open(input_file_name).readlines():
        if not line.strip():
            continue

        if "Date and Time" in line:
            continue

        if line.startswith("##########################################################"):
            number_of_logs += 1
            continue

        if line.startswith("Downloaded"):
            temp = line.split(": ", 1)[1]
            temp = int(temp)
            if temp > number_of_downloaded:
                number_of_downloaded = temp
            continue

        if line.startswith("Total Number of invalids"):
            temp = line.split(": ", 1)[1]
            temp = int(temp)
            total_number_of_invalids += temp
            continue

        if line.startswith("Page with most outgoing link"):
            temp_page = line.split(": ", 1)[1]
            continue

        if line.startswith("Number of outgoing links"):
            temp = line.split(": ", 1)[1]
            temp = int(temp)
            if temp > number_of_outgoing_link:
                number_of_outgoing_link = temp
                page_with_most_outgoing_link = temp_page[:-1]
            continue

        subdomain = line.split(' ', 1)[0]
        if subdomain in dict_of_subdomains:
            dict_of_subdomains[subdomain] += int(line.split(": ", 1)[1])
        else:
            dict_of_subdomains[subdomain] = int(line.split(": ", 1)[1])

    print "Number of Logs               = ", number_of_logs
    print "Downloaded                   = ", number_of_downloaded
    print "Total Number of invalids     = ", total_number_of_invalids
    print "Page with most outgoing link = ", page_with_most_outgoing_link
    print "Number of outgoing links     = ", number_of_outgoing_link
    print "----------------------------------------------------------"
    print "Subdomain                     : # of unique paths"
    print ""

    # sorting: dict_of_subdomains
    import operator
    sorted_dict_of_subdomains = sorted(dict_of_subdomains.items(), key=operator.itemgetter(1))
    sorted_dict_of_subdomains.reverse()

    for key, value in sorted_dict_of_subdomains:
        if key != "None":
            while True:
                if len(key) > 27:
                    break
                else:
                    key += " "
            print key, " : ", value

    with open(output_file_name, "w") as output_file:
        output_file.writelines("Author    : Kevin Permana,Cesar Eduardo Tejada,Jason Nghe"+ '\n')
        output_file.writelines("UCInet ID : 50259184_79277676_77653453" + '\n')
        output_file.writelines("----------------------------------------------------------" + '\n')
        output_file.writelines("Downloaded                   = "+ str(number_of_downloaded) + '\n')
        output_file.writelines("Total Number of invalids     = "+ str(total_number_of_invalids) + '\n')
        output_file.writelines("Page with most outgoing link = "+ str(page_with_most_outgoing_link) + '\n')
        output_file.writelines("Number of outgoing links     = "+ str(number_of_outgoing_link) + '\n')
        output_file.writelines("----------------------------------------------------------"+'\n')
        output_file.writelines("Subdomain                    : # of unique paths" + "\n")
        output_file.writelines('\n')

        for key, value in sorted_dict_of_subdomains:
            if key != "None":
                while True:
                    if len(key) > 27:
                        break
                    else:
                        key += " "
                output_file.writelines(key + " : " + str(value) + "\n")


        output_file.writelines("##########################################################"+ '\n')

    print "##########################################################"
    print "Successfully writing file     : ", output_file_name

if __name__ == "__main__":
    combine()
