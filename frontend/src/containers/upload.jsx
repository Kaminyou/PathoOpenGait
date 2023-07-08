import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";

import UnauthorizedPage from "../components/unauthorizedPage";
import UploadRecords from "../components/uploadRecords"
import DataModelChoice from "../components/dataModelChoice"

function UploadPage({ token }) {
  const [expanded, setExpanded] = useState(false);

  const [csvFile, setCSVFile] = useState(null);
  const [mp4File, setMP4File] = useState(null);
  const [loading, setLoading] = useState(false);
  const [availableDataTypes, setAvailableDataTypes] = useState([]);
  const [availableModelName, setAvailableModelName] = useState([]);
  const [dataType, setDataType] = useState(null);
  const [modelName, setModelName] = useState(null);

  const [date, setDate] = useState('');
  const [description, setDescription] = useState('');

  const fetchModelAndData = async () => {
    try {
      const response = await axios.get("/api/info/list/datatypes", {
        headers: { Authorization: 'Bearer ' + token }
      });
      setAvailableDataTypes(response.data.datatypes);
      setDataType(response.data.datatypes[0])
      let dataTypeTemp = response.data.datatypes[0]
      try {
        const response = await axios.get("/api/info/list/modelnames", {
          params: { datatype: dataTypeTemp }, headers: { Authorization: 'Bearer ' + token }
        });
        setAvailableModelName(response.data.modelnames)
        setModelName(response.data.modelnames[0])
      } catch (error) {
        console.error(error);
      }
    } catch (error) {
      console.error(error);
    }
  }

  const fetchDataTypes = async () => {
    try {
      const response = await axios.get("/api/info/list/datatypes", {
        headers: { Authorization: 'Bearer ' + token }
      });
      setAvailableDataTypes(response.data.datatypes);
      setDataType(response.data.datatypes[0])
    } catch (error) {
      console.error(error);
    }
  };

  const fetchModelNames = async () => {
    try {
      const response = await axios.get("/api/info/list/modelnames", {
        params: { datatype: dataType }, headers: { Authorization: 'Bearer ' + token }
      });
      setAvailableModelName(response.data.modelnames)
      setModelName(response.data.modelnames[0])
    } catch (error) {
      console.error(error);
    }
  };
  
  useEffect(() => {
    fetchModelAndData()
  }, []);

  useEffect(() => {
    fetchModelNames();
  }, [dataType]);

  useEffect(() => {
    const today = new Date();
    const formattedDate = today.toISOString().substr(0, 10);
    setDate(formattedDate);
  }, []);

  const handleExpand = () => {
    setExpanded(!expanded);
  };

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

  const handleDateChange = (event) => {
    setDate(event.target.value);
  };

  const handleDescriptionChange = (event) => {
    setDescription(event.target.value);
  };


  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('csvFile', csvFile);
    formData.append('mp4File', mp4File);
    formData.append('dataType', dataType);
    formData.append('modelName', modelName);
    formData.append('date', date);
    formData.append('description', description);

    const headers = {
      Authorization: 'Bearer ' + token
    };

    setLoading(true); // Set loading to true to disable the button

    axios.post('/api/user/upload/gait', formData, { headers })
      .then(response => {
        console.log(response.data); // Handle the response from the backend
        setLoading(false); // Set loading back to false after successful upload
        setDescription('')
        setCSVFile(null)
        setMP4File(null)
        swal({
          title: "Success",
          text: "Submit Success!",
          icon: "success",
        });
    
      })
      .catch(error => {
        console.error(error);
        setLoading(false); // Set loading back to false after upload failure
        swal({
          title: "Error",
          text: "Submit failed",
          icon: "error",
        });
  
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
          <div className="col-xs-12 col-md-12">
            <div className="about-text">
              <form onSubmit={handleSubmit} className="form-horizontal">
                <div className="form-group">
                  <label className="col-sm-1 control-label">Date</label>
                  <div className="col-sm-10">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Date"
                      value={date}
                      onChange={handleDateChange}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="col-sm-1 control-label">Description</label>
                  <div className="col-sm-10">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Description"
                      value={description}
                      onChange={handleDescriptionChange}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <div className="col-sm-offset-1 col-sm-10">
                    <button type="button" className="btn btn-secondary" onClick={handleExpand}>
                      {expanded ? 'Hide details' : 'Show details'}
                    </button>
                  </div>
                </div>
                {expanded && (
                  <DataModelChoice
                    dataType={dataType}
                    handleDataTypeChange={handleDataTypeChange}
                    availableDataTypes={availableDataTypes}
                    modelName={modelName}
                    handleModelNameChange={handleModelNameChange}
                    availableModelName={availableModelName}
                  />
                )}
                <div className="form-group">
                  <label className="col-sm-1 control-label">CSV File</label>
                  <div className="col-sm-10">
                    <input type="file" className="form-control-file" accept=".csv" onChange={handleCSVFileChange} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="col-sm-1 control-label">MP4 File</label>
                  <div className="col-sm-10">
                    <input type="file" className="form-control-file" accept=".mp4" onChange={handleMP4FileChange} />
                  </div>
                </div>
                <div className="form-group">
                  <div className="col-sm-offset-1 col-sm-10">
                    <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Uploading...' : 'Upload'}</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
          <div className="col-xs-12 col-md-12">
          <h4>Upload records</h4>
            <UploadRecords token={token}/>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadPage