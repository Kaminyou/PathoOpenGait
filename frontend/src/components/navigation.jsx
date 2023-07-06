import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { HashLink } from 'react-router-hash-link';
import axios from "axios";

function Navigation({ token }) {
  const [userCategory, setUserCategory] = useState('guest');

  const getUserCategory = () => {
    if (token || token!=="" || token!== undefined) {
      axios.get("/api/user/category", {
        headers: {Authorization: 'Bearer ' + token}
      })
      .then((res) => {
        setUserCategory(res.data.category);
        console.log(res.data.category)
      })
      .catch((error) => {
        console.error(error);
      });
    }
    else {
      setUserCategory('guest');
    }
  }

  useEffect(() => {
    getUserCategory();
  }, [token]);

  return (
    <nav id="menu" className="navbar navbar-default navbar-fixed-top">
      <div className="container">
        <div className="navbar-header">
          <button
            type="button"
            className="navbar-toggle collapsed"
            data-toggle="collapse"
            data-target="#bs-example-navbar-collapse-1"
          >
            {" "}
            <span className="sr-only">Toggle navigation</span>{" "}
            <span className="icon-bar"></span>{" "}
            <span className="icon-bar"></span>{" "}
            <span className="icon-bar"></span>{" "}
          </button>
          <HashLink className="navbar-brand page-scroll" smooth to="/#header">PathoOpenGait</HashLink>
          {/* <a className="navbar-brand page-scroll" href="#page-top">
            PathoOpenGait
          </a>{" "} */}
        </div>

        <div
          className="collapse navbar-collapse"
          id="bs-example-navbar-collapse-1"
        >
          {!token && token!=="" &&token!== undefined ? (
            <ul className="nav navbar-nav navbar-right">
            <li className="nav-item">
              <Link to={"/demo"}>Demo</Link>
            </li>
            <li className="nav-item">
              <Link to={"/login"}>Login</Link>
            </li>
            <li className="nav-item">
              <HashLink smooth to="/#contact" className="page-scroll">
                Contact
              </HashLink>
            </li>
            </ul>
          ):(
              {
                'guest': (
                  <ul className="nav navbar-nav navbar-right">
                  <li className="nav-item">
                    <Link to={"/demo"}>Demo</Link>
                  </li>
                  <li className="nav-item">
                    <Link to={"/logout"}>Logout</Link>
                  </li>
                  <li className="nav-item">
                    <HashLink smooth to="/#contact" className="page-scroll">
                      Contact
                    </HashLink>
                  </li>
                  </ul>
                ),
                'admin': (
                  <ul className="nav navbar-nav navbar-right">
                  <li className="nav-item">
                    <Link to={"/demo"}>Admin</Link>
                  </li>
                  <li className="nav-item">
                    <Link to={"/logout"}>Logout</Link>
                  </li>
                  <li className="nav-item">
                    <HashLink smooth to="/#contact" className="page-scroll">
                      Contact
                    </HashLink>
                  </li>
                  </ul>
                ),
                'manager': (
                  <ul className="nav navbar-nav navbar-right">
                  <li className="nav-item">
                    <Link to={"/demo"}>Manage</Link>
                  </li>
                  <li className="nav-item">
                    <Link to={"/logout"}>Logout</Link>
                  </li>
                  <li className="nav-item">
                    <HashLink smooth to="/#contact" className="page-scroll">
                      Contact
                    </HashLink>
                  </li>
                  </ul>
                ),
                'general': (
                  <ul className="nav navbar-nav navbar-right">
                  <li className="nav-item">
                    <Link to={"/profile"}>Profile</Link>
                  </li>
                  <li className="nav-item">
                    <Link to={"/upload"}>Upload</Link>
                  </li>
                  <li className="nav-item">
                    <Link to={"/dashboard"}>Dashboard</Link>
                  </li>
                  <li className="nav-item">
                    <Link to={"/logout"}>Logout</Link>
                  </li>
                  <li className="nav-item">
                    <HashLink smooth to="/#contact" className="page-scroll">
                      Contact
                    </HashLink>
                  </li>
                  </ul>
                )
              }[userCategory]
            
          )}
          
            {/* <li>
              <a href="#features" className="page-scroll">
                Features
              </a>
            </li>
            <li>
              <a href="#about" className="page-scroll">
                About
              </a>
            </li>
            <li>
              <a href="#services" className="page-scroll">
                Services
              </a>
            </li>
            <li>
              <a href="#portfolio" className="page-scroll">
                Gallery
              </a>
            </li>
            <li>
              <a href="#testimonials" className="page-scroll">
                Testimonials
              </a>
            </li>
            <li>
              <a href="#team" className="page-scroll">
                Team
              </a>
            </li>
            <li>
              <a href="#contact" className="page-scroll">
                Contact
              </a>
            </li> */}
        </div>
      </div>
    </nav>
  );
};

export default Navigation