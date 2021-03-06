import json
from spittalbase import SpittalBase
import logging

logger = logging.getLogger('spittalpond')

class SpittalModel(SpittalBase):
    """ Handles everything model related. """

    def create_version(self, version_type, version_name, module_supplier_id,
                       upload_id, model_key):
        """ Creates a generic version.

        With `generic` currently meaning the vuln and hazfp versions, as the
        exposure version is handled differently and needs different
        parameters.

        Args:
            version_type (str): defines the type of version to upload.
            version_name (str): A user-friendly name for this version.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict
            upload_id (int): the id returned from create_file_upload().
            model_key (string): The model key.

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/create" + self.types[version_type] + "/" +
            version_name + "/" +
            str(module_supplier_id) + "/" +
            str(upload_id) + "/" +
            model_key + "/"
        )
        return response

    def create_exposure_version(self, version_type, version_name,
                                module_supplier_id, exposure_upload_id,
                                correlations_upload_id):
        """ TODO: Document this function. Should be similar to above. """
        response = self.do_request(
            self.base_url +
            "/oasis/create" + self.types[version_type] + "/" +
            version_name + "/" +
            str(module_supplier_id) + "/" +
            str(exposure_upload_id) + "/" +
            str(correlations_upload_id) + "/"
        )
        return response

    def create_model_structures(self):
        """ Creates supporting module structure from the data_dict.

        Args:
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict
        """
        ##### Create the Model Structures ####
        logger.info('Creating the model structures.')
        for type_name, type_ in self.data_dict.iteritems():
            splitname = type_name.replace(".", "_").split("_")

            # FIXME: Really bad hack to include exposures_main
            # Need to find my naming conventions.
            bad_exposures_hack = splitname[0] == 'exposures'
            # For dictionary types.
            if splitname[0] == 'dict':
                creation_response = self.create_dict(
                    type_name,
                    type_['upload_id'],
                    type_['download_id'],
                    self.pub_user,
                    type_['module_supplier_id'],
                )
                logger.info(
                    'Create dict {dict_} response: '.format(dict_=type_name) +
                    str(creation_response.content)
                )

            # For version types.
            elif splitname[0] == 'version' or bad_exposures_hack:
                # Vuln and Haz version are handled the same.
                if splitname[1] in ['vuln', 'hazfp']:
                    creation_response = self.create_version(
                        type_name,
                        type_name,
                        type_['module_supplier_id'],
                        type_['upload_id'],
                        "ModelKey", # TODO FIXME: Get rid of this hard coding.
                    )

                # Again, need to fix the exposure hack here too.
                elif splitname[1] == 'main':
                    creation_response = self.create_exposure_version(
                        type_name,
                        type_name,
                        type_['module_supplier_id'],
                        type_['upload_id'],
                        self.data_dict['correlations_main']['upload_id'],
                    )
                logger.info(
                    'Create version {version} response: '
                    .format(version=type_name) +
                    str(creation_response.content)
                )
            type_['taskId'] = json.loads(
                creation_response.content
            )['taskId']


        print('Finished creating model strutures.')

    # TODO: Finish creating this method.
    def get_model(self, model_name):
        """ Return a previously uploaded model from the database.

        Args:
            model_name -- The name that the model was uploaded with.
        """
        pass
