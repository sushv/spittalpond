import json
from spittalbase import SpittalBase
import logging

logger = logging.getLogger('spittalpond')

class SpittalModel(SpittalBase):
    """ Handles everything model related. """

    def create_version(self, version_type, upload_id, pkey,
                       pub_user, module_supplier_id):
        """ Creates a version with the upload and download IDs.

        Args:
            version_type (str): defines the type of version to upload.
            upload_id (int): the id returned from create_file_upload().
            pkey (int): UNKONW
            pub_usr (str): the public user used to name certain things.
            module_supplier_id (int): id of the module that supplies the
                python and SQL code for this file.
                See /oasis/django/oasis/app/scripts/Dict

        Returns:
            HttpResponse: server's response.
        """
        response = self.do_request(
            self.base_url +
            "/oasis/create" + self.types[version_type] + "/" +
            pub_user + "/" +
            str(module_supplier_id) + "/" +
            str(upload_id) + "/" +
            str(pkey) + "/"
        )
        return response

    def create_model_structures(self, module_supplier_id=1):
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
            # For dictionary types.
            if splitname[0] == 'dict':
                creation_response = self.create_dict(
                    type_name,
                    type_['upload_id'],
                    type_['download_id'],
                    self.pub_user,
                    module_supplier_id
                )
                logger.info(
                    'Create dict {dict_} response: '.format(dict_=type_name) +
                    str(creation_response.content)
                )
                type_['id'] = json.loads(creation_response.content)['id']

            # For version types.
            elif splitname[0] == 'version':
                creation_response = self.create_version(
                    type_name,
                    type_['upload_id'],
                    type_['download_id'],
                    "ModelKey", # What is this?!
                    module_supplier_id
                )
                logger.info(
                    'Create version {version} response: '
                    .format(version=type_name) +
                    str(creation_response.content)
                )

                type_['id'] = json.loads(
                    creation_response.content
                )['id']

        print('Finished creating model strutures.')

    # TODO: Finish creating this method.
    def get_model(self, model_name):
        """ Return a previously uploaded model from the database.

        Args:
            model_name -- The name that the model was uploaded with.
        """
        pass
