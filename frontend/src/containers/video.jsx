import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useHistory } from "react-router";

import axios from "axios";
import swal from "sweetalert";
import UnauthorizedPage from "../components/unauthorizedPage";
import ProfilePanel from '../components/profilePanel'



function VideoPage({ token }) {
  const history = useHistory();
  let { id } = useParams();

  const [name, setName] = useState('');
  const [gender, setGender] = useState('');
  const [birthday, setBirthday] = useState('');

  const [diagnose, setDiagnose] = useState('');
  const [stage, setStage] = useState('');
  const [dominantSide, setDominantSide] = useState('');
  const [lded, setLDED] = useState('');
  const [description, setDescription] = useState('');

  const [result, setResult] = useState({});

  const infoKeyOrder = ['experiment date', 'upload date', 'trial ID'];
  const keyOrder = ['stride length', 'stride width', 'stride time', 'velocity', 'cadence', 'turn time'];

  const fetchResult = async () => {
    await axios.get("/api/user/request/result", { params: { id: id }, headers: {Authorization: 'Bearer ' + token}})
    .then((res) => {
      setResult(res.data.result)
      console.log(res.data.result)
    })
    .catch((error) => {
      console.error(error);
    });
  }

  useEffect(() => {
    fetchResult();
  }, [])

  const fetchDefault = async () => {
    try {
      const response = await axios.get("/api/user/profile/personal/uuid", {
        params: { id: id }, headers: { Authorization: 'Bearer ' + token }
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

  

  const onClick = (e) => {
    history.push({
      pathname:  "/dashboard",
    });
  }

  const [videoSrc, setVideoSrc] = useState('');

  useEffect(() => {
    fetch('/api/user/video?id=' + id, {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
      .then(response => response.blob())
      .then(blob => {
        const videoURL = URL.createObjectURL(blob);
        setVideoSrc(videoURL);
      })
      .catch(error => {
        // Handle error
        console.error('Error fetching video:', error);
      });

    return () => {
      URL.revokeObjectURL(videoSrc);
    };
  }, []);

  // if (!token) {
  //   // Render unauthorized page or redirect to unauthorized route
  //   return (
  //     <UnauthorizedPage/>
  //   )
  // }

  return (
    <div className="padding-block">
  <div className="container">
    <div className="row">
      <div className="col-xs-3 col-md-3">
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
      <div className="col-xs-4 col-md-4">
        <div className="video-container">
          <video controls src={videoSrc} style={{ width: "100%", height: "auto" }}></video>
        </div>
      </div>
      <div className="col-xs-5 col-md-5">
      <div className="panel panel-default">
        <div className="panel-heading">
          <h4>Date information</h4>
          </div>
          <div className="panel-body">
            {infoKeyOrder.map((key) => (
              <p key={key}>
                <strong>{key}:</strong> {result[key]}
              </p>
            ))}
          </div>
        <div className="panel-heading">
          <h4>Result</h4>
          </div>
          <div className="panel-body">
            {keyOrder.map((key) => (
              <p key={key}>
                <strong>{key}:</strong> {result[key]}
              </p>
            ))}
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
  );
}

export default VideoPage