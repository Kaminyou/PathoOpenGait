import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";

import UnauthorizedPage from "../components/unauthorizedPage";

function ProfilePage({ token }) {

  const [loading, setLoading] = useState(false);

  const [name, setName] = useState('');
  const [birthday, setBirthday] = useState('');

  const [diagnose, setDiagnose] = useState('');
  const [stage, setStage] = useState('');
  const [dominantSide, setDominantSide] = useState('');
  const [lded, setLDED] = useState('');
  const [description, setDescription] = useState('');

  const [showDialog, setShowDialog] = useState(false);
  const [password, setPassword] = useState('');

  const handleClose = () => {
    setShowDialog(false);
    setPassword('');
  };

  const fetchDefault = async () => {
    await axios.get("/api/user/profile/personal", {
      headers: {Authorization: 'Bearer ' + token}
    })
    .then((res) => {
      //console.log(res.data.profile)
      setName(res.data.profile['name'])
      setBirthday(res.data.profile['birthday'])
      setDiagnose(res.data.profile['diagnose'])
      setStage(res.data.profile['stage'])
      setDominantSide(res.data.profile['dominantSide'])
      setLDED(res.data.profile['lded'])
      setDescription(res.data.profile['description'])
    })
    .catch((error) => {
      console.error(error);
    });
  }
  useEffect(() => {
    fetchDefault();
  }, [])

  const handleChangePassword = () => {
    // Handle password change logic
    if (password === '') {
      swal({
        title: "Error",
        text: "Please provide password",
        icon: "error",
      });
      return
    }
    console.log('Password changed:', password);

    const formData = new FormData();
    formData.append("password", password)
    axios.post("/api/user/changepwd", formData, {
      headers: {Authorization: 'Bearer ' + token}
    })
    .then(res => {
      swal({
        title: "Success",
        text: "Change successfully!",
        icon: "success",
      });
    })
    .catch(
      err => {
        console.warn(err);
        swal({
          title: "Error",
          text: "Server error",
          icon: "error",
        });
      }
    );
    handleClose();
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };
  
  const handleNameChange = (event) => {
    setName(event.target.value);
  };
  
  const handleBirthdayChange = (event) => {
    setBirthday(event.target.value);
  };
  
  const handleDiagnoseChange = (event) => {
    setDiagnose(event.target.value);
  };
  
  const handleStageChange = (event) => {
    setStage(event.target.value);
  };
  
  const handleDominantSideChange = (event) => {
    setDominantSide(event.target.value);
  };
  
  const handleLDEDChange = (event) => {
    setLDED(event.target.value);
  };
  
  const handleDescriptionChange = (event) => {
    setDescription(event.target.value);
  };


  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', name);
    formData.append('birthday', birthday);
    formData.append('diagnose', diagnose);
    formData.append('stage', stage);
    formData.append('dominantSide', dominantSide);
    formData.append('lded', lded);
    formData.append('description', description);

    const headers = {
      Authorization: 'Bearer ' + token
    };

    setLoading(true); // Set loading to true to disable the button

    axios.post('/api/user/profile/update', formData, { headers })
      .then(response => {
        console.log(response.data); // Handle the response from the backend
        setLoading(false); // Set loading back to false after successful upload
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
          <div className="col-xs-12 col-md-10">
            <div className="about-text">
              <form onSubmit={handleSubmit} className="form-horizontal">
              <div className="form-group">

                <label className="col-sm-2 control-label">Password</label>
                <div className="col-sm-10">
                <button className="btn btn-primary" onClick={() => setShowDialog(true)}>
                  Change Password
                </button>
                </div>
                
                <hr id='normal-hr'/>

                <label className="col-sm-2 control-label">Name</label>
                <div className="col-sm-10">
                    <input
                    type="text"
                    className="form-control"
                    placeholder="Name"
                    value={name}
                    onChange={handleNameChange}
                    />
                </div>
                </div>

                <div className="form-group">
                <label className="col-sm-2 control-label">Birthday</label>
                <div className="col-sm-10">
                    <input
                    type="text"
                    className="form-control"
                    placeholder="yyyy-mm-dd"
                    value={birthday}
                    onChange={handleBirthdayChange}
                    />
                </div>
                </div>

                <div className="form-group">
                <label className="col-sm-2 control-label">Diagnose</label>
                <div className="col-sm-10">
                    <input
                    type="text"
                    className="form-control"
                    placeholder="Diagnose"
                    value={diagnose}
                    onChange={handleDiagnoseChange}
                    />
                </div>
                </div>

                <div className="form-group">
                <label className="col-sm-2 control-label">Stage</label>
                <div className="col-sm-10">
                    <input
                    type="text"
                    className="form-control"
                    placeholder="Stage"
                    value={stage}
                    onChange={handleStageChange}
                    />
                </div>
                </div>

                <div className="form-group">
                <label className="col-sm-2 control-label">Dominant Side</label>
                <div className="col-sm-10">
                    <input
                    type="text"
                    className="form-control"
                    placeholder="Dominant Side"
                    value={dominantSide}
                    onChange={handleDominantSideChange}
                    />
                </div>
                </div>

                <div className="form-group">
                <label className="col-sm-2 control-label">LDED</label>
                <div className="col-sm-10">
                    <input
                    type="text"
                    className="form-control"
                    placeholder="LDED"
                    value={lded}
                    onChange={handleLDEDChange}
                    />
                </div>
                </div>

                <div className="form-group">
                <label className="col-sm-2 control-label">Description</label>
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
                  <div className="col-sm-offset-2 col-sm-10">
                    <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Uploading...' : 'Upload'}</button>
                  </div>
                </div>

              </form>
              

            {showDialog && (
              <div className="modal show" tabIndex="-1" role="dialog" style={{ display: 'block' }}>
                <div className="modal-dialog" role="document">
                  <div className="modal-content">
                    <div className="modal-header">
                      <button type="button" className="close" onClick={handleClose}>
                        <span aria-hidden="true">&times;</span>
                      </button>
                      <h4 className="modal-title">Change Password</h4>
                    </div>
                    <div className="modal-body">
                      <div className="form-group">
                        <label>New Password</label>
                        <input
                          type="password"
                          className="form-control"
                          placeholder="Enter new password"
                          value={password}
                          onChange={handlePasswordChange}
                        />
                      </div>
                    </div>
                    <div className="modal-footer">
                      <button type="button" className="btn btn-default" onClick={handleClose}>
                        Cancel
                      </button>
                      <button type="button" className="btn btn-primary" onClick={handleChangePassword}>
                        Save Changes
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage