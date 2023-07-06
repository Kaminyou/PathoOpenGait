import React from "react";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

export const Header = (props) => {
  return (
    <header id="header">
      <div className="intro">
        <div className="overlay">
          <div className="container">
            <div className="row">
              <div className="col-md-8 col-md-offset-2 intro-text">
                <h1>
                  {props.data ? props.data.title : "Loading"}
                  <span></span>
                </h1>
                <p>{props.data ? props.data.paragraph : "Loading"}</p>
                
                  <Link style={{color: 'white'}} to={"/demo"}>
                  <a
                  className="btn btn-custom btn-lg page-scroll"
                >Demo</a>{" "}</Link>
                
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
