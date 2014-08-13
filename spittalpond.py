import requests
import json
import glob
import time
import os

class SpittalPond:
    """ Python implementation to the Oasis Django API

    This class provides an easy to use front-end interface
    to the Oasis mid-tier Django API.
    """

    # Valid dictionary types for Django mid-tier.
    # Ironically, stored in a dict that maps names to URLs.
    dict_types = {
        "lossbin":"/oasis/createLossBinDict",
        "hazardintensitybin":"/oasis/createHazardIntensityBinDict",
        "damagebin":"/oasis/createDamageBinDict",
        "event":"/oasis/createEventDict",
        "exposure":"/oasis/createExposureDict",
        "areaperil":"/oasis/createAreaPerilDict",
        "vuln":"/oasis/createVulnDict",
        "exposure":"/oasis/createExposureDict"
    }

    version_types = {
        "hazfp":"/oasis/createHazFPVersion",
        "vuln":"/oasis/createVulnVersion"
    }

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
            upload_filename + "/" +
            str(module_supplier_id) + "/"
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
            str(module_supplier_id) + "/"
        )
        down_id = json.loads(down_response.content)['id']
        return down_id

    def create_dict(self, dict_type, upload_id, download_id,
                    pub_user, module_supplier_id):
        """ Creates a dict with the upload and download IDs."""
        response = self.do_request(
            self.base_url +
            self.dict_types[dict_type] + "/" +
            pub_user + "/" +
            str(module_supplier_id) + "/" +
            str(upload_id) + "/" +
            str(download_id) + "/"
        )
        return response

    def create_version(self, version_type, upload_id, pkey,
                    pub_user, module_supplier_id):
        """ Creates a version with the upload and download IDs."""
        response = self.do_request(
            self.base_url +
            self.version_types[version_type] + "/" +
            pub_user + "/" +
            str(module_supplier_id) + "/" +
            str(upload_id) + "/" +
            str(pkey) + "/"
        )
        return response

    def create_exposure_version(self, pname, module_supplier_id,
                                upload_id, correlation_upload_id):
        """ Creates a new exposure version

        Aruguments:
        correlation_upload_id -- Correlation file upload id.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/createExposureVersion/" +
            pname + "/" +
            str(module_supplier_id) + "/" +
            str(upload_id) + "/" +
            str(correlation_upload_id) + "/"
        )
        return response

    def create_exposure_instance(self, pname, exposure_version_id,
                                exposure_dict_id, area_peril_dict_id,
                                vuln_dict_id):
        """ Creates an instance of the exposure data. """
        response = self.do_request(
            self.base_url +
            "/oasis/createExposureInstance/" +
            str(exposure_version_id) + "/" +
            str(exposure_dict_id) + "/" +
            str(area_peril_dict_id) + "/" +
            str(vuln_dict_id) + "/"
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

    def create_timestamps(self):
        """Create timestamp for destination files"""
        str_now = time.strftime("%Y%m%d_%H%M%S_", time.localtime())
        return str_now

    def upload_directory(self, directory_path, do_timestamps=True,
                        module_supplier_id=1, pkey=1):
        """ Upload an entire directory of files.

        In order to acheive this I created a file naming convention.
        """

        ##### Create all file uploads and upload files #####

        # The data_dict stores all the information on uploaded files
        # and there respective structures.
        # TODO: Think of a better name for the data_dict.
        data_dict = {}
        files_to_upload = glob.glob(directory_path + "*")
        timestamp = self.create_timestamps()
        # For all files in directory.
        for pathname in files_to_upload:
            filename = os.path.basename(pathname)
            # Timestamp files if nessecary.
            if do_timestamps:
                upload_filename = timestamp + filename


            # Create the file upload and get ID.
            up_id = self.create_file_upload(
                upload_filename,
                self.pub_user,
                module_supplier_id
            )

            # Create the file download and get ID.
            down_id = self.create_file_download(
                upload_filename,
                self.pub_user,
                module_supplier_id
            )

            # Actually Upload the File
            self.upload_file(
                pathname,
                upload_filename
            )

            # Save the data for later use.
            # Split the '.'s as well cause they are file extensions.
            splitname = filename.replace(".", "_").split("_")
            #data_name = splitname[0] + "_" + splitname[1]

            # Create an empty dict on first run.
            if (splitname[0] in data_dict.keys()) == False:
                data_dict[splitname[0]] = {}

            data_dict[splitname[0]][splitname[1]] = {
                'filepath': pathname,
                'upload_name': upload_filename,
                'upload_id': up_id,
                'download_id': down_id,
                #'id': json.loads(creation_response.content)['id']
            }


        ##### Create the Model Structures ####
        # For dictionary types.
        for dict_type, dict_ in data_dict['dict'].iteritems():
            creation_response = self.create_dict(
                dict_type,
                dict_['upload_id'],
                dict_['download_id'],
                self.pub_user,
                module_supplier_id
            )
            dict_['id'] = json.loads(creation_response.content)['id']

        # For version types.
        for version_type, version in data_dict['version'].iteritems():
            creation_response = self.create_version(
                version_type,
                version['upload_id'],
                version['download_id'],
                self.pub_user,
                module_supplier_id
            )
            version['id'] = json.loads(creation_response.content)['id']

        # The correlations file simply has to be uploaded.
        # create_exposure_version() will take care of the rest.
        for correlation in data_dict['correlations']:
            pass

        # For now we are assuming that there is only one exposure version.
        # so we do not need to loop through.
        creation_response = self.create_exposure_version(
            self.pub_user,
            module_supplier_id,
            data_dict['exposures']['main']['upload_id'],
            data_dict['correlations']['main']['upload_id']
        )
        data_dict['exposures']['main']['id'] = json.loads(
            creation_response.content
        )['id']

        # Create the exposure instance.
        self.create_exposure_instance(
            self.pub_user,
            data_dict['exposures']['main']['id'],
            data_dict['dict']['exposure']['id'],
            data_dict['dict']['areaperil']['id'],
            data_dict['dict']['vuln']['id']
        )

        print("Finally done")
        return data_dict
