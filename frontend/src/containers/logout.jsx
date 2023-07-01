import { useHistory } from "react-router";
import axios from "axios";

function LogOut({ removeToken }) {
  const history = useHistory();

  const logMeOut = () => {
    axios({
      method: "POST",
      url:"/api/token/logout",
    })
    .then((response) => {
      removeToken()
      history.push({
          pathname:  "/",
      });
    }).catch((error) => {
      if (error.response) {
        console.log(error.response)
        console.log(error.response.status)
        console.log(error.response.headers)
        }
    }
    )
  }

  return (
    <div class="back" id="back">
    <div className="div-center center-text" id="div-logout-center">
      <div className="content center-text" id="div-content">
      <h3>Log out?</h3>
        <button type="button" className="btn btn-primary" onClick={logMeOut}>Logout</button>
        
          
          {/* <button type="button" class="btn btn-link">Signup</button>
          <button type="button" class="btn btn-link">Reset Password</button> */}

      </div>
    </div>
  </div>
  )
}

export default LogOut