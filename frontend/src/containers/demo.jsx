import React, { useState, useEffect } from "react";
import UploadButton from "../components/uploadButton"
import { Checkbox, FormGroup, FormControlLabel } from '@mui/material';

function DemoPage({ token }) {
  const [checked, setChecked] = useState(false);

  const handleChange = () => {
    setChecked(!checked)
  }

  const onSubmit = (e) => {
    e.preventDefault();
    alert('submit!')
  }

  return (
    <div id="about">
      <div className="container">
        <div className="row">
          <div className="col-xs-12 col-md-8">
            <div className="about-text">
              <h2>Demo</h2>
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
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DemoPage