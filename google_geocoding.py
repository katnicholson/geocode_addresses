# Google Geocoding
# convert addresses into coordinates (latitude,longitude)

# (Author: KN, Updated: 3/28/2016)

import sys, urllib, urllib2, base64, hashlib, hmac, json, unicodedata, time, os, smtplib
from optparse import OptionParser
from options_key import Params

# Command line options to specify input output files
parser = OptionParser()

# User can define input/output files by
#  1) specifying file paths through the command line options
#  2) setting the default paths in this script to user's local file paths

# 1) Specify file paths according to -i input and -o output arguments, format below

# Options for Input/output .txt file
# Input file is a .txt tab-delimited text file with ID Address City/District State Country
# Output fle is a .txt file that writes above 5 fields + 7 geocode results
parser.add_option("-i", "--input-file", dest="input_file",
                  help="full input file name including .txt", metavar='"C:\\Users\\uname\\Documents\\geocode\\input.txt"')

parser.add_option("-o", "--output-file", dest="output_file",
                  help="full output file name ending in _geocoded.txt", metavar='"C:\\Users\\uname\\Documents\\geocode\\input_geocoded.txt"')

# (Optional) add email address to send Geocoding status notification when finished
parser.add_option("-e", "--email", dest="email",
                  help="email address for status notifications", metavar='"address@gmail.com"')

# load command line args into parser
(options, args) = parser.parse_args()

# 2) Set default paths (if options not specified case) to desired paths
# IF NOT USING COMMAND LINE OPTIONS DEFINE FILES HERE:
user_input_file = "C:\\Users\\uname\\Documents\\input_coords.csv"
user_output_file = "C:\\Users\\uname\\Documents\\output_coords.csv"

# Set path for input .csv with coordinates if user specified in command line option
if options.input_file:
    input_file = os.path.expanduser(options.input_file)
# Set to file path defined in above variables if user did not specify command line option
else:
    input_file = user_input_file
    # if user did not change these defaults, print file instructions
    if "uname" in user_input_file:
        print "MUST EITHER SPECIFY INPUT FILE WITH -i"
        print "OR CHANGE user_input_file PATH IN CODE"
        sys.exit()

# Set path file path to write URLs
if options.output_file:
    output_file = os.path.expanduser(options.output_file)
# Set to file path defined in above variables if user did not specify command line option
else:
    output_file = user_output_file
    # if user did not change these defaults, print file instructions
    if "uname" in user_output_file:
        print "MUST EITHER SPECIFY OUTPUT FILE WITH -o"
        print "OR CHANGE user_output_file PATH IN CODE"
        sys.exit()

# make email address optional argument, no notification if not specified

# adding status email address if specified
if options.email:
    email = options.email
    print "Using email address: %s for query status notifications\n" % email

# define function to send email on Windows
def send_email(to, msg):
    server = smtplib.SMTP('localhost')
    server.sendmail(options.email, to, msg)
    server.quit()

## MAIN CODE ##

# parse input arguments and define function to send requests

# define key and base url
google_url = "http://maps.googleapis.com"
geocoding_endpoint = "/maps/api/geocode/json?"
client = Params.client
privateKey = Params.privateKey
channel = ""

# set input fields
field1 = "ID"
field2 = "In_Address"
field3 = "In_District"
field4 = "In_State"
field5 = "In_Country"
# set output fields to write results
field6 = "Address_Matched"
field7 = "City_Matched"
field8 = "State_Matched"
field9 = "Country_Matched"
field10 = "Location_Type"
field11 = "Latitude"
field12 = "Longitude"

# store starting date and time of batch and display to user
process_start_dtime = time.asctime( time.localtime(time.time()) )
print "Process Start: %s\n" % process_start_dtime

# set read/write permissions to specified input/output files
f_in = open(input_file, 'r')
f_out = open(output_file, 'w')

# define function to read each line of input coordinates, generate URL, and write output of returned geocode results
def geocode_run():

    # read each line in input file and generate address to geocode
    for line in f_in:
        fields = line.strip().replace("\"", "").split('\t')
        #ADDRESS CUSTOMIZATION LINE
        address = "%s+%s,%s,%s" % (fields[1], fields[2], fields[3], fields[4])
        address = unicodedata.normalize('NFKD', address.decode("utf-8", "replace")).encode('ascii', 'ignore')
        address = address.replace("n/a", "").replace(" ", "+")
        print "Address %s: %s" % (fields[0], address)
        #Generate valid signature
        encodedParams = urllib.urlencode({"address":address, "client": client})
        #decode the private key into its binary format
        decodeKey = base64.urlsafe_b64decode(privateKey)
        urltosign = geocoding_endpoint + encodedParams
        #create a signature using the private key and the url encoded, string using HMAC SHA1. This signature will be binary.
        signature = hmac.new(decodeKey, urltosign, hashlib.sha1)
        #encode the binary signature into base64 for use within a URL
        encodedsignature = base64.urlsafe_b64encode(signature.digest())
        signedurl = google_url + geocoding_endpoint + encodedParams + "&signature=" + encodedsignature
        print "%s\n" % signedurl
        data = urllib.urlopen(signedurl)
        data_json = json.loads(data.read())
        city_name = "N/A"
        admin1 = "N/A"
        country = "N/A"
        streetNum = "N/A"
        street = "N/A"
        for i in range(len(data_json["results"])):
           for component in data_json["results"][i]["address_components"]:
              if "locality" in component["types"]:
                 city_name = component["long_name"]
           if city_name != "N/A":
              break
        for i in range(len(data_json["results"])):
           for component in data_json["results"][i]["address_components"]:
              if "administrative_area_level_1" in component["types"]:
                 admin1 = component["long_name"]
           if admin1 != "N/A":
              break
        for i in range(len(data_json["results"])):
           for component in data_json["results"][i]["address_components"]:
              if "country" in component["types"]:
                 country = component["long_name"]
           if country != "N/A":
              break
        for i in range(len(data_json["results"])):
           for component in data_json["results"][i]["address_components"]:
              if "street_number" in component["types"]:
                 streetNum = component["long_name"]
           if streetNum != "N/A":
              break
        for i in range(len(data_json["results"])):
           for component in data_json["results"][i]["address_components"]:
              if "route" in component["types"]:
                 street = component["long_name"]
           if street != "N/A":
              break
        p_city = unicodedata.normalize('NFKD', unicode(city_name)).encode('ascii', 'ignore')
        p_admin1 = unicodedata.normalize('NFKD', unicode(admin1)).encode('ascii', 'ignore')
        p_country = unicodedata.normalize('NFKD', unicode(country)).encode('ascii', 'ignore')
        p_address = unicodedata.normalize('NFKD', unicode(streetNum)).encode('ascii', 'ignore') + " " + unicodedata.normalize('NFKD', unicode(street)).encode('ascii', 'ignore')
        # write output
        try:
           f_out.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (fields[0], fields[1], fields[2], fields[3], fields[4], p_address, p_city, p_admin1 , p_country, data_json["results"][0]["geometry"]["location_type"], data_json["results"][0]["geometry"]["location"]["lat"], data_json["results"][0]["geometry"]["location"]["lng"]))
        # write "not found" for failed geocodes (true error returned, non ValueError type)
        except: f_out.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (fields[0], fields[1], fields[2], fields[3], fields[4], "not found"))
        time.sleep(.5)

## EXECUTE MAIN CODE ##

# write headers
f_out.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12))

# process each geocode request, passing through value errors (which do return successful results),
# writing 'not found' for the rest which are true failed addresses with no output
# runs through entire file until finished
# wrapped in function and exception to deal with non-systematic ValueErrors
try:
    geocode_run()
except ValueError:
    print "Value Error passed"
    geocode_run()
    
print "Finished"
print "Process End: %s" % time.asctime( time.localtime(time.time()) )
f_out.flush()
f_in.close()
f_out.close()

# send email when distance calculations are complete
if options.email: send_email(email, "geocoding addresses finished")
#if options.email: os.system('echo "geocoding addresses finished" | mail -s "geocoding finished" %s' % email)
