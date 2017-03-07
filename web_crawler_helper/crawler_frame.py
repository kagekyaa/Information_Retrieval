'''
file name: crawler_frame.py
Author: Kevin Permana,Cesar Eduardo Tejada,Jason Nghe
UCInet ID: 50259184_79277676_77653453
CS121 Winter 2017 HW 2
'''
import logging
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
from spacetime_local.IApplication import IApplication
from spacetime_local.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time

# Global Variables for Analytical Statistic:
maximumLink = ""
maximumNumber = 0
totalNumberOfInvalidLinks = 0
dictOfSubdomains = dict()

try:
    # For python 2
    from urlparse import urlparse, parse_qs, urljoin
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs


logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
url_count = (set()
             if not os.path.exists("successful_urls.txt") else
             set([line.strip() for line in open("successful_urls.txt").readlines() if line.strip() != ""]))
MAX_LINKS_TO_DOWNLOAD = 4000

@Producer(ProducedLink)
@GetterSetter(OneUnProcessedGroup)
class CrawlerFrame(IApplication):
    
    def __init__(self, frame):
        self.starttime = time()
        # Set app_id <student_id1>_<student_id2>...
        self.app_id = "50259184_79277676_77653453"
        # Set user agent string to IR W17 UnderGrad <student_id1>, <student_id2> ...
        # If Graduate student, change the UnderGrad part to Grad.
        self.UserAgentString = "IR W17 UnderGrad 50259184, 79277676, 77653453"
        
        self.frame = frame
        assert(self.UserAgentString != None)
        assert(self.app_id != "")
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def initialize(self):
        self.count = 0
        l = ProducedLink("http://www.ics.uci.edu", self.UserAgentString)
        print l.full_url
        self.frame.add(l)

    def update(self):
        for g in self.frame.get_new(OneUnProcessedGroup):
            print "Got a Group"
            outputLinks, urlResps = process_url_group(g, self.UserAgentString)
            for urlResp in urlResps:
                if urlResp.bad_url and self.UserAgentString not in set(urlResp.dataframe_obj.bad_url):
                    urlResp.dataframe_obj.bad_url += [self.UserAgentString]
            try:
                for l in outputLinks:
                    if not is_valid(l):
                        print "invalid url : ",l
                    else:
                        print "valid url: ",l
                    if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
                        lObj = ProducedLink(l, self.UserAgentString)
                        self.frame.add(lObj)
            except Exception:
                with open("unexpected_Error.txt", "a") as unerror:
                    unerror.writelines(str(Exception)+ '\n')
                continue
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def shutdown(self):
        print "downloaded ", len(url_count), " in ", time() - self.starttime, " seconds."
        write_analytics(self.starttime)
        pass

def save_count(urls):
    global url_count
    urls = set(urls).difference(url_count)
    url_count.update(urls)
    if len(urls):
        with open("successful_urls.txt", "a") as surls:
            surls.write(("\n".join(urls) + "\n").encode("utf-8"))

def process_url_group(group, useragentstr):
    rawDatas, successfull_urls = group.download(useragentstr, is_valid)
    save_count(successfull_urls)
    return extract_next_links(rawDatas), rawDatas

#######################################################################################
'''
    STUB FUNCTIONS TO BE FILLED OUT BY THE STUDENT.
    '''
def extract_next_links(rawDatas):
    '''
        rawDatas is a list of objs -> [raw_content_obj1, raw_content_obj2, ....]
        Each obj is of type UrlResponse  declared at L28-42 datamodel/search/datamodel.py
        the return of this function should be a list of urls in their absolute form
        Validation of link via is_valid function is done later (see line 42).
        It is not required to remove duplicates that have already been downloaded.
        The frontier takes care of that.
        
        Suggested library: lxml
        '''

    ##################################################################################
    # Initializing variables:
    global totalNumberOfInvalidLinks
    global dictOfSubdomains
    global url_count
    outputLinks = list()

    ##################################################################################

    print "##########################################################"
    print "length of RawDatas : ", len(rawDatas)
    print "Total Number of invalids so far ", totalNumberOfInvalidLinks
    print "------------------------------"
    for i,raw_content_obj in enumerate(rawDatas):
        
        print "URL         : ",raw_content_obj.url.encode('utf-8')
        print "is_directed : ",raw_content_obj.is_redirected
        if raw_content_obj.is_redirected:
            print "final URL   : ",raw_content_obj.final_url.encode('utf-8')
            if not is_valid(raw_content_obj.final_url):
                continue
        # print raw_content_obj.content
        print "Error Msg   : ",raw_content_obj.error_message
        # print "HTTP Header : ",raw_content_obj.headers
        print "HTTP Code   : ",raw_content_obj.http_code
        # Things that have to be set later by crawlers
        print "------------------------------"
        # print "bad_URL Status : ",raw_content_obj.bad_url
        # print "",raw_content_obj.out_links


        ##################################################################################
        #ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html',params='', query='', fragment=''

        # parsing the url from frontier:
        parsed = urlparse(raw_content_obj.final_url if raw_content_obj.final_url > 0 else raw_content_obj.url)
        # construct the baseURL:
        myBaseUrl = parsed.scheme + "://" + parsed.netloc

        ##################################################################################
        # Count Unique sub domains and its different paths:

        if parsed.hostname in dictOfSubdomains:
            dictOfSubdomains[parsed.hostname].add(raw_content_obj.final_url if raw_content_obj.final_url > 0 else raw_content_obj.url)
        else:
            temp = set()
            temp.add(raw_content_obj.final_url if raw_content_obj.final_url > 0 else raw_content_obj.url)
            dictOfSubdomains[parsed.hostname] = temp

        '''
        print "set Of Unique Subdomains : "
        for key,value in dictOfSubdomains.iteritems():
            print key, " : ", len(value)  # , value
        '''

        ##################################################################################
        # start parsing through the file:

        #if error dont even parse:
        if len(raw_content_obj.error_message) > 0:
            raw_content_obj.bad_url = True
            continue
        
        #if success, start parsing:
        if raw_content_obj.http_code == 200:
            
            try:
                htmlParse = html.document_fromstring(raw_content_obj.content)
            except etree.ParserError:
                return False
            except etree.XMLSyntaxError:
                return False

            # variables for counting most outgoing link from an url:
            global maximumNumber
            global maximumLink
            count = 0

            for element, attribute, link, pos in htmlParse.iterlinks():  # for every links in the file
                # print link         #originalLink before parsing
                
                ################################################
                #make relative link absolute:
                link = urljoin(myBaseUrl, link)
                # print "Absolute link : " , link

                with open('absoluteLinks.txt', 'a') as outputfile:
                    outputfile.writelines(link.encode('utf-8') + '\n')

                ################################################
                # check if its a trap or garbage link, don't feed into frontier:
                '''
                if not outputLinks_isValid(link):
                    raw_content_obj.bad_url = True  # mark True, so people don't get this type of link
                    continue
                '''
                # if its a link with query, trim the parameters, higher chance to be a trap link
                firstQuestionMark = int(link.find('?'))
                if firstQuestionMark != -1:
                    link = link[:firstQuestionMark]

                # if its an anchor, trim the anchor
                firstAnchor = int(link.find('#'))
                if firstAnchor != -1:
                    link = link[:firstAnchor]

                ################################################
                # double check http, before put the link into outputLinks
                if link.startswith("http"):
                    outputLinks.append(link)
                    # print "appended! : " , link
                    count = count + 1  # count number of outgoing links

                    with open('links2.txt', 'a') as outputfile:
                        outputfile.writelines(link.encode('utf-8') + '\n')

            # check and update the Most outgoing link if needed:
            if count > maximumNumber:
                maximumNumber = count
                maximumLink = raw_content_obj.url

        else:
            raw_content_obj.bad_url = True
            continue

        # end Parsing
        ##################################################################################

    print "##########################################################"
    print "Current url with most outgoing link : ", maximumLink.encode('utf-8')
    print "Number of outgoing links            : ", maximumNumber
    print "Downloaded so far                   : ", len(url_count)
    print ""
    print ""
    print ""

    return outputLinks

##################################################################################

def is_valid(url):
    '''
        Function returns True or False based on whether the url has to be downloaded or not.
        Robot rules and duplication rules are checked separately.
        
        This is a great place to filter out crawler traps.
        
    '''
    # variables:
    global totalNumberOfInvalidLinks

    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        totalNumberOfInvalidLinks = totalNumberOfInvalidLinks + 1
        return False
    try:
        if is_trap_or_garbage(url):
            totalNumberOfInvalidLinks = totalNumberOfInvalidLinks + 1
            return False
        isValid = re.search("\.ics\.uci\.edu\.?$", parsed.hostname) \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
                             + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|h5" \
                             + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                             + "|thmx|mso|arff|rtf|jar|csv"\
                             + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
        if isValid == False:
            totalNumberOfInvalidLinks = totalNumberOfInvalidLinks + 1


        return isValid

    except TypeError:
        print ("TypeError for ", parsed)

##################################################################################
##################################################################################
##################################################################################
''''
Helper Functions
'''
def is_trap_or_garbage(url):
    '''
        Function returns True or False based on whether the url is a garbage or trap url or not
    '''
    ################################################
    
    # Garbage Links:
    # HTML Anchor:
    if url.startswith("#"):
        return True
    # javascript redirect:
    if url.startswith("javascript"):
        return True
    # mailto :
    if url.startswith("mailto:"):
        return True
    
    # big file
    bigFile = int(url.find('.h5')) # >30gb
    if bigFile != -1:
        return True

    # bad query:
    badQuery = int(url.find('doku.php'))  # bad query
    if badQuery != -1:
        return True
    
    ################################################
    
    # Trap Links:
    if url.startswith("http://calendar.ics.uci.edu"): # not interesting, calendar
        return True
    if url.startswith("https://ganglia.ics.uci.edu"):
        return True
    if url.startswith("http://db.yeastgenome.org/"):
        return True
    if url.startswith("http://pasteur.ics.uci.edu/"): # dead link
        return True

##################################################################################

def write_analytics(startTime):
    '''
        Function that write Analytics into a file:
        1.  Keep track of all the subdomains that it visited, and
            count how many different URLs it has processed from each of those subdomains
        2.  Count how many invalid links it received from the frontier, if any
        3.  Find the page with the most out links (of all pages given to your crawler)
    '''
    print "The END!"

    global totalNumberOfInvalidLinks
    global dictOfSubdomains
    global maximumLink
    global maximumNumber
    global url_count

    print "##########################################################"

    print "Total Number of invalids            : ", totalNumberOfInvalidLinks
    print "Current url with most outgoing link : ", maximumLink
    print "Number of outgoing links            : ", maximumNumber

    print ""
    print "Subdomains : Number of unique Urls"
    for key, value in dictOfSubdomains.iteritems():
        print key, " : ", len(value)

    with open('analytics.txt', 'a') as outputfile:
        # Data and Time:
        import datetime
        start_time = datetime.datetime.fromtimestamp(startTime).strftime('%Y-%m-%d %H:%M:%S')
        current_time = time()
        end_time = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')

        outputfile.writelines("Start Date and Time          : "+ start_time+ '\n')
        outputfile.writelines("End   Date and Time          : "+ end_time+ '\n')
        outputfile.writelines("Downloaded                   : "+ str(len(url_count))+ '\n')

        # 2
        outputfile.writelines("Total Number of invalids     : "+ str(totalNumberOfInvalidLinks)+ '\n')

        # 3
        outputfile.writelines("Page with most outgoing link : "+ str(maximumLink)+ '\n')
        outputfile.writelines("Number of outgoing links     : "+ str(maximumNumber)+ '\n')

        # 1
        outputfile.write('\n')
        for key, value in dictOfSubdomains.iteritems():
            outputfile.writelines(str(key)+ " : "+ str(len(value))+ "\n")
        outputfile.write('\n')

        outputfile.writelines("########################################################## "+ '\n')

    print "##########################################################"

##################################################################################

def outputLinks_isValid(url):
    '''
        Function returns True or False based on whether the url has to be downloaded or not.
        This is a great place to filter out crawler traps.
    '''
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        if is_trap_or_garbage(url):
            return False
        return re.search("\.ics\.uci\.edu\.?$", parsed.hostname) \
               and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|h5" \
                                + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                + "|thmx|mso|arff|rtf|jar|csv" \
                                + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)

##################################################################################
##################################################################################
##################################################################################
