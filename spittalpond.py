import requests
import json

class SpittalPond:
    """" Python implementation to the Oasis Django API

    This class provides an easy to use front-end interface 
    to the Oasis mid-tier Django API. 
    """

    # Valid dictionary types for Django mid-tier.
    # Ironically, stored in a dict that maps names to URLs.
    dict_types = {
        "LossBinDict":"/oasis/createLossBinDict",
        "HazardIntensityBinDict":"/oasis/createHazardIntensityBinDict",
        "DamageBinDict":"/oasis/createDamageBinDict",
        "EventDict":"/oasis/createEventDict",
        "ExposureDict":"/oasis/createExposureDict",
        "AreaPerilDict":"/oasis/createAreaPerilDict",
        "VulnDict":"/oasis/createVulnDict",
    }

    def validate_dict_type(self, dict_type):
        if (dict_type in self.dict_types) == False:
            print("Failed to create a new dictionary!"
                "Invalid dict_type in arguments.")
            return False
        return True

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
        """ Uploads a file to the server.
        
        Uploads a local file but allows the option to rename it
        before sending it up to the server.
        """
        url = self.base_url + "/oasis/doTaskUploadFileHelper/"

        print(upload_filename)
        with open(local_absolute_filepath) as f:
            in_file = f
            response = self.do_request(
                url,
                #TODO: Get the upload_filename to actually work.
                in_file_dict={upload_filename:in_file}
            )
            return response

    def create_file_upload(self, upload_filename,
                            pub_user, module_supplier_id):
        """ Creates a file upload and returns the ID"""
        up_response = self.do_request(
            self.base_url +
            "/oasis/createFileUpload/" +
            pub_user + "/" +
            upload_filename + "/"
            + module_supplier_id + "/"
        )
        up_id = json.loads(up_response.content)['id']
        return up_id

    def create_file_download(self, upload_filename,
                            pub_user, module_supplier_id):
        """ Creates a file download and returns the ID"""
        down_response = self.do_request(
            self.base_url +
            "/oasis/createFileDownload/" +
            pub_user + "/" +
            upload_filename + "/" +
            module_supplier_id + "/"
        )
        down_id = json.loads(down_response.content)['id']
        print(json.loads(down_response.content))
        return down_id

    def create_dict(self, dict_type, upload_id, download_id,
                    pub_user, module_supplier_id):
        """ Creates a dict with the upload and download IDs."""
        self.validate_dict_type(dict_type)
        response = self.do_request(
            self.base_url +
            self.dict_types[dict_type] + "/" +
            pub_user + "/" +
            module_supplier_id + "/" +
            upload_id + "/" +
            download_id + "/"
        )
        return response

    def do_task(self, task_type, upload_id, sys_config=1):
        """ Creates a task on the job queue. """
        response = self.do_request(
            self.base_url +
            "/oasis/" + task_type + "/" +
            str(sys_config) + "/" +
            upload_id + "/"
        )
        return response
