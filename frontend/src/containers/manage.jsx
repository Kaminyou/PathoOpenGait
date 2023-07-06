import React, { useState, useEffect } from "react";
import axios from "axios";
import swal from "sweetalert";
import UnauthorizedPage from "../components/unauthorizedPage";
import UserList from '../components/managerUserList'
import CreateUser from '../components/managerCreateUser'


function ManagePage({ token }) {

  const [userList, setUserList] = useState([]);
  const [isManager, setIsManager] = useState(false);
  const MINUTE_MS = 2000; // 2 sec


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
    const interval = setInterval(() => {
        getUserList();
      }, MINUTE_MS);
    return () => clearInterval(interval);
  }, [])
  

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
          <div className="col-xs-4 col-md-4">
          <CreateUser token={token}/>
          </div>
          <div className="col-xs-8 col-md-8">
          <UserList userlist={userList} token={token}/>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ManagePage