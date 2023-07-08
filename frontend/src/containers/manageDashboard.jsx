import React, { useState, useEffect } from "react";
import axios from "axios";
import UnauthorizedPage from "../components/unauthorizedPage";
import SimpleDashboard from '../components/simpleDashboard'
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import ProfilePanel from '../components/profilePanel'


function ManageDashBoardPage({ token }) {

  const [name, setName] = useState('');
  const [gender, setGender] = useState('');
  const [birthday, setBirthday] = useState('');

  const [diagnose, setDiagnose] = useState('');
  const [stage, setStage] = useState('');
  const [dominantSide, setDominantSide] = useState('');
  const [lded, setLDED] = useState('');
  const [description, setDescription] = useState('');
  const [results, setResults] = useState([]);

  const [userList, setUserList] = useState([]);
  const [isManager, setIsManager] = useState(false);

  const [selectedUser, setSelectedUser] = useState('');

  const handleSelectedUserChange = (event) => {
    const newSelectedUser = event.target.value;
    setSelectedUser(newSelectedUser);
    fetchTargetUserProfile(newSelectedUser);
    fetchTargetUserResults(newSelectedUser);
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

  const fetchDefault = async () => {
    try {
      const response = await axios.get("/api/user/profile/personal", {
        headers: { Authorization: 'Bearer ' + token }
      });
      const { name, gender, birthday, diagnose, stage, dominantSide, lded, description } = response.data.profile;
      setName(name);
      setGender(gender);
      setBirthday(birthday);
      setDiagnose(diagnose);
      setStage(stage);
      setDominantSide(dominantSide);
      setLDED(lded);
      setDescription(description);
    } catch (error) {
      console.error(error);
    }
  };
  
  useEffect(() => {
    fetchDefault();
  }, []);

  const fetchResults = async () => {
    await axios.get("/api/user/request/results", {
      headers: {Authorization: 'Bearer ' + token}
    })
    .then((res) => {
      setResults(res.data.results)
    })
    .catch((error) => {
      console.error(error);
    });
  }

  useEffect(() => {
    fetchResults();
  }, [])

  const fetchTargetUserProfile= async (newSelectedUser) => {
    const formData = new FormData();
    formData.append('account', newSelectedUser);
    try {
      const response = await axios.post("/api/manage/profile/personal", formData, {
        headers: { Authorization: 'Bearer ' + token }
      });
      const { name, gender, birthday, diagnose, stage, dominantSide, lded, description } = response.data.profile;
      setName(name);
      setGender(gender);
      setBirthday(birthday);
      setDiagnose(diagnose);
      setStage(stage);
      setDominantSide(dominantSide);
      setLDED(lded);
      setDescription(description);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchTargetUserResults = async (newSelectedUser) => {
    const formData = new FormData();
    formData.append('account', newSelectedUser);
    await axios.post("/api/manage/request/results", formData, {
      headers: {Authorization: 'Bearer ' + token}
    })
    .then((res) => {
      setResults(res.data.results)
    })
    .catch((error) => {
      console.error(error);
    });
  }


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
    <div className="padding-block">
    <div className="container">
      <div className="row">
        <div className="col-md-3">
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
          <ProfilePanel
            name={name}
            gender={gender}
            birthday={birthday}
            diagnose={diagnose}
            stage={stage}
            dominantSide={dominantSide}
            lded={lded}
            description={description}
          />
        </div>
        <div className="col-md-9">
          <SimpleDashboard
            results={results}
            token={token}
          />
        </div>
      </div>
    </div>
  </div>
  )
}

export default ManageDashBoardPage