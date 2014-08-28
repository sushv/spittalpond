from spittalbase import SpittalBase
import json
import logging

logger = logging.getLogger('spittalpond')

class SpittalRun(SpittalBase):
    """ Handles everything related to running the data processs

    This is where all of the data and .csv files are created.
    """

    def create_cdf(self, name, benchmark_id, exposure_instance_id):
        response = self.do_request(
            self.base_url +
            "/oasis/createCDF/" +
            name + "/" +
            benchmark_id + "/" +
            exposure_instance_id + "/"
        )
        return response

    def create_cdf_samples(self, name, cdf_id, number_of_samples, sample_type):
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
        response = self.do_request(
            self.base_url +
            "/oasis/createGUL/" +
            name + "/" +
            str(cdf_samples_id) + "/" +
            str(loss_threshhold) + "/"
        )
        return response

    def create_file_download(self, name, filename, module_supplier_id):
        response = self.do_request(
            self.base_url +
            "/oasis/createFileDownload/" +
            name + "/" +
            filename + "/" +
            str(module_supplier_id) + "/"
        )
        return response

    def create_pub_gul(self, name, gul_id, download_file_id):
        """ Create the publish ground up loss. """
        response = self.do_request(
            self.base_url +
            "/oasis/createPubGUL/" +
            name + "/" +
            str(gul_id) + "/" +
            str(download_file_id) + "/"
        )
        return response

    def update_file_download(self, id, name, module_supplier_id, filename):
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

        self.data_dict['kernel_cdf'] = {}
        resp = self.create_cdf(gul_name, benchmark_id, exposure_instance)
        logger.info('Create cdf response: ' + resp.content)

        self.data_dict['kernel_cdf']['id'] = json.loads(
            resp.content
        )['id']


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
        """ Get the GUL data from the server. """

        self.data_dict['kernel_pubgul'] = {}
        resp = self.create_file_download(
            self.pub_user,
            filename,
            module_supplier_id
        )
        logger.info('Create kernel GUL file download response, ' + resp.content)
        self.data_dict['kernel_pubgul']['download_id'] = json.loads(
            resp.content
        )['id']

        resp = self.create_pub_gul(
            gul_name,
            self.data_dict['kernel_gul']['id'],
            self.data_dict['kernel_pubgul']['download_id']
        )
        logger.info('Create kernel publish GUL response , ' + resp.content)

        self.data_dict['kernel_pubgul']['id'] = json.loads(
            resp.content
        )['id']

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

        response1 = self.do_request(
            self.base_url +
            "/oasis/saveFilePubGUL/" +
            str(1) + "/" +
            str(self.data_dict['kernel_pubgul']['id']) + "/"
        )
        logger.info("Save pub GUL response " + response1.content)
        import time
        time.sleep(4)
        self.load_models()
        resp = self.download_file(
            self.data_dict['kernel_pubgul']['download_id']
        )
        logger.info("Download Herlp gul response " + resp.content)

        return resp
