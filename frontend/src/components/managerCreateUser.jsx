import React, { useState } from "react";
import axios from "axios";
import swal from "sweetalert";
import isEmpty from 'validator/lib/isEmpty'
import isEmail from 'validator/lib/isEmail';

export default function CreateUser({token}) {
  const [newAccount, setNewAccount] = useState("");
  const [newCategory, setNewCategory] = useState('general');
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const handleNewAccountChange = (e) => {
    setNewAccount(e.target.value)
  }

  const handleNewCategoryChange = (e) => {
    setNewCategory(e.target.value)
  }

  const handleNewEmailChange = (e) => {
    setNewEmail(e.target.value)
  }

  const handleNewPasswordChange = (e) => {
    setNewPassword(e.target.value)
  }

  const sendCreateUserRequest = () => {
    if (isEmpty(newAccount) || !isEmail(newEmail) || isEmpty(newCategory) || isEmpty(newPassword)) {
      swal({
        title: "Error",
        text: "Please provide vaild information",
        icon: "error",
      });
      return
    }
    const formData = new FormData();
    
    formData.append("account", newAccount);
    formData.append("category", newCategory);
    formData.append("email", newEmail);
    formData.append("password", newPassword)
    
    axios.post("/api/manage/createuser", formData, {
      headers: {Authorization: 'Bearer ' + token}
    })
    .then(res => {
      setNewAccount("");
      setNewCategory("");
      setNewEmail("");
      setNewPassword("");
      
      swal({
        title: "Success",
        text: "Create successfully!",
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
  }

  return (
    <div>
      <h4>Create User</h4>
      <div className="form-group">
        <label htmlFor="formWebURLInput">Account</label>
        <input type="text" className="form-control" id="formNewAccount" placeholder="account" value={newAccount} onChange={handleNewAccountChange}/>
      </div>

      <div className="form-group">
      <label htmlFor="formWebAccountInput">Category</label>
      <select disabled={true} className="form-control" id="formNewGroup" value={newCategory} onChange={handleNewCategoryChange}>
          <option value="general">General</option>
      </select>
      </div>

      <div className="form-group">
        <label htmlFor="formEmail">Email</label>
        <input type="text" className="form-control" id="fromNewEmail" placeholder="email" value={newEmail} onChange={handleNewEmailChange}/>
      </div>

      <div className="form-group">
        <label htmlFor="formWebAccountInput">Password</label>
        <input type="text" className="form-control" id="formNewPassword" placeholder="password" value={newPassword} onChange={handleNewPasswordChange}/>
      </div>
      <button type="button" className="btn btn-primary btn-block pantoneZOZl" onClick={sendCreateUserRequest}>Create</button>
      <br></br>
    </div>
  );
}