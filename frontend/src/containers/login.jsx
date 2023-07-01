import { useState } from 'react';
import { useHistory } from "react-router";
import axios from "axios";
import swal from "sweetalert";

function LoginPage({ setToken }) {
  const history = useHistory();
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");

  const handleAccountChange = (e) => {
    setAccount(e.target.value)
  }

  const handlePasswordChange = (e) => {
    setPassword(e.target.value)
  }

  const logMeIn = (e) => {
    axios(
      {
        method: "POST",
        url:"/api/token/login",
        data:{
          account: account,
          password: password,
        }
      }
    ).then((response) => {
      setToken(response.data.access_token)
      setAccount("")
      setPassword("")
      history.push({
        pathname: "/",
      });
    }).catch((error) => {
      if (error.response) {
        swal({
          title: "Error",
          text: "Invalid User",
          icon: "error",
        });
      }
    })
    setAccount("")
    setPassword("")
    e.preventDefault()
  }

  return (
  <div class="back" id="back">
    <div class="div-center" id="div-center">
      <div class="content" id="div-content">
      <h3>Login</h3>
        <hr id="normal-hr"/>
        <form>
          <div class="form-group">
            <label for="account">Account</label>
            <input type="email" class="form-control" id="inputAccount" placeholder="Enter your account" onChange={handleAccountChange} value={account}/>
          </div>
          <div class="form-group">
            <label for="exampleInputPassword1">Password</label>
            <input type="password" className="form-control" id="inputPassword" name="password" placeholder="Enter password" onChange={handlePasswordChange} value={password}/>
          </div>
          <hr id="normal-hr"/>
          <button type="submit" class="btn btn-primary" onClick={logMeIn}>Login</button>
          
          {/* <button type="button" class="btn btn-link">Signup</button>
          <button type="button" class="btn btn-link">Reset Password</button> */}

        </form>
      </div>
    </div>
  </div>
  )
}

export default LoginPage