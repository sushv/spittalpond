from spittalbase import SpittalBase
import json
import logging

logger = logging.getLogger('spittalpond')

class SpittalRun(SpittalBase):
    """ Handles everything related to running the data processs

    This is where all of the data and .csv files are created.
    """

    def create_cdf(self, name, benchmark_id, exposure_instance_id):
        """ Creates the CDF Django object.

        Args:
            name (str): UNKNOWN, assuming just a user-friendly name.
            benchmark_id (int): the id returned from create_benchmark().
            exposure_instance_id (int): id returned from create_exposure_instance().

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/createCDF/" +
            name + "/" +
            benchmark_id + "/" +
            exposure_instance_id + "/"
        )
        return response

    def create_cdf_samples(self, name, cdf_id, number_of_samples, sample_type):
        """ Create the CDF samples Django object.

        Args:
            name (str): UNKNOWN, assuming just a user-friendly name.
            cdf_id (int): id returned from create_cdf()
            number_of_samples(int): number of cdf samples to create.
            sample_type (int): UNKNOWN

        Returns:
            HttpResponse: server's response.
        """

        response = self.do_request(
            self.base_url +
            "/oasis/createCDFSamples/" +
            name + "/" +
            str(cdf_id) + "/" +
            str(number_of_samples) + "/" +
            str(sample_type) + "/"
        )
        return response

    def create_gul(self, name, cdf_samples_id, loss_threshhold=0):
        """ Creates the ground up loss.

        Args:
            name (str): UNKNOWN, assuming just a user-friendly name.
            cdf_samples_id (int): id returned from create_cdf_samples().
            loss_threshhold (int): UNKNOWN

        Returns:
            HttpResponse: server's response.
        """

        response = self.do_request(
            self.base_url +
            "/oasis/createGUL/" +
            name + "/" +
            str(cdf_samples_id) + "/" +
            str(loss_threshhold) + "/"
        )
        return response

    def create_pub_gul(self, name, gul_id, download_file_id):
        """ Create the publish ground up loss.

        Args:
            name (str): UNKNOWN, assuming just a user-friendly name.
            gul_id (int): id returned from create_gul().
            download_file_id: id returned from create_file_download().

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/createPubGUL/" +
            name + "/" +
            str(gul_id) + "/" +
            str(download_file_id) + "/"
        )
        return response

    def update_file_download(self, id, name, module_supplier_id, filename):
        """ Much like the create_file_download method but instead updates.

        Args:
            id (int): id returned from create_file_download.
            name (str): UNKNOWN, assuming just a user-friendly name.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict
            filename (str): name of the new file download.

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/updateFileDownload/" +
            str(id) + "/" +
            name + "/" +
            str(module_supplier_id) + "/" +
            filename + "/"
        )
        return response


    def create_gul_data(self, gul_name, benchmark_id, exposure_instance):
        """ Create the ground up loss data based on our exposure instance.

        Args:
            gul_name (str): the user friendly name of the gul to create
            benchmark_id (int): the id returned from create_benchmark().
            exposure_instance_id (int): id returned from create_exposure_instance().

        Returns:
            HttpResponse: server's response.
        """

        # Create the cdf Django kernel object.
        self.data_dict['kernel_cdf'] = {}
        resp = self.create_cdf(gul_name, benchmark_id, exposure_instance)
        logger.info('Create cdf response: ' + resp.content)

        self.data_dict['kernel_cdf']['id'] = json.loads(
            resp.content
        )['id']

        # Create the cdf_samples Django kernel object.
        self.data_dict['kernel_cdfsamples'] = {}
        resp = self.create_cdf_samples(
            gul_name,
            self.data_dict['kernel_cdf']['id'],
            10,
            2
        )
        logger.info('Create cdf_samples response: ' + resp.content)

        self.data_dict['kernel_cdfsamples']['id'] = json.loads(
            resp.content
        )['id']


        # Create the GUL Django kernel object.
        self.data_dict['kernel_gul'] = {}
        resp = self.create_gul(gul_name,
            self.data_dict['kernel_cdfsamples']['id'],
            0
        )
        logger.info('Create kernel gul response: ' + resp.content)

        self.data_dict['kernel_gul']['id'] = json.loads(
            resp.content
        )['id']

        print("Created GUL data")

    def get_gul_data(self, gul_name, filename, module_supplier_id):
        """ Get the GUL data from the server.

        Args:
            gul_name (str): The user friendly name of the GUL to create
            filename (str): the name of file to create and download.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict

        Returns:
            HttpResponse: server's response.
            This response also contains all the data from the GUL creation.
        """

        # Create a new file download.
        self.data_dict['kernel_pubgul'] = {}
        resp = self.create_file_download(
            filename,
            self.pub_user,
            module_supplier_id
        )
        logger.info('Create kernel GUL file download response, ' + resp.content)
        self.data_dict['kernel_pubgul']['download_id'] = json.loads(
            resp.content
        )['id']

        # Create the publish GUL.
        resp = self.create_pub_gul(
            gul_name,
            self.data_dict['kernel_gul']['id'],
            self.data_dict['kernel_pubgul']['download_id']
        )
        logger.info('Create kernel publish GUL response , ' + resp.content)

        self.data_dict['kernel_pubgul']['id'] = json.loads(
            resp.content
        )['id']

        # Update the file download.
        self.update_file_download(
            self.data_dict['kernel_pubgul']['download_id'],
            filename,
            module_supplier_id,
            filename,
        )
        logger.info("update kernel publish GUL download, " + resp.content)

        self.data_dict['kernel_pubgul']['download_id_2'] = json.loads(
            resp.content
        )['id']

        # This has to be done like at the very last!!
        self.load_models()

        # A makeshift save of the data.
        response1 = self.do_request(
            self.base_url +
            "/oasis/saveFilePubGUL/" +
            str(1) + "/" +
            str(self.data_dict['kernel_pubgul']['id']) + "/"
        )
        logger.info("Save pub GUL response " + response1.content)

        # TODO: CLEAN UP THIS HERE MESS.
        # Since the save file pub GUL takes time to finish
        # We must wait for it to save the file.
        import time
        time.sleep(4)

        # Reload everything again.
        self.load_models()

        # Actually download the file.
        resp = self.download_file(
            self.data_dict['kernel_pubgul']['download_id']
        )
        logger.info("Download Herlp gul response " + resp.content)

        return resp
