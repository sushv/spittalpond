import json
from spittalbase import SpittalBase
import logging

logger = logging.getLogger('spittalpond')

class SpittalExposure(SpittalBase):
    """ Handles everything exposure related.

    Mainly used for creating exposure instances for a specified model.
    Also, can create a benchmark for an exposure.
    """

    def create_exposure_version(self, pname, module_supplier_id,
                                upload_id, correlation_upload_id):
        """ Creates a new exposure version

        Args:
            pname (str): UNKNOWN, assuming just a user-friendly name.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict
            upload_id (int): the id returned from create_file_upload().
            correlation_upload_id (int): id returned from the correlation file.

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/createExposureVersion/" +
            pname + "/" +
            str(module_supplier_id) + "/" +
            str(upload_id) + "/" +
            str(correlation_upload_id) + "/"
        )
        logger.info(
            'Create_exposure_version response ' +
            str(response.content)
        )
        return response

    def create_exposure_instance(self, pname, exposure_version_id,
                                exposure_dict_id, area_peril_dict_id,
                                vuln_dict_id):
        """ Creates an instance of the exposure data.

        Args:
            pname (str): UNKNOWN, assuming just a user-friendly name.
            exposure_version_id (int): id returned by the respective do_task() method.
            exposure_dict_id (int): id returned by the respective do_task() method.
            area_peril_dict_id (int): id returned by the respective do_task() method.
            vuln_dict_id (int): id returned by the respective do_task() method.

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/createExposureInstance/" +
            pname + "/" +
            str(exposure_version_id) + "/" +
            str(exposure_dict_id) + "/" +
            str(area_peril_dict_id) + "/" +
            str(vuln_dict_id) + "/"
        )
        return response

    def create_hazfp_instance(self, pname, hazfp_version_id,
                                event_dict_id, area_peril_dict_id,
                                hazard_intensity_bin_id, pkey):
        """ Creates an instance of the hazfp data.

        Args:
            pname (str): UNKNOWN, assuming just a user-friendly name.
            hazfp_version_id (int): id returned by the respective do_task() method.
            event_dict_id (int): id returned by the respective do_task() method.
            area_peril_id (int): id returned by the respective do_task() method.
            hazard_intensity_bin_id (int): id returned by the respective do_task() method.
            pkey (int): UNKNOWN

        Returns:
            HttpResponse: server's response.
        """
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
        """ Creates an instance of the vulnerability data.

        Args:
            pname (str): UNKNOWN, assuming just a user-friendly name.
            vuln_version_id (int): id returned by the respective do_task() method.
            vuln_dict_id (int): id returned by the respective do_task() method.
            hazard_intensity_bin_dict_id (int): id returned by the respective do_task() method.
            damage_bin_dict_id (int): id returned by the respective do_task() method.
            pkey (int): UNKNOWN

        Returns:
            HttpResponse: server's response.
        """
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

    # TODO: At the moment this whole method is, more or less, hardcoded.
    # So it will only run is the 3 specific exposure files are present.
    # Work on making it more dynamic.
    def create_exposure_structure(self, model_data_dict, module_supplier_id=1):
        """ Creates supporting exposure structure from the data_dict.

        Args:
            model_data_dict (dict): the model data to build the exposure onto.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict
        """

        logger.info('Creating the exposure strutuces.')
        # Upload the lone dictionary.
        creation_response = self.create_dict(
            "dict_exposure",
            self.data_dict['dict_exposure']['upload_id'],
            self.data_dict['dict_exposure']['download_id'],
            self.pub_user,
            self.data_dict['dict_exposure']['module_supplier_id'],
        )
        logger.info('Create dict_exposure response: ' + creation_response.content)

        self.data_dict['dict_exposure']['taskId'] = json.loads(
            creation_response.content
        )['taskId']

        # The correlations file simply has to be uploaded.
        # create_exposure_version() will take care of the rest.

        # For now we assume that there is only one exposure version.
        # so we do not need to loop through.
        creation_response = self.create_exposure_version(
            "exposure_main",
            self.data_dict['exposures_main']['module_supplier_id'],
            self.data_dict['exposures_main']['upload_id'],
            self.data_dict['correlations_main']['upload_id'],
        )
        logger.info('Create exposure_verion response: ' + creation_response.content)

        self.data_dict['exposures_main']['taskId'] = json.loads(
            creation_response.content
        )['taskId']

        # Create the exposure instance.
        self.data_dict['exposures_instance'] = {}
        creation_response = self.create_exposure_instance(
            self.pub_user,
            self.data_dict['exposures_main']['taskId'],
            self.data_dict['dict_exposure']['taskId'],
            model_data_dict['dict_areaperil']['taskId'],
            model_data_dict['dict_vuln']['taskId']
        )
        logger.info('Create exposure_instance response: ' + creation_response.content)

        self.data_dict['exposures_instance']['taskId'] = json.loads(
            creation_response.content
        )['taskId']

        # Create the hazfp instance.
        self.data_dict['hazfp_instance'] = {}
        creation_response = self.create_hazfp_instance(
            self.pub_user,
            model_data_dict['version_hazfp']['taskId'],
            model_data_dict['dict_event']['taskId'],
            model_data_dict['dict_areaperil']['taskId'],
            model_data_dict['dict_hazardintensitybin']['taskId'],
            "ModelKey"
        )
        logger.info('Create hazfp_verion response: ' + creation_response.content)

        self.data_dict['hazfp_instance']['taskId'] = json.loads(
            creation_response.content
        )['taskId']

        # Create vuln instance.
        self.data_dict['vuln_instance'] = {}
        creation_response = self.create_vuln_instance(
            self.pub_user,
            model_data_dict['version_vuln']['taskId'],
            model_data_dict['dict_vuln']['taskId'],
            model_data_dict['dict_hazardintensitybin']['taskId'],
            model_data_dict['dict_damagebin']['taskId'],
            "ModelKey"
        )
        logger.info('Create vuln_instance response: ' + creation_response.content)

        self.data_dict['vuln_instance']['taskId'] = json.loads(
            creation_response.content
        )['taskId']
        print("Finished creating exposure structures.")

    def create_benchmark(self, name="Benchmark", chunk_size=10,
                        min_chunk=4, max_chunk=4):
        """ Creates a benchmark task based on this exposure.

        Args:
            name (str): the name of the benchmark.
            chunk_size (int): the number of simulations to run each chunk.
            min_chunk (int): UNKNOWN
            max_chunk (int): UNKNOWN

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/createBenchmark/" +
            name + "/" +
            str(self.data_dict['hazfp_instance']['taskId']) + "/" +
            str(self.data_dict['exposures_instance']['taskId']) + "/" +
            str(self.data_dict['vuln_instance']['taskId']) + "/" +
            str(chunk_size) + "/" +
            str(min_chunk) + "/" +
            str(max_chunk) + "/"
        )
        return response
