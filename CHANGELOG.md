# Changelog
## v0.2.2
### New features
- To protect patient's privacy, the default video change to a black background one with full keypoints shown. The setting can be changed by modify the `get_video` api in `backend/routers/user.py`

## v0.2.1
### Improvement
- Add an automatical timestamp txt fixing logic

## v0.2.0
### Improvement
- Enable raw svo and txt uploading
- Add algorithms to remove any non-targeted person
- Make Rscript execution independent between jobs (not computing in the source code folder)
- Make 3D estimation execution independent between jobs (not computing in the source code folder)

### New features
- Examine each field in frontend during uploading
- Block any modification in each field during uploading
- Enable providing a unique trial ID
- Show uploading progress

## v0.1.1
### New features
- Provide instruction for 3D trajetories conversion
- Provide solely 2D vedio inference mode
- Add a verifier for detected keypoints

## v0.1.0
### Initial version
- Support the algorithms mentioned in the publication
