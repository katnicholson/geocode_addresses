# Google Enterprise key values

# (Author: KN, Updated: 3/28/2016)

class Params:
    def __init__(self):
        self.parser = OptionParser()

        self.parser.add_option("-e", "--email", dest="email",
                          help="email address", metavar='"test123@gmail.com"')
		
		# enter enterprise client key and privateKey
		self.client = ""
		self.privateKey = ""
		
		#clientID and privatekey from Google API for Work
		#client = "userid/institution"
		#privateKey = "aA1p8hanU_meric....="
		#channel = ""