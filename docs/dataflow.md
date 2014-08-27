# Oasis Django API Data Flow

## Table of Contents
 * Overview
 * Typical Run
 * Variable Definitions


## Overview
### Upload Model
 1. Create File Upload and Download
 2. Actually Upload Files
 3. Create Django Objects
 4. Load Django Objects

## Detailed Run
A walk through the dataflow of loading a model, exposures, and creating a benchmark run.
### Upload Model
 1. The first API call that should be made is to create the file upload and download.
  * __API Call__: /oasis/createFileUpload/{pname}/{pFilename}/{pModuleSupplierId}/
  * __Example__: /oasis/createFileUpload/root/20140826_145254_dict_vuln.csv/27/
  * __Returns__: pUploadId

 The file download works exactly the same except the call is createFileDownload and return a download_id.
  
 2. The next step is to actually upload the files.
  * __API Call__: /oasis/doTaskUploadFileHelper
  * __Example__: /oasis/doTaskUploadFileHelper
  * __Returns__: None
    
 When using this API call a files must be passed into the POST files parameter.
 In python this is in the form of a dictionary when passed to the requests library. 
 Note: 'my_filename.csv' is the name of the file that will be used on the server. 
 Typically, this name is timestamped as to not overwrite a previously uploaded file.
 ```python
  requests.post(url, files={"my_filename.csv": file_object})
 ```

 3. Now we can create the Django objects for the model. 
 Here we use the upload and download IDs that we gto from the last API calls. 
 One type of object we need to create is the dictionary.
  * __API Call__: /oasis/create<dict type>Dict/{pname}/{pModuleSupplierId}/{pFileUploadId}/{pFileDownloadId}/
  * __Example__: /oasis/createEventDict/root/1/42/108/
  * __Returns__: <dictType>id  --  Example: pEventDictId
 
 The other type that we need to upload is the version.
  * __API_Call__: /oasis/create<version type>Version/{pName}/{pModuleSupplierId}/{pFileUploadId}/{pKey}/
  * __Example__: /oasis/createVulnVersion/ModelKey/27/83/105/
  * __Returns__: <version type>id  --  Example: pVulnVersionId
  
 This must be done for all of the Django object dictionaries 
 and versions that need to be uploaded.

 4. Finaly, to finish up we need to load the model. 
 Here we use the IDs we got from the last API calls.
  * __API Call__: /oasis/doTask<dict or version type>/{sysConfigId}/{id}/
  * __Example__: /oasis/doTaskVulnVersion/1/4/
  * __Returns__: pJobId
  
 Later this job ID is now will be used for create respective instances of the model.



## Variable Definitions
This the documentation on some of the popular variables used in the API. 
A quick reference to refresh your memory if you don't know what exactly it is.

 * __pFilename__: Name of the file that will be uploaded.
 * __pModuleSupplierId__: ID of the module that supplies the python and SQL code for this file. 
 See oasisdb table app_modulesupplier and django/oasis/app/scripts/Dict
 * __pAreaPerilDictId__:  ID returned by the respective /oasis/doTaskCreateAreaPerilDict
 * __pConfigId__:  Defines where and how to load the data. Database IP, etc.
 * __pname__: UNKNOWN