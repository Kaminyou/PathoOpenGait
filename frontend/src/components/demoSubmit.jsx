import React from "react";
import UploadButton from "../components/uploadButton"
import { Checkbox, FormGroup, FormControlLabel } from '@mui/material';

function DemoSubmit({ token, checked, handleChange, onSubmit }) {
  return (
    <>
      <p>Select an example or Upload a 3D video recorded by a Stereolabs ZED camera or 3D trajectories</p>
      <UploadButton/>
      <FormGroup className="m-3">
      <FormControlLabel control={
        <Checkbox
          checked={checked}
          onChange={handleChange}
          inputProps={{ 'aria-label': 'controlled' }}
        />
      } label="use an example" />
      </FormGroup>
      <button type="button" className="btn btn-primary pantoneZOZl" onClick={onSubmit}>Submit</button>
    </>
  )
}

export default DemoSubmit