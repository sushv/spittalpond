import requests
import json

class SpittalPond:
    """" Python implementation to the Oasis Django API
    
    This class provides an easy to use front-end interface 
    to the Oasis mid-tier Django API. 
    """
    def __init__(self, base_url, pub_user):
        """ Initiating instance."""
        self.base_url = "http://tmrbmub01prd:8000"
        self.pub_user = "root"
        self.is_logged_in = False
        self.cookies = None

    def do_request(self, url, in_data=None, in_file_dict=None):
        """ Makes a post request.
        
        Also automatically passes self.cookies to the post request.
        This authenticates each request.
        """
        url_string=url
        response=requests.post(
            url_string,
            data=in_data,
            files=in_file_dict,
            cookies=self.cookies  #For Authentication!
        )
        return response
        
    def do_login(self, password):
        """ Logs into Oasis Django mid-tier
        
        Also, set self.cookies to the return session ID.
        This allows for future authentication.
        """
        # Creating JSON string with authentication credentails.
        in_data = ('{{ "username":"{username}",'
                    '"password":"{password}" }}'
                    ).format(
                    username=self.pub_user, 
                    password=password
        )

        url = self.base_url + "/oasis/login"
        response = self.do_request(url, in_data)
        json_response = json.loads(response.content)
        
        if json_response["success"] == False:
            print("Invalid user id or password")
        else:
            self.cookies = dict(sessionid=response.cookies['sessionid'])
            print("You are logged into Mid-tier")

    def upload_file(self, local_absolute_filepath, upload_filename):
        url = self.base_url + "/oasis/doTaskUploadFileHelper/"

        with open(local_absolute_filepath) as f:
            in_file = f
            response = self.do_request(
                url,
                #TODO: Get the upload_filename to actually work.
                in_file_dict={upload_filename:in_file}
            )
            return response
