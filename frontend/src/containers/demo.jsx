import React, { useState, useEffect } from "react";
import axios from "axios";

import SimpleDashboard from '../components/simpleDashboard'
import ProfilePanel from '../components/profilePanel'

function DemoPage({ token }) {
  const [name, setName] = useState('');
  const [gender, setGender] = useState('');
  const [birthday, setBirthday] = useState('');

  const [diagnose, setDiagnose] = useState('');
  const [stage, setStage] = useState('');
  const [dominantSide, setDominantSide] = useState('');
  const [lded, setLDED] = useState('');
  const [description, setDescription] = useState('');
  const [results, setResults] = useState([]);

  const fetchDefault = async () => {
    try {
      const response = await axios.get("/api/demo/profile/personal");
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
    await axios.get("/api/demo/request/results")
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


  return (
    <div className="padding-block">
    <div className="container">
      <div className="row">
        <div className="col-md-3">
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

export default DemoPage