import requests
import json
import glob
import time
import os
import logging

logger = logging.getLogger('spittalpond')

class SpittalBase():
    """ A base class that contains generic spittal functions

    Classes such as SpittalModel and SpittalExposures will import this one.
    """


    # TODO: Maybe have individual type for each sub class?
    # Each subclass only really needs to know about itself.
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

    def __init__(self, base_url, pub_user):
        """ Initiating instance.

        Args:
            base_url (str): server's domain name and/or port (without final slash).
            pub_usr (str): the public user used to name certain things.
        """
        self.base_url = base_url
        self.pub_user = pub_user
        self.is_logged_in = False
        self.cookies = None
        # Each instance with have it's own data_dict
        self.data_dict = {}

    def do_request(self, url, in_data=None, in_file_dict=None):
        """ Makes a post request.

        Also automatically passes self.cookies to the post request.
        This authenticates each request.

        Args:
            url (str): the url to make a post request to.
            in_data (dict): optional, used if data needs to be passed.
            in_file_dict (dict): optional, passes file dict to server.

        Returns:
            HttpResponse: server's response
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
        """ Logs into Oasis Django mid-tier.

        Also, set self.cookies to the return session ID.
        This allows for future authentication.

        Args:
            password (str): server Djanger user password.
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

        logger.info( 'Log in response ' + str(response.content))

    def create_file_upload(self, upload_filename,
                            pub_user, module_supplier_id):
        """ Creates a file upload object and returns the ID

        Args:
            upload_filename (str): what the filename will be on the server.
            pub_usr (str): the public user used to name certain things.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict

        Returns:
            int: file upload id.
        """
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
        """ Creates a file download object and returns the ID

        Args:
            upload_filename (str): not to sure where this name is actually used.
            pub_usr (str): the public user used to name certain things.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict

        Returns:
            int: file download id
        """
        down_response = self.do_request(
            self.base_url +
            "/oasis/createFileDownload/" +
            pub_user + "/" +
            upload_filename + "/" +
            str(module_supplier_id) + "/"
        )
        down_id = json.loads(down_response.content)['id']
        return down_id

    def upload_file(self, local_absolute_filepath, upload_filename):
        """ Uploads a file to the server.

        Uploads a local file that is renamed on the server side to
        the upload_filename argument.

        Args:
            local_absolute_filepath (str): path to the file we need to upload.
            upload_filename (str): the name for the server-side file.

        Returns:
            HttpResponse: server's response.
        """
        url = self.base_url + "/oasis/doTaskUploadFileHelper/"

        with open(local_absolute_filepath) as f:
            in_file = f
            response = self.do_request(
                url,
                in_file_dict={upload_filename:in_file}
            )
            return response

    def create_timestamps(self):
        """ Create timestamp for destination files

        Returns:
            str: a timestamnp of the current time.
        """
        str_now = time.strftime("%Y%m%d_%H%M%S_", time.localtime())
        return str_now

    def check_status(self, job_id, config_id=1):
        """ Get the status of the respective job.

        Args:
            job_id (str): id of the job to check status of.
            config_id (int): UNKNOWN

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/statusAsync/" +
            str(config_id) + "/" +
            str(job_id) + "/"
        )
        return response

    def do_task(self, task_type, upload_id, sys_config=1):
        """ Creates a task on the job queue.

        Args:
            task_type (str): type of task to be added to the queue.
            upload_id (int): upload_id of the file to create task for.
            sys_config (int): defines where and how to load the data.

        Returns:
            HttpResponse: server's response.

        """
        response = self.do_request(
            self.base_url +
            "/oasis/doTask" + task_type + "/" +
            str(sys_config) + "/" +
            str(upload_id) + "/"
        )
        return response

    def create_dict(self, dict_type, upload_id, download_id,
                    pub_user, module_supplier_id):
        """ Creates a dict with the upload and download IDs.

        Args:
            dict_type (str): defines the type of dictionary to upload.
            upload_id (int): the id returned from create_file_upload().
            download_id (int): the id returned from create_file_download().
            pub_usr (str): the public user used to name certain things.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/create" + self.types[dict_type] + "/" +
            pub_user + "/" +
            str(module_supplier_id) + "/" +
            str(upload_id) + "/" +
            str(download_id) + "/"
        )
        return response


    def upload_directory(self, directory_path, do_timestamps=True,
                        module_supplier_id=1, pkey=1):
        """ Upload an entire directory of files.

        In order to achieve this I created a file naming convention.

        Args:
            directory_path (str): path to the directory to upload from.
            do_timestamps (bool): optional, timestamps files or not?
            module_supplier_id (int): overall module supplier for uploading.
            pkey (int): UNKNOWN
        """

        # The data_dict stores all the information on uploaded files
        # and there respective structures.
        # TODO: Think of a better name for the data_dict.
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

            # Actually upload the file to the server.
            self.upload_file(
                pathname,
                upload_filename
            )

            # Split the '.'s as well cause they are file extensions.
            splitname = filename.replace(".", "_").split("_")
            data_name = splitname[0] + "_" + splitname[1]

            # Save the data for later use.
            # Update data_dict.
            self.data_dict[data_name] = {
                'filepath': pathname,
                'upload_name': upload_filename,
                'upload_id': up_id,
                'download_id': down_id,
            }

        print("Uploaded directory")


    def load_models(self):
        """ Do tasks, load up models.

        Adds all the tasks in the data_dict to the job queue.
        """
        logger.info('Loading {name} data'.format(name=self.__class__.__name__))
        for type_name, type_ in self.data_dict.iteritems():
            # An exclude for correlations. Isn't created nor has an ID.
            if type_name == "correlations_main":
                continue
            task_response = self.do_task(
                self.types[type_name],
                type_['id']
            )
            self.data_dict[type_name]['job_id'] = json.loads(
                task_response.content
            )['JobId']
            logger.info(
                'Load {name} response: '.format(name=type_name) +
                task_response.content
            )

        print("Loaded model")
