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

    types = {
        "correlations_main":None,
        "dict_areaperil":"AreaPerilDict",
        "dict_damagebin":"DamageBinDict",
        "dict_event":"EventDict",
        "dict_exposure":"ExposureDict",
        "dict_hazardintensitybin":"HazardIntensityBinDict",
        "dict_vuln":"VulnDict",
        "exposures_instance":"ExposureInstance",
        "exposures_main":"ExposureVersion",
        "version_hazfp":"HazFPVersion",
        "version_vuln":"VulnVersion",
        "vuln_instance":"VulnInstance",
        "hazfp_instance":"HazFPInstance"
    }
    # TODO: Maybe consolidate all of these dicts.
    # Valid dictionary types for Django mid-tier.
    # Ironically, stored in a dict that maps names to URLs.
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
            "/oasis/create" + self.types[dict_type] + "/" +
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
            "/oasis/create" + self.types[version_type] + "/" +
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
            pname + "/" +
            str(exposure_version_id) + "/" +
            str(exposure_dict_id) + "/" +
            str(area_peril_dict_id) + "/" +
            str(vuln_dict_id) + "/"
        )
        print(response.content)
        return response

    def create_hazfp_instance(self, pname, hazfp_version_id,
                                event_dict_id, area_peril_dict_id,
                                hazard_intensity_bin_id, pkey):
        """ Creates an instance of the hazfp data."""
        response = self.do_request(
            self.base_url +
            "/oasis/createHazFPInstance/" +
            pname + "/" +
            str(hazfp_version_id) + "/" +
            str(event_dict_id) + "/" +
            str(area_peril_dict_id) + "/" +
            str(hazard_intensity_bin_id) + "/" +
            pkey + "/"
        )
        return response

    def create_vuln_instance(self, pname, vuln_version_id, vuln_dict_id,
                                hazard_intensity_bin_dict_id,
                                damage_bin_dict_id, pkey):
        response = self.do_request(
            self.base_url +
            "/oasis/createVulnInstance/" +
            pname + "/" +
            vuln_version_id + "/" +
            vuln_dict_id + "/" +
            hazard_intensity_bin_dict_id + "/" +
            damage_bin_dict_id + "/" +
            pkey + "/"
        )
        return response

    def do_task(self, task_type, upload_id, sys_config=1):
        """ Creates a task on the job queue. """
        response = self.do_request(
            self.base_url +
            "/oasis/doTask" + task_type + "/" +
            str(sys_config) + "/" +
            str(upload_id) + "/"
        )
        return response

    def create_timestamps(self):
        """ Create timestamp for destination files"""
        str_now = time.strftime("%Y%m%d_%H%M%S_", time.localtime())
        return str_now

    def check_status(self, job_id, config_id=1):
        """ Get the status of the respective job."""
        response = self.do_request(
            self.base_url +
            "/oasis/statusAsync/" +
            str(config_id) + "/" +
            str(job_id) + "/"
        )
        return response

    def upload_directory(self, directory_path, do_timestamps=True,
                        module_supplier_id=27, pkey=1):
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
            data_name = splitname[0] + "_" + splitname[1]

            # Update data_dict.
            data_dict[data_name] = {
                'filepath': pathname,
                'upload_name': upload_filename,
                'upload_id': up_id,
                'download_id': down_id,
                #'id': json.loads(creation_response.content)['id']
            }


        ##### Create the Model Structures ####
        # For dictionary types.
        for type_name, type_ in data_dict.iteritems():
            splitname = type_name.replace(".", "_").split("_")
            if splitname[0] == 'dict':
                creation_response = self.create_dict(
                    type_name,
                    type_['upload_id'],
                    type_['download_id'],
                    self.pub_user,
                    module_supplier_id
                )
                type_['id'] = json.loads(creation_response.content)['id']

            elif splitname[0] == 'version':
                # For version types.
                creation_response = self.create_version(
                    type_name,
                    type_['upload_id'],
                    type_['download_id'],
                    "ModelKey",
                    module_supplier_id
                )
                type_['id'] = json.loads(
                    creation_response.content
                )['id']


        # The correlations file simply has to be uploaded.
        # create_exposure_version() will take care of the rest.


        # For now we are assuming that there is only one exposure version.
        # so we do not need to loop through.
        creation_response = self.create_exposure_version(
            self.pub_user,
            module_supplier_id,
            data_dict['exposures_main']['upload_id'],
            data_dict['correlations_main']['upload_id']
        )
        data_dict['exposures_main']['id'] = json.loads(
            creation_response.content
        )['id']

        # Create the exposure instance.
        data_dict['exposures_instance'] = {}
        creation_response = self.create_exposure_instance(
            self.pub_user,
            data_dict['exposures_main']['id'],
            data_dict['dict_exposure']['id'],
            data_dict['dict_areaperil']['id'],
            data_dict['dict_vuln']['id']
        )
        data_dict['exposures_instance']['id'] = json.loads(
            creation_response.content
        )['id']

        # Create the hazfp instance.
        data_dict['hazfp_instance'] = {}
        creation_response = self.create_hazfp_instance(
            self.pub_user,
            data_dict['version_hazfp']['id'],
            data_dict['dict_event']['id'],
            data_dict['dict_areaperil']['id'],
            data_dict['dict_hazardintensitybin']['id'],
            "ModelKey"
        )
        data_dict['hazfp_instance']['id'] = json.loads(
            creation_response.content
        )['id']

        # Create vuln instance.
        data_dict['vuln_instance'] = {}
        creation_response = self.create_vuln_instance(
            self.pub_user,
            data_dict['version_vuln']['id'],
            data_dict['dict_vuln']['id'],
            data_dict['dict_hazardintensitybin']['id'],
            data_dict['dict_damagebin']['id'],
            "ModelKey"
        )
        data_dict['vuln_instance']['id'] = json.loads(
            creation_response.content
        )['id']


        # Do tasks (Load models)
        for type_name, type_ in data_dict.iteritems():
            # An exclude for correlations. Isn't created nor has an ID.
            if type_name == "correlations_main":
                continue
            task_response = self.do_task(
                self.types[type_name],
                type_['id']
            )
            data_dict[type_name]['job_id'] = json.loads(
                task_response.content
            )['JobId']

        print("Finally done")
        return data_dict


    def create_benchmark(self, name, hazfp_instance_id,
                         exposure_instance_id, vuln_instance_id,
                         chunk_size, min_chunk, max_chunk):
        response = self.do_request(
            self.base_url +
            "/oasis/createBenchmark/" +
            name + "/" +
            str(hazfp_instance_id) + "/" +
            str(exposure_instance_id) + "/" +
            str(vuln_instance_id) + "/" +
            str(chunk_size) + "/" +
            str(min_chunk) + "/" +
            str(max_chunk) + "/"
        )
        return response
