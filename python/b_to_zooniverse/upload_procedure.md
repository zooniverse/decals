# Upload Procedure
*Owner: [Mike Walmsley](mike.walmsley@physics.ox.ac.uk)*

This doc explains how to add new previously unclassified DECALS galaxies to Galaxy Zoo on Panoptes

## Warning
Don't do a new upload right after the previous upload. 
For identification of previous subjects to work correctly, all active subjects should have at least one classification.
It's better to upload a batch when the previous batch is nearly finished, to ensure this condition is met.


## Assumptions
You should have installed the `decals` package, located in `root/python`, with the following command:

`pip install -e {repo root loc}/python`

## Setup
Ensure the `settings.joint_catalog_loc`, `settings.expert_catalog_loc` and `settings.expert_catalog_interpreted_loc` file paths are up to date

If you would like to re-check which subjects were already classified in DR2:
- Set `settings.new_previous_subjects` to True
- Ensure the `settings.previous_subjects_loc` path points to the DR2 subject export
- Ensure `settings.nsa_v1_0_0_catalog_loc` points to a download of the NSA catalog v1_0_0
Otherwise (most common):
- Set `settings.new_previous_subjects` to False

Note that placing the new exports in the default folders `galaxy-zoo-panoptes/reduction/data/raw/...` is also convenient for the reduction scripts. See the associated readme for the `galaxy-zoo-panoptes` repo for more info.

## Upload Steps
- Run `pytest` from the repo root. Verify that all tests pass.
- Request a workflow classification export
- Request a subject export
- Go to the pub while Panoptes gets the classifications (several hours)
- Download both
- Update `latest_export_date_str` value with current date
- Rename with date and place workflow classification export in path matching `latest_workflow_classification_export_loc`
- Rename with date and place subject export in path matching `latest_subject_extract_loc`
- Update `subjects_not_yet_added_name` with a descriptive name for the subject set. The current date will be appended automatically.
- Update `max_new_subjects` to the number of new galaxies to upload. This changes the slice on `subjects_not_yet_added`.
- Ensure the `Upload first n DR5-only galaxies NOT already uploaded` block in - `upload_decals.upload_decals_to_panoptes` is the only uncommented block
- Run `upload_decals.py`. If re-running on the same day with the same `subjects_not_yet_added_name`, you will need to delete the (potentially empty) previously created set from the [lab](https://www.zooniverse.org/lab/5733/subject-sets) first.

## Important Follow-up (Don't Skip This!)
- Update the `decals` repo wiki with a brief description of the subject set, following the previous pattern. 
- I


*Note: don't try to automate/optimize.*
*This should all be replaced with a simple API call update, incrementing a database*