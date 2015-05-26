import urllib
import urllib2
import re
import logging
from string import maketrans
logging.basicConfig(format='%(asctime)s: %(message)s', filename='run.log',level=logging.DEBUG, datefmt='%d/%m/%Y %I:%M:%S %p')

## To use this script:
## 1. Fill the url of the search page in at url with %d instead of the page number
##    and %s instead of the activity name.
## 2. Fill in the activity type in activity, see below for the values.
## 3. If you start the script for the first time make sure that the two lines below 'to start with:' do
##    not start with a '#' and the three lines below 'to continue:' do start with a '#'. If you want
##    to continue after an error make sure it's the other way around.
## 4. To clear the log file before a new run; delete the file. Then run the script! Good luck.

##<option value="RUN">Running</option>
##<option value="BIKE">Cycling</option>
##<option value="MOUNTAINBIKE">Mountain Biking</option>
##<option selected="selected" value="WALK">Walking</option>
##<option value="HIKE">Hiking</option>
##<option value="DH_SKI">Downhill Skiing</option>
##<option value="XC_SKI">Cross-Country Skiing</option>
##<option value="SNOWBOARD">Snowboarding</option>
##<option value="SKATE">Skating</option>
##<option value="SWIMMING">Swimming</option>
##<option value="WHEELCHAIR">Wheelchair</option>
##<option value="ROWING">Rowing</option>
##<option value="ELLIPTICAL">Elliptical</option>
##<option value="OTHER">Other</option>
##<option value="YOGA">Yoga</option>
##<option value="PILATES">Pilates</option>
##<option value="CROSSFIT">CrossFit</option>
##<option value="SPINNING">Spinning</option>
##<option value="ZUMBA">Zumba</option>
##<option value="BARRE">Barre</option>
##<option value="GROUP_WORKOUT">Group Workout</option>
##<option value="DANCE">Dance</option>
##<option value="BOOTCAMP">Bootcamp</option>
##<option value="BOXING_MMA">Boxing / MMA</option>
##<option value="MEDITATION">Meditation</option>
##<option value="STRENGTH_TRAINING">Strength Training</option>
##<option value="CIRCUIT_TRAINING">Circuit Training</option>
##<option value="CORE_STRENGTHENING">Core Strengthening</option>
##<option value="ARC_TRAINER">Arc Trainer</option>
##<option value="STAIRMASTER_STEPWELL">Stairmaster / Stepwell</option>
##<option value="SPORTS">Sports</option>
##<option value="NORDIC_WALKING">Nordic Walking</option>

url = "http://runkeeper.com/search/routes/%d?distance=&lon=4.887&location=amsterdam&activityType=%s&lat=52.37" # CHANGE (1.)
count = 1
count2 = 1
activity = "RUN" # CHANGE (2.)
months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]



##################
## to continue: ## CHANGE (3.)
#count = 1411
#count2 = 142
#fileTimes = open("times.csv", "a")
##################
## to start with: ## CHANGE (3.)
fileTimes = open("times.csv", "w")
fileTimes.write("id,name,url,year,month,day,hour_start,minutes_start,hour_end,minutes_end,duration,pace (min/mi),calories,distance (mi)\n")
##################
file = open("runs%03d.csv" % count2, "w")
file.write("id,name,latitude,longitude,distance (mi),url\n")

while True:
    print "page: " + str(count)
    logging.info("page: " + str(count))
    for j in range(0,5):
            try:
                response = urllib2.urlopen(url % (count, activity))
                break
            except urllib2.URLError, e:
                print "timeout error, " + str(5 - j) + " retries remaining."
                logging.warning("timeout error, " + str(5 - j) + " retries remaining.")
                continue        
    html = response.read()
    #print html
    #break
    distMatcher = re.compile('<b>([0-9]*\.[0-9]*)</b>mi')
    nameMatcher = re.compile('Name:</label>\s*<h1>(.*?)</h1>')
    ownerMatcher = re.compile('<div class="routeOwnwer">(.*?)</div>')
    trackMatcher = re.compile('var pointJson = \[(.*?)\];')
    urlMatcher = re.compile('<a href="(.*?)" class="thumbnailUrl">')
    pointsMatcher = re.compile('\"latitude\":(.*?),\"longitude\":(.*?),\"delta')
    
    trackMatch = trackMatcher.findall(html)
    distMatch = distMatcher.findall(html)
    ownerMatch = ownerMatcher.findall(html)
    nameMatch = nameMatcher.findall(html)
    urlMatch = urlMatcher.findall(html)
    #print("trackMatch: " + str(len(trackMatch)) + str(len(distMatch)) + str(len(nameMatch)) + str(len(urlMatch)))
    if len(trackMatch) < 1:
        break
    for i in range(0,min(len(trackMatch),len(distMatch),len(nameMatch),len(urlMatch),len(ownerMatch))): # for each track
        trackId = (count - 1) * 6 + i + 1
        url2 = "http://runkeeper.com" + urlMatch[i]
        name = nameMatch[i].translate(maketrans(",","."))
        owner = ownerMatch[i].translate(maketrans(",","."))
        pointsMatch = pointsMatcher.findall(trackMatch[i])
        dist = float(distMatch[i])

        for j in range(0,len(pointsMatch)): # for each point in the track
            file.write("%d,%s,%s,%s,%f,%s,%s\n" % (trackId, name, pointsMatch[j][0], pointsMatch[j][1], dist, url2, owner))
        for j in range(0,5):
            try:
                response2 = urllib2.urlopen(url2)
                break
            except urllib2.URLError, e:
                print "timeout error, " + str(5 - j) + " retries remaining."
                logging.warning("timeout error, " + str(5 - j) + " retries remaining.")
                continue
        html2 = response2.read()
        activityMatcher = re.compile('routeActivityListItem')
        activityMatch = activityMatcher.findall(html2)
        if(activityMatch): # if there are recorded activities
            dateYearMatcher = re.compile('routeActivityListDate"><.*?>(.*?)</a>')
            timesMatcher = re.compile('routeActivityListTime">(.*?)</div>\s*</td>\s*<td>\s*(\S*?)\s*</td>\s*<td>\s*(\S*?)\s*<span class="details">min/mi</span>\s*</td>\s*<td>\s*(\S*)\s*</td>')
            dateYearMatch = dateYearMatcher.findall(html2)
            timesMatch = timesMatcher.findall(html2)
            for k in range(0,len(timesMatch)): # for each activity
                if len(timesMatch[k][0]) < 48:
                    continue
                year = int(timesMatch[k][0][24:28])
                month = months.index(timesMatch[k][0][4:7]) + 1
                day = int(timesMatch[k][0][8:10])
                hourStart = int(timesMatch[k][0][11:13])
                minutesStart = int(timesMatch[k][0][14:16])
                hourEnd = int(timesMatch[k][0][42:44])
                minutesEnd = int(timesMatch[k][0][45:47])
                string = "%d,%s,%s,%d,%d,%d,%d,%d,%d,%d,%s,%s,%f,%f\n" % \
                (trackId, name, url2, year, month, day, hourStart, minutesStart, hourEnd, minutesEnd, timesMatch[k][1], timesMatch[k][2], float(timesMatch[k][3]), dist)
                fileTimes.write(string)
                logging.info(string)
    count += 1
    if count % 10 == 1:
#        break
        count2 += 1
        file.close()
        file = open("runs%03d.csv" % count2, "w")
        file.write("id,name,latitude,longitude,distance,url\n")
#    break
    
file.close()
fileTimes.close()

print 'downloading complete'
