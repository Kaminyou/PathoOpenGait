import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import { Navigation } from "./components/navigation";
import SmoothScroll from "smooth-scroll";
import "./App.css";
import MainPage from "./containers/main"
import DemoPage from "./containers/demo";

export const scroll = new SmoothScroll('a[href*="#"]', {
  speed: 1000,
  speedAsDuration: true,
});

const App = () => {

  return (
    <div>
      <Router>
        <Navigation />
        <div>
        <Switch>
          <Route exact path='/'>
            <MainPage token={123} />
          </Route>
          <Route exact path='/demo'>
            <DemoPage token={123} />
          </Route>
        </Switch>
      </div>
      </Router>
      
    </div>
  );
};

export default App;
