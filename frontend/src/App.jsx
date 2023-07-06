import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import Navigation from "./components/navigation";
import SmoothScroll from "smooth-scroll";
import "./App.css";
import MainPage from './containers/main'
import DemoPage from './containers/demo'
import LoginPage from './containers/login'
import LogoutPage from './containers/logout'
import UploadPage from './containers/upload'
import ProfilePage from './containers/profile'
import DashBoardPage from './containers/dashboard'
import AdminPage from './containers/admin'
import ManagePage from './containers/manage'
import useToken from './components/useToken'

export const scroll = new SmoothScroll('a[href*="#"]', {
  speed: 1000,
  speedAsDuration: true,
});

function App() {

  const { token, removeToken, setToken } = useToken();

  return (
    <div>
      <Router>
        <Navigation token={token} />
        <div>
        <Switch>
          <Route exact path='/'>
            <MainPage token={token} />
          </Route>
          <Route exact path='/demo'>
            <DemoPage token={token} />
          </Route>
          <Route exact path='/login'>
            <LoginPage setToken={setToken} />
          </Route>
          <Route exact path='/logout'>
            <LogoutPage removeToken={removeToken} />
          </Route>
          <Route exact path='/upload'>
            <UploadPage token={token} />
          </Route>
          <Route exact path='/profile'>
            <ProfilePage token={token} />
          </Route>
          <Route exact path='/dashboard'>
            <DashBoardPage token={token} />
          </Route>
          <Route exact path='/admin' >
            <AdminPage token={token} />
          </Route>
          <Route exact path='/manage'>
            <ManagePage token={token} />
          </Route>
        </Switch>
      </div>
      </Router>
      
    </div>
  );
};

export default App;
