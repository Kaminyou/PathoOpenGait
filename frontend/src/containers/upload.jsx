import React, { useState } from "react";
import axios from "axios";

import UnauthorizedPage from "../components/unauthorizedPage";

function UploadPage({ token }) {

  const [csvFile, setCSVFile] = useState(null);
  const [mp4File, setMP4File] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dataType, setDataType] = useState('gait');
  const [modelName, setModelName] = useState('gait_basic');

  const handleCSVFileChange = (e) => {
    setCSVFile(e.target.files[0]);
  };

  const handleMP4FileChange = (e) => {
    setMP4File(e.target.files[0]);
  };

  const handleDataTypeChange = (e) => {
    setDataType(e.target.value);
  };

  const handleModelNameChange = (e) => {
    setModelName(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('csvFile', csvFile);
    formData.append('mp4File', mp4File);
    formData.append('dataType', dataType);
    formData.append('modelName', modelName);

    const headers = {
      Authorization: 'Bearer ' + token
    };

    setLoading(true); // Set loading to true to disable the button

    axios.post('/api/user/upload/gait', formData, { headers })
      .then(response => {
        console.log(response.data); // Handle the response from the backend
        setLoading(false); // Set loading back to false after successful upload
        alert('Upload successful');
      })
      .catch(error => {
        console.error(error);
        setLoading(false); // Set loading back to false after upload failure
        alert('Upload failed');
      });
  };

  if (!token) {
    // Render unauthorized page or redirect to unauthorized route
    return (
      <UnauthorizedPage/>
    )
  }

  return (
    <div className='padding-block'>
      <div className="container">
      <div className="row">
          <div className="col-xs-12 col-md-10">
            <div className="about-text">
              <form onSubmit={handleSubmit} className="form-horizontal">
                <div className="form-group">
                  <label className="col-sm-2 control-label">Data Type</label>
                  <div className="col-sm-10">
                    <input type="text" className="form-control" placeholder="Datatype" value={dataType} onChange={handleDataTypeChange} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="col-sm-2 control-label">Model Name</label>
                  <div className="col-sm-10">
                    <input type="text" className="form-control" placeholder="Model Name" value={modelName} onChange={handleModelNameChange} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="col-sm-2 control-label">CSV File</label>
                  <div className="col-sm-10">
                    <input type="file" className="form-control-file" accept=".csv" onChange={handleCSVFileChange} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="col-sm-2 control-label">MP4 File</label>
                  <div className="col-sm-10">
                    <input type="file" className="form-control-file" accept=".mp4" onChange={handleMP4FileChange} />
                  </div>
                </div>
                <div className="form-group">
                  <div className="col-sm-offset-2 col-sm-10">
                    <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Uploading...' : 'Upload'}</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadPage