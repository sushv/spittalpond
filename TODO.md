Todo List (in priority order):
 - [ ] Update the README.md with a simple summary and setup.
 - [ ] Deprecate/remove old methods in preference to the config interface.
 - [ ] Handle issues for when the Django API returns JSON with success = false.
 - [ ] Get rid of all the hardcoded values in spittalrun. This includes config_ID.
 - [ ] Start handling errors if the Django API does not return JSON. (server side error)
 - [ ] Give the option to pipe log messages into the console.
 - [ ] Complete the get_model() method in SpittalModel.
 - [ ] Possibly create logger_messages.py to consolidate all messages.
 - [ ] Rename 'structure' with the correcty terminology of 'Django model object'.
 - [ ] Better documentation of parameters. Maybe even have a consolidated list somehwere.
       Better yet, have that list update all of the arguments in our code.
 - [ ] Rather than trying to explain too much of the code in external documents
       throw in a few doctests to show example usage.
 - [ ] We really need to create a decorator to strify those int arguments...
