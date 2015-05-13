# Simple Python Web Crawler

print("Program Starting\n")

domain = raw_input("Enter Domain: ") #"example.com"
print("")

jsonOkay = True

emailOkay = True
if emailOkay:
    want_email = raw_input("Do you want email from this thing? [Y/n]")
    if want_email and not want_email.lower() == "y":
        emailOkay = False
        print("Okay, no email! Fine.\n")

    if emailOkay:
        print("Email Settings")
        FROM = raw_input("Enter From Address: ")
        TO = [raw_input("Enter To Address: ")]
        SERVICE = "smtp.gmail.com"
        PORT = 587
        USERNAME = raw_input("Enter Account Username: ")
        PASSWORD = raw_input("Enter Account Password: ")
        emailCount = 0
        import emailSender
        SUBJECT = "Web Craler: Starting"
        TEXT = str("Crawler pointing of this address")
        emailSender.send(FROM,TO,SUBJECT,TEXT,SERVICE,PORT,USERNAME,PASSWORD)
        print("")

import urllib2, urlparse, json, os, time, datetime
from bs4 import BeautifulSoup

if jsonOkay:
    if os.path.isfile("data.json"):
        os.remove("data.json")

def robots():
    try:
        robotsFile = urllib2.urlopen("http://" + linkDomain + "/robots.txt")
        try:
            collection = True
            for line in robotsFile:
                line = line.rstrip('\n')
                if "User-agent: " in line[:12]:
                    if line[12] != "*":
                        collection = False
                    else:
                        collection = True
                if collection:
                    if "Disallow: " in line[:10]:
                        domains[linkDomain]['ignore'].append(line[10:])
                    if "Crawl-delay: " in line[:13]:
                        domains[linkDomain]['delay'] = line[13:]
        except:
            print("problem is not from request")
    except:
        pass

def processURL(tag):
    if "#" in tag['href']:
        for place in range(len(tag['href'])):
            if tag['href'][place] == "#":
                tag['href'] = tag['href'][:place]
                break
    if len(tag['href']) > 1:
        # Join domain with path
        if urlparse.urlparse(tag['href']).netloc == "":
            if tag['href'][0] != "/":
                link = urlparse.urlparse(url[0]).netloc + "/" + tag['href']
            else:
                link = urlparse.urlparse(url[0]).netloc + tag['href']
        else:
            link = tag['href']
        # Remove www.
        if urlparse.urlparse(link).netloc[:4] == "www.":
            link = link.replace("www.", "")
        # Add scheme
        if not urlparse.urlparse(link).scheme:
            link = "http://" + link
    else:
        link = tag['href']
    return link

def emailSend():
    global emailCount
    SUBJECT = "Web Craler: Message"
    TEXT = "Log #" + str(emailCount) + "\n" + str(text)
    emailSender.send(FROM,TO,SUBJECT,TEXT,SERVICE,PORT,USERNAME,PASSWORD)
    emailCount += 1

def logData():
    try:
        inFile = open("data.json")
        dataLog = json.loads(inFile.read())
        inFile.close()
    except:
        print("No JSON file found\n")
        dataLog = []

    dataLog.append(text)

    with open('data.json', 'w') as outFile:
        json.dump(dataLog, outFile)
    outFile.close()

def message():
    global lastPageCount
    pageCount = 0
    queueCount = 0

    for subdomain, url in urls.iteritems():
        queueCount += len(url)
    for subdomain, url in domains.iteritems():
        pageCount += url['pages']
    lastPageCount = pageCount - lastPageCount
    print("Log " + str(emailCount) + " " + str(datetime.datetime.fromtimestamp(int(currentTime)).strftime('%Y-%m-%dT%H:%M:%S')) + " [Links in queue: " + str(queueCount) + " | " + str(round(lastPageCount/60.0,2)) + " ppm]\n")
    dataText = {str(currentTime):{"Domains": len(domainsList), "pages_visited": pageCount, "links_recorded": len(recorded), "links_in_queue": queueCount, "total_page_speed": round(pageCount/(hours * 60.0),2), "recent_page_speed": round(lastPageCount/60.0,2)}}
    lastPageCount = pageCount
    return dataText

urls = {domain:["http://" + domain]}
recorded = list()

domains = {domain:{'delay': 0, 'ignore': [], "connections": {"total":0, "external":0, "internal": 0}, "pages":0}}
domainsList = [domain]

# Fill out starting domains dictionary
try:
    robotsFile = urllib2.urlopen("http://" + domain + "/robots.txt")
    for line in robotsFile:
        line = line.rstrip('\n')
        if "Disallow: " in line[0:10]:
            domains[domain]['ignore'].append(line[10:])
        if "Crawl-delay: " in line[:13]:
            domains[domain]['delay'] = line[13:]
    print("Robots.txt Request Successful\n")
except:
    print("Robots.txt Request Unsuccessful\n")

urlsInQueue = True
lastPageCount = 0
lastTime = time.time()
hours = 0
print("Staring Time: " + str(lastTime) + "\n")

while urlsInQueue:
    urlsInQueue = False
    removeLinks = []
    addLinks = []
    for subdomain, url in urls.iteritems():
        if url:
            try:
                htmltext = urllib2.urlopen(url[0])
                soup = BeautifulSoup(htmltext.read())
                removeLinks.append(subdomain)

                # Page Count
                domains[subdomain]["pages"] += 1

                ignoreList = domains[subdomain]["ignore"]

                for tag in soup.findAll('a', href=True):
                    currentTime = time.time()
                    if (currentTime - lastTime) > 3600:
                        hours += 1
                        lastTime = time.time()
                        text = message()
                        if jsonOkay:
                            logData()
                        if emailOkay:
                            emailSend()
                    link = processURL(tag)
                    if len(link) > 1:
                        domains[subdomain]["connections"]["total"] += 1
                        linkDomain = urlparse.urlparse(link).netloc
                        if domain in linkDomain: # Internal
                            # Check new domain
                            if linkDomain:
                                if link not in recorded:
                                    recorded.append(link)
                                    if not any(x in link for x in ignoreList):
                                        addLinks.append([linkDomain, link])
                                if linkDomain not in domainsList:
                                    domainsList.append(linkDomain)
                                    domains[linkDomain] = {'delay': 0, 'ignore': [], "connections": {"total":0, "external":0, "internal": 0}, "pages":0}
                                    robots()
                                if linkDomain != subdomain:
                                    if linkDomain in domains[subdomain]["connections"].keys():
                                        domains[subdomain]["connections"][linkDomain] += 1
                                    else:
                                        domains[subdomain]["connections"][linkDomain] = 1
                                else:
                                    domains[subdomain]["connections"]["internal"] += 1
                        else: # External
                            domains[subdomain]["connections"]["external"] += 1
            except:
                pass
    # Removed scanned links
    for removeDomain in removeLinks:
        urls[removeDomain].pop(0)

    # Add scaned links
    for addDomain in addLinks:
        if addDomain[0] in urls.keys():
            urls[addDomain[0]].append(addDomain[1])
        else:
            urls[addDomain[0]] = [addDomain[1]]
    # Are Links in Queue
    for queueList in urls.values():
        if len(queueList) > 0:
            urlsInQueue = True

print("Done")
