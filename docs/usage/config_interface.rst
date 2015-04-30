Config Interface Usage
======================

Introduction
------------
Config interface makes use of toml. Toml is a minimal configuration file format
to read the data that are in key-value pairs. 

To learn more about the toml format, click here_.

Spittalpond Config Specification
--------------------------------
example.toml is separated into different logical sections of Oasis workflow.
Essentially, each section conveniently runs many underlying Oasis webservices.
Each section specified will be run based on key value pairs defined in it.
The sections will be run in sequential order.Some of sections are important and
must be defined to be able to run the toml file successfully.

Here is a sample example.toml_ file:

Following is a brief description of each section in example.toml:

**Meta**

Meta is an optional section. Essential key-value pairs in Meta are:

- url: which holds the Oasis url.
- log_file: which holds the name of the log file.
- log_level: allows the user to specify levels of logging.
- system_config: contains the value of the Oasis back-end database to be used for execution.

**Login**

Login section is an optional section. Key-value pairs in Login are:
user: contains the username to access Oasis.
password: password to access Oasis.

directory_path: holds the path of the directory containing input files to be
uploaded on Oasis.

**Model**

Model section defines essential details of the model to be created. Key-value pairs
in Model section are:

- name: defines the name of the Model to be created on Oasis.
- do_timestamps: defines timestamps for the upload files. This sub-section, allows
  the user to either turn it on to be used or turn it off.
- key: defines the license key for the Model.

There are seven main model sections to load the models into Oasis:

- model.dict.areaperil
- model.dict.event
- model.dict.vuln
- model.dict.hazardintensitybin
- model.version.hazfp
- model.version.vuln
- model.dict.damagebin

All the above sections have two key-value pairs:

- filename: defines the name of the input file to be uploaded.
- module_supplier_id: defines module supplier id.

**Exposure**

Exposure section defines details of the exposure instance to be created.
Key-value pairs in exposure section are:

- name: defines the name of the exposure instance to be created on Oasis.
- do_timestamps: defines timestamps for the upload files. This sub-section, 
  allows the user to either turn it on to be used or turn it off.

There are three main sections under exposure:

- exposure.dict.exposure
- exposure.version.exposure
- exposure.version.correlation

All the above sections have two key-value pairs:

- filename: defines the name of the input file to be uploaded.
- module_supplier_id: defines module supplier id.

**Benchmark**

Benchmark section runs the Benchmark in Oasis after all the input files have
been uploaded. There are four key-value pairs in this section:

- name: defines the name of the Benchmark instance to be created.
- chunk_size: allows user to specify chunk size parameter.
- min_chunk: allows user to specify minimum chunk.
- max_chunk: allows user to specify maximum chunks.

**GUL**

GUL section runs the GUL tasks in Oasis once the Benchmark section is 
successfully executed. There is only one key-value pair in this section:

- name: defines the name of the GUL instance to be created.

**Pubgul**

PubGul section runs once GUL tasks have been successfully executed.
This section essentially publishes the GUL results. Key-value pairs in this
section:

- name: defines the name of the pubgul instance to be created.
- filename: defines the name of the file in which the GUL results will be published.
- module_supplier_id: defines module supplier id.

**Instructions to run example.toml**

example.toml can be run by the following commands:

.. code:: sh

	$ cd path/to/spittalpond/
	$ python ./spittalpond/config_interface.py ../examples/example.toml

config_interface can be executed interactively by creating a spittalpond instance.
Following is an example of interactive execution:

.. code:: sh

	$ python -i .\config_interface.py .\example.toml
	You are logged into Mid-tier
	Finished creating model strutures.
	You are logged into Mid-tier
	Finished creating exposure structures.
	Finished benchmark creation.
	You are logged into Mid-tier
	Created GUL data
	You are logged into Mid-tier
	>>> s = spittalpond_instance
	>>> s.run.data_dict
	{'version_random': {'job_id': 63, 'taskId': 2}, 'kernel_pubgul': {'download_id_2': u'7', 'download_id': 182, 'job_id': 7
	0, 'taskId': u'7'}, 'kernel_cdf': {'job_id': 65, 'taskId': u'7'}, 'kernel_gul': {'job_id': 67, 'taskId': u'7'}, 'kernel_
	cdfsamples': {'job_id': 66, 'taskId': u'7'}, 'instance_random': {'job_id': 64, 'taskId': u'8'}}
	>>> s.run.create_gul("example_gul", 7, 10)
	<Response [200]>

.. note::	
	
	All sections in example.toml are mandatory for initial run. But once
	spittalpond data_dict is populated, each section can be executed
	independently. 

.. _here: https://github.com/toml-lang/toml/blob/master/README.md 
.. _example.toml: https://github.com/beckettsimmons/spittalpond/blob/develop/examples/example.toml