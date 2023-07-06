import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";

import UnauthorizedPage from "../components/unauthorizedPage";
import UploadRecords from "../components/uploadRecords"
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';

function ManageUploadPage({ token }) {
  const [expanded, setExpanded] = useState(false);

  const [csvFile, setCSVFile] = useState(null);
  const [mp4File, setMP4File] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dataType, setDataType] = useState('gait');
  const [modelName, setModelName] = useState('gait_basic');

  const [date, setDate] = useState('');
  const [description, setDescription] = useState('');

  const [userList, setUserList] = useState([]);
  const [isManager, setIsManager] = useState(false);

  const [selectedUser, setSelectedUser] = useState('');

  const handleSelectedUserChange = (event) => {
    const newSelectedUser = event.target.value;
    setSelectedUser(newSelectedUser);
  };

  const getUserList = async () => {

    await axios.get("/api/manage/listuser", {
      headers: {Authorization: 'Bearer ' + token}
    })
    .then((res) => {
      setUserList(res.data.currentUsers);
      setIsManager(true);
    })
    .catch((error) => {
      console.error(error);
      setIsManager(false);
    });
  }

  useEffect(() => {
    getUserList();
  }, []);


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

    formData.append('account', selectedUser); // special

    const headers = {
      Authorization: 'Bearer ' + token
    };

    setLoading(true); // Set loading to true to disable the button

    axios.post('/api/manage/upload/gait', formData, { headers })
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

  if (!isManager) {
    // Render unauthorized page or redirect to unauthorized route
    return (
      <p>You are not manager</p>
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
                  <label className="col-sm-1 control-label">User</label>
                  <div className="col-sm-10">
                  <FormControl variant="standard" sx={{ m: 1, minWidth: 120 }}>
                    <InputLabel id="demo-simple-select-standard-label">Select user</InputLabel>
                    <Select
                    labelId="demo-simple-select-standard-label"
                    id="demo-simple-select-standard"
                    value={selectedUser}
                    onChange={handleSelectedUserChange}
                    label="Gait-parameter"
                    >
                    <MenuItem value="">
                        <em>None</em>
                    </MenuItem>
                    {userList.map((user, index) => (
                        <MenuItem value={user.subordinate}>{user.subordinate}</MenuItem>

                    ))}
                    </Select>
                  </FormControl>
                  </div>
                  </div>
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
                  <>
                    <div className="form-group">
                      <label className="col-sm-1 control-label">Data Type</label>
                      <div className="col-sm-10">
                        <input disabled={true} type="text" className="form-control" placeholder="Datatype" value={dataType} onChange={handleDataTypeChange} />
                      </div>
                    </div>
                    <div className="form-group">
                      <label className="col-sm-1 control-label">Model Name</label>
                      <div className="col-sm-10">
                        <input disabled={true} type="text" className="form-control" placeholder="Model Name" value={modelName} onChange={handleModelNameChange} />
                      </div>
                    </div>
                  </>
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
          </div>
        </div>
      </div>
    </div>
  );
}

export default ManageUploadPage