import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import swal from "sweetalert";

import UnauthorizedPage from "../components/unauthorizedPage";
import UploadRecords from "../components/uploadRecords"
import DataModelChoice from "../components/dataModelChoice"

function UploadPage({ token }) {
  const [expanded, setExpanded] = useState(false);

  const [svoFile, setSVOFile] = useState(null);
  const [txtFile, setTXTFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [availableDataTypes, setAvailableDataTypes] = useState([]);
  const [availableModelName, setAvailableModelName] = useState([]);
  const [dataType, setDataType] = useState(null);
  const [modelName, setModelName] = useState(null);

  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedSize, setUploadedSize] = useState(0);
  const [totalSize, setTotalSize] = useState(0);

  const svoFileInputRef = useRef(null);
  const txtFileInputRef = useRef(null);

  const [date, setDate] = useState('');
  const [description, setDescription] = useState('');
  const [trialID, setTrialID] = useState('');

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

  const handleSVOFileChange = (e) => {
    setSVOFile(e.target.files[0]);
  };

  const handleTXTFileChange = (e) => {
    setTXTFile(e.target.files[0]);
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

  const handleTrialIDChange = (event) => {
    setTrialID(event.target.value);
  }

  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  const resetForm = () => {
    setLoading(false);
    setDescription('');
    setTrialID('');
    setSVOFile(null);
    setTXTFile(null);
    setUploadProgress(0);
    setUploadedSize(0);
    setTotalSize(0);

    if (svoFileInputRef.current) {
      svoFileInputRef.current.value = '';
    }

    if (txtFileInputRef.current) {
      txtFileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (date === '') {
      swal({
        title: "Error",
        text: "Trial Date is required",
        icon: "error",
      });
      return
    }

    if (trialID === '') {
      swal({
        title: "Error",
        text: "Trial ID is required",
        icon: "error",
      });
      return
    }

    if (trialID.indexOf(' ') >= 0) {
      swal({
        title: "Error",
        text: "Trial ID cannot contain a space",
        icon: "error",
      });
      return
    }

    if (svoFile === null) {
      swal({
        title: "Error",
        text: "Please select a svo file to upload",
        icon: "error",
      });
      return
    }

    if (txtFile === null) {
      swal({
        title: "Error",
        text: "Please select a txt file (svo timestamp) to upload",
        icon: "error",
      });
      return
    }

    const formData = new FormData();
    formData.append('svoFile', svoFile);
    formData.append('txtFile', txtFile);
    formData.append('dataType', dataType);
    formData.append('modelName', modelName);
    formData.append('date', date);
    formData.append('description', description);
    formData.append('trialID', trialID);

    const headers = {
      Authorization: 'Bearer ' + token
    };

    setLoading(true); // Set loading to true to disable the button

    axios.post('/api/user/upload/gait', formData, {
      headers,
      onUploadProgress: (progressEvent) => {
        setUploadedSize(progressEvent.loaded);
        setTotalSize(progressEvent.total);
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percentCompleted);
      }
    })
    .then(response => {
      console.log(response.data); // Handle the response from the backend
      swal({
        title: "Success",
        text: "Submit Success!",
        icon: "success",
      });
  
    })
    .catch(error => {
      console.error(error);
      swal({
        title: "Error",
        text: "Submit failed",
        icon: "error",
      });

    })
    .finally(() => {
      resetForm(); // Reset form in both success and error cases
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
                  <label className="col-sm-1 control-label">Trial Date</label>
                  <div className="col-sm-10">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Trial Date"
                      value={date}
                      onChange={handleDateChange}
                      disabled={loading}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="col-sm-1 control-label">Unique Trial ID</label>
                  <div className="col-sm-10">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="YYYY-MM-DD-PATIENT_ID-TRIAL_ID (suggested. e.g., 2024-01-01-1-1)"
                      value={trialID}
                      onChange={handleTrialIDChange}
                      disabled={loading}
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
                      disabled={loading}
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
                    disabled={loading}
                  />
                )}
                <div className="form-group">
                  <label className="col-sm-1 control-label">SVO File</label>
                  <div className="col-sm-10">
                    <input type="file" className="form-control-file" accept=".svo" onChange={handleSVOFileChange} ref={svoFileInputRef} disabled={loading}/>
                  </div>
                </div>
                <div className="form-group">
                  <label className="col-sm-1 control-label">TXT File</label>
                  <div className="col-sm-10">
                    <input type="file" className="form-control-file" accept=".txt" onChange={handleTXTFileChange} ref={txtFileInputRef} disabled={loading}/>
                  </div>
                </div>
                <div className="form-group">
                  <div className="col-sm-offset-1 col-sm-10">
                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '300px' }}>
                      {loading 
                        ? `Uploading ${uploadProgress}% (${formatBytes(uploadedSize)} / ${formatBytes(totalSize)})` 
                        : 'Upload'}
                    </button>
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